#!/bin/bash
#SBATCH --job-name=microtube_nu        # Job name
#SBATCH --partition=compute            # Partition name
#SBATCH --nodelist=node2
#SBATCH --nodes=1                      # Number of nodes
#SBATCH --ntasks-per-node=1            # Serial run - case is small (~18k cells)
#SBATCH --time=01:00:00                # Time limit (hh:mm:ss) - case runs in minutes
#SBATCH --output=log.slurm.%j.out      # Standard output log (%j = job ID)
#SBATCH --error=log.slurm.%j.err       # Standard error log

# --- 1. Load Environment ---
module load openmpi-4.1.5
module load gcc-11.5
module load openfoam-12
source /apps/codes/OpenFoam-12/OpenFOAM-12/etc/bashrc

echo "Job started on $(date)"
echo "Running on node: $(hostname)"

# --- 2. Go to Directory ---
cd $SLURM_SUBMIT_DIR

# --- 3. Clean Old Results ---
# Deletes old timestep folders, mesh, and any previous run artifacts to start fresh
rm -rf [1-9]* postProcessing processor* VTK dynamicCode constant/polyMesh log.blockMesh log.checkMesh log.foamRun

# --- 4. Run Mesh Generation (Serial) ---
echo "Running blockMesh..."
blockMesh > log.blockMesh 2>&1

echo "Checking Mesh..."
checkMesh > log.checkMesh 2>&1

# --- 5. Run Solver ---
echo "Running Solver..."
foamRun > log.foamRun 2>&1

# --- 6. Export results to VTK for post-processing ---
echo "Exporting to VTK..."
foamToVTK -latestTime > log.foamToVTK 2>&1

echo "Job finished on $(date)"
