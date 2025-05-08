#!/usr/bin/env python3

import sys
import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
import random


window = 2

uninteresting_words = set()
message_sets = []
file_names = []
with open(sys.argv[1], 'r') as file_list_file:
    for line in file_list_file:
        line = line.split()
        mode = line[0]
        path = line[1]
        if mode == 'ignore': continue
        if mode != 'uninteresting-words':
            file_names += [path]
        messages = []
        with open(path.strip(), 'r') as text_file:
            if mode == 'messages':
                messages += list(text_file)
            elif mode == 'book':
                messages += [message + '.' for message in ' '.join(text_file).split('.')]
            elif mode == 'uninteresting-words':
                uninteresting_words |= set(map(lambda line: line.strip(), text_file))
            else:
                raise Exception(f"Invalid text file type \"{mode}\"")
        messages = [nltk.word_tokenize(line.strip()) for line in messages]
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


def elt(list, index):
    if len(list) > index:
        return list[index]
    return ''
        
def first(list):
    return elt(list, 0)
def rest(list):
    return list[1:]


nodes = {}
inverse_nodes = {}
starts = []
vocabulary = {}

if '' in nodes:
    del nodes['']

def train(message, nodes):
    tokens = message[:]
    tokens = ['']*(window - 1) + tokens
    for token in tokens:
        if token in vocabulary:
            vocabulary[token] += 1
        else:
            vocabulary[token] = 1
    while tokens != []:
        key = first(tokens)
        for i in range(window - 1):
            index = i + 1
            if index >= len(tokens): break
            key += ' ' + tokens[index]
        key = key.strip().lower()
        value = elt(tokens, window)
        if key not in nodes:
            nodes[key] = []
        nodes[key] += [value]
        tokens = rest(tokens)

for message in messages:
    starts += [first(message)]
    train(message, nodes)
    train(list(reversed(message)), inverse_nodes)

print(len(vocabulary))


# def has_too_much_repetition(word):
#     first = None
#     second = None
#     for character in word:
#         if first == character and second == character:
#             return True
#         first = second
#         second = character
#     return False
# interesting_words = {}
# for word, frequency in vocabulary.items():
#     new_word = ''.join(character for character in word if character.isalpha() and character.isascii())
#     if has_too_much_repetition(word):
#         continue
#     if new_word in interesting_words:
#         interesting_words[new_word] += frequency
#     else:
#         interesting_words[new_word] = frequency
# max_interesting_word_length = max(interesting_words.values())
# interesting_words = {word
#                      for word, frequency in interesting_words.items()
#                      if frequency <= 0.0019*max_interesting_word_length}

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
    prompt = ''.join(character for character in prompt if character.isalpha() or character == ' ')
    prompt = {word for word in prompt.split(' ') if word != ''}

    seed_word_list = list(prompt & interesting_words)
    if seed_word_list:
        seed_word = random.choice(seed_word_list)
        print(f'Chose "{seed_word}"')
        matching_keys = list(filter(lambda key: seed_word in key.split(' '), nodes.keys()))
    else:
        matching_keys = []

    def make_chain(nodes, initial_chain, starts):
        choices = starts
        chain = initial_chain
        iterations = 0
        max_iterations = random.randint(50, 100)
        while choices:
            if iterations >= max_iterations:
                break
            choice = random.choice(choices)
            if choice is None or choice == '':
                break
            local_window = window
            if len(chain) < window - 1:
                local_window = len(chain) + 1
            key = choice
            for i in range(local_window - 1):
                key = chain[-1-i] + ' ' + key
                # key = ' '.join(chain[-(window - 1):]) + ' ' + choice
            chain += [choice]
            choices = nodes[key.lower()]
            iterations += 1
        return chain
    if matching_keys:
        seed_key = random.choice(matching_keys).split(' ')
        if len(seed_key) == 1:
            reverse_choices = [seed_key[0]]
            reverse_chain = []
            forward_choices = [seed_key[0]]
            forward_chain = []
        else:
            reverse_choices = [seed_key[0]]
            reverse_chain = [seed_key[1]]
            forward_choices = [seed_key[1]]
            forward_chain = [seed_key[0]]
        # print(seed_key)
        reversed_chain = list(reversed(make_chain(inverse_nodes, reverse_chain, reverse_choices)))
        chain = make_chain(nodes, forward_chain, forward_choices)
        # print(reversed_chain)
        # print(chain)
        tokens_out = reversed_chain + chain[2:]
    else:
        tokens_out = make_chain(nodes, [], starts)
    text_out = TreebankWordDetokenizer().detokenize(tokens_out)
    print(text_out)
    # print()
    return text_out.replace('\\n', '\n').strip()


prompt = ' '.join(sys.argv[2:])

print('READY')
print(len(nodes))
for i in range(100):
    do_bot(prompt)
# train(prompt)
## Now put the prompt in the data file for this channel.
