import os

from alt_lk import BBox, LatLng
from alt_lk.render import Map2D

LATLNG_NAGALAGAM_STREET = LatLng(6.958290212813488, 79.87920362657638)
LATLNG_AMBATHALE = LatLng(6.938450319627125, 79.94377775139459)


def main():
    dir_group = os.path.join("examples", "images", "example6_kelani")
    os.makedirs(dir_group, exist_ok=True)

    for i_image, latlng in enumerate(
        [LATLNG_NAGALAGAM_STREET, LATLNG_AMBATHALE]
    ):
        image_path = os.path.join(dir_group, f"kelani-{i_image}.png")
        bbox = BBox.from_point(latlng, span=0.03)
        Map2D(bbox).write(None, image_path, force=True)


if __name__ == "__main__":
    main()
