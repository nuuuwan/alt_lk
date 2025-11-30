import matplotlib.pyplot as plt
import numpy as np
from utils import Log

from alt_lk.alt.Alt import Alt
from alt_lk.render.AbstractPlot import AbstractPlot

log = Log("Map2D")


class Map2D(AbstractPlot):
    @property
    def cmap(self):
        return "turbo"

    def build_plot(self):
        log.debug("build_plot")
        alt = self.alt or Alt.get_matrix_subset(self.bbox)
        alt = self.get_mapped_alt(alt) if self.get_mapped_alt else alt

        log.debug(f"alt.shape={alt.shape}")
        lat, lng = np.mgrid[: alt.shape[0], : alt.shape[1]]

        dim_lat, dim_lng = alt.shape
        lat = -lat / dim_lat * self.bbox.lat_span + self.bbox.max_lat
        lng = lng / dim_lng * self.bbox.lng_span + self.bbox.min_lng

        plt.scatter(
            lng,
            lat,
            c=alt,
            s=1,
            cmap=self.cmap,
            marker="s",
            vmin=-100,
            vmax=100,
        )
        plt.colorbar()

        ax = plt.gca()
        ax.set_xlabel("lng")
        ax.set_ylabel("lat")
        log.debug("build_plot done!")
