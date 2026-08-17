import numpy as np
data = np.genfromtxt("NuZ_results_weighted.csv", delimiter=",", skip_header=1)
z_mm, Nu = data[:,0], data[:,3]
Nu_ave = np.trapz(Nu, z_mm) / (z_mm[-1] - z_mm[0])
print(f"Nu_ave = {Nu_ave:.3f}")
