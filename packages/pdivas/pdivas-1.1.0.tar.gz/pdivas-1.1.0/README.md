# PDIVAS : Pathogenicity Predictor for Deep-Intronic Variants causing Aberrant Splicing
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Sumary
- PDIVAS is a pathogenicity predictor for deep-intronic variants causing aberrant splicing.
- The deep-intronic variants can cause pathogenic pseudoexons or extending exons which disturb the normal gene expression and can be the causal of patiens with Mendelian diseases. 
- PDIVAS efficiently prioritizes the causal candidates from a vast number of deep-intronic variants detected by whole-genome sequencing. 
- The scope of PDIVAS prediction is variants in protein-coding genes on autosomes and X chromosome. 
- This command-line interface is compatible with variant files in VCF format. 
 
PDIVAS is modeled on random forest algorism to classify pathogenic and benign variants with referring to features from  
1) **Splicing predictors** of [SpliceAI](https://github.com/Illumina/SpliceAI) ([Jaganathan et al., Cell 2019](https://www.sciencedirect.com/science/article/pii/S0092867418316295?via%3Dihub)) and [MaxEntScan](http://hollywood.mit.edu/burgelab/maxent/Xmaxentscan_scoreseq.html) ([Yao and Berge, j. Comput. Biol. 2004](https://www.liebertpub.com/doi/10.1089/1066527041410418?url_ver=Z39.88-2003&rfr_id=ori%3Arid%3Acrossref.org&rfr_dat=cr_pub++0pubmed))  
(*)The output module of SpliceAI was customed for PDIVAS features (see the Option2, for the details).
          
 2) **Human splicing constraint score** of [ConSplice](https://github.com/mikecormier/ConSplice) ([Cormier et al., BMC Bioinfomatics 2022](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-022-05041-x)).

## Reference & contact
bioarxiv?  
a0160561@yahoo.co.jp (Ryo Kurosawa at Kyoto University)

## Details
Please view the detailed usage and methods at https://github.com/shiro-kur/PDIVAS and medRxiv. 

