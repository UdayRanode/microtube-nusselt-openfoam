# Microtube Nusselt Number Validation (OpenFOAM)

Recreation of **Case 1** from:

> Pourghasemi, M., Fathi, N., *"Error Quantification of Nusselt Number Analysis in Miniature Heat Sinks: Verification and Validation Assessment,"* ASME VVS2021-65326.

---

## Problem Statement

Laminar water flow through a straight circular **microtube** is simulated, with a constant, uniform heat flux applied at the wall. The goal is to compute the **local Nusselt number, Nu(z)**, along the tube length and confirm that it converges to the known analytical fully-developed value as the flow moves downstream -- a standard verification exercise for CFD heat-transfer solvers.

| Parameter | Value |
|---|---|
| Fluid | Water |
| Diameter, D | 500 um |
| Length, L | 30 mm |
| Reynolds number, Re | 100 |
| Wall heat flux, q" | 10 W/cm2 (100,000 W/m2) |
| Inlet temperature, T_in | 25 C (298.15 K) |
| **Target result** | Nu -> 4.36 (fully developed, constant q") |

Water properties (constant): rho = 997 kg/m3, mu = 8.9e-4 Pa.s, Cp = 4181 J/kg.K, Pr = 6.13, k ~ 0.606 W/m.K.

Inlet condition is specified as a fixed **mass flow rate** (mdot = 3.5e-05 kg/s), computed from Re = rho*U*D/mu so that U ~ 0.179 m/s.

The physics solved: continuity, momentum, and energy equations, discretized with a finite-volume method, solved with the SIMPLE algorithm -- matching the paper's numerical procedure.

---

## How to Run on HPC

### 1. Environment setup (required every new session)

```bash
module load openmpi-4.1.5
module load gcc-11.5
module load openfoam-12
source /apps/codes/OpenFoam-12/OpenFOAM-12/etc/bashrc
```

> **Important:** `module load openfoam-12` alone is *not* sufficient on this cluster -- it leaves `LD_LIBRARY_PATH` incomplete and `blockMesh`/`foamRun` will fail with `error while loading shared libraries`. The `source .../bashrc` line above is mandatory and must be run every time you open a new terminal/SSH session.

Verify it worked:
```bash
which blockMesh
```
Should print a path, not `command not found`.

### 2. Get the case

```bash
git clone https://github.com/UdayRanode/microtube-nusselt-openfoam.git
cd microtube-nusselt-openfoam/initial_dir
```

### 3. Python dependencies (for post-processing)

```bash
pip install pyvista numpy matplotlib --user
```

### 4. Submit the SLURM job

```bash
sbatch run_microtube.slurm
```

Check status:
```bash
squeue -u $USER
```

The job runs `blockMesh -> checkMesh -> foamRun -> foamToVTK` automatically. Check `log.slurm.<jobid>.out` and `log.foamRun` for progress/errors once it completes (should take well under a minute -- this is a small, ~18,000-cell case).

> **Note on account/partition:** this cluster ties student accounts to a partition of the *same name* as the account (e.g. account `student` maps to partition `student`, not a generically-named `compute` partition). If `sbatch` rejects the job with an account/partition error, check your own values with:
> ```bash
> sacctmgr show assoc user=$USER format=account,partition
> ```
> and update `#SBATCH --account=` / `#SBATCH --partition=` in `run_microtube.slurm` to match.

### 5. Post-process (compute and plot Nu(z))

```bash
cd initial_dir
python3 scripts/nuz2.py
python3 scripts/plot_nuz.py
```

`nuz2.py` reads the exported VTK fields and produces `NuZ_results_weighted.csv`. `plot_nuz.py` reads that CSV and produces `Nu_z_plot.png`, comparing against the theoretical Nu = 4.36 line.

> **Filename gotcha:** `foamToVTK` names its output files after the **case folder name**, not a fixed string. If your case folder isn't named `initial_dir`, open `scripts/nuz2.py` and update the `VOL_VTK` / `WALL_VTK` filename variables (e.g. `VTK/<your_folder_name>_<latest_timestep>.vtk`) before running.

---

## Repository / File Guide

```
initial_dir/
├── 0/                    Initial & boundary conditions
│   ├── U                 Inlet: fixed mass flow rate. Wall: no-slip.
│   ├── p                 Outlet: fixed pressure (101325 Pa). Inlet/wall: zeroGradient.
│   └── T                 Inlet: fixed 298.15 K. Wall: fixed heat flux (externalWallHeatFluxTemperature).
├── constant/
│   ├── momentumTransport         simulationType laminar (no turbulence model).
│   ├── thermophysicalTransport   simulationType laminar + Fourier conduction model.
│   └── thermophysicalProperties  Water's physical properties (rho, mu, Cp, Pr, molWeight).
├── system/
│   ├── blockMeshDict      Parametrized O-grid mesh (see "Mesh" section below).
│   ├── controlDict        application foamRun; solver fluid; -- steady-state SIMPLE run.
│   ├── fvSchemes          Discretization schemes (2nd-order upwind convection, as in the paper).
│   ├── fvSolution         Linear solver settings, SIMPLE relaxation factors, convergence tolerances.
│   └── wallTGraph / bulkTGraph / wallHeatFlux1   (Legacy function-object attempts -- not
│                                                   currently wired into controlDict; see notes below.)
├── scripts/
│   ├── nuz2.py            Reads VTK output, computes volume/area-weighted Nu(z), saves CSV.
│   └── plot_nuz.py        Plots Nu(z) against the Nu = 4.36 theoretical line.
└── run_microtube.slurm    SLURM batch script: blockMesh -> checkMesh -> foamRun -> foamToVTK.
```

`constant/polyMesh/` is intentionally **not** committed -- it's fully regenerated by `blockMesh` from `system/blockMeshDict`. Same for timestep folders, `VTK/`, `dynamicCode/`, and log files -- these are run outputs, not inputs.

---

## Recreating Figure 2 -- Constant Wall Temperature Case

The paper also reports Nu(z) for the same tube with a **fixed wall temperature** (80 C) instead of fixed heat flux, converging to a different theoretical value: **Nu -> 3.66**.

To recreate this from the current case, only **one file** needs to change -- everything else (mesh, flow rate, inlet properties) stays identical:

**Edit `0/T`:**
```
wall
{
    type            fixedValue;
    value           uniform 353.15;   // 80 C
}
```
This replaces the current `externalWallHeatFluxTemperature` (flux) boundary condition with a simple `fixedValue` (temperature) condition.

Then re-run the same pipeline (`blockMesh -> checkMesh -> foamRun -> foamToVTK -> nuz2.py`). In `nuz2.py`, the Nu(z) formula itself doesn't change -- T_wall(z) will simply come out as a near-constant ~353.15 K instead of a rising curve, and the comparison line in `plot_nuz.py` should be updated from 4.36 to **3.66**.

---

## Why a Coarser Mesh Than the Paper?

The paper's three mesh tiers (Table 1) range from 0.06M to 3.3M cells, generated in ANSYS Fluent Meshing with explicit boundary-layer inflation. This repository instead uses a **hand-built OpenFOAM `blockMesh` O-grid** (a central square block plus four curved arms -- the standard structured-mesh pattern for circular pipe cross-sections), currently set to **~18,000 cells**.

This is a deliberate choice, not a shortcut around mesh independence:

- **Purpose of this repo is workflow validation**, not literal replication of the paper's absolute cell counts. What matters for verification is that Nu(z) converges to the correct theoretical value (4.36) as the mesh refines -- which it does at this resolution, since the O-grid mesh already places its finest cells near the wall (`gradRing` grading parameter) exactly where the thermal boundary layer needs resolution, similar in spirit to the paper's inflation layers.
- **Practical constraint**: this case is meant to be runnable on a laptop as well as HPC, without requiring a proprietary mesher (ANSYS) or a large compute allocation for a first pass.
- **`blockMeshDict` is fully parametrized** (`nCore`, `nRing`, `nAxial`, `gradRing`) specifically so it can be trivially rerun at higher resolution -- e.g., increasing `nAxial` and `nRing` reproduces the spirit of the paper's own mesh-refinement study (Table 1 / Figure 3) and lets you compute your own observed order of accuracy, without needing ANSYS Meshing at all.

If reproducing the paper's exact cell counts and mesh-convergence numbers (p = 1.81) is the goal, rerun `blockMesh` at 2-3 scaled-up parameter sets and follow the L2-norm / Richardson-extrapolation procedure described in the paper's Section 2.

---

## Notes on OpenFOAM Version Differences

This case was originally developed on **OpenFOAM-13** and later ported to run on the HPC's **OpenFOAM-12**. A few version-specific issues were found and fixed along the way -- documented here in case they resurface:

- `blockMeshDict` arcs must use an explicit midpoint (`arc v1 v2 (x y z)`), not the `origin` shorthand.
- Negative variable substitution (`-$var`) inside coordinate tuples isn't parsed correctly on either version -- define a separate negated variable instead (e.g. `rNeg -0.00025;`).
- `constant/thermophysicalTransport` requires a nested sub-dictionary even for the simplest case:
  ```
  simulationType  laminar;
  laminar
  {
      model   Fourier;
  }
  ```
- v12's post-processing function objects (`cutLayerAverage`, `patchCutLayerAverage`) use a **different keyword interface** than v13's (`patch` singular vs `patches`, `direction` vs `layerDirection`, additional required keys like `nPoints`) -- and `cutLayerAverage` itself is a v13-only addition, not reliably available on v12. **For this reason, post-processing in this repo uses `foamToVTK` + `pyvista` instead of native OpenFOAM sampling function objects**, since this path is stable across both versions.
- Always run `blockMesh` / `checkMesh` / `foamRun` from the **case root** (containing `0/`, `constant/`, `system/`), not from inside `system/`.

---

## Resources

References followed while building this case:

- **[OpenFOAM Official Documentation (v2606)](https://doc.openfoam.com/2606/)** -- official reference documentation covering case setup, boundary conditions, function objects, and solver usage.
- **[CFD Direct: CFD General Principles](https://doc.cfd.direct/notes/cfd-general-principles/contents)** -- book/course notes covering the underlying numerical methods (finite volume discretization, SIMPLE algorithm, convergence) used by OpenFOAM's solvers.
- **[OpenFOAM Source Code -- fvOptions (GitLab, v2606)](https://gitlab.com/openfoam/core/openfoam/-/tree/OpenFOAM-v2606/src/fvOptions)** -- official OpenFOAM source repository, used for verifying exact keyword names and dictionary structures when version-specific syntax issues came up.

---

## License / Attribution

Educational recreation of a published verification & validation study for coursework purposes. Original paper: Pourghasemi & Fathi, ASME VVS2021-65326.
