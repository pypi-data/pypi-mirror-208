#cython: embedsignature=True
#cython: profile=False

import numpy as np
cimport numpy as np

from libc.stdint cimport uint32_t, int32_t, int64_t, uint16_t
from ailist.LabeledIntervalArray_core cimport LabeledIntervalArray, labeled_aiarray_t
from ..data.import_data import get_data_file


cdef kmer_count_t *_read_kmers(char *fname, labeled_aiarray_t *laia, int k, int last_n):
    cdef kmer_count_t *kc = interval_kmer_count(laia, fname, k, last_n)

    return kc


def read_kmers(LabeledIntervalArray laia, int k, int last_n = 0):

    cdef str twobit_name = get_data_file("hg38.2bit")
    cdef bytes fname = twobit_name.encode()
    cdef kmer_count_t *kc = _read_kmers(fname, laia.laia, k, last_n)

    result = {}
    cdef bytes kmer_seq
    cdef int count
    cdef uint32_t t
    for t in range(kc.n_kmers):
        kmer_seq = kc.kmers[t].name
        count = fetch_kmer(kc, kmer_seq)

        result[kmer_seq.decode()] = count

    # Delete
    kmer_count_destroy(kc)

    return result


cdef bytes _fetch_sequence(char *fname, char *name, int start, int end):
    cdef bytes seq = fetch_sequence(fname, name, start, end)

    return seq

def read_sequence(str chrom, int start, int end):

    cdef str twobit_name = get_data_file("hg38.2bit")
    cdef bytes fname = twobit_name.encode()
    cdef bytes name = chrom.encode()

    cdef bytes seq = _fetch_sequence(fname, name, start, end)
    cdef str py_seq = seq.decode()

    return py_seq


cdef void _gc_percent(char *fname, labeled_aiarray_t *laia, float[::1] gc):
    gc_content(laia, fname, &gc[0])

    return


def gc_percent(LabeledIntervalArray laia):
    cdef str twobit_name = get_data_file("hg38.2bit")
    cdef bytes fname = twobit_name.encode()

    cdef np.ndarray gc = np.zeros(laia.size, dtype=np.single)
    cdef float[::1] gc_mem = gc

    _gc_percent(fname, laia.laia, gc_mem)

    return gc
