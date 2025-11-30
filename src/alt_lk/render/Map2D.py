import contextily as ctx
import matplotlib.pyplot as plt
import numpy as np
import pyproj
from utils import Log

from alt_lk.alt.Alt import Alt
from alt_lk.render.AbstractPlot import AbstractPlot

log = Log("Map2D")

# transformer to EPSG:3857
proj = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)


class Map2D(AbstractPlot):
    @property
    def cmap(self):
        return "hsv"

    def build_plot(self):
        log.debug("build_plot")
        alt = self.alt or Alt.get_matrix_subset(self.bbox)

        lat_idx, lng_idx = np.mgrid[: alt.shape[0], : alt.shape[1]]
        dim_lat, dim_lng = alt.shape

        lat = -lat_idx / dim_lat * self.bbox.lat_span + self.bbox.max_lat
        lng = lng_idx / dim_lng * self.bbox.lng_span + self.bbox.min_lng

        # flatten
        lat_f = lat.ravel()
        lng_f = lng.ravel()
        alt_f = alt.ravel()

        # convert to web mercator
        x, y = proj.transform(lng_f, lat_f)

        fig, ax = plt.subplots(figsize=(8, 8))

        # underlying OSM map
        # bounds required: minx, miny, maxx, maxy in EPSG:3857
        xmin, ymin = proj.transform(self.bbox.min_lng, self.bbox.min_lat)
        xmax, ymax = proj.transform(self.bbox.max_lng, self.bbox.max_lat)
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

        # altitude overlay with transparency
        sc = ax.scatter(
            x,
            y,
            c=alt_f,
            s=1,
            cmap=self.cmap,
            marker="s",
            alpha=0.05,    # transparency
            vmin=0,
            vmax=50,
        )

        log.debug("build_plot done!")