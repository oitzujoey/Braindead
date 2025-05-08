#!/usr/bin/env python3

import sys
import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
import random


window = 2

message_sets = []
file_names = []
with open(sys.argv[1], 'r') as file_list_file:
    for line in file_list_file:
        line = line.split()
        mode = line[0]
        path = line[1]
        if mode == 'ignore': continue
        file_names += [path]
        messages = []
        with open(path.strip(), 'r') as text_file:
            if mode == 'messages':
                messages += list(text_file)
            elif mode == 'book':
                messages += [message + '.' for message in ' '.join(text_file).split('.')]
            else:
                raise Exception(f"Invalid text file type \"{mode}\"")
        messages = [nltk.word_tokenize(line.strip()) for line in messages]
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
starts = []
vocabulary = {}

if '' in nodes:
    del nodes['']

def train(message):
    global starts
    tokens = message[:]
    starts += [first(tokens)]
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
    train(message)

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


def do_bot(text_in):
    prompt = set(text_in.split(' '))
    # interesting_words_in_prompt = {word for word in prompt if word in interesting_words}
    # print(f'interesting_words_in_prompt {interesting_words_in_prompt}')
    def groom_choices(choices):
        new_choices = set()
        for choice in choices:
            new_choice = ''.join(character for character in choice if character.isalpha() and character.isascii())
            new_choices |= {new_choice.lower()}
        # print(new_choices)
        return new_choices
    choices = starts
    chain = []
    iterations = 0
    max_iterations = random.randint(50, 100)
    while choices:
        if iterations >= max_iterations:
            break
        # print(prompt)
        limited_selection = list(prompt & groom_choices(choices))
        # print(limited_selection)
        if limited_selection:
            choice = random.choice(limited_selection)
        else:
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
    text_out = TreebankWordDetokenizer().detokenize(chain)
    print(text_out)
    return text_out.replace('\\n', '\n').strip()


prompt = ' '.join(sys.argv[2:]).lower()
prompt = ''.join(character for character in prompt if character.isalpha() or character == ' ')
prompt = [word for word in prompt.split(' ') if word != '']
print(f'prompt: {prompt}')
print(f'Recognized words {[word for word in prompt if word in vocabulary.keys()]}')

print('READY')
print(len(nodes))

for i in range(100):
    do_bot(' '.join(prompt))
train(prompt)
## Now put the prompt in the data file for this channel.
