import os

from alt_lk import BBox, LatLng
from alt_lk.render import Map2D


def main():    
    dir_group = os.path.join('examples', 'images', 'example6_kelani')
    os.makedirs(dir_group, exist_ok=True)
    image_path = os.path.join(dir_group, f'kelani.png')
    bbox = BBox.from_point(LatLng(6.95, 79.92))
    Map2D(bbox).write(None, image_path, force=True)


if __name__ == '__main__':
    main()
