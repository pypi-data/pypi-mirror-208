import math
import itertools
import numpy as np
import algopy
from collections import Counter

def jc69_rate_matrix():
    nstates = 4
    pre_q_jc = np.ones((nstates, nstates), dtype=float)
    q_jc = pre_q_jc - np.diag(np.sum(pre_q_jc, axis=1))
    return q_jc * (1.0 / 3.0)

def tn93_rate_matrix():
    nstates = 4
    pre_q_jc = np.ones((nstates, nstates), dtype=float)
    q_jc = pre_q_jc - np.diag(np.sum(pre_q_jc, axis=1))
    return q_jc * (1.0 / 3.0)


#
def get_hamming(codons):
    ncodons = len(codons)
    ham = np.zeros((ncodons, ncodons), dtype=int)
    for i, ci in enumerate(codons):
        for j, cj in enumerate(codons):
            ham[i, j] = sum(1 for a, b in zip(ci, cj) if a != b)
    return ham

def get_eqs(seqs):
    '''
    Get equilibrium frequencies
    '''
    # Join all sequences and get its equilibrium frequency
    all_seqs = ''.join(seqs)
    seq_len = len(all_seqs)
    counter = {k: float(v)/seq_len for k, v in dict(Counter(all_seqs)).items()}
    return counter

def hamming(seq_1, seq_2):
    hamming = sum([seq_1[i] != seq_2[i] for i in range(len(seq_1)-1)])/len(seq_1)
    return hamming

def convert_seq_to_states(seq):
    states = 'ACGT-'
    return list(map(lambda x: states.index(x), seq))

def format_alignment_data(seq1, seq2, seq3):

    # ntaxa will alway be three
    mapped = list(map(lambda x: convert_seq_to_states, [seq1, seq2, seq3]))

    return mapped

def brute(ov, v_to_children, pattern, de_to_P, root_prior):
    """
    This function is only for testing and documentation.
    The P matrices and the root prior may be algopy objects.
    @param ov: ordered vertices with child vertices before parent vertices
    @param v_to_children: map from a vertex to a sequence of child vertices
    @param pattern: an array that maps vertex to state, or to -1 if internal
    @param de_to_P: map from a directed edge to a transition matrix
    @param root_prior: equilibrium distribution at the root
    @return: log likelihood
    """
    nvertices = len(pattern)
    nstates = len(root_prior)
    root = ov[-1]
    v_unknowns = [v for v, state in enumerate(pattern) if state == -1]
    n_unknowns = len(v_unknowns)

    # Construct the set of directed edges on the tree.
    des = set((p, c) for p, cs in v_to_children.items() for c in cs)

    ## Average over all transitions and add to de_to_P
    # to = list(map(np.mean, de_to_P[(0,1)]))
    # fro = list(map(np.mean, np.transpose(de_to_P[(0,1)])))

    # Compute the likelihood by directly summing over all possibilities.
    likelihood = 0
    for assignment in itertools.product(range(nstates), repeat=n_unknowns):

        # Fill in the state assignments for all vertices.
        augmented_pattern = np.array(pattern)
        for v, state in zip(v_unknowns, assignment):
            augmented_pattern[v] = state

        # Add to the log likelihood.
        edge_prob = 1.0
        for p, c in des:
            p_state = augmented_pattern[p]
            c_state = augmented_pattern[c]
            try:
                edge_prob *= de_to_P[p, c][int(p_state), int(c_state)]
            except:
                ## Average over all transitions and add to de_to_P
                edge_prob *= 0.99384114
        try:
            likelihood += root_prior[int(augmented_pattern[root])] * edge_prob
        except:
            likelihood += 0.99384114 * edge_prob

    # Return the log likelihood.
    return algopy.log(likelihood)

def fels(ov, v_to_children, pattern, de_to_P, root_prior):
    """
    The P matrices and the root prior may be algopy objects.
    @param ov: ordered vertices with child vertices before parent vertices
    @param v_to_children: map from a vertex to a sequence of child vertices
    @param pattern: an array that maps vertex to state, or to -1 if internal
    @param de_to_P: map from a directed edge to a transition matrix
    @param root_prior: equilibrium distribution at the root
    @return: log likelihood
    """
    nvertices = len(ov)
    nstates = len(root_prior)
    states = range(nstates)
    root = ov[-1]

    # Initialize the map from vertices to subtree likelihoods.
    likelihoods = algopy.ones(
            (nvertices, nstates),
            dtype=list(de_to_P.values())[0],
            )

    # Compute the subtree likelihoods using dynamic programming.
    for v in ov:
        for pstate in range(nstates):
            for c in v_to_children.get(v, []):
                P = de_to_P[v, c]
                likelihoods[v, pstate] *= algopy.dot(P[pstate], likelihoods[c])
        state = pattern[v]
        if state >= 0:
            for s in range(nstates):
                if s != state:
                    likelihoods[v, s] = 0

    # Get the log likelihood by summing over equilibrium states at the root.
    return algopy.log(algopy.dot(root_prior, likelihoods[root]))


def align_brute(ov, v_to_children, patterns, de_to_P, root_prior, pat_mults):
    npatterns = patterns.shape[0]
    lls = algopy.zeros(
            npatterns,
            dtype=list(de_to_P.values())[0],
            )
    for i in range(npatterns):
        lls[i] = brute(ov, v_to_children, patterns[i], de_to_P, root_prior)
    print(lls)
    return algopy.dot(lls, pat_mults)

def align_fels(ov, v_to_children, patterns, de_to_P, root_prior, pat_mults):
    npatterns = patterns.shape[0]
    lls = algopy.zeros(
            npatterns,
            dtype=list(de_to_P.values())[0],
            )
    for i in range(npatterns):
        lls[i] = fels(ov, v_to_children, patterns[i], de_to_P, root_prior)
    return algopy.dot(lls, pat_mults)

