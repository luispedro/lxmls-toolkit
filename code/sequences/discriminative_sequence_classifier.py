
import sys
import numpy as np
import matplotlib.pyplot as plt

from util.my_math_utils import *
from viterbi import viterbi
from viterbi_2 import viterbi_log
from forward_backward import forward_backward,sanity_check_forward_backward


class DiscriminativeSequenceClassifier():


    
    def __init__(self,dataset,feature_class):
        self.trained = False
        self.feature_class = feature_class
        self.nr_states = len(dataset.int_to_tag)
        self.dataset = dataset
        self.parameters = np.zeros([feature_class.nr_feats],dtype=float)
        

    def get_number_states(self):
        self.nr_states

    ################################
    ##  Build the node and edge potentials
    ## node - f(t,y_t,X)*w
    ## edge - f(t,y_t,y_(t-1),X)*w
    ## Only supports binary features representation
    ## If we have an HMM with 4 positions and transitins
    ## a - b - c - d
    ## the edge potentials have at position:
    ## 0 a - b
    ## 1 b - c
    ################################
    def build_potentials(self,sequence):
        nr_states = self.nr_states
        nr_pos = len(sequence.x)
        node_potentials = np.ones([nr_states,nr_pos],dtype=float)
        edge_potentials = np.ones([nr_states,nr_states,nr_pos-1],dtype=float)

        ## We will assume that transition features do not depend on any X information so
        ## they are the same for all positions this will speed up the code but if the features
        ## change need to uncomment the code in the main loop and comment here
        for tag_id in xrange(nr_states):
            for prev_tag_id in xrange(nr_states):
                edge_f_list = self.feature_class.get_edge_features(sequence,1,tag_id,prev_tag_id)
                #print "Edge list: tag:%i prev:%i"%(tag_id,prev_tag_id)
                #print edge_f_list
                #dot_w_f_edge = np.sum(self.parameters[edge_f_list])
                dot_w_f_edge = 0
                for fi in edge_f_list:
                    dot_w_f_edge += self.parameters[fi]
                try:
                    edge_potentials[prev_tag_id,tag_id,:] = exp(dot_w_f_edge)
                except:
                    print "overflow in exp of edge potentials"
                    print dot_w_f_edge
                    print self.parameters[edge_f_list]
                    edge_potentials[prev_tag_id,tag_id,:] = exp(0)
        #print "edge_potentials"
        #print edge_potentials
        ## Add first position
        for tag_id in xrange(nr_states):
            # Note that last pos does not care about tag in pos N
            edge_f_list = self.feature_class.get_edge_features(sequence,0,tag_id,-1)
            dot_w_f_edge = 0
            for fi in edge_f_list:
                dot_w_f_edge += self.parameters[fi]
            try:
                node_potentials[tag_id,0] *= exp(dot_w_f_edge)
            except:
                print "overflow in exp of node potentials"
                print dot_w_f_edge
                print self.parameters[edge_f_list]
                print node_potentials
                print dot_w_f_edge
                node_potentials[tag_id,0] *= exp(0)

        
        ## Add last position
        last_pos = len(sequence.x)
        for tag_id in xrange(nr_states):
            # Note that last pos does not care about tag in pos N
            edge_f_list = self.feature_class.get_edge_features(sequence,last_pos,-1,tag_id)
            dot_w_f_edge = 0
            for fi in edge_f_list:
                dot_w_f_edge += self.parameters[fi]
            try:
                node_potentials[prev_tag_id,last_pos -1] *= exp(dot_w_f_edge)
            except:
                print "overflow in exp of node potentials"
                import pdb
                pdb.set_trace()
                print dot_w_f_edge
                print self.parameters[edge_f_list]
                print node_potentials
                print dot_w_f_edge
                node_potentials[prev_tag_id,last_pos -1] *= exp(0)
                    
        #print "edge_potentials after final"
        #print edge_potentials
        for pos,word_id in enumerate(sequence.x):
            for tag_id in xrange(nr_states):
                #f(t,y_t,X)
                node_f_list = self.feature_class.get_node_features(sequence,pos,tag_id)
                #print "Node list: pos:%i tag:%i"%(pos,tag_id)
                #print node_f_list
                ##w*f - since f is only 0/1 its just the sum of active features
                
                #dot_w_f_node = np.sum(self.parameters[node_f_list,:])
                dot_w_f_node = 0
                for fi in node_f_list:
                    dot_w_f_node += self.parameters[fi]
                try:
                    node_potentials[tag_id,pos] *= exp(dot_w_f_node)
                except:
                    print "overflow in exp of node potentials"
                    print dot_w_f_node
                    print self.parameters[node_f_list]
                    node_potentials[tag_id,pos] *= 1
                
                ##Note this code is commented since we are assuming that transition features do not depende on X information
                # if(pos > 0):
                #     for prev_tag_id in all_tags:
                #         edge_f_list = self.feature_class.get_edge_features(sequence,pos,tag_id,prev_tag_id)
                #         dot_w_f_edge = np.sum(self.parameters[edge_f_list,:])
                #         edge_potentials[prev_tag_id,tag_id,pos-1] = np.exp(dot_w_f_edge)
        return node_potentials,edge_potentials


    ################################
    ##  Build the node and edge potentials on log space.
    ## node - f(t,y_t,X)*w
    ## edge - f(t,y_t,y_(t-1),X)*w
    ## Only supports binary features representation
    ## If we have an HMM with 4 positions and transitins
    ## a - b - c - d
    ## the edge potentials have at position:
    ## 0 a - b
    ## 1 b - c
    ################################
    def build_potentials_log(self,sequence):
        nr_states = self.nr_states
        nr_pos = len(sequence.x)
        node_potentials = np.zeros([nr_states,nr_pos],dtype=float)
        edge_potentials = np.zeros([nr_states,nr_states,nr_pos-1],dtype=float)


        ## We will assume that transition features do not depend on any X information so
        ## they are the same for all positions this will speed up the code but if the features
        ## change need to uncomment the code in the main loop and comment here
        for tag_id in xrange(nr_states):
            for prev_tag_id in xrange(nr_states):
                edge_f_list = self.feature_class.get_edge_features(sequence,1,tag_id,prev_tag_id)
                #print "Edge list: tag:%i prev:%i"%(tag_id,prev_tag_id)
                #print edge_f_list
                #dot_w_f_edge = np.sum(self.parameters[edge_f_list])
                dot_w_f_edge = 0
                for fi in edge_f_list:
                    dot_w_f_edge += self.parameters[fi]
                edge_potentials[prev_tag_id,tag_id,:-1] = dot_w_f_edge
        #print "edge_potentials"
        #print edge_potentials
        ## Add last position
        last_pos = len(sequence.x)-1
        for tag_id in xrange(nr_states):
            for prev_tag_id in xrange(nr_states):
                #print "Final Edge list: tag:%i prev:%i"%(tag_id,prev_tag_id)
                #print edge_f_list
                edge_f_list = self.feature_class.get_edge_features(sequence,last_pos,tag_id,prev_tag_id)
                #dot_w_f_edge = np.sum(self.parameters[edge_f_list])
                dot_w_f_edge = 0
                for fi in edge_f_list:
                    dot_w_f_edge += self.parameters[fi]
                edge_potentials[prev_tag_id,tag_id,last_pos -1] = dot_w_f_edge
                
                    
        #print "edge_potentials after final"
        #print edge_potentials
        for pos,word_id in enumerate(sequence.x):
            for tag_id in xrange(nr_states):
                #f(t,y_t,X)
                node_f_list = self.feature_class.get_node_features(sequence,pos,tag_id)
                #print "Node list: pos:%i tag:%i"%(pos,tag_id)
                #print node_f_list
                ##w*f - since f is only 0/1 its just the sum of active features
                
                #dot_w_f_node = np.sum(self.parameters[node_f_list,:])
                dot_w_f_node = 0
                for fi in node_f_list:
                    dot_w_f_node += self.parameters[fi]
                node_potentials[tag_id,pos] = dot_w_f_node
                ##Note this code is commented since we are assuming that transition features do not depende on X information
                # if(pos > 0):
                #     for prev_tag_id in all_tags:
                #         edge_f_list = self.feature_class.get_edge_features(sequence,pos,tag_id,prev_tag_id)
                #         dot_w_f_edge = np.sum(self.parameters[edge_f_list,:])
                #         edge_potentials[prev_tag_id,tag_id,pos-1] = np.exp(dot_w_f_edge)
        return node_potentials,edge_potentials


    
    def get_seq_prob(self,seq,node_potentials,edge_potentials):
        nr_pos = len(seq.x)
        #print "Node %i %i %.2f"%(0,seq.y[0],node_potentials[0,seq.y[0]])
        value = node_potentials[0,seq.y[0]]
        for pos in xrange(1,nr_pos):
            value *= node_potentials[pos,seq.y[pos]]
            #print "Node %i %i %.2f"%(pos,seq.y[pos],node_potentials[pos,seq.y[pos]])
            value *= edge_potentials[pos-1,seq.y[pos-1],seq.y[pos]]
            #print "Edge Node %i %i %i %.2f"%(pos-1,seq.y[pos-1],seq.y[pos],edge_potentials[pos-1,seq.y[pos-1],seq.y[pos]])
        return value
    
    def forward_backward(self,seq):
        node_potentials,edge_potentials = self.build_potentials(seq)
        forward,backward = forward_backward(node_potentials,edge_potentials)
        #print sanity_check_forward_backward(forward,backward)
        return forward,backward
        

    ###############
    ## Returns the node posterios
    ####################
    def get_node_posteriors(self,seq):
        nr_states = self.nr_states
        node_potentials,edge_potentials = self.build_potentials(seq)
        forward,backward = forward_backward(node_potentials,edge_potentials)
        #print sanity_check_forward_backward(forward,backward)
        H,N = forward.shape
        likelihood = np.sum(forward[:,N-1])
        #print likelihood
        return self.get_node_posteriors_aux(seq,forward,backward,node_potentials,edge_potentials,likelihood)
        

    def get_node_posteriors_aux(self,seq,forward,backward,node_potentials,edge_potentials,likelihood):
        H,N = forward.shape
        posteriors = np.zeros([H,N],dtype=float)
        
        for pos in  xrange(N):
            for current_state in xrange(H):
                posteriors[current_state,pos] = forward[current_state,pos]*backward[current_state,pos]/likelihood
        return posteriors

    def get_edge_posteriors(self,seq):
        nr_states = self.nr_states
        node_potentials,edge_potentials = self.build_potentials(seq)
        forward,backward = forward_backward(node_potentials,edge_potentials)
        H,N = forward.shape
        likelihood = np.sum(forward[:,N-1])
        return self.get_edge_posteriors_aux(seq,forward,backward,node_potentials,edge_potentials,likelihood)
        
    def get_edge_posteriors_aux(self,seq,forward,backward,node_potentials,edge_potentials,likelihood):
        H,N = forward.shape
        edge_posteriors = np.zeros([H,H,N-1],dtype=float)
        for pos in xrange(N-1):
            for prev_state in xrange(H):
                for state in xrange(H):
                    edge_posteriors[prev_state,state,pos] = forward[prev_state,pos]*edge_potentials[prev_state,state,pos]*node_potentials[state,pos+1]*backward[state,pos+1]/likelihood 
        return edge_posteriors

    def posterior_decode(self,seq):
        posteriors = self.get_node_posteriors(seq)
        print posteriors
        res =  np.argmax(posteriors,axis=0)
        new_seq =  seq.copy_sequence()
        new_seq.y = res
        return new_seq
    
    def posterior_decode_corpus(self,seq_list):
        predictions = []
        for seq in seq_list:
            predictions.append(self.posterior_decode(seq))
        return predictions


    
    
    def viterbi_decode(self,seq):
        node_potentials,edge_potentials = self.build_potentials(seq)
        viterbi_path,_ = viterbi(node_potentials,edge_potentials)
        res =  viterbi_path
        new_seq =  seq.update_from_sequence(res)
        return new_seq



    def viterbi_decode_corpus(self,seq_list):
        predictions = []
        for seq in seq_list:
            predictions.append(self.viterbi_decode(seq))
        return predictions


    def viterbi_decode_log(self,seq):
        node_potentials,edge_potentials = self.build_potentials_log(seq)
        viterbi_path,_ = viterbi_log(node_potentials,edge_potentials)
        res =  viterbi_path
        new_seq =  seq.update_from_sequence(res)
        return new_seq

    def viterbi_decode_log_raw(self,seq):
        "Return only the prediction list and not a sequence"
        node_potentials,edge_potentials = self.build_potentials_log(seq)
        viterbi_path,_ = viterbi_log(node_potentials,edge_potentials)
        res =  viterbi_path
        return res


    def viterbi_decode_corpus_log(self,seq_list):
        predictions = []
        for seq in seq_list:
            predictions.append(self.viterbi_decode_log(seq))
        return predictions

    def evaluate_corpus(self,seq_list,predictions):
        total = 0.0
        correct = 0.0
        for i,seq in enumerate(seq_list):
            pred = predictions[i]
            for i,y_hat in enumerate(pred.y):
                if(seq.y[i] == y_hat):
                    correct += 1
                total += 1
        return correct/total

    
