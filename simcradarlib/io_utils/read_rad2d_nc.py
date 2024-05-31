from simcradarlib.io_utils.structure_class import (
    StructBase,
    StructTime,
    StructGrid,
    StructProjection,
    StructSource,
    StructProduct,
    StructCoords,
    StructVariable,
    # npt,
)
import logging
from netCDF4 import num2date, Dataset
from typing import Tuple, Union, Dict
import numpy as np

module_logger = logging.getLogger(__name__)


def readnc_to_struct(
    filename: str,
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
    # Dict[str, npt.NDArray[Any | np.float32]] | npt.NDArray[Any | np.float32],
    Union[Dict[str, np.ndarray], np.ndarray],
]:

    """
    Funzione che legge un file netCDF e restituisce in output una tupla di due elementi.
    Il primo elemento della tupla in output rappresenta la macrostruttura delle informazioni
    sul contenuto del file netCDF in formato dizionario: i values sono istanze delle classi
    implementate in simcradarlib.io_utils.structure_class (replicano le strutture di IDL) e le
    corrispondenti keys sono stringhe identificative del tipo di informazione contenuta in
    ciascuna 'struttura'. Il secondo elemento è la matrice dei dati contenuta nel file netCDF.
    ______
    INPUT:
    - filename  --str  :  nome del file netCDF da leggere comprensivo del path.
    ______
    OUTPUT:
    -macro      --dict :  dizionario avente come values le strutture contenenti le informazioni sui dati,
                          lette dal file netCDF, e come chiavi stringhe identificative del tipo di
                          informazioni contenute nelle strutture.
                          Tali strutture sono istanze delle classi implementate in
                          simcradarlib.io_utils.structure_class e sono usate per leggere i campi e attributi
                          delle variabili del file netCDF.

                          In macro sono sempre presenti le chiavi:

                          - 'TIME'       : ha come value un'istanza della classe StructTime() in structure_class.py
                                           che legge i dati del tempo dal file netCDF in input.

                          - 'GRID'       : ha come value un'istanza della classe StructGrid() in structure_class.py
                                           che legge i dati per il grigliato.

                          -'SOURCE'      : ha come value un'istanza della classe StructSource() in
                                           structure_class.py che legge le info sulla provenienza dei dati.

                          -'PRODUCT'     : ha come value un'istanza della classe StructuProduct() in
                                           structure_class.py che legge le info sul tipo di prodotto contenuto nel
                                           file netCDF.

                          Se fallisce la lettura (da netCDF) degli attributi da assegnare alle strutture, gli
                          attributi di queste istanze, che sono istanze delle classi strutture, sono None.

                          A meno che non ci siano problemi nella lettura, il dizionario macro contiene almeno anche
                          le seguenti chiavi e corrisponenti strutture:

                          - 'VARIABILE'  : il value corrispondente è un'istanza della classe StructVariable(),
                                           definita in structure_class.py, che legge gli attributi del campo storato
                                           nel file netCDF.
                                           Se il file netCDF contiene più di una variabile associata ad un campo
                                           fisico, ci saranno più chiavi 'VARIABILE_{X}'->X=nome della variabile
                                           nel file netCDF.
                                           Esempio:
                                           Se il file netCDF contiene il campo "cum_pr_mm" di cumulata e la matrice
                                           dei fattori di adjustment per la correzione "adj", allora macro non ha
                                           una chiave "VARIABILE", ma due chiavi:
                                           - "VARIABILE_cum_pr_mm" con value dato dalla struttura delle info sulla
                                           cumulata.
                                           - "VARIABILE_adj" con value dato dalla struttura delle informazioni sul
                                           fattore adj.
                                           Tali strutture, cioè i values corrispondenti alle keys "VARIABILE_adj"
                                           e "VARIABILE_cum_pr_mm" saranno entrambe istanze della classe
                                           StructVariable.

                          - 'PROJECTION' : il value corrispondente è un'istanza della classe StructProjection(),
                                           definita in structure_class.py, che legge info sulla proiezione usata
                                           nel file netCDF.
                                           Se il netCDF contiene più di una variabile di tipo 'S1', ci saranno più
                                           chiavi '{X}'->X=variab di tipo 'S1' netCDF.
                                           (Questo potrebbe accadere se per caso nel file netCDF sono storate le
                                           coordinate del grigliato del campo in due diversi sistemi di riferimento)

                          - 'COORDS_X'   : il value corrispondente è un'istanza della classe StructCoords(),
                                           definita in structure_class.py, che legge le coordinate per l'asse x e
                                           relativi attributi dal file netCDF.
                                           Se trova le coordinate in diversi sistemi di riferimento, aggiunge un
                                           key:value per ogni tipo di sistema di riferimento.

                          - 'COORDS_Y'   : il value corrispondente è un'istanza della classe StructCoords(),
                                           definita in structure_class.py, che legge le coordinate per l'asse y e
                                           relativi attributi dal file netCDF.
                                           Se trova le coordinate in diversi sistemi di riferimento, aggiunge
                                           un key:value per ogni tipo di sistema di riferimento (SR).

    - dati_out --Union[np.ndarray, Dict] : array di dati letto dal file netCDF.
                                           Se il file netCDF contiene più campi di variabili, l'output è un
                                           dizionario avente
                                           -chiavi = stringhe dei nomi dei campi letti dal file netCDF.
                                           -values = np.ndarray dei dati letti, per ciascun campo.
                                           Esempio :
                                           Se il file netCDF contiene il campo "cum_pr_mm" di cumulata e la
                                           matrice dei fattori di adjustment per la correzione "adj", allora
                                           dati_out={"cum_pr_mm":np.ndarray, "adj":np.ndarray}

        KEYWORDS:

    - filename          --str     : stringa di input che contiene nome del file netCDF da leggere,
                                   incluso il path.

    - macro             --dict    : dizionario in output.

    - campo_data        --np.ndarray  : campo della variabile da leggere.

    - time_struct       --StructTime() : contiene info temporali del campo fisico letto.

    - grid_struct       --StructGrid() : contiene info sul grigliato del campo fisico letto.

    - xcoords_struct    --StructCoords() : contiene info sulle coordinate dei punti griglia sull'asse x.

    - ycoords_struct    --StructCoords() : contiene info sulle coordinate dei punti griglia sull'asse.

    - proj_struct       --StructProjection() : contiene info sul tipo di proiezione usata.

    - campo             --StructVariable() : contiene info e valori del campo fisico da leggere.

    - struct_product    --StructProduct() : contiene info sul tipo di prodotto.

    - struct_source     --StructSource() : contiene info sul tipo di dati e provenienza dati.
    _____________
    **OPZIONALI** :

    - campi_x       --dict    : dizionario avente values oggetti StructCoords() con chiavi il nome del tipo
                               di coordinata x nel caso siano scritte nel netCDF le coordinate in più SR.
    - campi_y       --dict    : dizionario avente values oggetti StructCoords() con chiavi il nome del tipo
                               di coordinata y nel caso siano scritte nel netCDF le coordinate in più SR.

    - strvar_campi  --dict    : dizionario avente values oggetti StructProjection() con chiavi il nome della
                               variabile di tipo 'S1' nel netCDF nel caso di più variabili 'S1' nel netCDF.
    - campi         --dict    : dizionario avente values oggetti StructVariable() con chiavi i nomi delle
                               variabili associate a campi fisici letti, preceduti dal prefisso
                               "VARIABILE_", se c'è più di un campo fisico nel netCDF.
    - campi_data    --dict    : dizionario avente come values i campi fisici nel netCDF con chiavi i nomi
                               delle variabili, nel caso in cui il file netCDF letto che contenga più di
                               un campo fisico.
    """

    nc = Dataset(filename, "r")

    """ __________________________________struttura TIME__________________________________
        Vengono gestiti anche i file netCDF in cui il campo 'time' non è netCDF compliant
        perchè presenta l'attributo 'units' in
                            "<unità> before <data_di_validità>"
        anzichè
                            "<unità> since 1970-01-01 00:00:00."
        dove <unità> è "seconds","minutes","hours","days".
        In ogni caso l'attributo 'acc_time_units' viene settato a <units> letto.
        Gli attributi 'date_time_validita' e 'date_time_emissione' sono restituiti
        in formato datetime.datetime e coincidono in questa implementazione,
        in attinenza alla routine IDL 'read_rad2d_netcdf()', che veniva usata per
        leggere files netCDF di campi osservati (quindi la data di validità e di
        emissione coincidevano).
    """

    time_struct = StructTime()

    try:

        time_to_read = nc["time"].units.split(" ")

        if "since" not in time_to_read:

            # se le units di time non sono CF-compliant, le correggo e
            # estraggo data_validita come datetime da num2date usando units ricorrette
            time_to_read[1] = "since"
            units_new = " ".join(time_to_read)
            time_struct.date_time_validita = num2date(nc["time"][:], units_new, only_use_cftime_datetimes=False)[0]
            time_struct.acc_time_unit = time_to_read[0]

        else:
            time_struct.date_time_validita = num2date(nc["time"][:], nc["time"].units, only_use_cftime_datetimes=False)[
                0
            ]
            time_struct.acc_time_unit = time_to_read[0]

        # data validità=data emissione perchè dato osservato. Per rendere il codice più generale sarebbe bello
        # inserire una keyword nel commento o nel file di config
        time_struct.date_time_emissione = time_struct.date_time_validita

    except Exception:

        module_logger.exception("Lettura time fallita")

    """ __________________________________struttura GRID__________________________________ """

    grid_struct = StructGrid()

    if "geo_dim" in nc.variables:
        grid_struct.limiti = nc["geo_dim"][:].data
    else:
        module_logger.debug("Non trovo la variabile geo_dim: prima lettura limiti griglia fallita!")

    if "mesh_dim" in nc.variables:
        grid_struct.dx = nc["mesh_dim"][:].data[0]
        grid_struct.dy = nc["mesh_dim"][:].data[1]
        grid_struct.units_dx = nc["mesh_dim"].units
        grid_struct.units_dy = nc["mesh_dim"].units
    else:
        module_logger.debug("Non trovo la variabile mesh_dim: prima lettura passo griglia fallita!")

    try:
        if "lon" and "lat" in nc.dimensions:
            grid_struct.nx = nc.dimensions["lon"].size
            grid_struct.ny = nc.dimensions["lat"].size
        elif "x" and "y" in nc.dimensions:
            grid_struct.nx = nc.dimensions["x"].size
            grid_struct.ny = nc.dimensions["y"].size
        else:
            module_logger.exception("Non calcolo numero punti griglia")
        module_logger.debug(f"Numero punti griglia nx={grid_struct.nx}, ny={grid_struct.ny}")
    except Exception:
        module_logger.exception("Non calcolo numero punti griglia")

    """ __________________________________struttura COORDS__________________________________
         Non presente in idl.
    """

    tmp_varx = [
        var for var in nc.variables if ((nc[var].size == grid_struct.nx) and ("standard_name" in nc[var].ncattrs()))
    ]
    if tmp_varx != []:
        n_typecoords_x = len(tmp_varx)
        campi_x = {}
        for v in tmp_varx:
            xcoords_struct = StructCoords()
            try:
                xcoords_struct.name = v
                xcoords_struct.vals = nc[v][:]
            except Exception:
                module_logger.warning("Coordinate x non lette")
            if hasattr(nc[v], "units"):
                xcoords_struct.units = nc[v].units
            if hasattr(nc[v], "long_name"):
                xcoords_struct.long_name = nc[v].long_name
            campi_x[v] = xcoords_struct

        if tmp_varx.__len__() == 1:
            campi_x["COORDS_X"] = campi_x.pop(v)
    else:
        n_typecoords_x = 0
        module_logger.debug("struttura COORDS_X non definita")

    tmp_vary = [
        var for var in nc.variables if ((nc[var].size == grid_struct.ny) and ("standard_name" in nc[var].ncattrs()))
    ]
    if tmp_vary != []:
        n_typecoords_y = len(tmp_vary)
        campi_y = {}
        for v in tmp_vary:
            ycoords_struct = StructCoords()
            try:
                ycoords_struct.name = v
                ycoords_struct.vals = nc[v][:]
            except Exception:
                module_logger.exception("Coordinate y non lette")
            if hasattr(nc[v], "units"):
                ycoords_struct.units = nc[v].units
            if hasattr(nc[v], "long_name"):
                ycoords_struct.long_name = nc[v].long_name
            campi_y[v] = ycoords_struct

        if tmp_vary.__len__() == 1:
            campi_y["COORDS_Y"] = campi_y.pop(v)
    else:
        n_typecoords_y = 0
        module_logger.debug("struttura COORDS_Y non definita")

    """ __________________________________struttura VARIABILE__________________________________ """

    tmp_var = [var for var in nc.variables if (nc[var].shape == (nc["time"].size, grid_struct.ny, grid_struct.nx))]

    if tmp_var != []:
        n_campi = len(tmp_var)
        campi = {}
        campi_data = {}
        for v in tmp_var:

            campo = StructVariable()
            campo.name = v
            basic_attrs_list = [
                "long_name",
                "standard_name",
                "units",
                "min_val",
                "max_val",
                "missing",
                "undetect",
                "accum_time_h",
            ]
            for basic_att in basic_attrs_list:
                if hasattr(nc[v], basic_att):
                    try:
                        campo.__setattr__(basic_att, getattr(nc[v], basic_att))
                    except AttributeError:
                        module_logger.warning(f"Non trovato attributo {basic_att}")
                        pass
            extra_params_var_search = [
                "offset",
                "scale_factor",
                "n_byte",
                "val_compresso",
                "_FillValue",
                "valid_min",
                "valid_max",
                "valid_range",
            ]
            for param_searched in extra_params_var_search:
                if hasattr(nc[v], param_searched):
                    try:
                        campo.addparams(param_searched, nc[v].getncattr(param_searched))
                    except Exception:
                        # campo.addparams(param_searched, nc[v].__dict__[param_searched])
                        module_logger.exception(
                            f"param {param_searched} non trovato per var={v}.\nParametri disponibili:\n{nc[v].__dict__.items()}"
                        )
            try:
                campi[v] = campo
                campi_data[v] = nc[v][:].data.astype(np.float32)
                if n_campi == 1:
                    campi["VARIABILE"] = campi.pop(v)
                    campi_data["VARIABILE"] = campi_data.pop(v)
            except Exception:
                module_logger.exception("lettura campo dati fallita!")

    else:
        n_campi = 0
        module_logger.warning([f"{var}.shape={nc[var].shape}, " for var in nc.variables])
        module_logger.warning(f"nx={grid_struct.nx},ny={grid_struct.ny}")

    """ __________________________________struttura PROJECTION__________________________________ """

    tmp_varp = [var for var in nc.variables if (nc[var].dtype == "S1")]
    if tmp_varp != []:
        n_stringvar = len(tmp_varp)
        if n_stringvar > 1:
            strvar_campi = {}
        for p in tmp_varp:
            proj_struct = StructProjection()
            proj_struct.proj_name = nc[p].projection_name if hasattr(nc[p], "projection_name") else None
            grid_mapping_name = nc[p].grid_mapping_name if hasattr(nc[p], "grid_mapping_name") else None

            if grid_mapping_name == "idl-lat-lon":
                try:
                    proj_struct.center_longitude = (
                        grid_struct.dx * float(grid_struct.nx - 1) * 0.5 + grid_struct.limiti[1]
                    )
                    proj_struct.center_latitude = (
                        grid_struct.dy * float(grid_struct.ny - 1) * 0.5 + grid_struct.limiti[0]
                    )
                except (TypeError, AttributeError, IndexError):
                    module_logger.exception("Coordinate del centro del grigliato non lette")
                    # manca earth radius che non so dove pescare quindi uso il try successivo che replica anche idl
            elif grid_mapping_name is not None:
                # se non è file da IDL allora lo leggo così:
                if hasattr(nc[p], "geo_dim"):
                    grid_struct.limiti = nc[p].geo_dim
                if hasattr(nc[p], "mesh_dim"):
                    grid_struct.dx = nc[p].mesh_dim[0]
                    grid_struct.dy = nc[p].mesh_dim[1]
                if hasattr(nc[p], "mesh_dim_units"):
                    grid_struct.units_dx = nc[p].mesh_dim_units[0]
                    grid_struct.units_dy = nc[p].mesh_dim_units[1]
                try:
                    proj_struct.center_longitude = (
                        grid_struct.dx * float(grid_struct.nx - 1) * 0.5 + grid_struct.limiti[1]
                    )
                    proj_struct.center_latitude = (
                        grid_struct.dy * float(grid_struct.ny - 1) * 0.5 + grid_struct.limiti[0]
                    )
                except Exception:
                    module_logger.exception(
                        "Non ho trovato mesh_dim e geo_dim come attributi della grid_mapping_variable,\nNon calcolo center_longitude e center_latitude."
                    )
            else:
                # quando grid_mapping_name è None, il netcdf non è convenzionale e aggiungo tutto
                # quello che è contenuto nella variabile S1 di proiezione come attributi
                # dell'istanza di pyproj, con il try successivo.
                pass
            try:  # aggiungo il resto come extra params per replicare idl
                for att_p in nc[p].ncattrs():
                    if att_p not in list(proj_struct.__dict__.keys()) + ["mesh_dim", "geo_dim", "mesh_dim_units"]:
                        setattr(proj_struct, att_p, nc[p].getncattr(att_p))
            except (TypeError, AttributeError, IndexError):
                pass

            if n_stringvar > 1:
                strvar_campi[p] = proj_struct

    else:
        n_stringvar = 0

    """ __________________________________struttura PRODUCT__________________________________ """

    struct_product = StructProduct()

    try:
        struct_product.name = nc.getncattr("MapType")
    except AttributeError:
        module_logger.exception("Lettura tipo di prodotto fallita")

    """ __________________________________struttura SOURCE__________________________________ """

    struct_source = StructSource()

    try:
        if hasattr(nc, "source"):
            struct_source.name_source = nc.source
        elif hasattr(nc, "Source"):
            struct_source.name_source = nc.Source
        elif hasattr(nc, "RADARS_NAME"):
            struct_source.name_source = nc.RADARS_NAME
        else:
            pass
    except AttributeError:
        module_logger.exception("Lettura source non possibile")

    nc.close()

    """ ___________________________________macrostruttura finale_________________________________________ """

    macro = {"TIME": time_struct, "GRID": grid_struct, "SOURCE": struct_source, "PRODUCT": struct_product}
    # dati_out: Dict[str, npt.NDArray[np.float32]] | npt.NDArray[np.float32] = np.empty(shape=(0), dtype=np.float32)
    dati_out: Union[Dict[str, np.ndarray], np.ndarray] = np.empty(shape=(0), dtype=np.float32)

    # aggiungo sottostruttura/e VARIABILE
    if n_campi > 0:

        if n_campi == 1:
            macro["VARIABILE"] = campi["VARIABILE"]
            dati_out = campi_data["VARIABILE"]
        else:
            for key, val in campi.items():
                macro[f"VARIABILE_{key}"] = val
            dati_out = campi_data
    else:
        module_logger.warning(f"N_campi = {n_campi}")

    # aggiungo sottostruttura/e COORDS
    if n_typecoords_x > 0:
        for type_coord, xcoords in campi_x.items():
            macro[type_coord] = xcoords

    if n_typecoords_y > 0:
        for type_coord, ycoords in campi_y.items():
            macro[type_coord] = ycoords

    # aggiungo sottostruttura/e di tipo str
    if n_stringvar > 0:
        if n_stringvar == 1:
            macro["PROJECTION"] = proj_struct
        else:
            for key_, val_ in strvar_campi.items():
                macro[key_] = val_

    return macro, dati_out
