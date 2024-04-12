from datetime import datetime
import numpy as np
import logging
import pyproj
from math import cos, radians, pi, degrees

from simcradarlib.io_utils.structure_class import (
    StructBase,
    StructTime,
    StructGrid,
    StructProjection,
    StructSource,
    StructProduct,
    StructCoords,
    StructVariable,
)
from typing import Union, Dict, Tuple

module_logger = logging.getLogger(__name__)


def read_zlr(
    filename: str, radar: str
) -> Tuple[
    Dict[
        str,
        Union[
            StructBase,
            StructTime,
            StructGrid,
            StructProjection,
            StructSource,
            StructProduct,
            StructCoords,
            StructVariable,
        ],
    ],
    np.ndarray,
]:

    """
     Funzione che legge un file binario di estensione .ZLR o .qual_ZLR e restituisce in output
     una tupla di due elementi.
     Il primo è la macrostruttura delle informazioni temporali, spaziali e di contenuto del
     file. Tale macrostruttura è un dizionario di istanze delle classi implementate in
     simcradarlib.io_utils.structure_class, le quali rappresentano le varie strutture di
     informazioni sul campo storato nel file ZLR.

     Il file binario non contiene di per sè informazioni sul tipo di prodotto o sorgente dati,
     quindi è necessario specificare il radar sorgente dei dati e le altre informazioni sono
     ricavate conoscendo il radar sorgente e dal filename.
     ______
     INPUT:
     - filename         --str     :  nome del file binario da leggere comprensivo del path.
     - radar            --str     :  nome del radar sorgente ('spc' o 'gat').
     ______
     OUTPUT:
     - macro            --dict    :  dizionario avente come values le strutture contenenti
                                     le informazioni sui dati e come chiavi stringhe identificative
                                     del tipo di informazioni contenute nelle strutture.
                                     Tali strutture sono istanze delle classi definite in
                                     structure_class.py.

                                     Keys():

                                     - 'TIME'       : ha come value un'istanza della classe StructTime()
                                                      che contiene le informazioni temporali.
                                     - 'GRID'       : ha come value un'istanza della classe StructGrid()
                                                      che contiene le informazioni sul grigliato
                                                      usato per georeferire la matrice dati.
                                     - 'SOURCE'     : ha come value un'istanza della classe StructSource()
                                                      che legge le info sulla provenienza dei dati.
                                     - 'PRODUCT'    : ha come value un'istanza della classe StructProduct()
                                                      che legge le info sul tipo di prodotto contenuto
                                                      nel file di input.
                                     - 'VARIABILE'  : con value un'istanza della classe StructVariable()
                                                      che specifica informazioni sul campo fisico
                                                      letto dal file di input.
                                     - 'PROJECTION' : con value un'istanza della classe StructProjection()
                                                      che contiene info sulla proiezione usata.
                                     - 'COORDS_X'   : con value un'istanza della classe StructCoords()
                                                      che contiene le coordinate per l'asse x e relative
                                                      informazioni.
                                     - 'COORDS_Y'   : con value un'istanza della classe StructCoords()
                                                      che contiene le coordinate per l'asse y e
                                                      relative informazioni.
     - campo_data    --np.ndarray :  campo della variabile da leggere di tipo np.float32.
     ________
     KEYWORDS:

    - filename          --str     : stringa di input che contiene nome del file binario da leggere, incluso il path.

    - radar             --str     : stringa che identifica il radar che ha acquisito i dati.

    -  macro            --dict    : dizionario in output.

    - campo_data        --np.array() : campo della variabile da leggere.

    - time_struct       --StructTime() : contiene info temporali del campo fisico letto.

    - grid_struct       --StructGrid() : contiene info sul grigliato del campo fisico letto.

    - xcoords_struct    --StructCoords() : contiene info sulle coordinate dei punti griglia sull'asse x.

    - ycoords_struct    --StructCoords() : contiene info sulle coordinate dei punti griglia sull'asse y.

    - proj_struct       --StructProjection() : contiene info sul tipo di proiezione usata.

    - campo             --StructVariable() : contiene info del campo fisico da leggere.

    - struct_product    --StructProduct() : contiene info sul tipo di prodotto.

    - struct_source     --StructSource() : contiene info sull provenienza dati.

    - latc              --float    : latitudine del centro del grigliato.

    - lonc              --float    : longitudine del centro del grigliato.

    - n_grid            --int      : numero nodi della griglia. Si ricava dalle dimensioni dell'array
                                     del campo letto. nx = ny = n_grid.
                                     Se n_grid=256 -> raggiotype=corto, se n_grid=512 -> raggiotype=medio.

    - projstring        --str      : stringa di proiezione usata da pyproj.

    - dy, dx            --float    : risoluzioni verticale e orizzontale proiettate in km.

    - x1,x2,y1,y2       --float    : estremi del grigliato proiettati in km.

    - lat1,lat2,lon1,lon2   --float  : estremi del grigliato riproiettati in lat-lon regolare.

    """

    if radar.lower() == "spc":
        latc = 44.6547
        lonc = 11.6236
    elif radar.lower() == "gat":
        latc = 44.7914
        lonc = 10.4992
    else:
        module_logger.warning("Radar non specificato")

    try:
        f = open(filename, "rb")
        cont = list(f.read())
        f.close()
    except FileNotFoundError:
        module_logger.exception(f"Non riesco a leggere il file di input {filename}")

    # ricavo il numero di punti griglia in base alla dimensione dell'array che leggo dal file ZLR
    # da n_grid ricavo il raggiotype
    try:
        n_grid = int(np.sqrt(len(cont)))
    except Exception:
        module_logger.exception("numero nodi griglia non calcolato")

    """ __________________________________struttura VARIABILE__________________________________ """

    campo = StructVariable()

    splitter_filename = filename.split(".")
    if splitter_filename[-1] == "ZLR":
        campo.name = "Z_60"
        campo.long_name = "radar reflectivity"
        campo.missing = np.float32(-20.0)
        campo.undetect = np.float32(80.0 / 255.0 - 20.0)
        campo.units = "dBZ"
    elif splitter_filename[-1] == "qual_ZLR":
        campo.name = "ZLR_QUA"  # ho riportato il valore di Map_type di idl, ma non so se va bene
        campo.long_name = "radar reflectivity quality"
        campo.missing = np.float32(-20.0)
        campo.undetect = np.float32(80.0 / 255.0 - 20.0)
        campo.units = "dBZ"

    try:
        if campo.name == "Z_60":
            campo_data = (
                np.array([float(k) for k in cont], dtype=np.float32).reshape((n_grid, n_grid)).T
            )  # trasposta in quanto scritta in C
            campo_data = campo_data * 80.0 / 255.0 - 20
        elif campo.name == "ZLR_QUA":
            campo_data = np.array([float(k) for k in cont], dtype=np.float32).reshape((n_grid, n_grid)) * 0.01
        campo_data = np.expand_dims(campo_data, axis=0)  # se voglio shape (1,ngrid,ngrid) e non (ngrid,ngrid)
    except Exception:
        module_logger.exception("Non riesco a fare la trasposta del campo letto")
        campo_data = np.empty((0,), dtype=np.float32)

    """ __________________________________struttura PROJECTION__________________________________ """

    proj_struct = StructProjection()

    try:
        proj_struct.center_latitude = latc
        proj_struct.center_longitude = lonc
        # proj_struct.proj_id = 0 # setto default 0 perchè ho visto che nei netCDF delle cumulate dei radar singoli
        # si usa cmq lat-lon regolare e non azimuthal equidistant
        proj_struct.addparams("proj_id", 0)
        proj_struct.proj_name = "Cartesian LatLon"
        proj_struct.earth_radius = 6370.997
    except Exception:
        module_logger.exception("Lettura proiezione fallita")

    """ __________________________________struttura GRID__________________________________ """

    grid_struct = StructGrid()

    try:
        grid_struct.nx = n_grid
        grid_struct.ny = n_grid
        if proj_struct.proj_id == 0:
            grid_struct.dx = degrees(1.0 / (proj_struct.earth_radius * cos(radians(latc))))
            grid_struct.dy = degrees(1.0 / proj_struct.earth_radius)
            grid_struct.units_dx = "degrees"
            grid_struct.units_dy = "degrees"
            projstring = f"+proj=eqc +lat_0={latc:.4f} +lon_0={lonc:.4f} +ellps=WGS84 +R={proj_struct.earth_radius:.4f}"
        else:
            module_logger.warning("proj_id non 0! Verificare proiezione!")
        p = pyproj.Proj(projstring)

        dy = 2 * pi * proj_struct.earth_radius * grid_struct.dy / 360.0  # *1000
        dx = 2 * pi * proj_struct.earth_radius * grid_struct.dx / 360.0  # *1000
        xc, yc = p(lonc, latc)
        x0 = xc - (grid_struct.nx - 1) * 0.5 * dx
        x1 = xc + (grid_struct.nx - 1) * 0.5 * dx
        y0 = yc - (grid_struct.ny - 1) * 0.5 * dy
        y1 = yc + (grid_struct.ny - 1) * 0.5 * dy

        lon1, lat1 = p(x0, y0, inverse=True)
        lon2, lat2 = p(x1, y1, inverse=True)

        grid_struct.limiti = np.array([lat1, lon1, lat2, lon2], dtype=np.float32)
    except Exception:
        module_logger.exception("Lettura proiezione fallita")

    """ __________________________________struttura COORDS__________________________________ """

    xcoords_struct = StructCoords()

    try:
        if proj_struct.proj_id == 0:
            xcoords_struct.name = "lon"
            xcoords_struct.long_name = "longitude"
            xcoords_struct.units = "degrees"
            xcoords_struct.vals = np.linspace(grid_struct.limiti[1], grid_struct.limiti[3], grid_struct.nx)
    except Exception:
        module_logger.exception("Lettura xcoord non eseguita")
        pass

    ycoords_struct = StructCoords()

    try:
        if proj_struct.proj_id == 0:
            ycoords_struct.name = "lat"
            ycoords_struct.long_name = "latitude"
            ycoords_struct.units = "degrees"
            ycoords_struct.vals = np.linspace(grid_struct.limiti[0], grid_struct.limiti[2], grid_struct.ny)
    except Exception:
        module_logger.exception("Lettura ycoord non eseguita")
        pass

    """ __________________________________struttura TIME__________________________________ """

    time_struct = StructTime()

    time_struct.date_time_validita = datetime.strptime(splitter_filename[0][-12:], "%Y%m%d%H%M")
    time_struct.date_time_emissione = time_struct.date_time_validita

    """ __________________________________struttura PRODUCT__________________________________ """

    struct_product = StructProduct()

    struct_product.name = "ZLR"
    struct_product.addparams("radar", radar)
    try:
        if n_grid == 256:
            struct_product.addparams("raggio", "corto")
        elif n_grid == 512:
            struct_product.addparams("raggio", "medio")
    except Exception:
        module_logger.exception("Calcolo raggiotype fallito")

    """ __________________________________struttura SOURCE__________________________________ """

    struct_source = StructSource()

    struct_source.name_source = radar
    struct_source.name_file = filename

    macro = {
        "TIME": time_struct,
        "GRID": grid_struct,
        "PROJECTION": proj_struct,
        "SOURCE": struct_source,
        "PRODUCT": struct_product,
        "VARIABILE": campo,
        "COORDS_X": xcoords_struct,
        "COORDS_Y": ycoords_struct,
    }

    return macro, campo_data.astype(np.float32)
