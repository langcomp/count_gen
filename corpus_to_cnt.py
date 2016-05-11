# makes a basic CNT file from a corpus, where each word and its
# preceding space is a region. Assumes that space is the only thing
# between words and lumps in the word final character with the last word

from __future__ import print_function
import argparse

item_number_offset = 1
cond_num = 1
delims = [' ']

parser = argparse.ArgumentParser(description='make cnt file from corpus')
parser.add_argument('corpus_file')
args = parser.parse_args()

rf = open(args.corpus_file)
items = []
for line in rf:
    breaks = [0]
    item = line.rstrip('\n')
    for i, char in enumerate(item):#enumerate(item[:-1]): ### To generate a cnt file WITHOUT a final dummy area, use the [:-1] command instead of the current command.
        if char in delims:
            breaks.append(i)
    items.append(breaks)
rf.close()

for i, item_breaks in enumerate(items):
    item_idx = i+item_number_offset
    print(item_idx, cond_num, len(item_breaks)-1, end=' ')
    for b in item_breaks:
        print(b, end=' ')
    print()
