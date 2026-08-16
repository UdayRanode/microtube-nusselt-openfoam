import pyvista as pv
import numpy as np

D = 0.0005
k_fluid = 0.606
q = 100000
L = 0.03
nBins = 40

# --- Bulk: use CELL data, weight by cell volume ---
vol = pv.read("VTK/initial_dir_625.vtk")
vol = vol.compute_cell_sizes(length=False, area=False, volume=True)
cell_centers = vol.cell_centers().points
z_vol = cell_centers[:, 2]
T_vol = vol.cell_data["T"]
Uz_vol = vol.cell_data["U"][:, 2]
Vol_vol = vol.cell_data["Volume"]

# --- Wall: use CELL data, weight by face area ---
wall = pv.read("VTK/wall/wall_625.vtk")
wall = wall.compute_cell_sizes(length=False, area=True, volume=False)
wall_centers = wall.cell_centers().points
z_wall = wall_centers[:, 2]
T_wall_cells = wall.cell_data["T"]
Area_wall = wall.cell_data["Area"]

z_edges = np.linspace(0, L, nBins + 1)
z_centers = 0.5 * (z_edges[:-1] + z_edges[1:])

Tbulk = np.zeros(nBins)
Twall = np.zeros(nBins)

for i in range(nBins):
    zlo, zhi = z_edges[i], z_edges[i+1]

    mask_v = (z_vol >= zlo) & (z_vol < zhi)
    if mask_v.sum() > 0:
        w = Uz_vol[mask_v] * Vol_vol[mask_v]
        num = np.sum(w * T_vol[mask_v])
        den = np.sum(w)
        Tbulk[i] = num / den if den != 0 else np.nan
    else:
        Tbulk[i] = np.nan

    mask_w = (z_wall >= zlo) & (z_wall < zhi)
    if mask_w.sum() > 0:
        num = np.sum(T_wall_cells[mask_w] * Area_wall[mask_w])
        den = np.sum(Area_wall[mask_w])
        Twall[i] = num / den if den != 0 else np.nan
    else:
        Twall[i] = np.nan

Nu = q * D / (k_fluid * (Twall - Tbulk))

print(f"{'z(mm)':>8} {'T_wall(K)':>10} {'T_bulk(K)':>10} {'Nu(z)':>8}")
for zc, tw, tb, nu in zip(z_centers, Twall, Tbulk, Nu):
    print(f"{zc*1000:8.2f} {tw:10.3f} {tb:10.3f} {nu:8.3f}")

np.savetxt("NuZ_results_weighted.csv",
           np.column_stack([z_centers*1000, Twall, Tbulk, Nu]),
           delimiter=",", header="z_mm,T_wall_K,T_bulk_K,Nu", comments="")
print("\nSaved to NuZ_results_weighted.csv")
