import contextily as cx
import matplotlib.pyplot as plt
import numpy as np
import pyproj
from matplotlib.colors import BoundaryNorm, ListedColormap
from utils import Log

from alt_lk.alt.Alt import Alt
from alt_lk.render.AbstractPlot import AbstractPlot

log = Log("Map2D")

# transformer to EPSG:3857
proj = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)


class Map2D(AbstractPlot):


    def build_plot(self):
        log.debug("build_plot")
        alt = self.alt or Alt.get_matrix_subset(self.bbox)

        lat_idx, lng_idx = np.mgrid[: alt.shape[0], : alt.shape[1]]
        dim_lat, dim_lng = alt.shape

        lat = -lat_idx / dim_lat * self.bbox.lat_span + self.bbox.max_lat
        lng = lng_idx / dim_lng * self.bbox.lng_span + self.bbox.min_lng

        lat_f = lat.ravel()
        lng_f = lng.ravel()
        alt_f = alt.ravel()

        x, y = proj.transform(lng_f, lat_f)

        fig, ax = plt.subplots(figsize=(16,16))

        # underlying OSM map
        # bounds required: minx, miny, maxx, maxy in EPSG:3857
        xmin, ymin = proj.transform(self.bbox.min_lng, self.bbox.min_lat)
        xmax, ymax = proj.transform(self.bbox.max_lng, self.bbox.max_lat)
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        cx.add_basemap(ax, source=cx.providers.CartoDB.Positron)


        cmap = ListedColormap([
            "#90daeeff",   
            "#ff000088",   
            "#ff880088",   
            "#ffffff00",   
        ])
        bounds = [-100, 0.0000001,  5, 10, 100]
        norm = BoundaryNorm(bounds, cmap.N)
    

        # altitude overlay with transparency
        sc = ax.scatter(
            x,
            y,
            c=alt_f,
            s=1,
            cmap=cmap,
            norm=norm,
            marker="s",
    
        )
        plt.colorbar(ax=ax, mappable=sc, label='Altitude (m)', fraction=0.036, pad=0.04)

        # Remove box and axes labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        log.debug("build_plot done!")