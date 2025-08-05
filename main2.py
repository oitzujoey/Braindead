#!/usr/bin/env python3

import sys
import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
import random


window = 10

uninteresting_words = set()
bad_words = set()
bad_training_phrases = set()
message_sets = []
file_names = []
with open(sys.argv[1], 'r') as file_list_file:
    for line in file_list_file:
        line = line.split()
        mode = line[0]
        path = line[1]
        if mode == 'ignore': continue
        if mode not in ['uninteresting-words', 'bad-training-phrases', 'bad-words']:
            file_names += [path]
        messages = []
        with open(path.strip(), 'r') as text_file:
            if mode == 'messages':
                messages += list(text_file)
            elif mode == 'book':
                messages += [message + '.' for message in ''.join(text_file).split('.')]
            elif mode == 'uninteresting-words':
                uninteresting_words |= set(map(lambda line: line.strip(), text_file))
            elif mode == 'bad-words':
                bad_words |= set(map(lambda line: line.strip(), text_file))
            elif mode == 'bad-training-phrases':
                bad_training_phrases |= set(map(lambda line: line.strip('\n'), text_file))
            else:
                raise Exception(f"Invalid text file type \"{mode}\"")
        messages = [list(line.strip().split()) for line in messages]
        if messages:
            message_sets += [messages]
# message_set_lengths = []
# for message_set in message_sets:
#     message_set_lengths += [len(message_set)]
# max_message_set_length = max(message_set_lengths)
# message_set_weights = []
# new_message_sets = []
# for file_name, message_set, length in zip(file_names, message_sets, message_set_lengths):
#     weight = max_message_set_length//length - 1
#     print(f'{weight} {file_name}')
#     new_message_sets += [message_set*(weight + 1)]
# message_sets = new_message_sets
messages = []
for message_set in message_sets:
    messages += message_set


class NotFound: pass
class End: pass


def elt(list, index):
    if len(list) > index:
        return list[index]
    return End
        
def first(list):
    return elt(list, 0)
def rest(list):
    return list[1:]


dictionaries = list(map(lambda _: {}, [None]*window))
starts = []
vocabulary = set()

def train(message:str, dictionaries:list):
    for dictionary_index, dictionary in enumerate(dictionaries):
        for token_index, token in enumerate(message):
            associated_token = elt(message, token_index + dictionary_index + 1)
            if token not in dictionary: dictionary[token] = {}
            if associated_token not in dictionary[token]: dictionary[token][associated_token] = 0.0
            dictionary[token][associated_token] += 1.0 # * (len(dictionaries) - dictionary_index)/len(dictionaries)
                

for message in messages:
    for bad_training_phrase in bad_training_phrases:
        if bad_training_phrase in ''.join(message):
            break
    else:
        starts += [first(message)]
        vocabulary |= set(message)
        train(message, dictionaries)

def groom_choices(choices):
    new_choices = set()
    for choice in choices:
        new_choice = ''.join(character for character in choice if character.isalpha() and character.isascii())
        new_choices |= {new_choice.lower()}
    new_choices -= uninteresting_words
    # print(new_choices)
    return new_choices
interesting_words = groom_choices(vocabulary)

def do_bot(text_in):
    prompt = text_in.lower()
    # prompt = ''.join(character for character in prompt if character.isalpha() or character == ' ')
    prompt = [word for word in prompt.split() if word != '']

    def make_chain(dictionaries, initial_chain, starts):
        choices = starts
        chain = initial_chain[:]
        iterations = 0
        max_iterations = random.randint(500, 1000)
        choice = random.choice(choices)
        while True:
            if iterations >= max_iterations: break
            if choice is End: break
            chain += [choice]
            local_window = window
            # if len(chain) < window - 1:
            #     local_window = len(chain) + 1
            key = choice

            choices_dicts = map(lambda dictionary: dictionary[key], dictionaries)
            choices_dict = {}
            for choices in choices_dicts:
                for choice, count in choices.items():
                    if choice not in choices_dict: choices_dict[choice] = 0
                    choices_dict[choice] += count
            words_list = list(choices_dict.keys())
            weights_list = list(choices_dict.values())
            # for i in range(local_window - 1):
            #     key = chain[-1-i] + key
                # key = ' '.join(chain[-(window - 1):]) + ' ' + choice
            # choices = nodes[key.lower()]
            if not words_list: break
            choice = random.choices(words_list, weights=weights_list)[0]
            iterations += 1
        return chain

    not_good = True
    max_attempts = 10
    attempts = 0
    while not_good:
        if attempts >= max_attempts:
            tokens_out = []
            break
        attempts += 1
        tokens_out = make_chain(dictionaries, prompt, starts)[len(prompt):]
        not_good = False
        for token in tokens_out:
            if token in bad_words:
                not_good = True
    text_out = (' '.join(tokens_out)
                .strip()
                .replace('<@ 1364673080189915287>', '<@1364673080189915287>')
                .replace('<@ 1231818732117164072>', '<@1231818732117164072>')
                .replace('<@ 1364796115215712277>', '<@1364796115215712277>')
                .replace('<@ 358375189458976771>', '<@358375189458976771>')
                .replace('<@ 842099537841094677>', '<@842099537841094677>')
                .replace('<@ 999175607181135872>', '<@999175607181135872>')
                .replace(': mikudayo:', ':mikudayo:')
                .replace('mikudayo', ':mikudayo:')
                .replace('https: //', 'https://'))
    print(text_out)
    # print()
    return text_out.replace('\\n', '\n')


prompt = ' '.join(sys.argv[2:])

# print('READY')
# print(dictionaries)
print(len(vocabulary))
print(len(dictionaries))
for i in range(100):
    do_bot(prompt)
# train(prompt)
## Now put the prompt in the data file for this channel.
