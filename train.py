import os
import re
import random
import dill
import argparse


class TextGenerator:
    def __init__(self, n=2):
        """Initialize model with length of ngram and empty dict of previous_next words"""
        self.n = n
        self.word_chain = {}

    def fit(self, path, text=None):
        """Take text or path to directory with texts and update model's wordchain"""
        if not text:
            text = self.__get_content(path)
        tokenized = self.__preprocess(text)
        prev_next = self.__ngrams(tokenized)
        self.__update_word_chain(prev_next)

    def generate(self, words_number, start=None):
        """Generate text word by word"""
        # take user's start word and preprocess it or generate random
        if not start:
            start = random.choice(list(self.word_chain))
        # add prefixes if user input does not contain enough words
        elif len(self.__preprocess(start)) < self.n - 1:
            for i in list(self.word_chain):
                if self.__preprocess(start)[0] == i[0]:
                    start = i
                    break
        else:
            start = self.__preprocess(start)
        # unpack tuple of pref
        words = [*start]
        # pref is last n -1 words of our text
        for _ in range(words_number):
            pref = tuple(words[-self.n + 1:])
            try:
                # predict next word on probability from word chain
                start = random.choices(
                            population=list(self.word_chain[pref].keys()),
                            weights=list(self.word_chain[pref].values()))
                words.append(*start)
            # if ngram does not exist in model.word_chain, program will not break
            except KeyError:
                # get first prefix from random ngram
                start = random.choice(list(self.word_chain))[0]
                words.append(start)
        return ' '.join(words)

    def __update_word_chain(self, other):
        """Take new wordchain and update model's wordchain"""
        # iterate over pref in model's wordchain
        for pref in self.word_chain:
            if pref in other:
                self.word_chain[pref] = self.__concat_dict(self.word_chain[pref], other[pref])
        # iterate over pref in new wordchain
        for pref in other:
            if pref not in self.word_chain:
                self.word_chain[pref] = other[pref]

    def __ngrams(self, tokens):
        """Get dictionary of prefixes and next words with their frequency"""
        #  get ngrams of given length n
        ngrams = []
        for i in range(len(tokens) - (self.n - 1)):
            ngrams.append((tokens[i: i + self.n]))
        prefixes = set(ngram[:self.n - 1] for ngram in ngrams)  # unique prefixes
        prev_next_dictionary = {}
        # iterate over prefixes and ngrams
        for pref in prefixes:
            next_words = []
            for ngram in ngrams:
                # split ngram to previous words and next word
                (*previous_words, next_word) = ngram
                previous_words = tuple(previous_words)
                #  if ngram starts with prefix, append last word of ngram to list of possible next words
                if previous_words == pref:
                    next_words.append(next_word)
                    # get dictionary with frequency of possible next words
                    frequency_dict = {word: next_words.count(word) for word in next_words}
                    prev_next_dictionary[previous_words] = frequency_dict
        return prev_next_dictionary

    @staticmethod
    def __preprocess(some_str):
        some_str = some_str.lower()
        # pattern to match any sequence of cyrillic letters
        # sequence might be separated by hyphen
        pattern = re.compile(r"""
                        [а-я]+      #   part before hyphen     
                            (            #   first group: hyphen and part after hyphen (optional)
                        -             
                        [а-я]+  
                            )*
                     """, re.VERBOSE)
        tokens = re.finditer(pattern, some_str)
        return tuple(i.group(0) for i in tokens)

    @staticmethod
    def __concat_dict(one, another):
        """Create new dict with keys from two dict and values as sum of values of corresponding keys"""
        keys = set(list(one) + list(another))
        new = {key: one.get(key, 0) + another.get(key, 0) for key in keys}
        return new

    @staticmethod
    def __get_content(path):
        """Read all files in directory and return their content as one string"""
        files = os.listdir(path)
        content = []
        for file_path in files:
            abs_path = os.path.join(path, file_path)
            with open(abs_path) as file:
                content.append(file.read())
        return ' '.join(content)


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--input-dir', type=str, help='path to directory with text files')
    parser.add_argument('-m', '--model', type=str, required=True, help='path to save model')
    args = parser.parse_args()
    # specify length of ngram
    model = TextGenerator(3)
    if args.input_dir:
        model.fit(args.input_dir)
    else:
        # read text from stdin
        text = input()
        model.fit(path=None, text=text)
    # save model
    with open(args.model, 'wb') as files:
        dill.dump(model, files)
