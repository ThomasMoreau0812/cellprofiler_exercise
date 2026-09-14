"""
CellProfiler Data Visualisation Script
=======================================
This script loads the CellProfiler output CSVs and produces several plots:
  1. Bar chart  – mean cell count per well
  2. Bar chart  – mean nuclei area per well (with error bars)
  3. Violin plot – nuclei area distribution per well
  4. Box plot    – nuclei DNA mean intensity per well
  5. Histogram   – distribution of cell areas
  6. Scatter plot – nuclei area vs. DNA mean intensity

All plots are saved as PNG files in the same folder as this script.

HOW TO RUN:
  Open a terminal / command prompt in this folder and type:
      python make_plots.py

REQUIREMENTS (already installed):
  pip install pandas matplotlib seaborn numpy
"""

# ── 1. Import the libraries we need ──────────────────────────────────────────
import pandas as pd          # for reading and working with tables (DataFrames)
import matplotlib.pyplot as plt  # the core plotting library
import seaborn as sns        # makes prettier plots on top of matplotlib
import numpy as np           # for maths/numbers
import os                    # for file paths

# ── 2. Settings ───────────────────────────────────────────────────────────────
# The folder where the CSV files live (same folder as this script)
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# Output folder for the plots (same folder, subfolder "plots")
PLOT_DIR = os.path.join(DATA_DIR, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)   # create the folder if it doesn't exist

# Set a consistent visual style for all plots
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.2)

print("Loading data ...")

# ── 3. Load the CSV files ─────────────────────────────────────────────────────
# Image-level table: one row per image (site). Contains per-image metadata
# like the well name and how many cells were detected.
img = pd.read_csv(os.path.join(DATA_DIR, "MyExpt_Image.csv"))

# Nuclei table: one row per detected nucleus. Contains shape and intensity
# measurements for every nucleus in every image.
nuc = pd.read_csv(os.path.join(DATA_DIR, "MyExpt_Nuclei.csv"))

# Cells table: one row per detected cell.
cells = pd.read_csv(os.path.join(DATA_DIR, "MyExpt_Cells.csv"))

print(f"  Image table:  {img.shape[0]} rows (images)")
print(f"  Nuclei table: {nuc.shape[0]} rows (nuclei)")
print(f"  Cells table:  {cells.shape[0]} rows (cells)")

# ── 4. Attach well labels to the per-object tables ────────────────────────────
# The nuclei/cells tables only contain an ImageNumber column.
# We merge with the image table to get the Well name for each nucleus/cell.
# Think of a merge like a VLOOKUP in Excel.

# Build a small lookup table: ImageNumber -> Well
well_lookup = img[["ImageNumber", "Metadata_Well"]].copy()
well_lookup.columns = ["ImageNumber", "Well"]

# Merge nuclei with well info
nuc = nuc.merge(well_lookup, on="ImageNumber", how="left")

# Merge cells with well info
cells = cells.merge(well_lookup, on="ImageNumber", how="left")

# Rename to shorter names for convenience
img = img.rename(columns={"Metadata_Well": "Well"})

print("\nData loaded and merged successfully!\n")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 1 – Bar chart: Mean cell count per well
# ─────────────────────────────────────────────────────────────────────────────
print("Making Plot 1: Bar chart – cell count per well ...")

# img already has one row per image; Count_Cells tells us how many cells
# were found in that image. We take the mean across sites for each well.
cell_counts = img.groupby("Well")["Count_Cells"].mean().reset_index()
# reset_index() turns the grouped result back into a normal DataFrame

fig, ax = plt.subplots(figsize=(7, 5))  # create a figure and axes

bars = ax.bar(
    cell_counts["Well"],          # x-axis: well names
    cell_counts["Count_Cells"],   # y-axis: mean cell count
    color=sns.color_palette("muted", len(cell_counts)),
    edgecolor="black",
    width=0.6,
)

# Add the exact number on top of each bar so it's easy to read
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,  # x position: centre of bar
        height + 1,                          # y position: just above bar
        f"{height:.1f}",                     # formatted number
        ha="center", va="bottom", fontsize=11
    )

ax.set_title("Mean Cell Count per Well", fontweight="bold")
ax.set_xlabel("Well")
ax.set_ylabel("Mean number of cells per image")
ax.set_ylim(0, cell_counts["Count_Cells"].max() * 1.2)  # a bit of headroom

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "01_barchart_cell_count.png"), dpi=150)
plt.close()
print("  Saved -> plots/01_barchart_cell_count.png")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 2 – Bar chart with error bars: Mean nuclei area per well
# ─────────────────────────────────────────────────────────────────────────────
print("Making Plot 2: Bar chart with error bars – nuclei area per well ...")

# Compute the mean AND standard deviation of AreaShape_Area grouped by well
nuc_area = nuc.groupby("Well")["AreaShape_Area"].agg(
    ["mean", "std"]).reset_index()

fig, ax = plt.subplots(figsize=(7, 5))

bars = ax.bar(
    nuc_area["Well"],
    nuc_area["mean"],
    yerr=nuc_area["std"],       # error bars = standard deviation
    capsize=5,                  # small horizontal cap on the error bars
    color=sns.color_palette("pastel", len(nuc_area)),
    edgecolor="black",
    width=0.6,
)

ax.set_title("Mean Nuclei Area per Well\n(error bars = std dev)",
             fontweight="bold")
ax.set_xlabel("Well")
ax.set_ylabel("Nuclei area (pixels²)")

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "02_barchart_nuclei_area.png"), dpi=150)
plt.close()
print("  Saved -> plots/02_barchart_nuclei_area.png")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 3 – Violin plot: Nuclei area distribution per well
# ─────────────────────────────────────────────────────────────────────────────
print("Making Plot 3: Violin plot – nuclei area per well ...")

fig, ax = plt.subplots(figsize=(8, 5))

sns.violinplot(
    data=nuc,
    x="Well",
    y="AreaShape_Area",
    hue="Well",    # required by seaborn 0.13+ to use palette
    palette="muted",
    legend=False,  # hide the legend since x-axis already shows wells
    inner="box",   # show a tiny box plot inside the violin
    ax=ax,
)

ax.set_title("Distribution of Nuclei Area per Well", fontweight="bold")
ax.set_xlabel("Well")
ax.set_ylabel("Nuclei area (pixels²)")

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "03_violin_nuclei_area.png"), dpi=150)
plt.close()
print("  Saved -> plots/03_violin_nuclei_area.png")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 4 – Box plot: DNA mean intensity per well
# ─────────────────────────────────────────────────────────────────────────────
print("Making Plot 4: Box plot – nuclei DNA intensity per well ...")

fig, ax = plt.subplots(figsize=(8, 5))

sns.boxplot(
    data=nuc,
    x="Well",
    y="Intensity_MeanIntensity_OrigDNA",  # mean DNA channel intensity
    hue="Well",
    palette="Set2",
    legend=False,
    ax=ax,
)

# Overlay the individual data points so we can see the raw data
sns.stripplot(
    data=nuc,
    x="Well",
    y="Intensity_MeanIntensity_OrigDNA",
    color="black",
    alpha=0.2,       # transparency so overlapping points are visible
    size=2,
    ax=ax,
)

ax.set_title("DNA Mean Intensity per Well\n(Nuclei)", fontweight="bold")
ax.set_xlabel("Well")
ax.set_ylabel("Mean intensity – DNA channel")

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "04_boxplot_dna_intensity.png"), dpi=150)
plt.close()
print("  Saved -> plots/04_boxplot_dna_intensity.png")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 5 – Histogram: Distribution of cell areas across all wells
# ─────────────────────────────────────────────────────────────────────────────
print("Making Plot 5: Histogram – cell area distribution ...")

fig, ax = plt.subplots(figsize=(8, 5))

# Plot one histogram per well, all overlapping with some transparency
wells = sorted(cells["Well"].unique())
colors = sns.color_palette("tab10", len(wells))

for well, color in zip(wells, colors):
    subset = cells[cells["Well"] == well]["AreaShape_Area"]
    ax.hist(
        subset,
        bins=50,         # number of bins (bars in the histogram)
        alpha=0.5,       # 50 % transparent so overlapping histograms are visible
        label=well,
        color=color,
        edgecolor="none",
    )

ax.set_title("Distribution of Cell Areas by Well", fontweight="bold")
ax.set_xlabel("Cell area (pixels²)")
ax.set_ylabel("Number of cells")
ax.legend(title="Well")

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "05_histogram_cell_area.png"), dpi=150)
plt.close()
print("  Saved -> plots/05_histogram_cell_area.png")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 6 – Scatter plot: Nuclei area vs. DNA mean intensity
# ─────────────────────────────────────────────────────────────────────────────
print("Making Plot 6: Scatter plot – nuclei area vs DNA intensity ...")

# To keep the plot readable, we sample at most 2000 nuclei
sample = nuc.sample(n=min(2000, len(nuc)), random_state=42)

fig, ax = plt.subplots(figsize=(8, 6))

sns.scatterplot(
    data=sample,
    x="AreaShape_Area",
    y="Intensity_MeanIntensity_OrigDNA",
    hue="Well",        # colour each point by well
    alpha=0.6,
    s=20,              # point size
    palette="tab10",
    ax=ax,
)

ax.set_title(
    "Nuclei Area vs. DNA Mean Intensity\n(random sample of 2 000 nuclei)", fontweight="bold")
ax.set_xlabel("Nuclei area (pixels²)")
ax.set_ylabel("DNA mean intensity")
ax.legend(title="Well", bbox_to_anchor=(1.02, 1), loc="upper left")

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "06_scatter_area_vs_dna.png"),
            dpi=150, bbox_inches="tight")
plt.close()
print("  Saved -> plots/06_scatter_area_vs_dna.png")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 7 – Violin + strip: Cell eccentricity per well (bonus!)
# ─────────────────────────────────────────────────────────────────────────────
print("Making Plot 7: Violin – cell eccentricity per well ...")

# Eccentricity = how elongated a shape is (0 = perfect circle, 1 = very elongated)
fig, ax = plt.subplots(figsize=(8, 5))

sns.violinplot(
    data=cells,
    x="Well",
    y="AreaShape_Eccentricity",
    palette="pastel",
    inner=None,   # don't draw the inner box so strips are more visible
    ax=ax,
)
sns.stripplot(
    data=cells,
    x="Well",
    y="AreaShape_Eccentricity",
    color="black",
    alpha=0.15,
    size=2,
    ax=ax,
)

ax.set_title(
    "Cell Shape Eccentricity per Well\n(0 = circle, 1 = very elongated)", fontweight="bold")
ax.set_xlabel("Well")
ax.set_ylabel("Eccentricity")

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, "07_violin_cell_eccentricity.png"), dpi=150)
plt.close()
print("  Saved -> plots/07_violin_cell_eccentricity.png")

# ─────────────────────────────────────────────────────────────────────────────
print("\n[OK]  All done!  Open the 'plots' folder to see your figures.")
print(f"   Folder: {PLOT_DIR}")
