import os

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from gig import Ent, EntType
from matplotlib import rcParams
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageChops
from shapely.geometry import MultiPolygon, Polygon

rcParams["font.family"] = "Menlo"

from alt_lk import Alt, LatLng

# Scale factor: converts metres to the same unit as lat/lng degrees
# so the 3D extrusion looks proportional
ALT_SCALE = 0.000005


def _biggest_polygon(geo) -> Polygon:
    geometry = geo.geometry
    merged = (
        geometry.union_all()
        if hasattr(geometry, "union_all")
        else geometry.unary_union
    )
    if isinstance(merged, MultiPolygon):
        return max(merged.geoms, key=lambda p: p.area)
    return merged


def _polygon_to_3d_faces(poly: Polygon, z_top: float):
    """Return the top face and side walls of an extruded polygon as lists of
    vertex arrays suitable for Poly3DCollection."""
    coords = list(poly.exterior.coords)
    # top face
    top = [(x, y, z_top) for x, y in coords]
    faces = [top]
    # side walls
    for (x0, y0), (x1, y1) in zip(coords[:-1], coords[1:]):
        wall = [
            (x0, y0, 0),
            (x1, y1, 0),
            (x1, y1, z_top),
            (x0, y0, z_top),
        ]
        faces.append(wall)
    return faces


def main(parent_ent_type):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)

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
    # Rank-based coloring: assign each district a rank 0..1 by altitude
    n = len(alt_values)
    sorted_alts = sorted(set(alt_values))
    rank_map = {
        v: i / (len(sorted_alts) - 1) for i, v in enumerate(sorted_alts)
    }
    norm = lambda v: rank_map[v]  # noqa: E731
    cmap = LinearSegmentedColormap.from_list(
        "altitude_gyr", ["green", "yellow", "red"]
    )

    # With computed_zorder=False, artists render in addition order.
    # Draw shortest districts first so tall highland prisms end up on top.
    parent_ent_and_alt.sort(key=lambda x: x[1], reverse=False)

    # Pre-compute polygons and centroids
    ent_poly_data = []
    for ent, alt in parent_ent_and_alt:
        geo = ent.geo()
        color = cmap(norm(alt))
        z_top = alt * ALT_SCALE
        poly = _biggest_polygon(geo)
        ent_poly_data.append((ent, alt, poly, color, z_top))

    # Pass 1: draw all polygons
    for ent, alt, poly, color, z_top in ent_poly_data:
        faces = _polygon_to_3d_faces(poly, z_top)
        r, g, b = to_rgb(color)
        dark_edge = (r * 0.5, g * 0.5, b * 0.5)
        collection = Poly3DCollection(
            faces,
            facecolor=color,
            edgecolor=dark_edge,
            linewidth=0.3,
            alpha=0.9,
            zorder=1,
        )
        ax.add_collection3d(collection)

    # Pass 2: draw labels with high zorder — with computed_zorder=False
    # these always render on top of all Poly3DCollection geometry.
    MAX_LABELS = 30
    label_data = ent_poly_data
    if len(label_data) > MAX_LABELS:
        # Greedy farthest-point selection for geographic spread.
        # Start with the entry whose centroid is most extreme (lowest lat),
        # then repeatedly pick the candidate farthest from all already-selected
        # centroids (Euclidean in lon/lat space).
        candidates = list(label_data)
        centroids = [(item[2].centroid.x, item[2].centroid.y) for item in candidates]

        def _min_dist_to_selected(idx, selected_idxs):
            cx, cy = centroids[idx]
            return min(
                (cx - centroids[s][0]) ** 2 + (cy - centroids[s][1]) ** 2
                for s in selected_idxs
            )

        # seed: pick the item with the lowest centroid latitude
        seed = min(range(len(candidates)), key=lambda i: centroids[i][1])
        selected_idxs = [seed]
        while len(selected_idxs) < MAX_LABELS:
            next_idx = max(
                (i for i in range(len(candidates)) if i not in selected_idxs),
                key=lambda i: _min_dist_to_selected(i, selected_idxs),
            )
            selected_idxs.append(next_idx)
        label_data = [candidates[i] for i in selected_idxs]
    for ent, alt, poly, color, z_top in label_data:
        centroid = poly.centroid
        ax.text(
            centroid.x,
            centroid.y,
            z_top,
            f"{ent.name}\n{alt:,.0f} m",
            ha="center",
            va="bottom",
            fontsize=5,
            color="white",
            zorder=10,
            path_effects=[pe.withStroke(linewidth=1.5, foreground="black")],
        )

    # fit axes to data
    all_coords = np.array(
        [
            (float(e.center_lon), float(e.center_lat))
            for e, _ in parent_ent_and_alt
        ]
    )
    ax.set_xlim(all_coords[:, 0].min() - 0.2, all_coords[:, 0].max() + 0.2)
    ax.set_ylim(all_coords[:, 1].min() - 0.2, all_coords[:, 1].max() + 0.2)
    ax.set_zlim(0, max(alt_values) * ALT_SCALE * 1.1)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_zlabel("")
    ax.view_init(elev=40, azim=-80)
    ax.set_box_aspect([1, 2, 0.06])
    ax.dist = (
        6  # default is 10; lower = less internal padding around the scene
    )
    ax.set_position([-0.2, -0.05, 1.4, 1.05])

    # remove outer box, panes and grid
    ax.set_axis_off()
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor("none")
    ax.grid(False)

    image_path = os.path.join(
        "examples",
        f"average_altitude_{parent_ent_type.name}_{child_ent_type.name}.png",
    )
    fig.subplots_adjust(top=1.0, bottom=0.0)
    plt.savefig(image_path, dpi=300)
    plt.close(fig)

    # Crop whitespace that the 3D renderer adds internally
    img = Image.open(image_path).convert("RGB")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        margin = 80
        w, h = img.size
        bbox = (
            max(0, bbox[0] - margin),
            max(0, bbox[1] - margin),
            min(w, bbox[2] + margin),
            min(h, bbox[3] + margin),
        )
        img = img.crop(bbox)

    # Add title and footer as PIL text so they don't affect 3D layout
    from PIL import ImageDraw, ImageFont

    title = (
        f"{parent_ent_type.name.capitalize()}s of Sri Lanka"
        " – Average Elevation"
    )
    footer = "Data: USGS 1 arc-second DEM · github.com/nuuuwan/alt_lk"

    padding = 64
    h_padding = 60
    line_h = 30
    new_img = Image.new(
        "RGB",
        (img.width + h_padding * 2, img.height + padding * 2),
        (255, 255, 255),
    )
    new_img.paste(img, (h_padding, padding))

    draw = ImageDraw.Draw(new_img)
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 32)
        font_footer = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22)
    except Exception:
        font_title = ImageFont.load_default()
        font_footer = font_title

    # Title centred at top
    tw = draw.textlength(title, font=font_title)
    draw.text(
        ((new_img.width - tw) / 2, (padding - line_h) // 2),
        title,
        font=font_title,
        fill=(40, 40, 40),
    )
    # Footer centred at bottom
    fw = draw.textlength(footer, font=font_footer)
    draw.text(
        (
            (new_img.width - fw) / 2,
            img.height + padding + (padding - line_h) // 2,
        ),
        footer,
        font=font_footer,
        fill=(130, 130, 130),
    )

    new_img.save(image_path)
    print(f'Wrote "{image_path}"')


if __name__ == "__main__":
    for parent_ent_type in [EntType.PROVINCE, EntType.DISTRICT, EntType.DSD]:
        main(parent_ent_type)
