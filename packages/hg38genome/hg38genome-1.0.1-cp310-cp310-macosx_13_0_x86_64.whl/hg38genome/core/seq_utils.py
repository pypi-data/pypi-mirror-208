from typing import Dict
from ailist import LabeledIntervalArray
import pandas as pd
import numpy as np

# Local imports
from ..data.import_data import get_data_file
from ..kmers.kmer_reader import read_kmers, read_sequence


def get_sequence(chrom: str,
                 start: int,
                 end: int) -> str:
    """
    Get sequence from chromosome

    Parameters
    ----------
        chrom : str
            Chromosome
        start : int
            Start position
        end : int
            End position

    Returns
    -------
        sequence : str
            Sequence
    """

    # Get sequence
    sequence = read_sequence(chrom, start, end)

    return sequence


def interval_kmers(intervals: LabeledIntervalArray,
                   k: int = 2,
                   last_n: int = 0) -> Dict[str,int]:
    """
    Get kmers from intervals

    Parameters
    ----------
        intervals : LabeledIntervalArray
            Intervals
        k : int
            Kmer length
        last_n : int
            Last n bases to query

    Returns
    -------
        kmers : Dict[str,int]
            Kmer counts
    """

    # Calculate kmers
    kmers = read_kmers(intervals, k, last_n)

    return kmers


def count_kmers(start: int,
                end: int,
                chrom: str,
                k: int = 2) -> Dict[str,int]:
    """
    Count kmers in interval

    Parameters
    ----------
        start : int
            Start position
        end : int
            End position
        chrom : str
            Chromosome
        k : int
            Kmer length

    Returns
    -------
        kmers : Dict[str,int]
            Kmer counts
    """

    # Calculate kmers
    intervals = LabeledIntervalArray()
    intervals.add(start, end, chrom)
    kmers = read_kmers(intervals, k)

    return kmers
