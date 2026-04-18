import os

import matplotlib.pyplot as plt
from gig import Ent, EntType
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap, Normalize

from alt_lk import Alt, LatLng


def main():
    fig, ax = plt.subplots(figsize=(8, 8))
    ent_type = EntType.PROVINCE

    ents = Ent.list_from_type(ent_type)
    ent_alt_data = []
    for ent in ents:
        latlng = LatLng(float(ent.center_lat), float(ent.center_lon))
        alt = Alt.from_latlng(latlng)
        ent_alt_data.append((ent, alt))

    alt_values = [alt.alt_m for _, alt in ent_alt_data]
    norm = Normalize(vmin=min(alt_values), vmax=max(alt_values))
    cmap = LinearSegmentedColormap.from_list(
        "altitude_gor", ["green", "orange", "red"]
    )

    for ent, alt in ent_alt_data:
        print(ent.name, alt)
        geo = ent.geo()
        geo.plot(ax=ax, color=cmap(norm(alt.alt_m)), edgecolor="black")
        ax.text(
            float(ent.center_lon),
            float(ent.center_lat),
            f"{ent.name}\n{alt.alt_m:,.0f} m",
            ha="center",
            va="center",
            fontsize=8,
            color="black",
            bbox={
                "boxstyle": "round,pad=0.25",
                "facecolor": "white",
                "edgecolor": "black",
                "alpha": 0.8,
            },
            zorder=5,
        )

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("Altitude (m)")

    ax.set_title("Provinces Colored by Altitude")
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")

    image_path = os.path.join(
        "examples", f"average_altitude_{ent_type.name}.png"
    )
    plt.tight_layout()
    plt.savefig(image_path, dpi=300)
    plt.close(fig)
    print(f'Wrote "{image_path}"')


if __name__ == "__main__":
    main()
