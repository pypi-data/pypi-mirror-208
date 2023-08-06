#from icecream import ic
import logging
import json
from timeit import default_timer as timer

from flask import Flask, Response, jsonify, request

import allel
import numpy as np
import pandas as pd
from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.tools.inputs import inputs
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import RobustScaler
import yaml

from divbrowse import log
from divbrowse.lib.annotation_data import AnnotationData
from divbrowse.lib.genotype_data import GenotypeData
from divbrowse.lib.variant_calls_slice import VariantCallsSlice
from divbrowse.lib.analysis import Analysis

from divbrowse.lib.utils import ApiError
from divbrowse.lib.utils import StrictEncoder



try:
    with open('divbrowse.config.yml') as config_file:
        config = yaml.full_load(config_file)
except FileNotFoundError:
    print('ERROR: Divbrowse config file `divbrowse.config.yml` not found in current directory!')
    exit(1)

#print(config)


log.info('Instanciate GenotypeData classes')
gd = GenotypeData(config)

log.info('Instanciate AnnotationData classes')
ad = AnnotationData(config, gd)


genes_only = ad.genes.loc[(ad.genes['type'] == 'gene')]
print(genes_only)

num_samples = 1316 # 300
num_genes = len(genes_only)
#num_genes = 10

print(num_genes)







def count_genic_variants(row):
    print(str(row['seqid'])+' / '+str(row['ID']))
    _chromosome_gff3 = row['seqid']
    _chromosome_vcf = ad.metadata_gff3['gff3_to_vcf_chromosome_mapping'][ _chromosome_gff3 ]
    number_of_variants = gd.count_variants_in_window(str(_chromosome_vcf), row['start'], row['end'])
    return pd.Series( [number_of_variants ], index=['number_of_variants'])






def count_genes_and_save_csv(genes_only):
    genes_number_of_variants = genes_only.apply(count_genic_variants, axis=1, result_type='expand')
    #print(genes_number_of_variants)
    merged = pd.concat([genes_only, genes_number_of_variants], axis=1)
    genes_only = merged.copy()
    #genes_only.to_csv('genes_list.csv', index=False)
    genes_only_export = genes_only[['ID', 'seqid', 'start', 'end', 'strand', 'primary_confidence_class', 'number_of_variants']]
    #genes_only_export.to_json('genes_list.json', orient='columns', index=False)
    genes_only_export.to_csv('genes_list_shape_core1000_and_cultivars_2022-11-12.csv', index=False)


#genes_only = genes_only.iloc[:20]
count_genes_and_save_csv(genes_only)

print('DONE')
exit()




supermatrix = np.empty((num_samples**2, num_genes), dtype=np.dtype('float64')).T # len(genes_only)

i = 0
for gene in genes_only.itertuples():
    #print(gene)
    #print(str(gene.ID)+' = '+str(gene.seqid)+' / '+str(gene.start)+' - '+str(gene.end))
    
    _chromosome_vcf = ad.metadata_gff3['gff3_to_vcf_chromosome_mapping'][ gene.seqid ]
    slice = gd.get_slice_of_variant_calls(chrom=str(_chromosome_vcf), startpos=int(gene.start), endpos=int(gene.end), samples=gd.samples)

    #print(type(slice.numbers_of_alternate_alleles))
    #print(slice.numbers_of_alternate_alleles.shape)
    #print(slice.numbers_of_alternate_alleles)

    #imputed = impute_with_mean(slice.numbers_of_alternate_alleles)
    analysis = Analysis(slice)
    imputed = analysis.get_imputed_calls()


    distances = pairwise_distances(imputed, n_jobs=1, metric='euclidean')
    #print(distances.shape)
    #print(distances.dtype)
    #print(distances)

    distances_flatten = distances.flatten()
    #print(distances_flatten.shape)
    #print(distances_flatten)
    supermatrix[i] = distances_flatten

    #if i > 5:
    #    break

    i += 1
    print(str(i)+' / '+str(num_genes))

print("====================================================")
print(supermatrix.shape)
print(supermatrix)

np.save('gene_distances_2022-11-10.npy', supermatrix)