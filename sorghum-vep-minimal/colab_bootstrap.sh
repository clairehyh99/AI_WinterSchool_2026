#!/bin/bash
set -e

echo "=== Bootstrapping minimal Sorghum VEP in Colab ==="

# Create bin directory
mkdir -p bin

# Download standalone micromamba for linux-64
if [ ! -f bin/micromamba ]; then
    echo "Downloading standalone micromamba for Linux x86_64..."
    curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
fi

# Set executable permission
chmod +x bin/micromamba

# Create the conda environment in /content/vep_env using environment.yml
echo "Creating isolated VEP conda environment at /content/vep_env..."
./bin/micromamba env create -p /content/vep_env -f environment.yml -y

echo "=== VEP environment created successfully at /content/vep_env ==="
echo "VEP path: /content/vep_env/bin/vep"
echo "bgzip path: /content/vep_env/bin/bgzip"
echo "tabix path: /content/vep_env/bin/tabix"
