import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

nuclei = pd.read_csv("MyExpt_Nuclei.csv")

image = pd.read_csv("MyExpt_Image.csv")

Wells_numbers = image[["ImageNumber", "Metadata_Well"]]

nuclei = nuclei.merge(Wells_numbers, on="ImageNumber", how="left")

stat_nuclei = nuclei.groupby(
    ["Metadata_Well", "AreaShape_Area"]).agg(["mean", "std"])

mean_area = nuclei.groupby("Metadata_Well")["AreaShape_Area"].mean()
std_area = nuclei.groupby("Metadata_Well")["AreaShape_Area"].std()
fig, ax = plt.subplots(figsize=(7, 5))

ax.bar(mean_area.index, mean_area.values,
       yerr=std_area.values, capsize=5)

ax.set_title("Mean Nuclei Area per Well +/- Standard Deviation")
ax.set_xlabel("Well")
ax.set_ylabel("Mean area (pixels squared)")

plt.tight_layout()
plt.savefig("my_barchart.png", dpi=150)
