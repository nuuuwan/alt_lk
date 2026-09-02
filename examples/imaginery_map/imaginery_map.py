from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from matplotlib.colors import to_rgba
from matplotlib.patheffects import withStroke

from alt_lk import Alt, LatLng

MAP_BOUNDS = (79.35, 82.05, 5.75, 9.95)
MAX_IMAGE_DIMENSION = 2_400
OFFSETS_M = (500, 1_000, 1_500, 2_000)
BOUNDING_BOX_PADDING = 0.03
SEA_COLOR = "#AAD3DF"
LAND_COLOR = "#C8E6C9"
MOUNTAIN_SOURCE_URL = (
    "https://en.wikipedia.org/wiki/List_of_mountains_of_Sri_Lanka"
)

MOUNTAINS_OVER_2000_M = (
    ("Pidurutalagala", 2524, 7.000833, 80.773889),
    ("Kirigalpotta", 2395, 6.799167, 80.766667),
    ("Top Pass Hill", 2383, 7.007500, 80.758333),
    ("Thotupola Kanda", 2359, 6.833056, 80.819722),
    ("Ramboda Hill", 2322, 7.016111, 80.753333),
    ("Agrabopath", 2318, 6.813056, 80.783056),
    ("Leopards Rock", 2284, 6.991389, 80.761389),
    ("Adam's Peak", 2243, 6.809444, 80.499722),
    ("Kikilimana", 2240, 6.985000, 80.746667),
    ("Court's Lodge Point", 2235, 6.986111, 80.793611),
    ("Great Western Mountain", 2216, 6.966667, 80.693889),
    ("Pattipola Mountain", 2208, 6.851944, 80.801667),
    ("World's End Rock", 2202, 6.774167, 80.782222),
    ("Mount Oliphant", 2190, 6.973889, 80.735278),
    ("Hakgala", 2172, 6.918056, 80.811944),
    ("Conical Hill", 2168, 6.912500, 80.775833),
    ("Kabaragala Summit", 2162, 7.027444, 80.738444),
    ("Park Green Mountain", 2149, 7.013611, 80.815833),
    ("Uda Radella", 2143, 6.962500, 80.725556),
    ("Haddon Hill", 2131, 6.967222, 80.753611),
    ("Perettasi Mountain", 2129, 7.076111, 80.733333),
    ("North Cove Mountain", 2119, 6.792028, 80.746583),
    ("New Zealand Farm Mountain", 2108, 6.858889, 80.793333),
    ("One Tree Hill", 2100, 6.957500, 80.762500),
    ("Mahakudagala", 2100, 7.043056, 80.844444),
    ("Kandapola Kanda", 2088, 6.978889, 80.825000),
    ("Frotoft Hill", 2082, 7.090750, 80.723972),
    ("Udaweriya", 2079, 6.794444, 80.865278),
    ("Waterfall Point", 2076, 6.927778, 80.764444),
    ("Robgill Hill", 2072, 6.830833, 80.685000),
    ("Mahamuni Kanda", 2069, 6.763333, 80.587222),
    ("North Bogawanthalawa Peak", 2055, 6.769167, 80.658889),
    ("Deegalhinna", 2045, 7.047222, 80.744028),
    ("Kuraatte Kanda", 2039, 6.985556, 80.849444),
    ("Namunukula", 2036, 6.933056, 81.113611),
    ("Gommoliya", 2034, 6.766667, 80.809167),
    ("Meeriyathenna", 2034, 6.788333, 80.863333),
    ("Elbedda", 2016, 6.847222, 80.664722),
    ("Balathuduwa", 2012, 6.761389, 80.812500),
    ("Bena Samanalagala", 2010, 6.798333, 80.488333),
)


def _load_map_data(offset_m: int) -> np.ma.MaskedArray:
    min_lng, max_lng, min_lat, max_lat = MAP_BOUNDS
    i_north, i_west = Alt.latlng_to_indices(LatLng(max_lat, min_lng))
    i_south, i_east = Alt.latlng_to_indices(LatLng(min_lat, max_lng))

    matrix = np.asarray(Alt.matrix())
    region = matrix[i_north:i_south, i_west:i_east]
    sample_step = max(1, int(np.ceil(max(region.shape) / MAX_IMAGE_DIMENSION)))
    adjusted = region[::sample_step, ::sample_step] - offset_m
    return np.ma.masked_less_equal(adjusted, 0)


def _crop_to_land(
    elevation: np.ma.MaskedArray,
) -> tuple[np.ndarray, tuple[int, int]]:
    land_mask = ~np.ma.getmaskarray(elevation)
    rows, columns = np.where(land_mask)
    if rows.size == 0:
        raise ValueError("The offset leaves no elevation above sea level")

    row_padding = max(
        1, int(np.ceil((rows.max() - rows.min() + 1) * BOUNDING_BOX_PADDING))
    )
    column_padding = max(
        1,
        int(
            np.ceil((columns.max() - columns.min() + 1) * BOUNDING_BOX_PADDING)
        ),
    )
    first_row = max(0, rows.min() - row_padding)
    last_row = min(land_mask.shape[0], rows.max() + row_padding + 1)
    first_column = max(0, columns.min() - column_padding)
    last_column = min(land_mask.shape[1], columns.max() + column_padding + 1)

    cropped = land_mask[first_row:last_row, first_column:last_column]
    return cropped, (first_row, first_column)


def _annotate_mountains(
    ax,
    source_shape: tuple[int, int],
    crop_origin: tuple[int, int],
) -> None:
    source_height, source_width = source_shape
    first_row, first_column = crop_origin
    min_lng, max_lng, min_lat, max_lat = MAP_BOUNDS
    texts = []
    marker_x = []
    marker_y = []

    for rank, (name, elevation_m, lat, lng) in enumerate(
        MOUNTAINS_OVER_2000_M, start=1
    ):
        x = (lng - min_lng) / (max_lng - min_lng) * source_width - first_column
        y = (max_lat - lat) / (max_lat - min_lat) * source_height - first_row
        marker_x.append(x)
        marker_y.append(y)
        texts.append(
            ax.text(
                x,
                y,
                f"#{rank} {name}\n{elevation_m} m",
                color="#263F37",
                fontsize=5,
                ha="center",
                va="center",
                path_effects=[withStroke(linewidth=1.5, foreground="white")],
            )
        )

    ax.scatter(
        marker_x,
        marker_y,
        s=8,
        color="#315B45",
        edgecolors="white",
        linewidths=0.4,
        zorder=3,
    )
    adjust_text(
        texts,
        x=marker_x,
        y=marker_y,
        ax=ax,
        ensure_inside_axes=True,
        expand=(1.08, 1.15),
        force_text=(0.7, 0.9),
        force_points=(0.4, 0.6),
        arrowprops={"arrowstyle": "-", "color": "#607D72", "lw": 0.35},
    )


def main(offset_m: int, labelled: bool = False) -> None:
    label_suffix = ".labelled" if labelled else ""
    output_path = Path(__file__).with_name(
        f"imaginery_map_{offset_m}m{label_suffix}.png"
    )
    elevation = _load_map_data(offset_m)
    land_mask, crop_origin = _crop_to_land(elevation)

    map_image = np.empty((*land_mask.shape, 4))
    map_image[:] = to_rgba(SEA_COLOR)
    map_image[land_mask] = to_rgba(LAND_COLOR)

    fig, ax = plt.subplots(figsize=(10, 10), facecolor=SEA_COLOR)
    ax.set_facecolor(SEA_COLOR)
    ax.imshow(
        map_image,
        origin="upper",
        interpolation="nearest",
        aspect="auto",
    )
    if labelled:
        _annotate_mountains(ax, elevation.shape, crop_origin)

    ax.axis("off")

    if labelled:
        ax.set_position((0, 0.025, 1, 0.975))
        fig.text(
            0.5,
            0.008,
            f"Source: {MOUNTAIN_SOURCE_URL}",
            color="#263F37",
            fontsize=4.5,
            ha="center",
            va="bottom",
        )
    else:
        ax.set_position((0, 0, 1, 1))
    fig.savefig(output_path, dpi=220, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    for offset_m in OFFSETS_M:
        main(offset_m)
    main(2_000, labelled=True)
