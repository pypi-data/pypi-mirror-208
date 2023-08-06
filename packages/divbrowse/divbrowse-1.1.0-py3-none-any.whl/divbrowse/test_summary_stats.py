from dataclasses import dataclass
#from icecream import ic
import allel
import numpy as np
import pandas as pd
from timeit import default_timer as timer


def line():
    print('######################################################################################')


# function to calculate the mean of a numpy array

def calculate_mean(array):
    return np.mean(array)


# function to calculate minor allele frequency from a numpy array holding number of alternate allele calls
def calculate_minor_allele_freq(array):
    # slice of variant calls missing values to nan
    slice_of_variant_calls_missing_values_to_nan = np.where(array == -1, np.nan, array)
    # calculate the mean of the array
    mean = np.nanmean(slice_of_variant_calls_missing_values_to_nan, axis=0)
    # calculate the mean of the array divided by 2
    mean_halfed = mean / 2
    # calculate the minor allele frequency
    minor_allele_freq = np.where(mean_halfed < 0.5, mean_halfed, 1 - mean_halfed)
    return minor_allele_freq


# function to heterozygosity frequency from a numpy array holding number of alternate allele calls

def calculate_heterozygosity_freq(array):
    # slice of variant calls missing values to nan
    slice_of_variant_calls_missing_values_to_nan = np.where(array == -1, np.nan, array)
    # calculate the mean of the array
    mean = np.nanmean(slice_of_variant_calls_missing_values_to_nan, axis=0)
    # calculate the mean of the array divided by 2
    mean_halfed = mean / 2
    # calculate the minor allele frequency
    heterozygosity_freq = np.where(mean_halfed < 0.5, mean_halfed, 1 - mean_halfed)
    return heterozygosity_freq




def calc_maf(numbers_of_alternate_alleles):
    slice_of_variant_calls_missing_values_to_nan = np.where(numbers_of_alternate_alleles == -1, np.nan, numbers_of_alternate_alleles)
    means = np.nanmean(slice_of_variant_calls_missing_values_to_nan, axis=0) #, keepdims=True

    means_halfed = means / 2
    maf = np.where(means_halfed < 0.5, means_halfed, 1 - means_halfed)
    return np.nan_to_num(maf, nan=-1).tolist()


def calc_variants_summary_stats(numbers_of_alternate_alleles):    
    result = {}

    #start = timer()
    #result['maf'] = self.calculate_minor_allele_freq()
    result['maf'] = calc_maf(numbers_of_alternate_alleles)
    #log.debug("//////////////////////// calc_variants_summary_stats::calculate_minor_allele_freq => %f", timer() - start)

    start = timer()
    df_numbers_of_alternate_alleles = pd.DataFrame(numbers_of_alternate_alleles)
    counts = df_numbers_of_alternate_alleles.apply(pd.Series.value_counts, axis=0, normalize=True).fillna(0)
    #print("//////////////////////// calc_variants_summary_stats => %f", timer() - start)
    #print(counts)

    try:
        result['missing_freq'] = counts.loc[-1].values.tolist()
    except KeyError:
        result['missing_freq'] = np.zeros(counts.columns.size).tolist()

    df_numbers_of_alternate_alleles_with_nan = df_numbers_of_alternate_alleles.replace(-1, np.nan)
    #ic(df_numbers_of_alternate_alleles_with_nan.shape)
    counts_without_missing = df_numbers_of_alternate_alleles_with_nan.apply(pd.Series.value_counts, axis=0, normalize=True, dropna=True).fillna(0)
    counts_without_missing.index = counts_without_missing.index.astype(int, copy=False)

    try:
        result['heterozygosity_freq'] = counts_without_missing.loc[1].values.tolist()
    except KeyError:
        result['heterozygosity_freq'] = np.zeros(counts_without_missing.columns.size).tolist()


    #self.variants_summary_stats = result

    return result

def calc_variants_summary_stats_numpy(numbers_of_alternate_alleles):
    result = {}
    default = {-1: 0, 0: 0, 1: 0, 2: 0}
    num_samples = numbers_of_alternate_alleles.shape[0]

    def unique(arr):
        values, counts = np.unique(arr, return_counts=True)
        A = default
        B = dict(zip(values, counts))
        result = { k: A.get(k,0) + B.get(k,0) for k in list(B.keys()) + list(A.keys()) }
        return result

    start = timer()
    _counts = np.apply_along_axis(func1d=unique, axis=0, arr=numbers_of_alternate_alleles)

    counts = pd.DataFrame.from_records(_counts).T
    #print("//////////////////////// calc_variants_summary_stats_numpy => %f", timer() - start)
    #print(counts)
    

    result['missing_freq'] = (counts.loc[-1].values / num_samples).tolist()

    counts_without_missing = num_samples - counts.loc[-1].values
    #print(counts_without_missing)
    result['heterozygosity_freq'] = (counts.loc[1].values / counts_without_missing).tolist()

    return result


def allel_freq(test_slice, numbers_of_alternate_alleles):
    result = {}
    
    #print(test_slice)
    #print(test_slice.shape)

    #result['maf'] = calc_maf(numbers_of_alternate_alleles)

    num_samples = test_slice.shape[1]
    g = allel.GenotypeArray(test_slice)
    
    miss = g.count_missing(axis=1)
    #print(miss)
    #print(miss.shape)
    result['missing_freq'] = (miss / num_samples).tolist()

    called = g.count_called(axis=1)
    #print(called)
    #print(called.shape)

    het = g.count_het(axis=1)
    #print(het)
    #print(het.shape)

    het_freq = het / called
    #print(het_freq)
    result['heterozygosity_freq'] = het_freq.tolist()

    return result

    """
    ac = g.count_alleles()
    print(ac)
    print(ac.shape)
    freq = ac.to_frequencies()
    print(freq)
    print(freq.shape)
    """



#exit()


numbers_of_alternate_alleles = np.load('_______testdata_numbers_of_alternate_alleles_______.npy')
print(numbers_of_alternate_alleles.shape)
start = timer()
result = calc_variants_summary_stats(numbers_of_alternate_alleles)
print("//////////////////////// calc_variants_summary_stats => %f", timer() - start)
print(result)
line()

start = timer()
result = calc_variants_summary_stats_numpy(numbers_of_alternate_alleles)
print("//////////////////////// calc_variants_summary_stats_numpy => %f", timer() - start)
print(result)
line()

test_slice = np.load('_______testdata_sliced_variant_calls_______.npy')
start = timer()
result = allel_freq(test_slice, numbers_of_alternate_alleles)
print("//////////////////////// allel_freq => %f", timer() - start)
print(result)