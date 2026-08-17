import numpy as np
import matplotlib.pyplot as plt

# --- Load your results ---
data = np.genfromtxt("NuZ_results_weighted.csv", delimiter=",", skip_header=1)
z_mm, T_wall, T_bulk, Nu = data[:,0], data[:,1], data[:,2], data[:,3]

Nu_theoretical = 4.36   # fully-developed, uniform heat flux, circular tube

fig, ax = plt.subplots(figsize=(6, 5))

ax.plot(z_mm, Nu, '-', color='black', linewidth=1)
ax.plot(z_mm, Nu, 'o', markerfacecolor='none', markeredgecolor='blue',
        markersize=6, label='Present work')

ax.axhline(Nu_theoretical, color='red', linestyle='--', linewidth=1.2)
ax.annotate(f'$Nu_{{Fully\\ developed,\\ Theoretical}}$ = {Nu_theoretical}',
            xy=(2, Nu_theoretical), xytext=(2, Nu_theoretical - 1.0),
            fontsize=9, color='black')

ax.set_xlabel('z (mm)')
ax.set_ylabel('Nu (z)')
ax.set_xlim(0, 30)
ax.set_ylim(2, max(Nu)*1.05)
ax.grid(True, linestyle=':', linewidth=0.5)
ax.legend(loc='upper right', frameon=False)

ax.text(0.5, 0.95,
        'Local Nusselt number along the microtube\n'
        'Water, D = 500 $\\mu$m, L = 30 mm, Re = 100\n'
        'q" = 10 W/cm$^2$, T$_{in}$ = 25 $^o$C',
        transform=ax.transAxes, fontsize=8.5, va='top', ha='center',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))

plt.tight_layout()
plt.savefig("Nu_z_plot.png", dpi=300)
plt.savefig("Nu_z_plot.pdf")
print("Saved Nu_z_plot.png / .pdf")
