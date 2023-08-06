from __future__ import unicode_literals, print_function
from efficiency.log import show_var


class NLP:
    def __init__(self, disable=['ner', 'parser', 'tagger', "lemmatizer"]):
        import spacy

        self.nlp = spacy.load('en_core_web_sm', disable=disable)
        try:
            self.nlp.add_pipe(self.nlp.create_pipe('sentencizer'))
        except:
            self.nlp.add_pipe('sentencizer')

    def sent_tokenize(self, text):
        doc = self.nlp(text)
        sentences = [str(sent).strip() for sent in doc.sents]
        return sentences

    def word_tokenize(self, text, lower=False):  # create a tokenizer function
        if text is None: return text
        text = ' '.join(text.split())
        if lower: text = text.lower()
        toks = [tok.text for tok in self.nlp.tokenizer(text)]
        return ' '.join(toks)

    @staticmethod
    def sent_bleu(ref_list, hyp):
        from nltk.translate import bleu
        from nltk.translate.bleu_score import SmoothingFunction
        smoothie = SmoothingFunction().method4
        refs = [ref.split() for ref in ref_list]
        hyp = hyp.split()
        return bleu(refs, hyp, smoothing_function=smoothie)


class Translator:
    def __init__(self, cache_file_pattern='.cache_{src}2{tgt}.json', load_translator=True):
        self.cache_file_pattern = cache_file_pattern
        from collections import defaultdict
        self.cache = defaultdict(dict)
        if load_translator:
            from googletrans import Translator
            self.translator = Translator()

    def load_cache(self):
        from efficiency.log import fread
        fread(self.cache_file)

    def translate(self, text, src_lang='en', tgt_lang='de', verbose=True, enable_cache=False):
        if src_lang == tgt_lang:
            return text

        if enable_cache:
            this_cache_file = self.cache_file_pattern.format(src=src_lang, tgt=tgt_lang)
            lang_pair = tuple((src_lang, tgt_lang))
            if lang_pair not in self.cache:
                import os
                if os.path.exists(this_cache_file):
                    from efficiency.log import fread
                    self.cache[lang_pair] = fread(this_cache_file)

            if text in self.cache[lang_pair]:
                translated_text = self.cache[lang_pair][text]
            else:
                translated_text = self.translator.translate(text, src=src_lang, dest=tgt_lang).text
                self.cache[lang_pair][text] = translated_text
                from efficiency.log import fwrite
                fwrite(self.cache[lang_pair], this_cache_file)
        else:
            translated_text = self.translator.translate(text, src=src_lang, dest=tgt_lang).text

        if translated_text == text:
            print("[Warn] Translation is failed. You have very likely reached the limit of the `googletrans' library. "
                  "Try to wait for a while or change your IP address. Alternatively, you can also edit the source "
                  "code here to change it to Google cloud API by setting up your credentials.")
            import pdb;
            pdb.set_trace()
        if verbose:
            from efficiency.log import show_var
            show_var(['text', 'translated_text', ])
        return translated_text


class Chatbot:
    model_version2engine = {
        'gpt4': "gpt-4",
        'gpt3.5': "gpt-3.5-turbo",
        'gpt3': "text-davinci-003",

        'gpt3.043': "text-davinci-003",
        'gpt3.042': "text-davinci-002",
        'gpt3.041': "text-davinci-001",
        'gpt3.04': "davinci",
        'gpt3.03': "curie",
        'gpt3.02': "babbage",
        'gpt3.01': "ada",

    }
    engine2pricing = {
        "gpt-3.5-turbo": 0.002,
        "gpt-4-32k": 0.12,
        "gpt-4": 0.06,
        "text-davinci-003": 0.0200,
        "text-davinci-002": 0.0200,
        "text-davinci-001": 0.0200,
        "davinci": 0.0200,
        "curie": 0.0020,
        "babbage": 0.0005,
        "ada": 0.0004,
    }

    def __init__(self, model_version='gpt3.5', max_tokens=100, output_file='.cache_gpt_responses.csv',
                 system_prompt="You are a helpful assistant.",
                 openai_key_alias='OPENAI_API_KEY', ):
        import os
        openai_api_key = os.environ[openai_key_alias]

        self.model_version = model_version
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.output_file = output_file
        self.gpt_files = [output_file]

        import openai
        openai.api_key = openai_api_key
        self.openai = openai
        self.num_tokens = []
        self.cache = self.load_cache()
        # self.list_all_models()
        self.clear_dialog_history()

    def clear_dialog_history(self):
        self.dialog_history = [
            {"role": "system", "content": self.system_prompt},
            # {"role": "user", "content": "Who won the world series in 2020?"},
            # {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        ]

    def dialog_history_to_str(self, disable_system_role=False):
        dialog_history_text = []
        if not disable_system_role:
            dialog_history_text += [self.system_prompt]
        for turn in self.dialog_history:
            if turn['role'] == 'user':
                prefix = 'Q'
            elif turn['role'] == 'assistant':
                prefix = 'A'
            else:
                continue
            this_text = f"{prefix}: {turn['content']}"
            if prefix == 'A':
                this_text += '\n'
            dialog_history_text.append(this_text)
        dialog_history_text = '\n'.join(dialog_history_text) + '\nA:'
        return dialog_history_text

    def list_all_models(self):
        model_list = self.openai.Model.list()['data']
        model_ids = [x['id'] for x in model_list]
        model_ids.sort()
        print(model_ids)
        import pdb;
        pdb.set_trace()

    @property
    def _total_cost(self):
        return sum(self.num_tokens) // 1000 * self.engine2pricing[self.engine]

    def print_cost(self):
        print(f"[Info] Spent ${self._total_cost} for {sum(self.num_tokens)} tokens.")

    def save_cache(self, question, response_text):
        if not (question in self.cache):
            self.cache[question] = response_text
            datum = [{
                'pred': response_text,
                'query': question,
            }]
            from efficiency.log import write_dict_to_csv
            write_dict_to_csv(datum, self.output_file, mode='a')

    def load_cache(self):
        cache = {}
        from efficiency.log import fread
        for file in self.gpt_files:
            data = fread(file, verbose=False)
            cache.update({i[f'query{q_i}']: i[f'pred{q_i}'] for i in data
                          for q_i in list(range(10)) + ['']
                          if f'query{q_i}' in i})
        return cache

    def ask(self, *args, **kwargs):
        import openai
        try:
            return self.raw_query(*args, **kwargs)
        except openai.error.InvalidRequestError:
            import pdb;
            pdb.set_trace()
            if len(self.dialog_history) > 10:
                import pdb;
                pdb.set_trace()
            for turn_i, turn in enumerate(self.dialog_history):
                if turn['role'] == 'assistant':
                    turn['content'] = turn['content'][:1000]

        except openai.error.RateLimitError or openai.error.APIError:
            sec = 100
            print(f'[Info] openai.error.RateLimitError. Wait for {sec} seconds')
            self.print_cost()
            '''
            Default rate limits for gpt-4/gpt-4-0314 are 40k TPM and 200 RPM. Default rate limits for gpt-4-32k/gpt-4-32k-0314 are 80k PRM and 400 RPM. 
            https://platform.openai.com/docs/guides/rate-limits/overview
            '''

            import time
            time.sleep(sec)
            return self.ask(*args, **kwargs)
        except:
            sec = 100
            print(f'[Info] Unknown error. Wait for {sec} seconds')
            self.print_cost()
            '''
            Default rate limits for gpt-4/gpt-4-0314 are 40k TPM and 200 RPM. Default rate limits for gpt-4-32k/gpt-4-32k-0314 are 80k PRM and 400 RPM. 
            https://platform.openai.com/docs/guides/rate-limits/overview
            '''

            import time
            time.sleep(sec)
            return self.ask(*args, **kwargs)

    def raw_query(self, question,
                  turn_off_cache=False,
                  continued_questions=False,
                  sentence_completion_mode=False,
                  max_tokens=None, stop_sign="\nQ: ",
                  model_version=[None, 'gpt3', 'gpt3.5', 'gpt4'][0],
                  engine=[None, "text-davinci-003", "gpt-3.5-turbo", "gpt-4-32k-0314", "gpt-4-0314", "gpt-4"][0],
                  enable_pdb=False, verbose=True, only_response=True, disable_system_role=False,
                  save_cache_with_system_role=False,
                  ):
        if model_version is not None:
            engine = self.model_version2engine[model_version]
        elif engine is not None:
            engine = engine
        else:
            engine = self.model_version2engine[self.model_version]

        max_tokens = self.max_tokens if max_tokens is None else max_tokens
        verbose = True if enable_pdb else verbose

        self.engine = engine
        if_newer_engine = engine.startswith('gpt-3.5') or engine.startswith('gpt-4')

        if not continued_questions:
            self.clear_dialog_history()

        self.dialog_history.append({"role": "user", "content": question}, )
        if not if_newer_engine:
            if sentence_completion_mode:
                if disable_system_role:
                    prompt = question
                else:
                    prompt = '\n'.join([self.system_prompt, question])
            else:
                prompt = self.dialog_history_to_str(disable_system_role=disable_system_role)
        else:
            prompt = question

        cache_input = prompt if save_cache_with_system_role else question
        if enable_pdb:
            import pdb;
            pdb.set_trace()
        if (cache_input in self.cache) & (not turn_off_cache):
            response_text = self.cache[cache_input]
            if not if_newer_engine: response_text = response_text.split(stop_sign, 1)[0]
            if verbose: print(f'[Info] Using cache for {cache_input}')
        else:
            openai = self.openai
            if if_newer_engine:
                response = openai.ChatCompletion.create(
                    model=engine,
                    temperature=0,
                    max_tokens=max_tokens,
                    messages=self.dialog_history,
                )
                response_text = response['choices'][0]['message']['content']
            else:
                response = openai.Completion.create(
                    model=engine,
                    # prompt=[question],
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=0,
                    stop=stop_sign,
                )
                response_text = response['choices'][0]['text']
            self.num_tokens.append(response['usage']["total_tokens"])
            response_text = response_text.strip()
            if verbose: self.print_cost()

        if if_newer_engine:
            output = f"S: {self.dialog_history[0]['content']}\n\n" \
                     f"Q: {self.dialog_history[-1]['content']}\n\nA: {response_text}\n"
        else:
            output = f"{prompt} {response_text}\n"

        if verbose:
            print()
            print(output)

        self.dialog_history.append({"role": "assistant", "content": response_text}, )

        if enable_pdb:
            import pdb;
            pdb.set_trace()

        self.save_cache(cache_input, response_text)

        if only_response:
            return response_text
        return response_text, output


def main():
    raw_text = 'Hello, world. Here are two people with M.A. degrees from UT Austin. This is Mr. Mike.'
    nlp = NLP()
    sentences = nlp.sent_tokenize(raw_text)
    words = nlp.word_tokenize(sentences[0], lower=True)
    show_var(['sentences', 'words'])

    chat = Chatbot()
    query = 'What is the best way to learn Machine Learning?'
    response = chat.ask(query)


if __name__ == '__main__':
    main()
