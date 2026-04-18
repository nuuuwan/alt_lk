import os

import matplotlib.pyplot as plt
from gig import Ent, EntType
from matplotlib import rcParams
from matplotlib.colors import LinearSegmentedColormap, Normalize

rcParams["font.family"] = "Menlo"

from alt_lk import Alt, LatLng


def main():
    fig, ax = plt.subplots(figsize=(8, 8))
    parent_ent_type = EntType.DISTRICT
    child_ent_type = EntType.GND

    parent_ents = Ent.list_from_type(parent_ent_type)
    child_ents = Ent.list_from_type(child_ent_type)
    parent_ent_and_alt = []
    for parent_ent in parent_ents:
        child_ents_for_parent = [
            ent for ent in child_ents if parent_ent.id in ent.id
        ]
        assert (
            len(child_ents_for_parent) > 0
        ), f"No child ents found for {parent_ent.name}"

        weighted_alt_sum = 0
        area_sum = 0
        for child_ent in child_ents_for_parent:
            latlng = LatLng(
                float(child_ent.center_lat), float(child_ent.center_lon)
            )
            alt = Alt.from_latlng(latlng)
            area = child_ent.area_sqkm
            weighted_alt_sum += alt.alt_m * area
            area_sum += area

        alt_avg = weighted_alt_sum / area_sum
        parent_ent_and_alt.append((parent_ent, alt_avg))

    alt_values = [alt for _, alt in parent_ent_and_alt]
    norm = Normalize(vmin=min(alt_values), vmax=max(alt_values))
    cmap = LinearSegmentedColormap.from_list(
        "altitude_gor", ["green", "orange", "red"]
    )

    for ent, alt in parent_ent_and_alt:
        geo = ent.geo()
        geo.plot(
            ax=ax,
            facecolor=cmap(norm(alt)),
            edgecolor="black",
        )

        label_x = float(ent.center_lon)
        label_y = float(ent.center_lat)
        try:
            from shapely.geometry import MultiPolygon, Polygon

            geometry = geo.geometry
            merged = (
                geometry.union_all()
                if hasattr(geometry, "union_all")
                else geometry.unary_union
            )
            if isinstance(merged, MultiPolygon):
                biggest = max(merged.geoms, key=lambda p: p.area)
            elif isinstance(merged, Polygon):
                biggest = merged
            else:
                biggest = merged
            centroid = biggest.centroid
            label_x, label_y = centroid.x, centroid.y
        except Exception:
            pass

        ax.text(
            label_x,
            label_y,
            f"{ent.name}\n{alt:,.0f} m",
            ha="center",
            va="center",
            fontsize=6,
            color="black",
            zorder=5,
            bbox={
                "boxstyle": "round,pad=0.3",
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.7,
            },
        )

    ax.set_title(
        f"{parent_ent_type.name.capitalize()}s of Sri Lanka by Average Elevation"
    )
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.text(
        0.5,
        0.01,
        "Data: USGS 1 arc-second DEM · github.com/nuuuwan/alt_lk",
        ha="center",
        va="bottom",
        fontsize=7,
        color="grey",
    )

    image_path = os.path.join(
        "examples",
        f"average_altitude_{parent_ent_type.name}_{child_ent_type.name}.png",
    )
    fig.subplots_adjust(bottom=0.03)
    plt.savefig(image_path, dpi=300)
    plt.close(fig)
    print(f'Wrote "{image_path}"')


if __name__ == "__main__":
    main()
