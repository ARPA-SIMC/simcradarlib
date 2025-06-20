import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm, colors
import os

from mpl_toolkits.axisartist import SubplotHost  # , ParasiteAxesAuxTrans
from mpl_toolkits.axisartist.grid_helper_curvelinear import GridHelperCurveLinear

import mpl_toolkits.axisartist.angle_helper as angle_helper

from matplotlib.projections import PolarAxes
from matplotlib.transforms import Affine2D
import logging
import numpy as np
import yaml

from simcradarlib.odim.odim_pvol import OdimHierarchyPvol
from simcradarlib.geo_utils.georef import spherical_to_xyz
from simcradarlib import visualization
from typing import Optional

module_logger = logging.getLogger(__name__)


def plot_ppi_curvilinear(
    fig: matplotlib.figure.Figure,
    cmap: Optional[matplotlib.colors.ListedColormap],
    norm: Optional[matplotlib.colors.BoundaryNorm],
    livelli: Optional[list],
    label: str,
    labels_ticks: Optional[list],
    data: np.ndarray,
    n_circles: int,
    xyz: np.ndarray,
    r: np.ndarray,
    r_scale: float = 1000.0,
    r_legend: bool = False,
    title: str = None,
):

    """
    Plot PPI di volume radar.

    INPUT:
    -fig           --matplotlib.figure.Figure : figura in cui plottare il PPI
    -cmap          --Optional[matplotlib.colors.ListedColormap] :
                                                colormap per il PPI. Se None si applica
                                                matplotlib.cm.Blues
    -norm          --Optional[matplotlib.colors.BoundaryNorm] : normalizzazione della colormap
                                                per il PPI. Se None si applica
                                                normalizzazione tra 0 e 1 alla colormap.
    -livelli       --Optional[list] : lista dei livelli della variabile radar da plottare
                                      associati a ciascuna banda della colormap.
    -label         --str : label della colorbar (consigliato usare unità della variabile
                                                 radar da plottare)
    -label_ticks   --Optional[list] : lista dei labels nella colorbar. Possono essere i livelli
                                      associati a ciascuna banda della colormap.
    -data          --np.ndarray :  array dei dati da plottare nel PPI.
    -n_circles     --int (default=4): intero che rappresenta il numero di cerchi evidenziati dentro il PPI.
    -xyz           --np.ndarray : array delle coordinate x,y,z cartesiane del PPI.
    -r             --np.ndarray : array dei ranges [m]
    -r_scale       --float : dimensione del bin lungo la direzione radiale.
    -r_legend      --bool (default=False) : se True scrive la legenda nella direzione radiale "r [km]"
    -title         --Optional[str] = None: titolo

    OUTPUT :
    restituisce il plot del PPI.
    Se si usa questa funzione in un ciclo, ad esempio, iterando sugli angoli di elevazione,
    mettere subito dopo la chiamata alla funzione un plt.show() altrimenti viene visualizzato
    solo l'ultima figura.
    """

    # PolarAxes.PolarTransform takes radian. However, we want our coordinate
    # system in degree
    # tr = Affine2D().translate(0, -90).scale(np.pi/180., 1.) + PolarAxes.PolarTransform()
    tr_scale = Affine2D().scale(np.pi / 180.0, 1.0)
    tr = Affine2D().translate(90, 0) + tr_scale + PolarAxes.PolarTransform()
    # tr = tr_scale + PolarAxes.PolarTransform() + Affine2D().rotate_deg(180)

    # polar projection, which involves cycle, and also has limits in
    # its coordinates, needs a special method to find the extremes
    # (min, max of the coordinate within the view).

    # 20, 20 : number of sampling points along x, y direction
    extreme_finder = angle_helper.ExtremeFinderCycle(
        360,
        360,
        lon_cycle=360.0,  # viene ignorata la riga 401 ovvero in sostanza =360,
        lat_cycle=None,
        lon_minmax=None,
        lat_minmax=(0, np.inf),
    )

    grid_locator1 = angle_helper.LocatorDMS(18)
    # Find a grid values appropriate for the coordinate (degree,
    # minute, second).

    tick_formatter1 = angle_helper.FormatterDMS()
    # And also uses an appropriate formatter.  Note that,the
    # acceptable Locator and Formatter class is a bit different than
    # that of mpl's, and you cannot directly use mpl's Locator and
    # Formatter here (but may be possible in the future).

    grid_helper = GridHelperCurveLinear(
        tr, extreme_finder=extreme_finder, grid_locator1=grid_locator1, tick_formatter1=tick_formatter1
    )

    ax1 = SubplotHost(fig, 1, 1, 1, grid_helper=grid_helper)

    ax1.pcolormesh(xyz[0, :, :, 0] / r_scale, xyz[0, :, :, 1] / r_scale, data, cmap=cmap, norm=norm)
    # make ticklabels of right and top axis visible.
    ax1.axis["right"].major_ticklabels.set_visible(True)
    ax1.axis["left"].major_ticklabels.set_visible(False)
    ax1.axis["top"].major_ticklabels.set_visible(True)
    ax1.axis["bottom"].major_ticklabels.set_visible(True)

    # let right axis shows ticklabels for 1st coordinate (angle)
    ax1.axis["right"].get_helper().nth_coord_ticks = 0
    # ax1.axis["left"].get_helper().nth_coord_ticks = 0
    # let bottom axis shows ticklabels for 2nd coordinate (radius)
    ax1.axis["bottom"].get_helper().nth_coord_ticks = 0
    # n_circles=4
    r_circles = r[:: int(len(r) / n_circles)]
    for r_c in r_circles:
        ax1.axis[f"{r_c}"] = ax1.new_floating_axis(nth_coord=1, value=r_c / r_scale)
        ax1.axis[f"{r_c}"].major_ticklabels.set_visible(False)
        ax1.axis[f"{r_c}"].major_ticks.set_visible(False)

    ax1.axis["range"] = ax1.new_floating_axis(0, -45)
    if r_legend:
        range_unit = "km"
        if r_scale != 1000:
            range_unit = input("range unit?")
        ax1.axis["range"].label.set_text(f"$r$ $[{range_unit}]$")

    fig.add_subplot(ax1)

    ax1.set_aspect(1.0)
    ax1.set_xlim(xyz[0, ..., 0].min() / r_scale, xyz[0, ..., 0].max() / r_scale)
    ax1.set_ylim(xyz[0, ..., 1].min() / r_scale, xyz[0, ..., 1].max() / r_scale)

    ax1.grid(True, zorder=0)

    # fig.colorbar(cm.ScalarMappable(norm,cmap),
    # ticks=livelli,orientation='horizontal',
    # shrink=0.8, pad=0.03,label='dBZ',aspect=40)

    if cmap is None or livelli is None:
        logging.exception("cmap o livelli = None. Use Greys.")
        norm = colors.Normalize(0, 1)
        cmap = cm.Blues
    cmp = cm.ScalarMappable(norm, cmap)
    cmp.set_array(data)
    print("set array done")
    clbclass = fig.colorbar(cmp, orientation="horizontal", shrink=0.8, pad=0.03, aspect=40, ax=plt.gca())
    clbclass.set_label(label, labelpad=-0.4, y=1.16, rotation=0, fontsize=10)
    if livelli is not None:
        clbclass.set_ticklabels(labels_ticks)
    if title:
        plt.suptitle(title, y=0.92, fontweight="semibold")
    # plt.draw()
    # plt.show()


def plot_ppi_from_vol(
    f_vol: str, elangle: float, intitle: str, rad_qty: str, outname: Optional[str] = None, save: bool = False
):

    """
    funzione che plotta il PPI all'elevazione elangle dal volume fvol,
    usando simcradarlib.visualization.plot_ppi.plot_ppi_curvilinear().
    Se save=True, allora outname deve essere diverso da None e deve
    essere il filename della figura che viene salvata.

    La colormap usata per plottare il PPI è ricavata usando i colori definiti
    nel file di configurazione, definito in config, per la grandezza radar corrispondente.
    Se in config non è presente un campo con attributo varsn uguale a rad_qty il plot
    finale è realizzato usando una scala di blu e normalizzazione tra 0 e 1 del campo.
    In questa implementazione config è simcradarlib.visualization.config_plot.yml e
    attualmente contiene le specifiche per DBZH, ACRR (cum), RATE (rainrate).

    INPUT:
    -f_vol     --str    : filename del volume radar
    -elangle   --float  : angolo di elevazione del PPI
    -intitle   --str    : titolo della figura del PPI
    -rad_qty   --str    : nome della grandezza radar storata nel volume f_vol
                          che voglio plottare. Tale stringa deve corrispondere
                          all'attributo quantity del what del dataset in cui tale
                          grandezza è storata all'interno di f_vol.
                          Es: "DBZH" per la riflettività corretta se il volume è
                          stato ripulito, "TH" per il dato di riflettività grezza.
    -outname   --Optional[str] = None : filename con cui salvo la figura
    -save      --bool = False : se True salvo la Figura (in questo caso outname deve
                                essere diverso da None. Se False il plot non viene
                                salvato.
    OUTPUT:
    plotta il PPI della grandezza radar rad_qty e lo salva se save=True.
    """
    rfvol = OdimHierarchyPvol()
    rfvol.read_odim(f_vol)

    iel = rfvol.elangles.index(elangle)
    var_ = rfvol.get_data_by_elangle(elangle, rad_qty)
    rstart = rfvol.group_datasets_where[iel].rstart
    nbins = rfvol.group_datasets_where[iel].nbins
    rscale = rfvol.group_datasets_where[iel].rscale
    r = np.arange(rstart, rstart + (nbins + 1) * rscale, rscale)

    nrays = rfvol.group_datasets_where[0].nrays
    az_binsize = 360.0 / nrays
    az = np.arange(0.0, 360.0 + az_binsize, 360.0 / nrays)

    site = (rfvol.root_where.lon, rfvol.root_where.lat, rfvol.root_where.height)

    myxyz, myproj = spherical_to_xyz(r, az, elangle, site)

    config = os.path.dirname(visualization.plot_ppi.__file__)
    config = os.path.join(config, "config_plot.yml")
    with open(config, "r") as stream:
        config_dict = yaml.safe_load(stream)

    cmap, norm, livelli, colori, units = (None, None, None, None, "")
    for varc in config_dict["variables"]:
        if config_dict["variables"][varc]["varsn"] == rad_qty:
            units = config_dict["variables"][varc]["units"]
            livelli = config_dict["variables"][varc]["livelli"]
            colori = config_dict["variables"][varc]["colori"]
    if None not in (livelli, colori):
        cmap, norm = matplotlib.colors.from_levels_and_colors(livelli, colori, extend="neither")

    fig = plt.figure(1, figsize=(10, 10))
    fig.clf()
    plot_ppi_curvilinear(
        fig, cmap, norm, livelli, units, livelli, var_, 4, myxyz, r, r_scale=1000.0, r_legend=True, title=intitle
    )
    if save:
        try:
            plt.savefig(outname, dpi=300, bbox_inches="tight")
        except Exception:
            logging.exception("Non salvo la figura!")
