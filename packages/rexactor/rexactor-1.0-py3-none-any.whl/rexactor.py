import sys
import os
from grex import *
from trex import *
from operators import *
import pandas as pd
import tapcap


def generate(pysharkList, threshold1, threshold2):
    count = 0

    #init lists to be used
    tokenList = []
    posList = []

    #init single byte token list
    singleByteTokens = []

    #init prefix and suffix lists
    prefixList = []
    suffixList = []

    print("Mining tokens...")
    posList = track_positions(pysharkList)

    #reverse the packets
    revPack = reverse_packets(pysharkList)

    #make certain reverse tokens and track their (reverse) positions
    #revTokenList = make_tokens(revPack, 1, 1, 1, 2)
    #revPosList = track_positions(revPack)

    prefixList = make_tokens(pysharkList, threshold1, 1, 1, 2)
    suffixList = make_tokens(pysharkList, threshold2, 1, 1, 2)

    prefixes = find_prefixes(pysharkList, prefixList)
    suffixes = find_suffixes(pysharkList, suffixList)

    for item in prefixes:
        if item in suffixes:
            suffixes.remove(item)

    #CHOICE operators, start with the prefix if there is any
    prefix = match_beginning_operator(choice_operator(prefixes))
    if prefix == "^()":
        prefix = ""

    #build suffix
    suffix = match_end_operator(choice_operator(suffixes))
    if suffix == "()$":
        suffix = ""

    #print("Single Byte Tokens Created: ", singleByteTokens)
    print("Prefixes: ", prefix)
    print("Suffixes: ", suffix)

    #remove max length of prefix/suffix from string
    splice_prefix(pysharkList, prefixes)
    splice_suffix(pysharkList, suffixes)

    print("aligning...")
    regex = align(pysharkList)
    regexfinal = removeStars(regex)
    regex_string = ""
    result = ""

    escaped_regex = extraBack(regex_string.join(regexfinal))
    result = prefix + escaped_regex + suffix
    print("Regex: " + str(result))

def main(filepath, preThres, sufThres):

    colnames=["frame_number", "time", "highest_protocol", "l4_protocol", "text", "src_ip", "src_port", "dst_ip", "dst_port", "len", "ipflags", "tos", "bytes"]
    file = pd.read_csv(filepath, names=colnames, delimiter="|", header=None)
    pysharkList = [i for i in list(file["text"]) if i != '']
    count = 0

    generate(pysharkList, preThres, sufThres)

if __name__ == "__main__":
    main()
