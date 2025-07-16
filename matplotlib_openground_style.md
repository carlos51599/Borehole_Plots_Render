
# Making Your Matplotlib Borehole Section Look Like Openground

## 1. Hatch Patterns for Geological Units

Define hatch patterns per lithology for both plot and legend:

```python
hatch_map = {
    "CLAY": "...",      # dots
    "SAND": "///",      # diagonal lines
    "GRAVEL": "\\",   # cross lines
    "LIMESTONE": "xx",  # cross marks
    "TOPSOIL": "ooo"    # circles
}
```

Apply them in your plotting loop:

```python
ax.fill_betweenx(
    [row["ELEV_TOP"], row["ELEV_BASE"]],
    bh_x - width / 2, bh_x + width / 2,
    facecolor=color,
    hatch=pattern,
    edgecolor="black",
    linewidth=0.5
)
```
Adjust density by repeating hatch chars. You can set global hatch line width and color:

```python
import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 1.0
mpl.rcParams['hatch.color'] = 'black'
```

## 2. Consistent Fonts

Set font globally at the start of your script:

```python
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
mpl.rcParams['axes.labelsize'] = 11
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['legend.fontsize'] = 10
```

## 3. Vertical Exaggeration

Adjust the aspect ratio for vertical exaggeration:

```python
ax.set_aspect(5.0)  # 5× vertical exaggeration
```

Or, tweak your figure height:

```python
fig, ax = plt.subplots(figsize=(width_inches, height_inches * exaggeration_factor))
```

## 4. Ground Surface Line

Plot a polyline through borehole tops:

```python
ax.plot(x_vals, surface_elev, color="k", linestyle="-", linewidth=1.5, zorder=10)
```

## 5. Gridlines and Ticks

Add major/minor gridlines and control tick spacing:

```python
import matplotlib.ticker as ticker

ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
ax.grid(which='major', axis='both', linestyle='--', color='gray', linewidth=0.8)
ax.grid(which='minor', axis='both', linestyle=':', color='gray', linewidth=0.5)
```

## 6. Legend with Color and Hatch

Show both color and hatch using patches:

```python
from matplotlib.patches import Patch

legend_patches = []
for leg in unique_leg:
    label = leg_label_map[leg]
    patch = Patch(
        facecolor=color_map[leg],
        edgecolor='black',
        hatch=hatch_map.get(leg, ""),
        label=label
    )
    legend_patches.append(patch)

ax.legend(handles=legend_patches, title="Geology", bbox_to_anchor=(1.02, 1), loc="upper left")
```

## 7. Borehole Labels

Label each borehole at the bottom (or top) with optional offset:

```python
for bh in boreholes:
    x = bh_x_map[bh]
    offset = borehole_offset_map.get(bh, 0.0)
    label = f"{bh}\n({offset:+.2f} m)"
    ax.annotate(label, xy=(x, ax.get_ylim()[0]), xycoords='data',
                xytext=(0, -15), textcoords='offset points',
                ha='center', va='top', fontsize=10)
```

## 8. High-Resolution Output

Save as PDF (best for print):

```python
plt.tight_layout()
plt.savefig("section_plot.pdf")
```

Or as a high-DPI PNG:

```python
plt.tight_layout()
plt.savefig("section_plot.png", dpi=300)
```

## 9. Example Reference Links

- [Matplotlib Hatch Demo](https://matplotlib.org/stable/gallery/shapes_and_collections/hatch_style_reference.html)
- [Andy McDonald: Lithology Log Plotting with Python](https://andymcdonaldgeo.medium.com/displaying-lithology-data-on-a-well-log-plot-using-python-41e1a26b17a7)
- [FloPy Cross-section Example](https://github.com/modflowpy/flopy/blob/develop/examples/Notebooks/flopy3_cross_section.ipynb)

---

**Summary:**  
Combine hatch fills, strong gridlines, consistent sans-serif fonts, a polyline for ground surface, and a legend with color+hatch swatches. Use vertical exaggeration and save to vector PDF for professional results. Fine-tune tick spacing and label placement to match the Openground section style.

---
