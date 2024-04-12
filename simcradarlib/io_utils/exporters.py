from netCDF4 import Dataset
import netCDF4
import numpy as np
from datetime import datetime, timedelta
import h5py
from cftime import date2num
from simcradarlib.io_utils.structure_class import StructVariable, StructProjection
from typing import Optional


class ExportableVar(StructVariable):

    """
    Classe figlia di StructVariable, definita in simcradarlib.io_utils.structure_class, che implementa
    un campo fisico georeferenziato 2D o ND per N>2 (forecast), esportabile in formato netCDF o ODIM OPERA.
    NB: Questa classe permette l'export in ODIM soltanto per campi 2D, mentre per campi 3D usare il
    modulo simcradarlib.odim .
    Si riportano gli attributi dell'istanza:
    -name                   --str    (default=None)  : nome della variabile.
    -long_name              --str    (default=None)  : nome esteso della variabile.
    -standard_name          --str    (default=None)  : nome standard della variabile, netCDF compliant.
    -units                  --str    (default=None)  : unità fisiche della variabile letta.
    -min_val                --float  (default=None)  : valore minimo variabile.
    -max_val                --float  (default=None)  : valore massimo variabile.
    -missing                --float  (default=None)  : valore degli out of range/dato mancante.
    -undetect               --float  (default=None)  : valore sottosoglia, assegnato ai punti in cui il valore
                                                       rilevato<min_val.
    attributi opzionali per la scrittura del campo in formato ODIM OPERA v.2.1:
    -dset_order             --int    (default=1)     : indice del gruppo "root/dataset<dset_order>".
                                                       Esempio: dset_order=1 per "root/dataset1"
    -data_order             --int    (default=1)     : indice del gruppo "root/dataset<dset_order>/data<data_order>".
                                                       Esempio: set_order=1, data_order=2 per
                                                                "root/dataset1/data2"
    -dset_prod_name         --str    (default="")    : valore dell'attributo 'product' del gruppo
                                                       "root/dataset<dset_order>/what".
                                                       Esempio: per il campo di SRI 2D istantaneo,
                                                       dset_prod_name='SURF'.
    -data_prod_name         --str    (default="")    : valore dell'attributo 'prod' del gruppo
                                                       "root/dataset<dset_order>/data<data_order>/what"
    -dset_qty_name          --str    (default="")    : valore dell'attributo 'quantity' del gruppo
                                                       "root/dataset<dset_order>/what".
                                                       Esempio: per il campo 2D di SRI,
                                                       dset_qty_name="RRATE".
    -data_qty_name          --str    (default="")    : valore dell'attributo 'quantity' del gruppo
                                                       "root/dataset<dset_order>/data<data_order>/what"
    -h_object               --str    (default="")    : valore dell'attributo 'object' del gruppo
                                                       "root/what".
                                                       Esempio: per il campo 2D di SRI,
                                                       h_object="COMP".
    -source                 --str    (default="")    : valore dell'attributo 'source' del gruppo
                                                       "root/what".
    """

    def __init__(
        self,
        name: Optional[str] = None,
        long_name: Optional[str] = None,
        standard_name: Optional[str] = None,
        units: Optional[str] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        missing: Optional[np.float32] = None,
        undetect: Optional[np.float32] = None,
        dset_order: int = 1,
        data_order: int = 1,
        dset_prod_name: str = "",
        data_prod_name: str = "",
        dset_qty_name: str = "",
        data_qty_name: str = "",
        h_object: str = "",
        source: str = "",
    ):

        super().__init__(name, long_name, standard_name, units, min_val, max_val, missing, undetect)
        self.dset_order = dset_order
        self.data_order = data_order
        self.dset_prod_name = dset_prod_name
        self.data_prod_name = data_prod_name
        self.dset_qty_name = dset_qty_name
        self.data_qty_name = data_qty_name
        self.h_object = h_object
        self.source = source

    def export_to_hdf_2d(self, out_filename: str, field_values: np.ndarray, mode: str, t: datetime, metadata: dict):

        """
        Metodo di istanza della classe ExportableVar, che eredita da StructVariable, figlia di StructBase.
        Scrive il campo di valori 'field_values' in un file output in formato ODIM OPERA v. 2.1
        (valid for geographical image data Groups).

        INPUT :
        - out_filename        --str        : filename di output.
        - field_values        --np.ndarray : array del campo di valori da scrivere come dataset
                                             nel file ODIM, in "root/dataset<dset_order>/data<data_order>/data"
        - mode                --str        : modalità con cui apro out_filename
                                             ('w'='scrittura, 'a'=append).
        - t                   --datetime   : oggetto datetime.datetime che contiene data e ora
                                             del campo se istantaneo o di cumulata se cumulata
                                             o della data prevista se forecast.
        - metadata            --dict       : dizionario dei metadati di pysteps.

        GERARCHIA HDF in output:
        root:
        |___dataset<dset_order> (group):
        |   |_________________ what (group):
        |   |                        +attrs:
        |   |                              -product
        |   |                              -quantity
        |   |_________________ data<data_order> (group):
        |                      |                data (dataset)
        |                      |______________________ what (group):
        |                                                    +attrs:
        |                                                          -missing
        |                                                          -product
        |                                                          -quantity
        |
        |
        |___what (group):
        |         +attrs:
        |              -date    (mandatory odim v.2.1)
        |              -time    (mandatory odim v.2.1)
        |              -version (mandatory odim v.2.1)
        |              -object  (mandatory odim v.2.1)
        |              -source  (mandatory odim v.2.1)
        |              -forecast_runs (solo se dataset<dset_order>/what.product=FORECAST
        |                              e il campo scritto come dataset da 3dimensioni)
        |___where (group):
                   +attrs:
                       -LL_lat
                       -LL_lon
                       -UR_lat
                       -UR_lon
                       -projdef
                       -xscale
                       -yscale
                       -xsize (solo se dataset<dset_order>/what.product=FORECAST)
                       -ysize (solo se dataset<dset_order>/what.product=FORECAST)

        """

        if mode == "w":
            # wrl.io.hdf.to_hdf5(
            # out_filename,
            # field_values,
            # mode=mode,
            # metadata={},
            # dataset=f"dataset{self.dset_order}/data{self.data_order}/data",
            # )

            # hf = h5py.File(out_filename, "a")
            hf = h5py.File(out_filename, "w")
            dset_shape = field_values.shape[:2]
            if field_values.shape.__len__() == 3:
                dset_shape = field_values.shape[1:3]
            hf.create_dataset(
                f"dataset{self.dset_order}/data{self.data_order}/data",
                shape=dset_shape,
                dtype=np.float32,
                data=field_values,
                compression="gzip",
            )

            g2 = hf.create_group(f"dataset{self.dset_order}/what")
            # g2.attrs.__setitem__('nodata',field.missing)
            g2.attrs.__setitem__("product", self.dset_prod_name.encode("utf-8"))
            g2.attrs.__setitem__("quantity", self.dset_qty_name.encode("utf-8"))

            g3 = hf.create_group("what")
            g3.attrs.__setitem__("date", t.strftime("%Y%m%d").encode("utf-8"))
            g3.attrs.__setitem__("time", t.strftime("%H%M%S").encode("utf-8"))
            g3.attrs.__setitem__("version", f"h5py {h5py.__version__}".encode("utf-8"))
            g3.attrs.__setitem__("object", self.h_object.encode("utf-8"))
            g3.attrs.__setitem__("source", self.source.encode("utf-8"))

            g4 = hf.create_group("where")
            g4.attrs.__setitem__("LL_lat", metadata["ll_lat"])
            g4.attrs.__setitem__("LL_lon", metadata["ll_lon"])
            g4.attrs.__setitem__("UR_lat", metadata["ur_lat"])
            g4.attrs.__setitem__("UR_lon", metadata["ur_lon"])
            g4.attrs.__setitem__("projdef", metadata["projection"].encode("utf-8"))
            g4.attrs.__setitem__("xscale", metadata["xpixelsize"])
            g4.attrs.__setitem__("yscale", metadata["ypixelsize"])

            g5 = hf.create_group(f"dataset{self.dset_order}/data{self.data_order}/what")
            g5.attrs.__setitem__("nodata", self.missing)
            g5.attrs.__setitem__("product", self.data_prod_name.encode("utf-8"))
            g5.attrs.__setitem__("quantity", self.data_qty_name.encode("utf-8"))

            # forse dovrei togliere il vincolo di FORECAST in what/product e lasciare solo la condizione sulla shape
            if (len(field_values.shape) == 3) & ("FORECAST" in g2.attrs.__getitem__("product").decode("utf-8")):
                g3.attrs.__setitem__("forecast runs", field_values.shape[0])
                g4.attrs.__setitem__("xsize", field_values.shape[2])
                g4.attrs.__setitem__("ysize", field_values.shape[1])
            elif len(field_values.shape) == 2:
                g4.attrs.__setitem__("xsize", field_values.shape[1])
                g4.attrs.__setitem__("ysize", field_values.shape[0])

            hf.close()

        elif mode == "a":

            hf = h5py.File(out_filename, "a")

            dset_shape = field_values.shape[:2]
            if field_values.shape.__len__() == 3:
                dset_shape = field_values.shape[1:3]
            hf.create_dataset(
                f"dataset{self.dset_order}/data{self.data_order}/data",
                shape=dset_shape,
                dtype=np.float32,
                data=field_values,
                compression="gzip",
            )

            g2 = hf.create_group(f"dataset{self.dset_order}/what")
            g2.attrs.__setitem__("nodata", self.missing)
            g2.attrs.__setitem__("product", self.dset_prod_name.encode("utf-8"))
            g2.attrs.__setitem__("quantity", self.dset_qty_name.encode("utf-8"))

            g5 = hf.create_group(f"dataset{self.dset_order}/data{self.data_order}/what")
            g5.attrs.__setitem__("nodata", self.missing)
            g5.attrs.__setitem__("product", self.data_prod_name.encode("utf-8"))
            g5.attrs.__setitem__("quantity", self.data_qty_name.encode("utf-8"))

            hf.close()

    def export_to_netcdf(
        self,
        out_filename: str,
        description: str,
        t: datetime,
        tcum: int,
        units0: str,
        lats: np.ndarray,
        lons: np.ndarray,
        field_values: np.ndarray,
        geo_dims: np.ndarray,
        mesh_dims: np.ndarray,
        ps: StructProjection,
        source: str,
        product_name: str,
    ) -> None:
        """
        Metodo di istanza della classe ExportableVar, che eredita da StructVariable, figlia di StructBase.
        Scrive un campo in file netCDF.

        INPUT  :
        - out_filename    --str                         : filename di output.
        - description     --str                         : descrizione di output.
        - t               --datetime                    : oggetto datetime di data&ora di validità del campo
                                                          (data realtime se dato osservato, data finale di
                                                          cumulata, data del t0 di forecast).
        - tcum            --int                         : tempo di cumulata ( 0 se campo istantaneo ).
        - units0          --int                         : unità di misura del tempo di cumulazione se cumulata
                                                          o di radar_frequency se forecast
                                                          (minuti 'minutes', ore 'hours', giorni 'days').
        - lats            --np.array                    : latitudini del grigliato.
        - lons            --np.array                    : longitudini del grigliato.
        - field           --StructVariable              : struttura con gli attributi del campo da scrivere
                                                          in output in forma di istanza della classe
                                                          simcradarlib.io_utils.structure_class.StructVariable.
        - field_values    --np.array                    : array di dati da scrivere in output.
                                                          Se è un forecast shape=(steps,ny,nx)
                                                          dove ny,nx sono i passi griglia in verticale
                                                          e orizzontale. Steps sono il numero di lead times.
        - geo_dims        --np.array                    : limiti della griglia in formato
                                                          np.array( [ ll_lat, ll_lon, ur_lat, ur_lon] ).
        - mesh_dims       --np.array                    : ampiezze orizzontale e verticale della cella del
                                                          grigliato (in km).
        - ps              --StructProjection            : istanza di classe StructProjection.

        """
        output_nc = Dataset(out_filename, "w", format="NETCDF4")
        output_nc.description = description
        # output_nc.history = "Created " + time.ctime(time.time())
        output_nc.institute = "Arpae - SIMC"
        output_nc.RADARS_NAME = source
        output_nc.MapType = product_name

        # dimensions
        if len(field_values.shape) == 3:
            output_nc.createDimension("time", field_values.shape[0])
        else:
            output_nc.createDimension("time", 1)
        output_nc.createDimension("lon", field_values.shape[-1])
        output_nc.createDimension("lat", field_values.shape[-2])
        output_nc.createDimension("geo_dim", geo_dims.shape[0])
        output_nc.createDimension("mesh_dim", mesh_dims.shape[0])

        ps_mode = "pyproj"
        if ps.projection_index is not None:
            ps_mode = "idl"
            output_nc.createDimension(ps_mode, 0)
        else:
            output_nc.createDimension("proj_string", len(ps.projection_name))

        # variables
        time = output_nc.createVariable("time", "f8", ("time",))
        lon = output_nc.createVariable("lon", "f4", ("lon",))
        lat = output_nc.createVariable("lat", "f4", ("lat",))
        field_out = output_nc.createVariable(
            self.name,
            "f8",
            (
                "time",
                "lat",
                "lon",
            ),
        )
        geo_dim = output_nc.createVariable("geo_dim", "f4", ("geo_dim",))
        mesh_dim = output_nc.createVariable("mesh_dim", "f4", ("mesh_dim",))
        if ps_mode == "pyproj":
            proiezione = output_nc.createVariable("proj_string", "S1", ("proj_string"))
            proiezione.long_name = ps.long_name
            str_out = netCDF4.stringtochar(np.array([ps.projection_name], "S{}".format(len(ps.projection_name))))
            proiezione[:] = str_out
            proiezione.projection_name = ps.projection_name
        else:
            proiezione = output_nc.createVariable(ps_mode, "S1", ps_mode)
            proiezione[:] = np.ma.masked_array(ps.projection_index)
            proiezione.projection_name = ps.projection_name
            proiezione.grid_mapping_name = ps.grid_mapping_name
            proiezione.projection_index = ps.projection_index

        time.long_name = "time"
        time.units = "{} since 1970-01-01 00:00:00".format(units0)
        time[:] = date2num(t, time.units, "standard")  # int( timedelta(**{units0: tcum}).seconds/60 ) # conta i minuti

        # per files compatibili con vecchie procedure idl tipo read_nctogrib() usare la sintassi:
        # e commentare sopra!!!
        # time.units = f"hour before {t.strftime('%Y-%m-%d %H:%M')}:0"
        # time[:] = int(timedelta(**{units0: tcum}).seconds / 3600)  # conta la porzione di ora

        lon.long_name = "longitudes"
        lon[:] = lons
        lon.setncattr("units", "degrees_east")
        lon.standard_name = "longitude"

        lat.long_name = "latitudes"
        lat[:] = lats
        lat.setncattr("units", "degrees_north")
        lat.standard_name = "latitude"

        field_out.long_name = self.long_name
        field_out.standard_name = self.standard_name
        if len(field_values.shape) == 2:
            field_out[:] = np.expand_dims(field_values, axis=0)
        elif len(field_values.shape) == 3:
            field_out[:] = field_values
        field_out.setncattr("units", self.units)
        field_out.valid_min = np.float32(self.min_val)
        field_out.valid_max = np.float32(self.max_val)
        field_out.coordinates = "lat lon"
        field_out.undetected = np.float32(self.undetect)
        # cum.undetectable = np.float32(0.)
        field_out.var_missing = np.float32(self.missing)
        field_out.accum_time_h = timedelta(**{units0: tcum}).seconds / 3600  # conta la porzione di ora

        geo_dim.long_name = "Geo limits [yLL,xLL,yUR,xUR]"
        geo_dim[:] = geo_dims
        geo_dim.setncattr("units", "degree")

        mesh_dim.long_name = "Grid Mesh Size [X_mesh_size, Y_mesh_size]"
        mesh_dim[:] = mesh_dims
        mesh_dim.setncattr("units", "degree")

        output_nc.close()
