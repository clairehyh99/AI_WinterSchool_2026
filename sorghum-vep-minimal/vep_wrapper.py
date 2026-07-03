#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

def find_binary(name):
    # Try current PATH first
    path = shutil.which(name)
    if path:
        return path
    # Try standard Colab VEP environment paths
    colab_path = f"/content/vep_env/bin/{name}"
    if os.path.exists(colab_path):
        return colab_path
    # Try active conda env path
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        env_path = os.path.join(conda_prefix, "bin", name)
        if os.path.exists(env_path):
            return env_path
    return name

def write_snps_to_vcf(snp_list, vcf_path, chrom="Chr09"):
    """
    Converts a list of dicts (with 'pos', 'ref', 'alt', and optional 'id') or a pandas DataFrame
    into a standard VCF file for VEP.
    """
    import pandas as pd
    if isinstance(snp_list, pd.DataFrame):
        rows = snp_list.to_dict('records')
    else:
        rows = snp_list

    with open(vcf_path, 'w') as f:
        f.write("##fileformat=VCFv4.2\n")
        f.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        for row in rows:
            variant_id = row.get('id', row.get('snp_id', '.'))
            pos = row['pos']
            ref = row['ref']
            alt = row['alt']
            f.write(f"{chrom}\t{pos}\t{variant_id}\t{ref}\t{alt}\t.\t.\t.\n")
    print(f"Wrote {len(rows)} variants to VCF file: {vcf_path}")

def run_vep(vcf_in, txt_out, extra_args=None):
    """
    Runs Ensembl VEP offline using the local Sorghum Chr09 FASTA and GFF3 files.
    """
    vep_bin = find_binary("vep")
    gff_file = "sorghum_Chr09.gff3.gz"
    fasta_file = "sorghum_Chr09.fa"
    
    if not os.path.exists(gff_file):
        raise FileNotFoundError(f"GFF3 annotation file not found: {gff_file}. Please run prepare_data.py first.")
    if not os.path.exists(fasta_file):
        raise FileNotFoundError(f"FASTA reference file not found: {fasta_file}. Please run prepare_data.py first.")
        
    cmd = [
        vep_bin,
        "-i", vcf_in,
        "-o", txt_out,
        "--offline",
        "--gff", gff_file,
        "--fasta", fasta_file,
        "--species", "sorghum_bicolor",
        "--force_overwrite"
    ]
    if extra_args:
        cmd.extend(extra_args)
        
    print(f"Running VEP: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("VEP execution complete.")

def load_vep_results(txt_path):
    """
    Reads the VEP output text file and loads it into a Pandas DataFrame.
    """
    import pandas as pd
    
    header_row = None
    with open(txt_path, 'r') as f:
        for idx, line in enumerate(f):
            if line.startswith("#Uploaded_variation"):
                header_row = idx
                break
    
    if header_row is None:
        raise ValueError(f"Could not find VEP header row starting with '#Uploaded_variation' in {txt_path}")
        
    headers = []
    with open(txt_path, 'r') as f:
        for idx, line in enumerate(f):
            if idx == header_row:
                headers = line.strip().lstrip('#').split('\t')
                break
                
    df = pd.read_csv(
        txt_path,
        sep='\t',
        comment='#',
        header=None,
        names=headers,
        skiprows=header_row + 1
    )
    return df
