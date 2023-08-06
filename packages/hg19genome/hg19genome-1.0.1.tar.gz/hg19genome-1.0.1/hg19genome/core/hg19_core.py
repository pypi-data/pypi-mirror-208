from typing import Dict, List, Tuple
from ailist import LabeledIntervalArray
from intervalframe import IntervalFrame
import numpy as np
import os

# Local imports
from .seq_utils import *
from .interval_utils import *
from ..data.import_data import get_data_file


def get_include():
	"""
	Get file directory if C headers

	Parameters
	----------
		None

	Returns
	-------
		location : str
			Directory to header files
	"""

	# Grab file location
	location = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]

	return location


class Hg19Genome(object):
    """
    Genome object for hg19
    """

    def __init__(self):
        """
        Initialize genome object
        """
        
        self.version = "hg19"
        self.n_CpGs = 28217448
        self.n_bases = 3137161264
        self.chrom_sizes = {"chr1":249250621,
                        "chr2":243199373,
                        "chr3":198022430,
                        "chr4":191154276,
                        "chr5":180915260,
                        "chr6":171115067,
                        "chr7":159138663,
                        "chr8":146364022,
                        "chr9":141213431,
                        "chr10":135534747,
                        "chr11":135006516,
                        "chr12":133851895,
                        "chr13":115169878,
                        "chr14":107349540,
                        "chr15":102531392,
                        "chr16":90354753,
                        "chr17":81195210,
                        "chr18":78077248,
                        "chr19":59128983,
                        "chr20":63025520,
                        "chr21":48129895,
                        "chr22":51304566,
                        "chrX":155270560,
                        "chrY":59373566,
                        "chrM":16571,
                        "chr1_gl000191_random":106433,
                        "chr1_gl000192_random":547496,
                        "chr4_ctg9_hap1":590426,
                        "chr4_gl000193_random":189789,
                        "chr4_gl000194_random":191469,
                        "chr6_apd_hap1":4622290,
                        "chr6_cox_hap2":4795371,
                        "chr6_dbb_hap3":4610396,
                        "chr6_mann_hap4":4683263,
                        "chr6_mcf_hap5":4833398,
                        "chr6_qbl_hap6":4611984,
                        "chr6_ssto_hap7":4928567,
                        "chr7_gl000195_random":182896,
                        "chr8_gl000196_random":38914,
                        "chr8_gl000197_random":37175,
                        "chr9_gl000198_random":90085,
                        "chr9_gl000199_random":169874,
                        "chr9_gl000200_random":187035,
                        "chr9_gl000201_random":36148,
                        "chr11_gl000202_random":40103,
                        "chr17_ctg5_hap1":1680828,
                        "chr17_gl000203_random":37498,
                        "chr17_gl000204_random":81310,
                        "chr17_gl000205_random":174588,
                        "chr17_gl000206_random":41001,
                        "chr18_gl000207_random":4262,
                        "chr19_gl000208_random":92689,
                        "chr19_gl000209_random":159169,
                        "chr21_gl000210_random":27682,
                        "chrUn_gl000211":166566,
                        "chrUn_gl000212":186858,
                        "chrUn_gl000213":164239,
                        "chrUn_gl000214":137718,
                        "chrUn_gl000215":172545,
                        "chrUn_gl000216":172294,
                        "chrUn_gl000217":172149,
                        "chrUn_gl000218":161147,
                        "chrUn_gl000219":179198,
                        "chrUn_gl000220":161802,
                        "chrUn_gl000221":155397,
                        "chrUn_gl000222":186861,
                        "chrUn_gl000223":180455,
                        "chrUn_gl000224":179693,
                        "chrUn_gl000225":211173,
                        "chrUn_gl000226":15008,
                        "chrUn_gl000227":128374,
                        "chrUn_gl000228":129120,
                        "chrUn_gl000229":19913,
                        "chrUn_gl000230":43691,
                        "chrUn_gl000231":27386,
                        "chrUn_gl000232":40652,
                        "chrUn_gl000233":45941,
                        "chrUn_gl000234":40531,
                        "chrUn_gl000235":34474,
                        "chrUn_gl000236":41934,
                        "chrUn_gl000237":45867,
                        "chrUn_gl000238":39939,
                        "chrUn_gl000239":33824,
                        "chrUn_gl000240":41933,
                        "chrUn_gl000241":42152,
                        "chrUn_gl000242":43523,
                        "chrUn_gl000243":43341,
                        "chrUn_gl000244":39929,
                        "chrUn_gl000245":36651,
                        "chrUn_gl000246":38154,
                        "chrUn_gl000247":36422,
                        "chrUn_gl000248":39786,
                        "chrUn_gl000249":38502}

        self.chromosomes = np.array(["chr1","chr2","chr3","chr4","chr5","chr6","chr7",
                                    "chr8","chr9","chr10","chr11","chr12","chr13",
                                    "chr14","chr15","chr16","chr17","chr18","chr19",
                                    "chr20","chr21","chr22","chrX","chrY","chrM",
                                    "chr1_gl000191_random", "chr1_gl000192_random",
                                    "chr4_ctg9_hap1", "chr4_gl000193_random",
                                    "chr4_gl000194_random", "chr6_apd_hap1",
                                    "chr6_cox_hap2", "chr6_dbb_hap3",
                                    "chr6_mann_hap4", "chr6_mcf_hap5",
                                    "chr6_qbl_hap6", "chr6_ssto_hap7",
                                    "chr7_gl000195_random", "chr8_gl000196_random",
                                    "chr8_gl000197_random", "chr9_gl000198_random",
                                    "chr9_gl000199_random", "chr9_gl000200_random",
                                    "chr9_gl000201_random", "chr11_gl000202_random",
                                    "chr17_ctg5_hap1", "chr17_gl000203_random",
                                    "chr17_gl000204_random", "chr17_gl000205_random",
                                    "chr17_gl000206_random", "chr18_gl000207_random",
                                    "chr19_gl000208_random", "chr19_gl000209_random",
                                    "chr21_gl000210_random", "chrUn_gl000211",
                                    "chrUn_gl000212", "chrUn_gl000213", "chrUn_gl000214",
                                    "chrUn_gl000215", "chrUn_gl000216", "chrUn_gl000217",
                                    "chrUn_gl000218", "chrUn_gl000219", "chrUn_gl000220",
                                    "chrUn_gl000221", "chrUn_gl000222", "chrUn_gl000223",
                                    "chrUn_gl000224", "chrUn_gl000225", "chrUn_gl000226",
                                    "chrUn_gl000227", "chrUn_gl000228", "chrUn_gl000229",
                                    "chrUn_gl000230", "chrUn_gl000231", "chrUn_gl000232",
                                    "chrUn_gl000233", "chrUn_gl000234", "chrUn_gl000235",
                                    "chrUn_gl000236", "chrUn_gl000237", "chrUn_gl000238",
                                    "chrUn_gl000239", "chrUn_gl000240", "chrUn_gl000241",
                                    "chrUn_gl000242", "chrUn_gl000243", "chrUn_gl000244",
                                    "chrUn_gl000245", "chrUn_gl000246", "chrUn_gl000247",
                                    "chrUn_gl000248", "chrUn_gl000249"])

        self.main_chromosomes = np.array(["chr1","chr2","chr3","chr4","chr5","chr6","chr7",
                                        "chr8","chr9","chr10","chr11","chr12","chr13",
                                        "chr14","chr15","chr16","chr17","chr18","chr19",
                                        "chr20","chr21","chr22","chrX","chrY","chrM"])

        self.autosomes = np.array(["chr1","chr2","chr3","chr4","chr5","chr6","chr7",
                                    "chr8","chr9","chr10","chr11","chr12","chr13",
                                    "chr14","chr15","chr16","chr17","chr18","chr19",
                                    "chr20","chr21","chr22"])


    def exons(self,
              chromosome: str = None,
              upstream: int = 0,
              downstream: int = 0) -> IntervalFrame:
        """
        Exons

        Parameters
        ----------
            chromosome : str
                Chromosome name
            upstream : int
                Upstream distance
            downstream : int
                Downstream distance
        
        Returns
        -------
            features : IntervalFrame
                Exons

        """

        features = get_exons(chromosome=chromosome,
                            upstream=upstream,
                            downstream=downstream)

        return features


    def tss(self,
            chromosome: str = None,
            upstream: int = 0,
            downstream: int = 0,
            gene_type: str = "all",
            filter_duplicates: bool = True) -> IntervalFrame:
        """
        Transcription Start Sites

        Parameters
        ----------
            chromosome : str
                Chromosome name
            upstream : int
                Upstream distance
            downstream : int
                Downstream distance
            gene_type : str
                Gene type
            filter_duplicates : bool
                Filter duplicates

        Returns
        -------
            features : IntervalFrame
        """

        return get_tss(chromosome=chromosome,
                       upstream=upstream,
                       downstream=downstream,
                       gene_type=gene_type,
                       filter_duplicates=filter_duplicates)
    
    def tes(self,
            chromosome: str = None,
            upstream: int = 0,
            downstream: int = 0,
            filter_duplicates: bool = True) -> IntervalFrame:
        """
        Transcription End Sites

        Parameters
        ----------
            chromosome : str
                Chromosome name
            upstream : int
                Upstream distance
            downstream : int
                Downstream distance
            filter_duplicates : bool
                Filter duplicates
        
        Returns
        -------
            features : IntervalFrame
        """

        return get_tes(chromosome=chromosome,
                       upstream=upstream,
                       downstream=downstream,
                       filter_duplicates=filter_duplicates)

    
    def cpg_islands(self,
                    chromosome: str = None,
                    upstream: int = 0,
                    downstream: int = 0) -> IntervalFrame:
        """
        CpG Islands

        Parameters
        ----------
            chromosome : str
                Chromosome name
            upstream : int
                Upstream distance
            downstream : int
                Downstream distance
            
        Returns
        -------
            features : IntervalFrame
        """

        return get_cpg_islands(chromosome=chromosome,
                               upstream=upstream,
                               downstream=downstream)


    def genes(self,
              chromosome: str = None,
              upstream: int = 0,
              downstream: int = 0,
              gene_type: int = "all") -> IntervalFrame:
        """
        Genes

        Parameters
        ----------
            chromosome : str
                Chromosome name
            upstream : int
                Upstream distance
            downstream : int
                Downstream distance
            gene_type : str
                Gene type

        Returns
        -------
            features : IntervalFrame
        """

        return get_gene_body(chromosome=chromosome,
                             upstream=upstream,
                             downstream=downstream,
                             gene_type=gene_type)

    def tfbs(self,
             chromosome: str = None,
             upstream: int = 0,
             downstream: int = 0) -> IntervalFrame:
        """
        Transcription Factor Binding Sites

        Parameters
        ----------
            chromosome : str
                Chromosome name
            upstream : int
                Upstream distance
            downstream : int
                Downstream distance
            
        Returns
        -------
            features : IntervalFrame
        """

        return get_tfbs(chromosome, upstream, downstream)


    def ctcf(self,
            chromosome: str = None,
            upstream: int = 0,
            downstream: int = 0) -> IntervalFrame:
        """
        CTCF Binding Sites

        Parameters
        ----------
            chromosome : str
                Chromosome name
            upstream : int
                Upstream distance
            downstream : int
                Downstream distance
        
        Returns
        -------
            features : IntervalFrame
        """
        
        return get_ctcf(chromosome, upstream, downstream)

    
    def bin_bias(self,
                 bin_size: int = 100000) -> IntervalFrame:
        """
        Bin Bias

        Parameters
        ----------
            bin_size : int
                Bin size
            
        Returns
        -------
            features : IntervalFrame
        """
        
        bias = get_bin_bias(bin_size)
        
        return bias
    

    def blacklist(self) -> IntervalFrame:
        """
        Blacklist

        Parameters
        ----------
            None

        Returns
        -------
            features : IntervalFrame
        """
        
        return get_blacklist()


    def repeats(self) -> IntervalFrame:
        """
        Repeats

        Parameters
        ----------
            None

        Returns
        -------
            features : IntervalFrame
        """
        
        return get_repeats()
    

    def get_snps(self) -> IntervalFrame:
        """
        SNPs

        Parameters
        ----------
            None

        Returns
        -------
            features : IntervalFrame
        """

        return get_snps()


    def kmers(self,
              intervals: LabeledIntervalArray,
              k: int = 2,
              last_n: int = 0) -> IntervalFrame:
        """
        K-mers

        Parameters
        ----------
            intervals : LabeledIntervalArray
                Intervals
            k : int
                K-mer length
            last_n : int
                Last N k-mers

        Returns
        -------
            features : IntervalFrame
        """

        return interval_kmers(intervals, k, last_n)

    
    def sequence(self,
                chromosome: str,
                start: int,
                end: int) -> str:
        """
        Get sequence

        Parameters
        ----------
            chromosome : str
                Chromosome name
            start : int
                Start position
            end : int
                End position

        Returns
        -------
            sequence : str
        """

        return get_sequence(chromosome, start, end)


    @property
    def reference_file(self):
        """
        Genome reference file name
        """

        return  get_data_file("hg19.2bit")