from os import path
from collections import OrderedDict
import pandas as pd
from efficient_apriori import apriori

def reverse_packets(packets):
    x = 0
    i = 0
    p2 = []
    tempstr = " "
    while i < len(packets):
        temp = packets[i]
        temp = temp[::-1]
        p2.append(temp)
        x += 1
        i += 1
    return p2

def load_file(filepath, col_name):
    if not path.exists(filepath):
        print("CSV file not found. Please run TapCap first to create tabularized data.")
        exit()
    df = pd.read_csv(filepath)
    return filepath[col_name].tolist()

def make_tokens(input_data, min_sup, min_conf, max_len, win_size):
    tokens = {}
    old_itemsets = {}

# Holds the list of transactions
# example: [("apple, "orange", "banana"),
#           ("orange", "banana", "clementine"),
#           ("apple", "orange")]
#
# The apriori algorithm as described by Agarwal will consider each of the lists
# as "transactions" and compare the list to one another to calculate confidence,
# support, lift, and conviction.
#
# We will start the apriori loop here with a min window size and break when we can
# no longer make item sets.
    while True:
        # loop through payloads
        transactions = []
        for input_string in input_data:
            end = win_size
            start = 0
            potential_tokens = []
            # increment our sliding window
            #
            # round 1:
            # '|P|O|S|T| |/| |H|T|T|P| |/| |1|.|1|'
            # |winsize|
            #
            # round 2:
            # '|P|O|S|T| |/| |H|T|T|P| |/| |1|.|1|'
            #    |winsize|
            #
            # round end:
            # '|P|O|S|T| |/| |H|T|T|P| |/| |1|.|1|'
            #                            |winsize|
            #
            # Remember for each loop from the 'while', winsize increases for longer substrings.
            while end <= len(input_string):
                # add the windowed substring to list of potentials.
                potential_tokens.append(str(input_string[start:end]))
                end = end + 1
                start = start + 1
            # add the potentials to the transactions
            transactions.append(potential_tokens)

        itemsets = {}
        rules = {}
        # Prune the substrings to only the frequent ones using apriori item sets.
        itemsets, rules = apriori(transactions, min_support=min_sup, min_confidence=min_conf, max_length=max_len)
        # Prune the itemsets - if any old/shorter tokens are substrings of the new strings in the itemsets,
        # remove the old ones and keep the more specific ones if the support is the same.
        #
        # data = ["the cat makes cupcakes", "the cat eats cupcakes"]
        # tokens = ["cup", "cake", "cat", "the"]
        # itemsets = ["cupcake", "the cat"]
        # tokens (post-loop) = ["cupcake", "the cat"]
        #
        # In the same idea, if a new token has a support greater than the min but there already
        # exists a token that is a substring of it and it has greater support, keep the more
        # generalized version.
        total_cov = 0.0
        support = 0.0

        for item in itemsets.values():
            for token in list(item.keys()):
                doNotAdd = False
                for old_token in list(tokens.keys()):
                    support_diff = ((tokens[old_token] - item[token])/tokens[old_token])
                    # get rid of shorter tokens with the same support
                    if old_token in token[0] and support_diff < 0.001:
                        tokens.pop(old_token)
                    # do not add the more specific tokens with significantly less support than a current one
                    elif old_token in token[0] and support_diff > 0.05:
                        doNotAdd = False
                if not doNotAdd:
                    tokens[token[0]] = item[token]
        # If no more frequent item sets can be generated, return
        if len(itemsets) == 0:
            return tokens
        # Increment window size and repeat
        win_size = win_size + 1

# Returns a list of dictionaries where each entry represents the character and
# frequency of that character across all packets at that index. We use this to
# find single byte tokens and character ranges.

def track_positions(input_data):
    # keep track of list size
    last_index = 0
    positions = []
    class_frequencies = []
    num_inputs = len(input_data)

    # loop through all the inputs
    for input_string in input_data:
        curr_index = 0

        for input_char in input_string:
            # if this is the longest string we've had yet, add a dictionary
            if (curr_index >= last_index):
                last_index = curr_index
                position_dictionary = {}
                position_dictionary[input_char] = 1
                positions.append(position_dictionary)
            # else, check if we have seen this char or not in the dictionary
            else:
                # increment if seen
                if input_char in positions[curr_index]:
                    positions[curr_index][input_char] = positions[curr_index][input_char] + 1
                # else make a dictionary for it
                else:
                    positions[curr_index][input_char] = 1
            curr_index = curr_index + 1

    single_byte_tokens = {}
    # convert counts to frequencies
    for i in range (len(positions) - 1):
        for key in list(positions[i].keys()):
            positions[i][key] = positions[i][key]/num_inputs
            # if frequency == 1.0, single byte token
            if positions[i][key] == 1:
                single_byte_tokens[key] = i

    return positions, single_byte_tokens

# Takes a list of tokens and data as input and returns a list of dictionaries
# where the token position in the input string corresponds to the beginning of where
# it is found. ex: [{'POST': 0, 'HTTP/': 7}, {'POST': 0, 'HTTP/': 7}, {'HTTP/': 17}, {'HTTP/': 22}]
def track_token_positions(input_data, tokens):
    positions = []
    # loop through the inputs
    for input_string in input_data:
        position_dictionary = OrderedDict()
        # loop through the tokens
        for token in tokens:
            if token in input_string:
                position_dictionary[input_string.index(token)] = token;
        positions.append(position_dictionary);
    return positions

# return a list of tokens which are positionally found at the beginning, i.e. prefix
def find_prefixes(input_data, tokens):
    positions = track_token_positions(input_data, tokens)
    prefixes = {}
    for dictionary in positions:
        if 0 not in dictionary.keys():
            continue
        prefixes[dictionary[0]] = 1
    return list(prefixes.keys())

    # We may want to count prefixes which cover a vast majority of cases instead of all,
    # so this code allows a noise threshold.
    count = 0
    empty_list = []
    for prefix in prefixes:
        count += tokens[prefix]
        if (len(input_data) - count)/len(input_data) > 0.01:
            return empty_list
        else:
            return list(prefixes.keys())

# return a list of tokens which are positionally found at the end, i.e. suffix
def find_suffixes(input_data, tokens):
    reverse_input = []
    reverse_tokens = {}
    for item in input_data:
        reverse_input.append(item[::-1])
    for token in tokens:
        reverse_tokens[token[::-1]] = tokens[token]
    reversed_result = find_prefixes(reverse_input, reverse_tokens)
    result = []
    for item in reversed_result:
        result.append(item[::-1])
    return result

# remove the found prefix from the input data. If we don't do this, alignment
# fixates on the prefix.
def splice_prefix(input_data, prefixes):
    for i in range(len(input_data)):
        for prefix in prefixes:
            if prefix in input_data[i]:
                input_data[i] = input_data[i][len(prefix):]

# remove the found suffix from the input data. If we don't do this, alignment
# fixates on the suffix.
def splice_suffix(input_data, suffixes):
    for i in range(len(input_data)):
        for suffix in suffixes:
            if suffix in input_data[i]:
                input_data[i] = input_data[i][:len(input_data[i]) - len(suffix)]
