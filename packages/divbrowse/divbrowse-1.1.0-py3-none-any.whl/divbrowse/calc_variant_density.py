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

import base64
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
sns.set_style('white')
sns.set_style('ticks')

plt.switch_backend('agg')
#plt.style.use('seaborn-whitegrid')


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

print(gd.list_chrom)

#exit()

_chr = 'chr1H'
chrom_range = gd.idx_pos.locate_key(_chr)
print(chrom_range)
pos = gd.pos[chrom_range]
print(pos.shape)






slice = gd.get_slice_of_variant_calls(
    chrom = 'chr1H',
    startpos = 539425,
    endpos = 539904,
    count = None,
    samples = gd.samples,
    variant_filter_settings = None,
    calc_summary_stats = True
)

#print(slice)


start = timer()
analysis = Analysis(slice)
distances = analysis.calc_distance_matrix(samples = gd.samples)
log.debug("==== Analysis() + analysis.calc_distance_to_reference() => calculation time: %f", timer() - start)

print(distances)
print(distances.shape)

#fig = Figure()
#ax = fig.subplots()
#ax = fig.add_subplot(1, 1, 1)
#print(ax)
sns.set(font_scale=2)
cmap = sns.color_palette('viridis', as_cmap=True)

clustergrid = sns.clustermap(distances, figsize=(20, 20), cmap = cmap, xticklabels=False, yticklabels=False) # , xticklabels=gd.samples.tolist(), yticklabels=gd.samples.tolist()
#clustergrid = sns.clustermap(slice.numbers_of_alternate_alleles, figsize=(20, 20), square=True, cmap = cmap)
#print(clustergrid)

# heatmap of distance matrix, unsorted
#plt.figure(figsize=(20,20))
#ax = sns.heatmap(distances, cmap = cmap, xticklabels=False, yticklabels=False)

#plt.savefig('heatmap_1_distances.png')
#fig.savefig('clustermap_7.png') # , format="png"
#clustergrid.savefig('clustermap_7.png')

buf = BytesIO()
clustergrid.savefig(buf, format='png')
data = base64.b64encode(buf.getbuffer()).decode("ascii")
print(data)

exit()






start = timer()

bin_width = 1000000
bins = np.arange(0, pos.max(), bin_width)
# set X coordinate as bin midpoints
x = (bins[1:] + bins[:-1])/2
print(bins)
print(x)
# compute variant density
h, _ = np.histogram(pos, bins=bins)
print(h)
print(h.shape)
y = h / bin_width

print("//////////////////////// # compute variant density => %f", timer() - start)



"""
# plot
fig, ax = plt.subplots(figsize=(20, 12))
#sns.despine(ax=ax, offset=5)
ax.plot(x, y)
ax.set_xlabel('Position (bp)')
ax.set_ylabel('Density (bp$^{-1}$)')
ax.set_title('Variant density');

plt.savefig('variant_density.png')
"""

sns.set_theme(style="whitegrid")

# Draw a scatter plot while assigning point colors and sizes to different
# variables in the dataset
f, ax = plt.subplots(figsize=(20, 12))
sns.despine(f, left=True, bottom=True)
clarity_ranking = ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]
sns.scatterplot(x=x, y=y, sizes=(1, 8), linewidth=0, ax=ax)
plt.savefig('variant_density_3.png')


exit()


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