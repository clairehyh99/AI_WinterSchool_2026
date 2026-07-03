#!/usr/bin/env python3
import os
import sys
import urllib.request
import gzip
import shutil
import subprocess

# Target configurations
FASTA_URL = "https://github.com/scicrow/AI_WinterSchool_2026/raw/main/Sbicolor_454_v3.0.1_Chr09.fa.gz"
GFF3_URL = "https://ftp.ensemblgenomes.ebi.ac.uk/pub/plants/release-59/gff3/sorghum_bicolor/Sorghum_bicolor.Sorghum_bicolor_NCBIv3.59.gff3.gz"

FASTA_OUT_GZ = "sorghum_Chr09.fa.gz"
FASTA_OUT = "sorghum_Chr09.fa"
GFF3_OUT_FULL = "sorghum_full.gff3.gz"
GFF3_OUT_CHR09 = "sorghum_Chr09.gff3"

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

def download_file(url, dest):
    print(f"Downloading {url} to {dest}...")
    # Add User-Agent headers to avoid getting blocked by FTP/HTTP gateways
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    print("Download complete.")

def decompress_gz(src, dest):
    print(f"Decompressing {src} to {dest}...")
    with gzip.open(src, 'rb') as f_in, open(dest, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print("Decompression complete.")

def prepare_fasta():
    if not os.path.exists(FASTA_OUT):
        if not os.path.exists(FASTA_OUT_GZ):
            download_file(FASTA_URL, FASTA_OUT_GZ)
        decompress_gz(FASTA_OUT_GZ, FASTA_OUT)
    
    # Index the FASTA
    print("Indexing FASTA using pysam...")
    try:
        import pysam
        if not os.path.exists(FASTA_OUT + ".fai"):
            pysam.faidx(FASTA_OUT)
        print("FASTA indexing complete.")
    except ImportError:
        print("Warning: pysam not installed. Attempting to use samtools from environment...")
        samtools_bin = find_binary("samtools")
        subprocess.run([samtools_bin, "faidx", FASTA_OUT], check=True)
        print("FASTA indexing complete.")

def prepare_gff():
    if not os.path.exists(GFF3_OUT_CHR09 + ".gz"):
        if not os.path.exists(GFF3_OUT_FULL):
            download_file(GFF3_URL, GFF3_OUT_FULL)
        
        print(f"Filtering and renaming GFF3 coordinates for Chr09...")
        with gzip.open(GFF3_OUT_FULL, 'rt') as f_in, open(GFF3_OUT_CHR09, 'w') as f_out:
            for line in f_in:
                if line.startswith('#'):
                    # Update sequence-region header if it points to chromosome 9
                    if line.startswith("##sequence-region 9 "):
                        line = line.replace("##sequence-region 9 ", "##sequence-region Chr09 ")
                    elif line.startswith("##sequence-region 9\t"):
                        line = line.replace("##sequence-region 9\t", "##sequence-region Chr09\t")
                    f_out.write(line)
                else:
                    parts = line.split('\t')
                    # Chromosome 9 in Ensembl GFF3 is labeled "9"
                    if parts[0] == "9":
                        parts[0] = "Chr09"
                        f_out.write('\t'.join(parts))
        
        # Compress with bgzip
        bgzip_bin = find_binary("bgzip")
        print(f"Compressing GFF3 with bgzip (using {bgzip_bin})...")
        subprocess.run([bgzip_bin, "-f", GFF3_OUT_CHR09], check=True)
        
        # Index with tabix
        tabix_bin = find_binary("tabix")
        print(f"Indexing GFF3 with tabix (using {tabix_bin})...")
        subprocess.run([tabix_bin, "-p", "gff", GFF3_OUT_CHR09 + ".gz"], check=True)
        
        # Clean up intermediate uncompressed file if it still exists
        if os.path.exists(GFF3_OUT_CHR09):
            os.remove(GFF3_OUT_CHR09)
        print("GFF3 preparation complete.")
    else:
        print("Prepared GFF3 file already exists.")

def main():
    print("=== Preparing minimal Sorghum Chr09 reference data ===")
    prepare_fasta()
    prepare_gff()
    print("=== Data preparation finished successfully! ===")

if __name__ == "__main__":
    main()
