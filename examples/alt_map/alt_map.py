from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LightSource, LinearSegmentedColormap, Normalize

from alt_lk import Alt, LatLng

OUTPUT_PATH = Path(__file__).with_name("alt_map.png")
MAP_BOUNDS = (79.35, 82.05, 5.75, 9.95)
MAX_IMAGE_DIMENSION = 2_400

TERRAIN_CMAP = LinearSegmentedColormap.from_list(
    "sri_lanka_terrain",
    [
        (0.00, "#1f6b45"),
        (0.08, "#55a64a"),
        (0.22, "#a9c95c"),
        (0.42, "#d8c87a"),
        (0.65, "#a77b52"),
        (0.84, "#75554a"),
        (1.00, "#f0eee7"),
    ],
)


def _load_map_data() -> np.ma.MaskedArray:
    min_lng, max_lng, min_lat, max_lat = MAP_BOUNDS
    north_west = Alt.latlng_to_indices(LatLng(max_lat, min_lng))
    south_east = Alt.latlng_to_indices(LatLng(min_lat, max_lng))
    i_north, i_west = north_west
    i_south, i_east = south_east

    matrix = np.asarray(Alt.matrix())
    region = matrix[i_north:i_south, i_west:i_east]
    sample_step = max(1, int(np.ceil(max(region.shape) / MAX_IMAGE_DIMENSION)))
    sampled = region[::sample_step, ::sample_step]
    return np.ma.masked_less_equal(sampled, 0)


def main() -> None:
    elevation = _load_map_data()
    norm = Normalize(vmin=0, vmax=2_500)

    light_source = LightSource(azdeg=315, altdeg=42)
    color = TERRAIN_CMAP(norm(elevation.filled(0)))
    shaded = light_source.shade_rgb(
        color,
        elevation.filled(0),
        blend_mode="soft",
        vert_exag=0.45,
    )
    shaded[..., 3] = (~elevation.mask).astype(float)

    fig, ax = plt.subplots(figsize=(8, 11), facecolor="#dcebf0")
    ax.set_facecolor("#dcebf0")
    ax.imshow(
        shaded,
        extent=MAP_BOUNDS,
        origin="upper",
        interpolation="bilinear",
    )

    fig.text(
        0.08,
        0.965,
        "SRI LANKA ELEVATION",
        color="#17352d",
        fontsize=24,
        fontweight="bold",
        va="top",
    )
    fig.text(
        0.08,
        0.932,
        "USGS 1 arc-second digital elevation model",
        color="#48645d",
        fontsize=9,
        va="top",
    )

    colorbar = fig.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=TERRAIN_CMAP),
        ax=ax,
        orientation="horizontal",
        fraction=0.035,
        pad=0.035,
        aspect=35,
    )
    colorbar.set_label("ELEVATION (METRES)", color="#294840", fontsize=9)
    colorbar.set_ticks([0, 500, 1_000, 1_500, 2_000, 2_500])
    colorbar.outline.set_visible(False)
    colorbar.ax.tick_params(colors="#294840", labelsize=8, length=0)

    ax.set_xlim(MAP_BOUNDS[:2])
    ax.set_ylim(MAP_BOUNDS[2:])
    ax.set_aspect(1 / np.cos(np.deg2rad(7.8)))
    ax.axis("off")

    fig.subplots_adjust(left=0.04, right=0.96, top=0.89, bottom=0.08)
    fig.savefig(OUTPUT_PATH, dpi=220, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
