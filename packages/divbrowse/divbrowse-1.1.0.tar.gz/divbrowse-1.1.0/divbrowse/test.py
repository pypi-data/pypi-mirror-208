import allel

test = allel.gff3_to_dataframe('171030_Hv_IBSC_PGSB_r1_HighConf_genes_only_reformatted.gff', attributes=['ID', 'confidence', 'Parent', 'description', 'ontology'])

print(test)