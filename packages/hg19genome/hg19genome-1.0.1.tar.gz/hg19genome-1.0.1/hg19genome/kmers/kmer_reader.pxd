import numpy as np
cimport numpy as np
cimport cython
from libc.stdint cimport uint32_t, int32_t, int64_t, uint16_t
from ailist.LabeledIntervalArray_core cimport LabeledIntervalArray, labeled_aiarray_t


cdef extern from "interval_kmer.c":
    # C is include here so that it doesn't need to be compiled externally
    pass

cdef extern from "2bit.c":
    # C is include here so that it doesn't need to be compiled externally
    pass

cdef extern from "2bit.h":
    # C is include here so that it doesn't need to be compiled externally
    pass

cdef extern from "interval_kmer.h":
	
    ctypedef struct kmer_t:
        char *name
        int count

    ctypedef struct kmer_count_t:
        int max_kmers
        int n_kmers
        kmer_t *kmers
        void *kmer_lookup

    #-------------------------------------------------------------------------------------
    # interval_kmer.c
    #=====================================================================================

    void kmer_count_destroy(kmer_count_t *kc) nogil
    int fetch_kmer(kmer_count_t *kc, char *seq) nogil
    kmer_count_t *interval_kmer_count(labeled_aiarray_t *laia, char *fname, int kmer, int last_n) nogil
    char *fetch_sequence(char *fname, char *name, int start, int end) nogil
    void gc_content(labeled_aiarray_t *laia, char *fname, float gc[]) nogil


cdef kmer_count_t *_read_kmers(char *fname, labeled_aiarray_t *laia, int k, int last_n)
cdef bytes _fetch_sequence(char *fname, char *name, int start, int end)
cdef void _gc_percent(char *fname, labeled_aiarray_t *laia, float[::1] gc)