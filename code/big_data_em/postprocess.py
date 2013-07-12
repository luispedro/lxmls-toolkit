import sys
sys.path.append('.')
import pickle
import readers.simple_sequence as ssr
import sequences.hmm as hmmc
import readers.pos_corpus as pcc
import sequences.confusion_matrix as cm
import pdb

corpus = pcc.PostagCorpus()
test_seq = corpus.read_sequence_list_conll("../data/test-23.conll")
hmm = hmmc.HMM(corpus.word_dict, corpus.tag_dict)
values = pickle.loads(open('initial-matrices.pkl').read().decode('string-escape'))
log_likelihood,hmm.initial_probabilities, hmm.transition_probabilities, hmm.emission_probabilities,hmm.final_probabilities = values
print log_likelihood

viterbi_pred_test = hmm.viterbi_decode_corpus(test_seq)
posterior_pred_test = hmm.posterior_decode_corpus(test_seq)
eval_viterbi_test =   hmm.evaluate_corpus(test_seq, viterbi_pred_test)
eval_posterior_test = hmm.evaluate_corpus(test_seq, posterior_pred_test)
