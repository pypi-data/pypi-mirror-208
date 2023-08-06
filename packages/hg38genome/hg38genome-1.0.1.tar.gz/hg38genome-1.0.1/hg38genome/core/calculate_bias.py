from ailist import LabeledIntervalArray
from intervalframe import IntervalFrame
import pandas as pd
import numpy as np

# Local imports
from .hg38_core import Hg38Genome
from ..kmers.kmer_reader import gc_percent


def calculate_bias(intervals: LabeledIntervalArray,
                    include_blacklist: bool = True,
                    include_repeat: bool = True,
                    include_gc: bool = True) -> IntervalFrame:
    """
    Calculate bias per interval
    
    Parameters
    ----------
        intervals : LabeledIntervalArray
            Labeled intervals
        include_blacklist : bool
            Flag to include blacklist
        include_repeat : bool
            Flag to include repeat
        include_gc : bool
            Flag to include gc

    Returns
    ----------
        bias_record : IntervalFrame
            Bias for given intervals
    """

    # Assign genome
    genome = Hg38Genome()

    # Initialize bias records
    bias_record = IntervalFrame(intervals=intervals)

    # Calculate blacklist
    if include_blacklist:
        blacklist = genome.blacklist()
        bias_record.df.loc[:,"blacklist"] = intervals.percent_coverage(blacklist.index)

    # Calculate repeat
    if include_repeat:
        repeat = genome.repeats()
        bias_record.df.loc[:,"repeat"] = intervals.percent_coverage(repeat.index)

    # Calculate gc
    if include_gc:
        bias_record.df.loc[:,"gc"] = gc_percent(intervals)

    return bias_record


def calculate_bin_bias(bin_size: int = 100000,
                        include_blacklist: bool = True,
                        include_repeat: bool = True,
                        include_gc: bool = True) -> IntervalFrame:
    """
    Calculate bias per bin
    
    Parameters
    ----------
        bin_size : int
            Size of bins
        include_blacklist : bool
            Flag to include blacklist
        include_repeat : bool
            Flag to include repeat
        include_gc : bool
            Flag to include gc

    Returns
    ----------
        bias_record : IntervalFrame
            Bias for given bin size
    """

    # Assign genome
    genome = Hg38Genome()

    # Initialize bins
    intervals = LabeledIntervalArray.create_bin(genome.chrom_sizes, bin_size=bin_size)

    # Initialize bias records
    bias_record = calculate_bias(intervals,
                                include_blacklist,
                                include_repeat,
                                include_gc)

    return bias_record