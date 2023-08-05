#import useful modules
import torch
import pyro
import pandas as pd
import numpy as np
import re
from enum import Enum
import string
import math
import itertools
import random

LOWERCASE_ALPHABET = list(string.ascii_lowercase)
UPPERCASE_ALPHABET = list(string.ascii_uppercase)

def check_row_sum(tensor, tol=1e-6):
    """
        Function to check if each row of a given tensor sum up to 1
    """
    row_sums = tensor.sum(dim=1)
    return torch.all(torch.abs(row_sums - 1) < tol)


def generate_codons_distribution(nb_AAs, nb_codons):
    """
        Function to generate the distribution of the codons within the differents amino acids
    """
    if nb_AAs == 1:
        return [nb_codons]
    
    num = random.randint(1, nb_codons - (nb_AAs - 1))  # ensures there's enough "total" left for future numbers
    return [num] + generate_codons_distribution(nb_AAs - 1, nb_codons - num)

def generate_prob_dist(length):
    """
        Function to generate a list of length numbers summing up to 1
    """
    # Generate random numbers
    numbers = [random.random() for _ in range(length)]

    # Normalize the numbers so that their sum equals 1
    total = sum(numbers)
    normalized_numbers = [n / total for n in numbers]

    return normalized_numbers

class SyncCDsGeneratorConf:
    def __init__(self, bases=None, codons=None, nb_codons=None,
                 start_codons=None, nb_AAs=None, nb_start_codons=2,
                 stop_codons=None, AAs=None, translation_dict={},
                 nb_stop_codons=1,
                  transition_prob_t=None, emission_prob_t=None, AAs_initial_prob_dist=None,
                  codon_length=None, constraints_dict=None, AAs_stop_prob_dist=None):
        """
        Initialize a new instance of SyncCDsGeneratorConf

        Args:
            bases (list): list of bases
            codons (list): list of codons
            nb_codons (int): number of codons
            start_codons (list): list of start codons
            nb_AAs (int): number of amino acids
            stop_codons (list): list of stop codons
            AAs (list): list of amino acids

            translation_dict (dict): dictionary containing the rules of translation of the codons into amino acids
                key: amino aicd
                value: codons encoding the amino acid

            transition_prob_t (squared 2D tensor of the same shape as the AAs list): transition probability table between the different amino acids
                transition_prob_t[i][j] represents the probability that the amino acid at index i in
                AAs is followed by the amino acid at index j in AAs

            emission_prob_t (squared 2D tensor of shape(len(AAs), L), where L is the maximum length of values in the translation_dict): emission probability table
                emission_prob_t[i][j] is the probability that the amino acid at index i in AAs is
                encoded by the codon j in the list of values corresponding to that amino acid in the 
                translation dict
            
            AAs_initial_prob_dist (1D numpy array): array containing the initial probability
            distribution of the different amino acids
                AAs_initial_prob_dist[i] is the probability that a sequence starts with the amino acid
                at the index i in AAs
            
            codon_length (int): length of a codon
            constraints_dict (dict): dictionary containing the constraints of emission of codons
            based on the previously translated sequence
                key: a regex pattern representing the form of the previously translated sequence
                value: a dictionary giving the emission contraints for the concerned amino acids
                    key: an amino acid (an element of AAs)
                    value: a 1D array of length L giving the emission probability table of the key amino acid when the previously translated sequence matches the regex. 
            
            AAs_stop_prob_dist (1D numpy array): array containing the end probability distribution of 
            the different amino acids.
                AAs_stop_prob_dist[i] is the probability that a sequence ends with the amino acid at
                the index i in AAs.

            Example:
                conf = SynCDsGen.SyncCDsGeneratorConf()

                conf.bases = ['a', 'b', 'c']
                conf.codons = ['aa', 'ab', 'ac', 'ba', 'ca', 'bb', 'bc', 'cb']
                conf.start_codons = ['aa', 'ab']
                conf.stop_codons = ['ac']
                conf.AAs = ['A', 'B', 'C', 'D']
                conf.translation_dict = {
                    'A':  ['aa', 'ab'],
                    'B': ['ac'],
                    'C': ['ba', 'bc', 'cb'],
                    'D': ['ca', 'bb']
                }
                conf.transition_prob_t = torch.Tensor([[0,  0, 1/2, 1/2],
                                            [0, 0, 1/2, 1/2],
                                            [0, 0, 1/2, 1/2],
                                            [0, 0, 1/2, 1/2]])

                conf.emission_prob_t = torch.Tensor([[1/2, 1/2, 0.0],
                                        [1, 0.0, 0.0],
                                        [0.6, 0.2, 0.2],
                                        [0.7, 0.3, 0.0]])
        """
        self.bases = bases
        self.codons = codons
        self.nb_codons = nb_codons
        self.start_codons = start_codons
        self.nb_AAs = nb_AAs
        self.nb_start_codons = nb_start_codons
        self.stop_codons = stop_codons
        self.AAs = AAs
        self.translation_dict = translation_dict
        self.nb_stop_codons = nb_stop_codons
        self.transition_prob_t = transition_prob_t
        self.emission_prob_t = emission_prob_t
        self.AAs_initial_prob_dist = AAs_initial_prob_dist
        self.codon_length = codon_length
        self.constraints_dict = constraints_dict
        self.AAs_stop_prob_dist = AAs_stop_prob_dist

        if all(el is not None for el in [self.nb_codons, self.nb_AAs, self.codon_length]):
            #if we specified the number of codons and the number of amino acids, we automatically
            #compute the parameters of the configurator
            if self.codon_length is None:
                self.codon_length = 2
            
            self.nb_bases = math.ceil(math.log(self.nb_codons, self.codon_length))
            self.bases = LOWERCASE_ALPHABET[:self.nb_bases]

            # Generate all possible arrangements of the bases
            arrangements = list(itertools.permutations(self.bases, self.codon_length))
            possible_codons = [''.join(arrangement) for arrangement in arrangements]
            self.codons = possible_codons[:self.nb_codons]

            self.start_codons = self.codons[:self.nb_start_codons]
            self.stop_codons = self.codons[self.nb_start_codons:self.nb_start_codons+self.nb_stop_codons]

            #define the list of amino acids
            self.AAs = UPPERCASE_ALPHABET[:self.nb_AAs]

            #generate the distribution of codons between the different amino acids
            codons_dist = generate_codons_distribution(self.nb_AAs - 2, self.nb_codons - self.nb_start_codons - self.nb_stop_codons)
            
            pos = 0
            self.translation_dict[self.AAs[0]] = self.codons[:self.nb_start_codons]
            pos += self.nb_start_codons
            self.translation_dict[self.AAs[1]] = self.codons[pos:pos+1]
            pos += 1

            for i, nb in enumerate(codons_dist):
                self.translation_dict[self.AAs[i+2]] = self.codons[pos:nb]
                pos += nb
            
            #construct the transition probability table
            self.transition_prob_t = torch.zeros((self.nb_AAs, self.nb_AAs))
            for i in range(2, self.nb_AAs):
                self.transition_prob_t[:, i] = 1/(self.nb_AAs-2)

            #build the emission matrix
            n_cols = max(max(codons_dist), 2)
            self.emission_prob_t = torch.zeros((self.nb_AAs, n_cols))
            
            #emission distribution of the start codons
            new_row = [0] * n_cols
            for i in range(self.nb_start_codons):
                new_row[i] = 1/self.nb_start_codons
            self.emission_prob_t[0, :] = torch.tensor(new_row)

            #emission distribution of the stop codons
            new_row = [0] * n_cols
            new_row[0] = 1
            self.emission_prob_t[1, :] = torch.tensor(new_row)

            #emission distributions of the other amino acids
            for i, nb in enumerate(codons_dist):
                new_row = [0] * n_cols
                emission_dist = generate_prob_dist(nb)

                for k in range(nb):
                    new_row[k] = emission_dist[k]

                self.emission_prob_t[i+2] = torch.tensor(new_row)

    def is_AA_start_AA(self, AA):
        coding_codons = self.translation_dict[AA]

        for codon in coding_codons:
            if codon in self.start_codons:
                return 1
        return 0
    
    def is_AA_stop_AA(self, AA):
        """
            Function to check if a given amino acid is encoded by a stop codon

            Returns True if AA is encoded by stop codons and False otherwise
        """
        coding_codons = self.translation_dict[AA]

        for codon in coding_codons:
            if codon in self.stop_codons:
                return 1
        return 0

    def get_AAs_initial_prob_dist(self):
        start_codons_prob_dist = [self.is_AA_start_AA(AA) for AA in self.AAs]
        nb_start_AAs = start_codons_prob_dist.count(1)

        start_codons_prob_dist = np.array(start_codons_prob_dist)/ nb_start_AAs

        return(start_codons_prob_dist)
    
    def get_AAs_stop_prob_dist(self):
        """
            Function to compute the distribution probability of stop AAs

            Returns a numpy array of the size of the array AAs. The arrays indicates the probability
            of appearance of each AA as a stop codon at the end of a sequence; AAs encoded by stop
            codons have the same probability of appearance, and the others have a 0 probability of
            appearance
        """
        stop_codons_prob_dist = [self.is_AA_stop_AA(AA) for AA in self.AAs]
        nb_stop_AAs = stop_codons_prob_dist.count(1)

        stop_codons_prob_dist = np.array(stop_codons_prob_dist)/ nb_stop_AAs

        return(stop_codons_prob_dist)

class Position(Enum):
        START = 1
        STOP = 2

class SynCDsGenerator:
    def __init__(self, generatorConf:SyncCDsGeneratorConf):
        self.generatorConf = generatorConf
        self.AAs_indices_sequences = []
        self.CDs_indices_sequences = []

        #check the validity of the attributes of the generator configuration
        assert all(c in self.generatorConf.bases for codon in self.generatorConf.codons for c in codon), "The characters used for codons should be in the list of SyncCDsGeneratorConf.bases"
        assert len(generatorConf.start_codons) > 0, "For yncCDsGeneratorConf, the list of start codons should not be empty"
        assert all(codon in self.generatorConf.codons for codon in self.generatorConf.start_codons), "Start codons should be a subset of codons"
        assert all(codon in self.generatorConf.codons for codon in self.generatorConf.stop_codons), "Stop codons should be a subset of codons"
        assert len(generatorConf.stop_codons) > 0, "For yncCDsGeneratorConf, the list of stop codons should not be empty"
        assert len(generatorConf.translation_dict) == len(generatorConf.AAs), "For yncCDsGeneratorConf, translation dict should have the same size with the AAs list" #the translation_dict and the AAs list should have the same size
        assert generatorConf.transition_prob_t.size()[0] == generatorConf.transition_prob_t.size()[1] == len(generatorConf.AAs), "The emission_prob_t should be a squared tensor, and its size should be equal to the size of the AAs list"

        max_nb_syn_codons = max([len(syn_codons) for syn_codons in self.generatorConf.translation_dict.values()])
        assert generatorConf.emission_prob_t.size()[1] == max_nb_syn_codons, f"The second dimension of the emission_prob_t tensor should be {max_nb_syn_codons}, got {generatorConf.emission_prob_t.size()[1]}"
        
        assert check_row_sum(self.generatorConf.emission_prob_t), "Each row of the emission_prob_t should sum up to 1"
        assert check_row_sum(self.generatorConf.transition_prob_t), "Each row of the transition_prob_t should sum up to 1"

        if self.generatorConf.codon_length is None:
            l = len(self.generatorConf.codons[0])
            assert all(len(codon) == l for codon in self.generatorConf.codons), f"All the codons should have the same length"
            self.generatorConf.codon_length = l
        else:
            assert all(len(codon) == self.generatorConf.codon_length for codon in self.generatorConf.codons), f"All the codons should have the same length, since the codon length had been set to {self.generatorConf.codon_length}"

        if self.generatorConf.AAs_initial_prob_dist is None:
            self.generatorConf.AAs_initial_prob_dist = self.generatorConf.get_AAs_initial_prob_dist()
        else:
            assert np.sum(self.generatorConf.AAs_initial_prob_dist)==1, f"AAs_stop_prob_dist should sum up to 1, got {np.sum(self.generatorConf.AAs_stop_prob_dist)}"

        if self.generatorConf.AAs_stop_prob_dist is None:
            self.generatorConf.AAs_stop_prob_dist = self.generatorConf.get_AAs_stop_prob_dist()
        else:
            assert np.sum(self.generatorConf.AAs_stop_prob_dist)==1, f"AAs_stop_prob_dist should sum up to 1, got {np.sum(self.generatorConf.AAs_stop_prob_dist)}"
    
    def AA_indices_sequence_to_AA_sequence(self, X):
        return ''.join([self.generatorConf.AAs[i] for i in X])

    def CD_indices_sequence_to_CD_sequence(self, X):
        """
            input:
                X: list of indices of the AAs of the sequence concate to the list of indices of the codons of the sequence
        """
        N = len(X)
        AA_ind,  CDs_ind = X[0:N//2], X[N//2:]

        return ''.join([self.generatorConf.translation_dict[self.generatorConf.AAs[a]][int(i)] for a, i in zip(AA_ind, CDs_ind)])
    
    def generate_token(self, position:Position):
        """
            Function to generate the start token of a sequence

            Returns the start AA and the corresponding codon
        """
        assert position in (Position.START, Position.STOP), "position should be an instance of the Position class"
        
        if position == Position.START:
            prob_t = self.generatorConf.AAs_initial_prob_dist
            names = ["x_start", "y_start"]
        elif position == Position.STOP:
            prob_t = self.generatorConf.AAs_stop_prob_dist
            names = ["x_end", "y_end"]

        state = pyro.sample(names[0],
                                pyro.distributions.Categorical(torch.Tensor(prob_t)))
        emission_p_t = self.generatorConf.emission_prob_t[state]

        observation = pyro.sample(names[1],
                                    pyro.distributions.Categorical(emission_p_t))

        return state, observation
    
    def build_dataframe(self):
        AAs_sequences = np.apply_along_axis(self.AA_indices_sequence_to_AA_sequence, 1, self.AAs_indices_sequences)

        joined_sequences = np.hstack((self.AAs_indices_sequences, self.CDs__indices_sequences))
        CDs_sequences = np.apply_along_axis(self.CD_indices_sequence_to_CD_sequence, 1, joined_sequences)

        self.synthetic_data = pd.DataFrame({'AAs': AAs_sequences, 'CDs': CDs_sequences})


class StochasticSynCDsGenerator(SynCDsGenerator):
    def __init__(self, generatorConf:SyncCDsGeneratorConf):
        super().__init__(generatorConf)

    def sample(self, n_samples=100, length=50):
        assert length > 3, f"Waiting length > 3, got {length}"

        AAs_samples = []
        CDs_samples = []

        for j in torch.arange(0, n_samples):
            hidden_states = []
            observations = []

            #generate the first AA of the AA sequence from the start codons
            state, observation = self.generate_token(Position.START)
            hidden_states.append(state)
            observations.append(observation)

            for k in torch.arange(1, length-1):
                transition_p_t = self.generatorConf.transition_prob_t[state]
                state = pyro.sample("x_{}_{}".format(j, k),
                                    pyro.distributions.Categorical(transition_p_t))
                emission_p_t = self.generatorConf.emission_prob_t[state]

                observation = pyro.sample("y_{}_{}".format(j, k),
                                          pyro.distributions.Categorical(emission_p_t))

                hidden_states.append(state)
                observations.append(observation)   
            
            #generate the stop codon
            state, observation = self.generate_token(Position.STOP)
            hidden_states.append(state)
            observations.append(observation)   

            AA_sample = torch.Tensor(hidden_states)
            CDs_sample = torch.Tensor(observations)

            AAs_samples.append(AA_sample)
            CDs_samples.append(CDs_sample)

        self.AAs_indices_sequences = torch.vstack(AAs_samples).numpy().astype(int)
        self.CDs__indices_sequences = torch.vstack(CDs_samples).numpy().astype(int)

        self.build_dataframe()

        return self.synthetic_data, self.AAs_indices_sequences, self.CDs__indices_sequences


class AutoregressiveSynCDsGenerator(SynCDsGenerator):
    def __init__(self, generatorConf:SyncCDsGeneratorConf):
        SynCDsGenerator.__init__(self, generatorConf)

        assert len(self.generatorConf.constraints_dict) > 0, "For a StochasticSynCDsGenerator, we should set the SyncCDsGeneratorConf's constraints_dict to a non empty dictionary"

        assert all(AA in self.generatorConf.AAs for constraint in self.generatorConf.constraints_dict.values() for AA in constraint), "The AAs used in  SyncCDsGeneratorConf.constraints_dict should be present in SyncCDsGeneratorConf.AAs"

    def sample(self, n_samples=100, length=50):

        if self.generatorConf.AAs_initial_prob_dist is None:
            self.generatorConf.AAs_initial_prob_dist = self.generatorConf.get_AAs_initial_prob_dist()

        assert length > 3, f"Waiting length > 3, got {length}"

        AAs_samples = []
        CDs_samples = []

        for j in torch.arange(0, n_samples):
            hidden_states = []
            observations = []

            #generate the first AA of the AA sequence from the start codons
            state, observation = self.generate_token(Position.START)
            hidden_states.append(state)
            observations.append(observation)

            for k in torch.arange(1, length-1):
                transition_p_t = self.generatorConf.transition_prob_t[state]
                state = pyro.sample("x_{}_{}".format(j, k),
                                    pyro.distributions.Categorical(transition_p_t))
                
                hidden_AAs_sequence = self.AA_indices_sequence_to_AA_sequence(hidden_states)

                emission_p_t = self.generatorConf.emission_prob_t[state]

                for pattern in self.generatorConf.constraints_dict:
                    constraints = self.generatorConf.constraints_dict[pattern]
                    if re.match(pattern, hidden_AAs_sequence) and self.generatorConf.AAs[state] in constraints:
                        emission_p_t = constraints[self.generatorConf.AAs[state]]
                        break

                observation = pyro.sample("y_{}_{}".format(j, k),
                                          pyro.distributions.Categorical(emission_p_t))

                hidden_states.append(state)
                observations.append(observation)

            #generate the stop codon
            state, observation = self.generate_token(Position.STOP)
            hidden_states.append(state)
            observations.append(observation)    

            AA_sample = torch.Tensor(hidden_states)
            CDs_sample = torch.Tensor(observations)

            AAs_samples.append(AA_sample)
            CDs_samples.append(CDs_sample)

        self.AAs_indices_sequences = torch.vstack(AAs_samples).numpy().astype(int)
        self.CDs__indices_sequences = torch.vstack(CDs_samples).numpy().astype(int)

        self.build_dataframe()

        return self.synthetic_data, self.AAs_indices_sequences, self.CDs__indices_sequences
