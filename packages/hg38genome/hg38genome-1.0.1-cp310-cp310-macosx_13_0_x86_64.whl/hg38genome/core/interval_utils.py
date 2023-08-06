from typing import Dict, List, Tuple
from ailist import LabeledIntervalArray
from intervalframe.read.read_h5 import read_h5_intervalframe
from intervalframe import IntervalFrame
import h5py
import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype

# Local imports
from ..data.import_data import get_data_file


def add_upstream(intervals: IntervalFrame,
                 n: int,
                 selection: np.ndarray | None = None) -> IntervalFrame:
    """
    Add upstream to intervals

    Parameters
    ----------
        intervals : IntervalFrame
            Intervals to add upstream to
        n : int
            Number of bases to add upstream
        selection : np.ndarray
            Selection of intervals to add upstream to

    Returns
    -------
        iframe : IntervalFrame
            Intervals with upstream added
    """

    # Extract arrays
    starts = intervals.index.starts
    ends = intervals.index.ends
    labels = intervals.index.labels

    # Add upstream 
    if selection is None:
        starts = starts - n
    else:
        starts[selection] = starts[selection] - n

    # Correct zeros
    starts[starts < 0] = 0

    # Construct IntervalFrame
    new_intervals = LabeledIntervalArray()
    new_intervals.add(starts, ends, labels)
    iframe = IntervalFrame(new_intervals, intervals.df)

    return iframe


def add_downstream(intervals: IntervalFrame,
                   n: int,
                   selection: np.ndarray | None = None) -> IntervalFrame:
    """
    Add downstream to intervals

    Parameters
    ----------
        intervals : IntervalFrame
            Intervals to add downstream to
        n : int
            Number of bases to add downstream
        selection : np.ndarray
            Selection of intervals to add downstream to
    
    Returns
    -------
        iframe : IntervalFrame
            Intervals with downstream added
    """

    # Extract arrays
    starts = intervals.index.starts
    ends = intervals.index.ends
    labels = intervals.index.labels

    # Add downstream 
    if selection is None:
        ends = ends + n
    else:
        ends[selection] = ends[selection] + n

    # Construct IntervalFrame
    new_intervals = LabeledIntervalArray()
    new_intervals.add(starts, ends, labels)
    iframe = IntervalFrame(new_intervals, intervals.df)

    return iframe


def adjust_bounds(iframe: IntervalFrame,
                  upstream: int,
                  downstream: int,
                  filter_duplicates: bool = True) -> IntervalFrame:
    """
    Adjust bounds of intervals

    Parameters
    ----------
        iframe : IntervalFrame
            Intervals to adjust
        upstream : int
            Number of bases to add upstream
        downstream : int
            Number of bases to add downstream
        filter_duplicates : bool
            Filter duplicates

    Returns
    -------
        iframe : IntervalFrame
            Intervals with bounds adjusted
    """

    # Filter duplicates
    if filter_duplicates:
        selection1 = np.logical_and(iframe.df.loc[:,"Strand"].values=="+",
                                    ~pd.Index(iframe.df.loc[:,"gene_name"].values).duplicated(keep="first"))
        selection2 = np.logical_and(iframe.df.loc[:,"Strand"].values=="-",
                                    ~pd.Index(iframe.df.loc[:,"gene_name"].values).duplicated(keep="last"))
        is_unique = np.logical_or(selection1, selection2)
        iframe = iframe.iloc[is_unique,:]

    if upstream != 0:
        selection = iframe.df.loc[:,"Strand"].values=="+"
        iframe = add_upstream(iframe, upstream, selection)
        selection = iframe.df.loc[:,"Strand"].values=="-"
        iframe = add_upstream(iframe, upstream, selection)

    if downstream != 0:
        selection = iframe.df.loc[:,"Strand"].values=="+"
        iframe = add_downstream(iframe, downstream, selection)
        selection = iframe.df.loc[:,"Strand"].values=="-"
        iframe = add_downstream(iframe, downstream, selection)

    return iframe


def get_gene_info(structure: str,
                chromosome: str = None,
                source: str = "HAVANA",
                level: int = 3,
                gene_type: str = "all",
                annotations: List[str] = ["gene_type","gene_name","strand"],
                upstream: int = 0,
                downstream: int = 0,
                filter_duplicates: bool = True) -> IntervalFrame:
    """
    Get gene information

    Parameters
    ----------
        structure : str
            Structure to get information for
        chromosome : str
            Chromosome to get information for
        source : str
            Source of information
        level : int
            Level of information
        gene_type : str
            Type of gene to get information for
        annotations : List[str]
            Annotations to get information for
        upstream : int
            Number of bases to add upstream
        downstream : int
            Number of bases to add downstream
        filter_duplicates : bool
            Filter duplicate entries

    Returns
    -------
        iframe : IntervalFrame
            IntervalFrame with gene information
    """

    # Structure file map
    file_map = {"gene":"genes.parquet",
                "exon":"exons.parquet",
                "transcript":"transcripts.parquet",
                "start_codon":"start_codons.parquet",
                "end_codon":"stop_codons.parquet",
                "UTR":"UTRs.parquet",
                "CDS":"CDSs.parquet",
                "tss":"tss.parquet",
                "tes":"tes.parquet",}

    # Read file
    parquet_file = get_data_file(file_map[structure])
    iframe = IntervalFrame.read_parquet(parquet_file)

    # Filter calls
    chosen = iframe.df.loc[:,"Source"].values == source
    chosen = np.logical_and(chosen, iframe.df.loc[:,"level"].values <= level)
    if gene_type != "all":
        chosen = np.logical_and(chosen, iframe.df.loc[:,"gene_type"].values == gene_type)
    if chromosome is not None:
        chosen = np.logical_and(chosen, iframe.df.loc[:,"Seqid"].values == chromosome)
    iframe = iframe.iloc[chosen,:]

    # Adjust intervals
    iframe = adjust_bounds(iframe, upstream, downstream,filter_duplicates)

    return iframe


def get_feature_info(structure: str,
                    chromosome: str = None,
                    upstream: int = 0,
                    downstream: int = 0) -> IntervalFrame:
    """
    Get feature information

    Parameters
    ----------
        structure : str
            Structure to get information for
        chromosome : str
            Chromosome to get information for
        upstream : int
            Number of bases to add upstream
        downstream : int
            Number of bases to add downstream
    
    Returns
    -------
        iframe : IntervalFrame
            IntervalFrame with feature information
    """

    # Structure file map
    file_map = {"CTCF":"CTCF.parquet",
                "CpG_islands":"CpG_islands.parquet",}

    # Find file
    parquet_file = get_data_file(file_map[structure])
    iframe = IntervalFrame.read_parquet(parquet_file)

    # Adjust intervals
    iframe = adjust_bounds(iframe, upstream, downstream)

    return iframe


def get_exons(chromosome: str = None,
              upstream: int = 0,
              downstream: int = 0) -> IntervalFrame:
    """
    Get exons

    Parameters
    ----------
        chromosome : str
            Chromosome
        upstream : int
            Add value to most upstream position
        downstream : int
            Add value to most downstream position
    
    Returns
    -------
        exons : IntervalFrame
            Exon locations
    """

    exons = get_gene_info("exon",
                        chromosome = chromosome,
                        upstream = upstream,
                        downstream = downstream)

    return exons


def get_gene_body(chromosome: str = None,
                  upstream: int = 0,
                  downstream: int = 0,
                  gene_type: str = "all") -> IntervalFrame:
    """
    Get genes

    Parameters
    ----------
        upstream : int
            Add value to most upstream position
        downstream : int
            Add value to most downstream position
        gene_type : str
            Filter based GeneType

    Returns
    -------
        genes : IntervalFrame
            Gene locations
    """

    genes = get_gene_info("gene",
                        chromosome = chromosome,
                        upstream = upstream,
                        downstream = downstream,
                        gene_type = gene_type)

    return genes


def get_tss(chromosome: str = None,
            upstream: int = 0,
            downstream: int = 0,
            gene_type: str = "all",
            filter_duplicates: bool = True) -> IntervalFrame:
    """
    Get TSS

    Parameters
    ----------
        chromosome : str
            Chromosome
        upstream : int
            Add value to most upstream position
        downstream : int
            Add value to most downstream position
        gene_type : str
            Type of gene to return
        filter_duplicates : bool
            Filter duplicate gene entries

    Returns
    -------
        tss : IntervalFrame
            TSS locations
    """

    tss = get_gene_info("tss",
                        chromosome = chromosome,
                        upstream = upstream,
                        downstream = downstream,
                        gene_type = gene_type,
                        filter_duplicates = filter_duplicates)

    return tss


def get_tes(chromosome: str = None,
            upstream: int = 0,
            downstream: int = 0,
            gene_type: str = "all",
            filter_duplicates: bool = True) -> IntervalFrame:
    """
    Get TSS

    Parameters
    ----------
        chromosome : str
            Chromosome
        upstream : int
            Add value to most upstream position
        downstream : int
            Add value to most downstream position
        gene_type : str
            Type of gene to return
        filter_duplicates : bool
            Filter duplicate gene entries

    Returns
    -------
        tss : IntervalFrame
            TSS locations
    """

    tes = get_gene_info("tes",
                        chromosome = chromosome,
                        upstream = upstream,
                        downstream = downstream,
                        gene_type = gene_type,
                        filter_duplicates = filter_duplicates)

    return tes


def get_cpg_islands(chromosome: str = None,
                    upstream: int = 0,
                    downstream: int = 0) -> IntervalFrame:
    """
    Get CpG islands

    Parameters
    ----------
        upstream : int
            Add value to most upstream position
        downstream : int
            Add value to most downstream position

    Returns
    -------
        cpgs : IntervalFrame
            CpG island locations
    """

    cpgs = get_feature_info("CpG_islands",
                            chromosome = chromosome,
                            upstream = upstream,
                            downstream = downstream)

    return cpgs


def get_blacklist() -> IntervalFrame:
    """
    Get blacklist

    Returns
    -------
        blacklist : IntervalFrame
            Blacklist locations
    """

    par = get_data_file("blacklist_v2.parquet")
    blacklist = IntervalFrame.read_parquet(par)

    return blacklist


def get_repeats() -> IntervalFrame:
    """
    Get repeats

    Returns
    -------
        repeats : IntervalFrame
            Repeat locations
    """

    par = get_data_file("hg38_repeats.parquet")
    repeats = IntervalFrame.read_parquet(par)

    return repeats


def get_ctcf(chromosome: str = None,
             upstream: int = 0,
             downstream: int = 0) -> IntervalFrame:
    """
    Get CTCF

    Parameters
    ----------
        chromosome : str
            Chromosome
        upstream : int
            Add value to most upstream position
        downstream : int
            Add value to most downstream position

    Returns
    -------
        ctcf : IntervalFrame
            CTCF locations
    """

    ctcf = get_feature_info("CTCF",
                            chromosome = chromosome,
                            upstream = upstream,
                            downstream = downstream)

    return ctcf


def get_tfbs(chromosome: str = None,
             upstream: int = 0,
             downstream: int = 0) -> IntervalFrame:
    """
    Get TFBS

    Parameters
    ----------
        chromosome : str
            Chromosome
        upstream : int
            Add value to most upstream position
        downstream : int
            Add value to most downstream position

    Returns
    -------
        tfbs : IntervalFrame
            TFBS locations
    """

    # Read TFBS parquet file
    parquet_file = get_data_file("Top1000sites_TF.parquet")
    tfbs = IntervalFrame.read_parquet(parquet_file)
    if chromosome is not None:
        tfbs = tfbs.loc[chromosome,:]
    if upstream is not None:
        tfbs = add_upstream(tfbs, upstream)
    if downstream is not None:
        tfbs = add_downstream(tfbs, downstream)

    return tfbs


def get_bin_bias(bin_size: int = 100000) -> IntervalFrame:
    """
    Get bin bias

    Parameters
    ----------
        bin_size : int
            Bin size
    
    Returns
    -------
        bins : IntervalFrame
            Bin bias
    """

    parquet_file = get_data_file("bin"+str(bin_size)+"_bias.parquet")
    bins = IntervalFrame.read_parquet(parquet_file)
        
    return bins


def get_genes(value: str,
              chromosome: str = None,
              upstream: int = 0,
              downstream: int = 0,
              gene_type: str = "all") -> IntervalFrame:
    """
    Get genes

    Parameters
    ----------
        value : str
            "exons", "tss", or "genes"
        chromosome : str
            Filter based on chromosome
        upstream : int
            Add value to most upstream position
        downstream : int
            Add value to most downstream position
        gene_type : str
            Filter based GeneType
    
    Returns
    -------
        intervals : IntervalFrame
            Gene locations
    """

    # Function calls
    calls = {"exons": get_exons,
             "tss": get_tss,
             "genes": get_gene_body}
    
    # Get intervals
    if value == "genes":
        intervals = calls[value](chromosome, upstream, downstream, gene_type)
    else:
        intervals = calls[value](chromosome, upstream, downstream)

    return intervals


def get_snps() -> IntervalFrame:
    """
    Get SNPs

    Parameters
    ----------
        None

    Returns
    -------
        snps : IntervalFrame
            SNP locations
    """

    # Read SNPs parquet file
    parquet_file = get_data_file("common_hg38_34k.parquet")
    snps = IntervalFrame.read_parquet(parquet_file)

    return snps


