import sys
sys.path.append('.')
import numpy as np
import readers.pos_corpus as pcc
import pickle

def read_blocks(ifname):
    block = []
    with open(ifname) as f:
        for line in f:
            if not line.strip():
                yield block
                block = []
            block.append(line)
    yield block



def as_escaped(ifname):
    for block in read_blocks(ifname):
        if block:
            s = ''.join(block)
            s = s.encode('string-escape')
            yield s

mapping = {}
for line in open('readers/en-ptb.map'):
    coarse,fine = line.strip().split("\t")
    mapping[coarse.lower()] = fine.lower()

corpus = pcc.PostagCorpus()
train_seq = corpus.read_sequence_list_conll("../data/train-02-21.conll")
pickle.dump((corpus.word_dict, corpus.tag_dict, mapping), open('word_tag_dict_mapping.pkl','w'))

with open('encoded.txt','w') as output:
    for s in as_escaped("../data/train-02-21.conll"):
        output.write(s+'\n')
