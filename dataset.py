'''

The main Dataset class for the entire model is written here.
It keeps track of train_data and the corpus and everything to do
with the book dataset. Also supports multithreading.

'''


import os
import time
import string
import asyncio
import warnings

from torch.utils.data import Dataset
from typing import List, Optional, Union

warnings.filterwarnings('ignore')

import logger


class BookCorpusDataset(Dataset):

    '''
    Class:
        - The main dataset which contains all the required data for training
        the model.
        - Supports multiprocessing.
    Args:
        chunk_size:
            - The amount of words in a batch.
            - This is set to None, when just_corpus=True.
        just_corpus:
            - Whether the dataset should only prepare the corpus (when not training).
            - You can't run generate_batches() if this is set to True.
        save_corpus:
            - Whether to save the corpus in a file or not.
        cache_train_data:
            - Whether or not to save the training data instead of processing it every time
            at runtime.
        train_data_file:
            - The filename to load the training data from.
        corpus_from_file:
            - The filename to load the corpus from.
    '''

    def __init__(self,
                 chunk_size=3,
                 just_corpus=False,
                 save_corpus=True,
                 cache_train_data=False,
                 train_data_file: Optional[str]=None,
                 corpus_from_file: Optional[str]=None):
        try:
            assert bool(train_data_file) == bool(corpus_from_file)
        except AssertionError:
            raise ValueError('''If train_data_file is None, then so should the corpus_from_file.
            corpus_from_file is dependant on train_data_file.''')

        start = time.time()
        self.n_batches = 500
        self._just_corpus = just_corpus
        self.loop = asyncio.get_event_loop()
        self.chunk_size = chunk_size if not self._just_corpus else None

        if just_corpus:
            return

        self.file_contents = self._run_load_corpus(True)

        self.prep_data = []

    def generate_batches(self):
        try:
            assert not self._just_corpus
        except AssertionError:
            raise AssertionError('If you want to run: generate_batches(), you must set (just_corpus = False) in the constructor.')

        beginning = 0
        last_idx = self.chunk_size

        for i in range(self.n_batches):
            sample = self._get_batch(beginning, last_idx)
            self.prep_data.append(sample)

            beginning = last_idx
            last_idx += self.chunk_size

    def _run_load_corpus(self, just_contents=False):
        return self.loop.run_until_complete(load_corpus('data', just_contents=just_contents))

    def _get_batch(self, beginning, last_idx):
        starting_phrase = self.train_data[beginning:last_idx]
        target_word = self.train_data[beginning + 1:last_idx + 1]

        return (starting_phrase, target_word)

    def __getitem__(self, index):
        return self.prep_data[index]

    def __len__(self):
        return len(self.prep_data)



async def load_corpus(text_file_dir, **kwargs) -> Union[list, str]:
    corpus = ''
    files_str = os.listdir(text_file_dir)
    files = [open('data/' + f, 'r', encoding='utf-8') for f in files_str]

    logger.INFO('Collecting tokens from:\n')
    files_str.sort(key=len)

    for c in files_str:
        logger.info(c)
    print()

    for f in files:
        corpus += f.read()

    return corpus


def split_tokens(text: str):
    words = text.split(' ')
    tokens = []

    for word in words:
        tokens.append(' ')
        # remove special chars
        token = ''
        for char in word:
            if char.isalnum(): token += char
        
        tokens.append(token)
        
        # check if special chars are in the token and add them
        for char in word:
            if char in string.punctuation:
                tokens.append(char)
    
    # remove first redundant space
    tokens = tokens[1:]

    return tokens


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # start = time.time()
    # corpus, text = loop.run_until_complete(load_corpus('data'))
    # end = time.time()
    # print(end - start)
    split_tokens('hello. ok! or ok dave')
