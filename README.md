# AI_WinterSchool_2026

Workshops for Day 3 of the 2026 Winter School for AI in Predictive Agriculture @ UQ, Queensland AU.
Using DNA foundation models to inform SNP selection for genomic prediction tasks.

## Workshop Files

- `data/panicle_length_genomatrix_snps.vcf`: A sorghum genotype matrix of 1000 SNPs across 527 accessions. SNPs match Chr9_random1000 SNPs.
- `data/pheno_PL_filtered.tsv`: Phenotype data for panicle length in sorghum across 527 accessions.
- `data/DS24-Chr9_random1000_maf05.tsv`: 1000 randomly selected SNPs from *Sorghum bicolor* chromosome 9.
- `data/sap_flowering.pheno`: Tab-separated values file containing phenotype data ("days to flowering") for the Sorghum Association Panel (SAP) population (Chromosome 1).
- `data/snp_matrix_1000.csv.gz`: Compressed CSV file containing a genotype matrix of 1,000 randomly selected SNPs from Chromosome 1. The accessions in this matrix correspond to those in `sap_flowering.pheno`.
- `data/260706_df_full_comparison.csv`: CSV file containing Plant Caduceus model inference scores (including embedding distance, expression score, and log-likelihood probability score along with ensemble ranks) for the 1,000 selected Chromosome 1 SNPs in `sap_flowering_1000.vcf`.
- `data/sap_flowering_alleles.tsv`: TSV file mapping each of the 1,000 Chromosome 1 SNPs to its exact reference genome allele and alternative allele.

---

## Sorghum bicolor Minimal Ensembl VEP (Chr09)

A minimal, offline setup of Ensembl Plant VEP (Variant Effect Predictor) tailored for predicting variant effects on **Chromosome 9** of *Sorghum bicolor*. Designed to be loaded and run in seconds inside Google Colab without overriding or breaking your existing Python/ML environment.

The codebase for this minimal setup is located in the [sorghum-vep-minimal/](sorghum-vep-minimal/) directory.

### Features
- **Ultra-fast setup**: Uses a standalone `micromamba` binary to install VEP and `htslib` into an isolated prefix. Takes ~60 seconds to set up.
- **Isolated environment**: Preserves Colab's default Python environment (including PyTorch, CUDA, and transformers).
- **Coordinate-aligned**: Automatically resolves naming mismatches between Ensembl GFF3 (which uses `9`) and Phytozome FASTA (which uses `Chr09`).
- **Python Integration**: Seamlessly write variant DataFrames to VCF, run VEP, and read predicted consequences back into Pandas DataFrames.

---

### Quick Start in Google Colab

Run the following cell to bootstrap the environment and download reference data.

#### 1. Installation & Setup
```bash
# 1. Clone this repository
!git clone https://github.com/scicrow/AI_WinterSchool_2026.git
%cd AI_WinterSchool_2026/sorghum-vep-minimal

# 2. Bootstrap the isolated VEP conda environment
!bash colab_bootstrap.sh

# 3. Download and filter Chr09 GFF3/FASTA files
!python prepare_data.py
```

#### 2. Running VEP from Python
Here is how you can integrate VEP into your python workflow:

```python
import pandas as pd
from vep_wrapper import write_snps_to_vcf, run_vep, load_vep_results

# Define some test SNPs on Chromosome 9
snps = [
    {"id": "test_snp_1", "pos": 12682424, "ref": "C", "alt": "G"},
    {"id": "test_snp_2", "pos": 25373090, "ref": "A", "alt": "G"}
]

# 1. Convert to VCF format
write_snps_to_vcf(snps, "input_variants.vcf")

# 2. Run VEP programmatically in offline mode
run_vep("input_variants.vcf", "vep_predictions.txt")

# 3. Load VEP predictions directly into a Pandas DataFrame
df_predictions = load_vep_results("vep_predictions.txt")
display(df_predictions.head())
```

---

### Local Installation

If running locally on a system with Conda/Mamba installed:

```bash
# Navigate to the tool directory
cd sorghum-vep-minimal

# Create the environment
conda env create -f environment.yml

# Activate the environment
conda activate sorghum-vep

# Download and index reference data
python prepare_data.py
```

### sorghum-vep-minimal Structure
- [environment.yml](sorghum-vep-minimal/environment.yml): Conda environment configuration.
- [colab_bootstrap.sh](sorghum-vep-minimal/colab_bootstrap.sh): Automates isolated conda setup in Colab.
- [prepare_data.py](sorghum-vep-minimal/prepare_data.py): Handles downloading, renaming, and indexing chromosome 9 files.
- [vep_wrapper.py](sorghum-vep-minimal/vep_wrapper.py): Provides Python APIs to generate VCFs, invoke VEP, and load predictions.