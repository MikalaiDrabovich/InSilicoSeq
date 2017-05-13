#!/usr/bin/env python
# -*- coding: utf-8 -*-

from iss import util
from iss.error_models import ErrorModel
from Bio.Seq import MutableSeq
from Bio.SeqRecord import SeqRecord

import random
import numpy as np


class CDFErrorModel(ErrorModel):
    """CDFErrorModel class.

    Error model based on .npz files derived from alignment with bowtie2.
    the npz file must contain:

    - the length of the reads
    - the mean insert size
    - the distribution of qualities for each position (for R1 and R2)
    - the substitution for each nucleotide at each position (for R1 and R2)"""
    def __init__(self, npz_path):
        super().__init__()
        self.npz_path = npz_path
        self.error_profile = self.load_npz(npz_path)

        self.read_length = self.error_profile['read_length']
        self.insert_size = self.error_profile['insert_size']

        self.quality_forward = self.error_profile['quality_hist_forward']
        self.quality_reverse = self.error_profile['quality_hist_reverse']

        self.subst_choices_for = self.error_profile['subst_choices_forward']
        self.subst_choices_rev = self.error_profile['subst_choices_forward']

    def gen_phred_scores(self, histograms):
        """Generate a list of phred scores based on real datasets"""
        phred_list = []
        for w in histograms:
            random_quality = np.random.choice(
                w[0][1:], p=w[1]
            )
            phred_list.append(round(random_quality))
        return phred_list

    def mut_sequence(self, record, orientation):
        # TODO
        """modify the nucleotides of a SeqRecord according to the phred scores.
        Return a sequence"""

        # get the right subst_matrix
        if orientation == 'forward':
            nucl_choices = self.subst_choices_for
        elif orientation == 'reverse':
            nucl_choices = self.subst_choices_rev
        else:
            print('this is bad')  # TODO error message and proper logging

        mutable_seq = record.seq.tomutable()
        quality_list = record.letter_annotations["phred_quality"]
        position = 0
        for nucl, qual in zip(mutable_seq, quality_list):
            if random.random() > util.phred_to_prob(qual):
                mutable_seq[position] = np.random.choice(
                    nucl_choices[position][nucl][0],
                    p=nucl_choices[position][nucl][1])
            position += 1
        return mutable_seq.toseq()
