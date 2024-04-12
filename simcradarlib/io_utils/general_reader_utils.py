import os
import gzip
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
from simcradarlib.io_utils.read_rad2d_nc import readnc_to_struct
from simcradarlib.io_utils.read_rad2d_zlr import read_zlr
from math import pi
import pyproj
from typing import Callable, Tuple, Union, Dict, NoReturn, List
import logging
import numpy as np

module_logger = logging.getLogger(__name__)


def get_reader(
    filename: str,
) -> Union[
    Callable[
        [str],
        Tuple[
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
            # npt.NDArray[Any | np.float32] | Dict[str, npt.NDArray[Any | np.float32]],
            Union[np.ndarray, Dict[str, np.ndarray]],
        ],
    ],
    NoReturn,
    Callable[
        [str, str],
        Tuple[
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
            # npt.NDArray[Any | np.float32],
            np.ndarray,
        ],
    ],
]:

    """
    Funzione che restituisce in output la funzione per la lettura di un file
    compatibile con la sua estensione (.nc,.ZLR).

    INPUT :
    - filename    --str      : nome file dati da leggere comprensivo di path.

    OUTPUT :
                  --Callable : funzione che legge il file in input e restituisce in output il
                               campo dati e le strutture delle informazioni spaziali, temporali
                               e sul tipo di prodotto.
                               Tale funzione è
                               - simcradarlib.io_utils.read_rad2d_nc.readnc_to_struct se file in
                               input ha estensione '.nc' (file netCDF in input)
                               - simcradarlib.io_utils.read_rad2d_zlr.read_zlr se file in input
                               ha estensione '.ZLR'
    """

    filename_splitter = filename.split(".")[-1]
    if filename_splitter.lower() == "nc":
        return readnc_to_struct
    elif filename_splitter[-3:] == "ZLR":
        return read_zlr
    else:
        raise Exception(f"Estensione del file {filename} non supportata")
        # correzione Emanuele !!


def unzip_to_nc(filename: str, unzip_dir: str) -> str:

    """
    Funzione che prende in input un file netCDF gunzippato ('filename') e lo unzippa esportando
    il suo contenuto in un file netCDF 'lettura_input.nc', in una directory temporanea unzip_dir.

    INPUT :
    - filename      --str                           : nome file dati da leggere comprensivo di path.
    - unzip_dir     --str                           : nome directory dove unzippare il file da leggere
                                                    (compositi sono in archivio in formato .nc.gz).

    OUTPUT :
    - file_towrite  --ncdf filename                 : file netCDF di nome "lettura_input.nc" in cui viene
                                                      copiato il contenuto del file gunzippato in input.
    """

    file_towrite = os.path.join(unzip_dir, "lettura_input.nc")
    unzip = open(file_towrite, "wb")
    with gzip.open(filename, "rb") as readzip:
        fdata = readzip.read()
    unzip.write(fdata)
    unzip.close()

    return file_towrite


def get_meta_for_pysteps_from_macro(macro: dict, timestamps: Union[np.ndarray, List]) -> dict:

    """
    Funzione che crea un dizionario di metadati compatibile con i metodi di pysteps.

    INPUT:
    - macro        --dict : dizionario delle strutture che contengono le info sul campo fisico
                            letto da un file netCDF o ZLR tramite
                            simcradarlib.io_utils.read_rad2d_nc.readnc_to_struct() e
                            simcradarlib.io_utils.read_rad2d_zlr.read_zlr rispettivamente.
                            E' il primo elemento della tupla in output da ciascun metodo
                            readnc_to_struct e read_zlr.
    - timestamps : --np.ndarray[datetime] :
                            array di oggetti datetime.datetime delle date dei campi analizzati.

    OUTPUT:
    - metadata   --dict : dizionario dei metadati compatibile con i metodi di pysteps.

    KEYWORDS:
    - 'projection' -str    : stringa di proiezione per la georeferenziazione dei dati
                           tramite pyproj
    - 'llon'       -float32: longitudine dell'estremo sud-occidentale della griglia.
    - 'llat'       -float32: latitudine  dell'estremo sud-occidentale della griglia.
    - 'ur_lon'     -float32: longitudine dell'estremo nord-orientale della griglia.
    - 'ur_lat'     -float32: latitudine  dell'estremo nord-orientale della griglia.
    - 'x1'         -float32: coordinata cartesiana x dell'estremo occidentale della griglia.
    - 'y1'         -float32: coordinata cartesiana y dell'estremo inferiore della griglia.
    - 'y2'         -float32: coordinata cartesiana y dell'estremo superiore della griglia.
    - 'xpixelsize' -float32: risoluzione orizzontale della griglia [km]
    - 'ypixelsize' -float32: risoluzione verticale della griglia [km]
    - 'yorigin'    -str    : location del primo elemento nell'array di dati.
                           ( 'lower'=lower border)
    - 'institution' -str   : istituzione.
    - 'accutime'    -float32: tempo di accumulazione dei dati (0 per rainrate).
    - 'unit'        -str   : unità di misura dei dati (‘mm/h’, ‘mm’ or ‘dBZ’).
    - 'transform'   -str   : tipo di trasformazione utilizzata ('dB').
    - 'zerovalue'   : valore assegnato ai norain pixel (missing).
    - 'threshold'   : minimo valore dei rain pixel ammesso (0 anche in dBZ).
    - 'cartesian_unit' -str : unità delle coordinate cartesiane x,y ('m' o 'km').
    - 'timestamps' : array di oggetti datetime delle date dei campi analizzati.

    """

    latc = macro["PROJECTION"].center_latitude
    lonc = macro["PROJECTION"].center_longitude

    R = macro["PROJECTION"].earth_radius
    if R is None:
        R = 6370.997
    projstring = "None"
    if macro["PROJECTION"].struct_hasitem("projection_index"):
        proj_id_structure = macro["PROJECTION"].projection_index
    elif macro["PROJECTION"].struct_hasitem("proj_id"):
        proj_id_structure = macro["PROJECTION"].proj_id
    else:
        proj_id_structure = None
    if proj_id_structure is not None:
        if int(proj_id_structure) == 0:
            projstring = f"+proj=eqc +lat_0={latc:.4f} +lon_0={lonc:.4f} +ellps=WGS84 +R={R:.4f}"
        else:
            # """ da capire come fare se non lat-lon! Quali sono le altre opzioni?"""
            # non lat-lon regolare
            module_logger.info("proiezione composito non lat-lon regolare")
            module_logger.info(f" projection_index trovato : {proj_id_structure}")
            # if( 'spc' and 'gat' in macro['SOURCE'].name_source):
            #   pass
            # elif('spc' or 'gat' in struct['SOURCE'].name_source):
            #   pass
    else:
        module_logger.warning(
            f"Non riesco ad individuare stringa di proiezione tramite {proj_id_structure}.\
        struct PROJECTION has items : {macro['PROJECTION'].__dict__}"
        )

    p = pyproj.Proj(projstring)

    xc, yc = p(lonc, latc)
    # calcolo dx e dy come lunghezza d'arco
    dy = 2 * pi * R * macro["GRID"].dy / 360.0  # *1000
    dx = 2 * pi * R * macro["GRID"].dx / 360.0

    try:
        macrovars = [v for v in macro.keys() if type(macro[v]) == StructVariable]
        if len(macrovars) == 1:
            macrovar = macro["VARIABILE"]
        elif len(macrovars) > 1:
            macrovar = [
                macro[v]
                for v in macro.keys()
                if (macro[v].struct_getitem("standard_name") is not None and macro[v].struct_getitem("units") is not None)
            ][0]
    except (IndexError, AttributeError, KeyError):
        macrovar = StructVariable()

    metadata = {
        "projection": projstring,
        "llon": macro["GRID"].limiti[1],
        "llat": macro["GRID"].limiti[0],
        "ur_lon": macro["GRID"].limiti[3],
        "ur_lat": macro["GRID"].limiti[2],
        "x1": xc - (macro["GRID"].nx - 1) * 0.5 * dx,
        "y1": yc - (macro["GRID"].ny - 1) * 0.5 * dy,
        "x2": xc + (macro["GRID"].nx - 1) * 0.5 * dx,
        "y2": yc + (macro["GRID"].ny - 1) * 0.5 * dy,
        "xpixelsize": dx,  # mesh_dim[0]*100000.,#1223.19,
        "ypixelsize": dy,  # mesh_dim[1]*100000.,#924.7,
        "yorigin": "lower",
        "institution": "Arpae",
        "accutime": macrovar.accum_time_h,
        "unit": macrovar.units,
        "transform": "None",
        "zerovalue": macrovar.missing,
        "threshold": 0.0,
        "cartesian_unit": "km",
        "timestamps": np.array(timestamps),
    }

    return metadata


def dpc_utm_grid_from_meta_pysteps(metadata: dict, nx: int, ny: int) -> Tuple[np.ndarray, np.ndarray]:

    """
    Funzione che calcola le coordinate UTM per il grigliato del mosaico nazionale del DPC
    a partire dal dizionario di metadati di pysteps.

    INPUT:
    - metadata  -dict : dizionario dei metadati restituito da pysteps durante l'import.
    - nx        -int  : numero punti griglia in orizzontale.
    - ny        -int  : numero punti griglia in verticale.

    OUTPUT:
    - projlons  -np.ndarray : vettore delle coordinate UTM sull'asse orizzontale del
                              grigliato del composito. Tale array ha shape=(nx,).
    - projlats  -np.ndarray : vettore delle coordinate UTM sull'asse verticale del
                              grigliato del composito. Tale array ha shape=(ny,).
    """

    # dx = metadata["xpixelsize"]
    # dy = metadata["ypixelsize"]
    ll_lat = metadata["ll_lat"]
    ll_lon = metadata["ll_lon"]
    ur_lat = metadata["ur_lat"]
    ur_lon = metadata["ur_lon"]
    proj = metadata["projection"]

    p = pyproj.Proj(proj)
    # Proietto lat/lon in coord. cartesiane
    x1, y1 = p(ll_lon, ll_lat)
    x2, y2 = p(ur_lon, ur_lat)
    # Creo grigliato regolare in coordinate cartesiane
    utmlons = np.linspace(x1, x2, nx)
    utmlats = np.linspace(y2, y1, ny)  # dati scritti da nord a sud
    # Griglia regolare in UTM
    # grid_utmlon,grid_utmlat=np.meshgrid(utmlons,utmlats)
    # Griglia riproiettata in lat/lon
    # projlons,projlats=p(grid_utmlon,grid_utmlat,inverse=True)

    # return projlons, projlats
    return utmlons, utmlats
