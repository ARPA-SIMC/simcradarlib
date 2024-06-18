from simcradarlib.io_utils.structure_class import StructBase
from typing import Optional
import numpy as np
import h5py

"""
Questo modulo contiene le classi che implementano i vari oggetti di cui è costituito un file HDF ODIM OPERA v.2.1,
cioè i gruppi e i dataset.

  **********************************Breve spiegazione struttura HDF ODIM OPERA*************************************
  Un file HDF è in sintesi un file con struttura gerarchica di contenuti, organizzati su livelli dal livello root a
  quelli sottostanti. I gruppi sono oggetti aventi un'insieme di attributi relativi ai dati e possono contenere i
  dataset, che sono oggetti per storare i dati veri e propri (matrici di dati).
  Es GERARCHIA HDF:
  root                                                       (livello gerarchico più alto)
  |
  |_what     <gruppo>:
  |    |_______________ attributi <dizionario>
  |
  |_dataset1 <gruppo>:                                       (secondo livello gerarchico)
            |___________what  <gruppo>:
            |               |___________attributi <dizionario>
            |
            |___________data1 (gruppo):                      (terzo livello gerarchico)
                             |_________what <gruppo>:
                             |            |________attributi <dizionario>
                             |
                             |_________data <dataset>: contiene matrice di dati.

 Negli HDF ODIM OPERA sono solitamente presenti ad ogni livello gerarchico i 3 gruppi
 what, where, how (l'esempio sopra presenta solo what).

 Nell'implementazione di questa libreria si indica con livello gerarchico il path degli oggetti gruppi e dataset
 all'interno della struttura gerarchica del file.
 Ad esempio, nella struttura riportata sopra, l'oggetto dataset corrisponde al livello gerarchico "dataset1/data1/data",
 mentre l'oggetto gruppo dataset1 corrisponde al livello gerarchico "dataset1" e l'oggetto sottogruppo data1 del gruppo
 dataset1 corrisponde al livello gerarchico "dataset1/data1".
 ****************************************************************************************************************

Ogni classe eredita da simcradarlib.io_utils.structure_class.StructBase.
Ogni classe ha il metodo di istanza (talvolta ereditato):
 odim_create()
    per creare un oggetto gruppo o dataset in un file ODIM aperto in scrittura.
    e può avere un metodo di istanza
 odim_setattrs()
    per assegnare attributi a un gruppo o dataset di un file ODIM aperto in scrittura.
"""


class OdimDset(StructBase):

    """
    Classe che implementa un oggetto <dataset> di ODIM OPERA v.2.1 .

    Classe figlia di simcradarlib.io_utils.structure_class.StructBase
    con attributi dell'istanza:

    -data       --np.ndarray : array dei valori di dati da storare.
    -hierarchy  --str        : stringa del livello gerarchico nell'ODIM
                               (es: "dataset1/data1/data").

    _____________________________Esempio__________________________________
    Si può implementare un dataset di file ODIM OPERA, al livello gerarchico
    "dataset1/data1/data" e corrispondente a una matrice di dati np.ndarray,
    come istanza di OdimDset:

    istanza = OdimDset(data=np.ndarray,
                       hierarchy="dataset1/data1/data")
    """

    def __init__(self, data: np.ndarray, hierarchy: str):
        super().__init__()
        self.data = data
        self.hierarchy = hierarchy

    def odim_create(self, hf: h5py._hl.files.File) -> None:

        """
        Metodo di istanza della classe OdimDset, che crea nel file ODIM,
        aperto in scrittura tramite h5py.File(), un oggetto dataset
        al livello gerarchico definito dall'attributo 'hierarchy' dell'istanza
        della classe OdimDset e lo riempe con l'array dei dati storati
        nell'attributo 'data' dell'istanza della classe OdimDset.

        INPUT:
        -hf --h5py._hl.files.File : oggetto di h5py corrispondente al file ODIM
                                    aperto in scrittura.

        _____________________________Esempio__________________________________
        Si può creare un oggetto dataset al livello gerarchico
        "dataset1/data1/data" all'interno di un file ODIM OPERA aperto in
        scrittura con:

        istanza=OdimDset(data=np.ndarray, hierarchy="dataset1/data1/data")
        hf = h5py.File('nomefile.hdf','w')
        istanza.odim_create(hf)
        """

        hf.create_dataset(
            self.hierarchy,
            shape=self.data.shape,
            dtype=np.float32,
            data=self.data,
            compression="gzip",
        )


class OdimDset8bImage(OdimDset):

    """
    Classe che implementa un oggetto <dataset> di file ODIM OPERA v.2.1
    per dati 8bit unsigned (uchar) cioè Eight-bit Image.
    Può essere un qualsiasi 2D dataset (polare, cartesiano,cross-section)

    Classe figlia di simcradarlib.odim.odim_utils.OdimDset con attributi dell'istanza:

    -data           --np.array: array dei valori di dati da storare.
    -hierarchy      --str     : stringa del livello gerarchico nel file ODIM.
                                (Es: "dataset1/data1/data")
    -CLASS          --str (default='IMAGE')
    -IMAGE_VERSION  --str (default='1.2')

    _____________________________Esempio__________________________________
    Si può implementare un dataset del file ODIM a livello gerarchico
    "dataset1/data1/data" per un 2D dataset cartesiano 8bit unsigned come
    istanza della classe OdimDset8bImage:

    istanza = OdimDset8bImage(data=np.ndarray,
                              hierarchy="dataset1/data1/data")
    """

    def __init__(self, data: np.ndarray, hierarchy: str, CLASS: str = "IMAGE", IMAGE_VERSION: str = "1.2"):
        super().__init__(data, hierarchy)
        self.data = data
        self.hierarchy = hierarchy
        self.CLASS = CLASS
        self.IMAGE_VERSION = IMAGE_VERSION

    def odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list) -> None:

        """
        Metodo di istanza della classe OdimDset8bImage per assegnare una lista di
        attributi ad un dataset del file ODIM, aperto in scrittura tramite h5py.File().

        Se il file ODIM non contiene il dataset a cui voglio assegnare gli attributi,
        viene creato e poi vengono assegnati gli attributi.

        Gli attributi della lista sono assegnati all'oggetto <dataset> del file ODIM
        aperto se sono anche attributi dell'istanza di classe OdimDset8bImage che lo
        implementa, quindi è accessibile il loro valore (tali attributi sono assegnati
        all'istanza passandoli al costruttore nell'inizializzazione o tramite il metodo
        addparams perchè eredita da simcradarlib.odim.odim_utils.OdimDset quindi da
        simcradarlib.io_utils.structure_class.StructBase).

        INPUT:
        -hf  --h5py._hl.files.File : oggetto di h5py corrispondente al file ODIM
                                     aperto in scrittura.
        -attrslist          --list : lista dei nomi degli attributi da storare.

        _____________________________Esempio__________________________________
        Si possono assegnare gli attributi 'CLASS','IMAGE_VERSION' ad un dataset
        di dati cartesiani 8bit unsigned, al livello gerarchico
        "dataset1/data1/data",
        in un file ODIM OPERA aperto in scrittura con h5py con:

        istanza = OdimDset8bImage(data=np.ndarray, hierarchy="dataset1/data1/data")
        hf = h5py.File('nomefile.hdf','w')
        istanza.odim_setattrs(['CLASS','IMAGE_VERSION'])
        """

        try:
            g = hf.require_dataset(self.hierarchy, self.data.shape, np.array(self.data).dtype)
        except ValueError:
            self.odim_create(hf)
            g = hf.require_dataset(self.hierarchy, self.data.shape, np.array(self.data).dtype)
        for attr in attrslist:
            if self.struct_hasitem(attr):
                attr_val = self.struct_getitem(attr)
                if attr_val is not None:
                    if type(attr_val) == str:
                        g.attrs.__setitem__(attr, np.bytes_(self.struct_getitem(attr)))
                    else:
                        g.attrs.__setitem__(attr, self.struct_getitem(attr))


class OdimGroup(StructBase):

    """
    Classe figlia di simcradarlib.io_utils.structure_class.StructBase e
    implementa un oggetto gruppo di un file ODIM OPERA v.2.1.

    Gli attributi dell'istanza sono:

    -hierarchy  --str :  stringa del livello gerarchico nel file ODIM
                         a cui è collocato il gruppo implementato dall'istanza.
                         (Es: "dataset1/data1" o "dataset1" o "what"..)

    _____________________________Esempio__________________________________
    Si può implementare il gruppo al livello gerarchico "dataset1" di
    un file ODIM OPERA creando l'istanza di OdimGroup con:

    istanza = OdimGroup(hierarchy="dataset1")

    Nota: tutte le classi in odim.odim_utils che implementano gruppi specifici
    di un file ODIM OPERA v.2.1 sono classi figlie di OdimGroup ed ereditano i
    suoi metodi di classe e l'attributo 'hierarchy'.
    Quindi per implementare un gruppo "where", "what", "how", che hanno
    attributi diversi a seconda del prodotto e del livello gerarchico,
    usare le classi corrispondenti in odim.odim_utils, figlie di
    OdimGroup.
    """

    def __init__(
        self,
        hierarchy: str,
    ):
        super().__init__()
        self.hierarchy = hierarchy

    def odim_create(self, hf: h5py._hl.files.File):

        """
        Metodo di istanza della OdimGroup che crea nel file ODIM, aperto
        in lettura tramite h5py.File(), il gruppo al livello gerarchico
        definito dall'attributo 'hierarchy' dell'istanza della classe OdimGroup.

        INPUT:
        -hf  --h5py._hl.files.File : oggetto di h5py corrispondente al file ODIM
                                     aperto in scrittura.

        _____________________________Esempio__________________________________
        Si può creare un oggetto gruppo al livello gerarchico
        "dataset1/data1" all'interno di un file ODIM OPERA aperto in
        scrittura con:

        istanza=OdimGroup(hierarchy="dataset1/data1")
        hf = h5py.File('nomefile.hdf','w')
        istanza.odim_create(hf)
        """

        hf.create_group(self.hierarchy)

    def odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):

        """
        Metodo di istanza della classe odim.odim_utils.OdimGroup per assegnare una
        lista di attributi ad un gruppo del file ODIM, aperto in scrittura tramite
        h5py.File().

        Se il file ODIM non contiene il gruppo a cui voglio assegnare gli attributi,
        viene creato e poi vengono assegnati gli attributi.

        Gli attributi della lista sono assegnati all'oggetto <gruppo> del file ODIM
        aperto se sono anche attributi dell'istanza di classe OdimGroup che lo
        implementa, quindi è accessibile il loro valore (tali attributi sono
        assegnati all'istanza passandoli al costruttore nell'inizializzazione o tramite
        il metodo addparams perchè eredita da OdimDset quindi da
        simcradarlib.io_utils.structure_class.StructBase).

        INPUT:
        -hf  --h5py._hl.files.File : oggetto di h5py corrispondente al file ODIM
                                     aperto in scrittura.
        -attrslist          --list : lista dei nomi degli attributi da storare.

        ________________________________Esempio____________________________________
        Si possono assegnare gli attributi 'lon','lat' ad un gruppo al livello
        gerarchico "where", in un file ODIM OPERA aperto in scrittura con h5py,
        con:

        istanza = OdimGroup(hierarchy="where")
        istanza.addparams(['lon','lat'],[8.5,44.5])
        hf = h5py.File('nomefile.hdf','w')
        istanza.odim_setattrs(['lon','lat'])

        Nota: Per implementare il gruppo "where" al livello gerarchico root di
        un file ODIM OPERA v.2.1 si usi la classe odim.odim_utils.OdimWhere,
        figlia di OdimGroup. Quindi odim.odim_utils.OdimWhere eredita i metodi
        di classe di OdimGroup, ma presenta attributi dell'istanza corrispondenti
        agli attributi previsti per il gruppo root "where" di file ODIM OPERA v.2.1.
        """
        try:
            g = hf.require_group(self.hierarchy)
        except ValueError:
            self.odim_create(hf)
        for attr in attrslist:
            if self.struct_hasitem(attr):
                attr_val = self.struct_getitem(attr)
                if attr_val is not None:
                    if type(attr_val) == str:
                        g.attrs.__setitem__(attr, np.bytes_(self.struct_getitem(attr)))
                    else:
                        g.attrs.__setitem__(attr, self.struct_getitem(attr))


class OdimWhat(OdimGroup):

    """
    Classe che implementa il gruppo "what" a livello gerarchico del root
    di un ODIM OPERA v. 2.1 .

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:

    -obj                   --str  : tabella2 del manuale
                                    (es: PVOL,SCAN)
    -version               --str  : versione odim <H5rad M.m>
                                    (M=major version
                                     m=minor version)
    -date                  --str  : YYYYMMDD
    -time                  --str  : HHmmss (in UTC)
    -source                --str (default=None)  :
                                    <TYP:VALUE>|[<TYP:VALUE>]
                                    rif. Tabella3 manuale. Esempi:
                                    SPC: 'WMO:16144,RAD:IY46,PLC:itspc'
                                    GAT: 'RAD:IYai,PLC:itgat,NOD:itgat'

    OdimWhat eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo "what" nel file HDF aperto da h5py.
    odim_setattrs__(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a "what" gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.

    _____________________________Esempio__________________________________
    Si può implementare il gruppo "what" al livello gerarchico del root di
    un file ODIM OPERA di un volume polare acquisito alle 10:35 il 22/09/2022
    dal radar di SPC, creando l'istanza di OdimWhat:

    istanza = OdimWhat(hierarchy='what',
                        obj='PVOL',
                        version='H5rad 2.1',
                        date='20200922',
                        time='103500',
                        source='WMO:16144,RAD:IY46,PLC:itspc,NOD:itspc'
                        )
    """

    def __init__(
        self,
        hierarchy: str,
        obj: Optional[str],
        version: Optional[str],
        date: Optional[str],
        time: Optional[str],
        source: Optional[str] = None,
    ):

        super().__init__(hierarchy)
        self.object = obj
        self.version = version
        self.date = date
        self.time = time
        self.source = source


class OdimWherePolar(OdimGroup):

    """
    Classe che implementa il gruppo "where" del root di un ODIM OPERA v. 2.1
    per dato polare cioè
    vol['what'].attrs['object']='PVOL' o 'SCAN'.

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:

    -lon                   --float: radar antenna longitude(degrees).
    -lat                   --float: radar antenna latitude(degrees).
    -height                --float: height center radar antenna (meters)
                                    above sea level.

    OdimWherePolar eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo "where" nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a "where" gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.

    _____________________________Esempio__________________________________
    Si può implementare il gruppo "where" al livello gerarchico del root di
    un file ODIM OPERA di un volume polare acquisito dal radar di SPC,
    creando l'istanza di OdimWherePolar:

    istanza_root_where=OdimWherePolar(  hierarchy="where",
                                        lon=11.623600006103516,
                                        lat=44.654701232910156,
                                        height=31.0
                                      )
    """

    def __init__(self, hierarchy: str, lon: float, lat: float, height: float):

        super().__init__(hierarchy)
        self.lon = lon
        self.lat = lat
        self.height = height


class OdimWherePolarDset(OdimGroup):

    """
    Classe che implementa il sottogruppo "where" di un gruppo "dataset<n>" di file
    ODIM OPERA v. 2.1 per dato polare, cioè vol['what'].attrs['object']='PVOL' o 'SCAN'.
    Quindi il gruppo al livello gerarchico "dataset<n>" corrisponde all' elevazione
    <n>-esima del volume polare acquisito e il suo sottogruppo "where" contiene nei
    suoi attributi le informazioni geografiche per i dati all'elevazione <n>-esima.

    In un file ODIM per volume polare, posso usare questa classe per implementare
    il gruppo al livello "dataset1/where" che contiene le informazioni geografiche per
    la prima elevazione, "dataset2/where" per la seconda elevazione, inizializzando
    l'istanza con i corretti valori per gli attributi del gruppo "where" del
    gruppo "dataset<n>" di un ODIM di volume polare, corrispondente all'elevazione
    <n>-esima.

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:

    -elangle               --float: Antenna elevation angle (degrees) above the horizon.
    -nbins                 --int: Number of range bins in each ray.
    -rstart                --float: range (km) of the start of the first range bin.
    -rscale                --float: distance (meters) between two successive range bins.
    -nrays                 --int: Number of azimuth gates (rays) in the object.
    -a1gate                --int: Index of the first azimuth gate radiated in the scan.

    OdimWherePolarDset eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo "dataset<n>/where" nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a "dataset<n>/where" gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.

    _____________________________Esempio__________________________________
    Si può implementare il gruppo "dataset1/where" con le informazioni geografiche
    del PPI alla prima elevazione di un volume polare acquisito dal radar di SPC,
    creando l'istanza di OdimWherePolarDset:

    dset1_where=OdimWherePolarDset(hierarchy="dataset1/where",
                                   elangle=0.5,
                                   nbins=849,
                                   rstart=0.0,
                                   rscale=250.0,
                                   nrays=400,
                                   a1gate=259
                                   )

    """

    def __init__(
        self,
        hierarchy: str,
        elangle: Optional[float] = None,
        nbins: Optional[int] = None,
        rstart: Optional[float] = None,
        rscale: Optional[float] = None,
        nrays: Optional[int] = None,
        a1gate: Optional[int] = None,
    ):

        super().__init__(hierarchy)
        self.elangle = elangle
        self.nbins = nbins
        self.rstart = rstart
        self.rscale = rscale
        self.nrays = nrays
        self.a1gate = a1gate


class OdimWhereSector(OdimGroup):

    """
    Classe che implementa il gruppo "where" di settore di volume (ODIM OPERA v. 2.1)
    per dato polare cioè vol['what'].attrs['object']='PVOL' o 'SCAN'.

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:
    -startaz               --float: The azimuth angle of the start of the first gate in the sector (degrees)
    -stopaz                --float: The azimuth angle of the end of the last gate in the sector (degrees)

    OdimWhereSector eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.
    """

    def __init__(self, hierarchy: str, startaz: Optional[float], stopaz: Optional[float]):
        super().__init__(hierarchy)
        self.startaz = startaz
        self.stopaz = stopaz


class OdimWhereGeoimage(OdimGroup):

    """
    Classe che implementa il gruppo "where" a livello gerarchico del root
    di un file ODIM OPERA v. 2.1 per dati di mappa geografica
    (geographical image data) cioè vol['what'].attrs['object']='IMAGE'.

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:
    -projdef               --str: projection string according PROJ.4
    -xsize                 --int: Number of pixels in the X dimension
    -ysize                 --int: Number of pixels in the Y dimension
    -xscale                --float: pixelsize in the X dimension in projection-specific coordinates
    -yscale                --float: pixelsize in the Y dimension in projection-specific coordinates
    -LL_lon                --float: Longitude of the lower left pixel corner
    -LL_lat                --float: Latitude of the lower left pixel corner
    -UL_lon                --float: Longitude of the upper left pixel corner
    -UL_lat                --float: Latitude of the upper left pixel corner
    -UR_lon                --float: Longitude of the upper right pixel corner
    -UR_lat                --float: Latitude of the upper right pixel corner
    -LR_lon                --float: Longitude of the lower right pixel corner
    -LR_lat                --float: Latitude of the lower right pixel corner

    OdimWhereGeoimage eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.

    _____________________________Esempio__________________________________
    Si può implementare il gruppo "where" con le informazioni geografiche
    della mappa cartesiana di dati di POH sull'Emilia-Romagna, creando
    l'istanza di OdimWhereGeoimage:

    root_where_image=OdimWhereGeoimage(  hierarchy="where",
                                         projdef="+proj=aeqd +lat_0=44.6547N \
                                                  +lon_0=11.6236E +units=m +datum=WGS84",
                                         xsize=400,
                                         ysize=400,
                                         xscale=1000.0,
                                         yscale=1000.0,
                                         LL_lon =9.177717208862305,
                                         LL_lat =42.827919006347656,
                                         UL_lon =9.021688461303711,
                                         UL_lat =46.425174713134766,
                                         UR_lon =14.22551155090332,
                                         UR_lat =46.425174713134766,
                                         LR_lon =14.069482803344727,
                                         LR_lat =42.827919006347656
                                       )

    """

    def __init__(
        self,
        hierarchy: str,
        projdef: Optional[str] = None,
        xsize: Optional[int] = None,
        ysize: Optional[int] = None,
        xscale: Optional[float] = None,
        yscale: Optional[float] = None,
        LL_lon: Optional[float] = None,
        LL_lat: Optional[float] = None,
        UL_lon: Optional[float] = None,
        UL_lat: Optional[float] = None,
        UR_lon: Optional[float] = None,
        UR_lat: Optional[float] = None,
        LR_lon: Optional[float] = None,
        LR_lat: Optional[float] = None,
    ):
        super().__init__(hierarchy)
        self.projdef = projdef
        self.xsize = xsize
        self.ysize = ysize
        self.xscale = xscale
        self.yscale = yscale
        self.LL_lon = LL_lon
        self.LL_lat = LL_lat
        self.UL_lon = UL_lon
        self.UL_lat = UL_lat
        self.UR_lon = UR_lon
        self.UR_lat = UR_lat
        self.LR_lon = LR_lon
        self.LR_lat = LR_lat


class OdimWhereCross(OdimGroup):
    """
    Classe che implementa il gruppo "where" a livello gerarchico del root
    di un file ODIM OPERA v. 2.1 per dati di cross section/RHI per cui
    vol['what'].attrs['object']='XSEC' (2-D vertical cross section(s)).

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:

    -xsize                 --int: Number of pixels in the X dimension
    -ysize                 --int: Number of pixels in the Y dimension
    -xscale                --float: pixelsize in the X dimension in projection-specific coordinates
    -yscale                --float: pixelsize in the Y dimension in projection-specific coordinates
    -minheight             --float: Minimum height in meters above mean sea level
    -maxheight             --float: Maximum height in meters above mean sea level

    OdimWhereCross eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.
    """

    def __init__(
        self, hierarchy: str, xsize: int, ysize: int, xscale: float, yscale: float, minheight: float, maxheight: float
    ):
        super().__init__(hierarchy)
        self.xsize = xsize
        self.ysize = ysize
        self.xscale = xscale
        self.yscale = yscale
        self.minheight = minheight
        self.maxheight = maxheight


class OdimWhereCrossSection(OdimWhereCross):  # verifica se davvero così
    """
    Classe che implementa il gruppo 'where' del root di un ODIM OPERA v. 2.1
    per dati di cross section tali che vol['what'].attrs['object']='XSEC'
    (2-D vertical cross section(s)).

    Classe figlia di simcradarlib.odim.odim_utils.OdimWhereCross con attributi dell'istanza:

    -xsize                 --int: Number of pixels in the X dimension
    -ysize                 --int: Number of pixels in the Y dimension
    -xscale                --float: pixelsize in the X dimension in projection-specific coordinates
    -yscale                --float: pixelsize in the Y dimension in projection-specific coordinates
    -minheight             --float: Minimum height in meters above mean sea level
    -maxheight             --float: Maximum height in meters above mean sea level

    e attributi cross section specific:

    -start_lon             --float: Start position’s longitude
    -start_lat             --float: Start position’s latitude
    -stop_lon              --float: Stop position’s longitude
    -stop_lat              --float: Stop position’s latitude

    OdimWhereCrossSection eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.
    """

    def __init__(
        self,
        hierarchy: str,
        xsize: int,
        ysize: int,
        xscale: float,
        yscale: float,
        minheight: float,
        maxheight: float,
        start_lon: float,
        start_lat: float,
        stop_lon: float,
        stop_lat: float,
    ):
        super().__init__(hierarchy, xsize, ysize, xscale, yscale, minheight, maxheight)
        self.start_lon = start_lon
        self.start_lat = start_lat
        self.stop_lon = stop_lon
        self.stop_lat = stop_lat


class OdimWhereRhi(OdimWhereCross):

    """
    Classe che implementa il gruppo 'where' del root di un file ODIM OPERA v. 2.1
    per dati di RHI per cui vol['what'].attrs['object']='XSEC'(2-D vertical cross section(s)).

    Classe figlia di simcradarlib.odim.odim_utils.OdimWhereCross con attributi dell'istanza:

    -xsize                 --int: Number of pixels in the X dimension
    -ysize                 --int: Number of pixels in the Y dimension
    -xscale                --float: pixelsize in the X dimension in projection-specific coordinates
    -yscale                --float: pixelsize in the Y dimension in projection-specific coordinates
    -minheight             --float: Minimum height in meters above mean sea level
    -maxheight             --float: Maximum height in meters above mean sea level

    e attributi RHI specific:

    -lon                   --float: Radar Antenna Longitude (degrees)
    -lat                   --float: Radar Antenna Latitude (degrees)
    -az_angle              --float: Azimuth angle
    -angles                --np.array: Elevation angles, in degrees, in the order of acquisition.
    -Range                 --float: Maximum range in km

    OdimWhereRhi eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.
    """

    def __init__(
        self,
        hierarchy: str,
        xsize: int,
        ysize: int,
        xscale: float,
        yscale: float,
        minheight: float,
        maxheight: float,
        lon: float,
        lat: float,
        az_angle: float,
        angles: np.array,
        Range: float,
    ):
        super().__init__(hierarchy, xsize, ysize, xscale, yscale, minheight, maxheight)
        self.lon = lon
        self.lat = lat
        self.az_angle = az_angle
        self.angles = angles
        self.range = Range


class OdimWhereVertProfile(OdimWherePolar):

    """
    Classe che implementa il gruppo "where" a livello gerarchico del
    root di un ODIM OPERA v. 2.1 per profili verticali
    (vol['what'].attrs['object']='VP').

    Classe figlia di simcradarlib.odim.odim_utils.OdimWherePolar con attributi dell'istanza:

    -lon                   --float: radar antenna longitude(degrees).
    -lat                   --float: radar antenna latitude(degrees).
    -height                --float: height center radar antenna (meters)
                                    above sea level.

    OdimWhereVertProfile eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.
    """

    def __init__(
        self,
        hierarchy: str,
        lon: float,
        lat: float,
        height: float,
        levels: int,
        interval: float,
        minheight: float,
        maxheight: float,
    ):

        super().__init__(hierarchy, lon, lat, height)
        self.levels = levels
        self.interval = interval
        self.minheight = minheight
        self.maxheight = maxheight


class OdimHow(OdimGroup):

    """
    Classe che implementa il gruppo "how" a livello gerarchico del root
    di un file ODIM OPERA v. 2.1 per qualsiasi object.

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:

    -task                --float (default=None): Name of the acquisition task or product generator
    -startepochs         --int (default=None): Seconds after a standard 1970 epoch for which the
                                                 starting time of the data/product is valid.
    -endepochs           --int (default=None): Seconds after a standard 1970 epoch for which the
                                                 ending time of the data/product is valid.
    -system              --str (default=None): Tabella10 manuale
    -software            --str (default=None): Tabella11 manuale
    -sw_version          --str (default=None): Software version in string format,es:“5.1” or “8.11.6.2”
    -zr_a                --float (default=None): Z-R constant A in Z = A R^b
    -zr_b                --float (default=None): Z-R exponent b in Z = A R^b
    -kr_a                --float (default=None): Kdp -R constant A in R = A Kdp^b
    -kr_b                --float (default=None): Kdp -R exponent b in R = A Kdp^b
    -simulated           --str (default=None): “True” if data are simulated, otherwise “False”

    OdimHow eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.

    _____________________________Esempio__________________________________
    Si può implementare il gruppo "how" del root con le informazioni sulle modalità
    di acquisizione dati di file ODIM OPERA v.2.1, creando l'istanza di OdimHow;
    in particolare nell'esempio di volume polare acquisito da SPC alle 10:35 del
    20/09/2022 si ha:

    root_how = OdimHow( hierarchy="how",
                        task='Scan-2_CCW',
                        startepochs=1600770913,
                        endepochs=1600771174,
                        system='ELDES-GPM500CMOD',
                        software='METRANET2/mse2hdf',
                        sw_version='2.2.0.13-ppa_03',
                        simulated="False"
                      )
    """

    def __init__(
        self,
        hierarchy: str,
        task: Optional[str] = None,
        startepochs: Optional[float] = None,
        endepochs: Optional[float] = None,
        system: Optional[str] = None,
        software: Optional[str] = None,
        sw_version: Optional[str] = None,
        zr_a: Optional[float] = None,
        zr_b: Optional[float] = None,
        kr_a: Optional[float] = None,
        kr_b: Optional[float] = None,
        simulated: Optional[str] = None,
    ):

        super().__init__(hierarchy)
        self.task = task
        self.startepochs = startepochs
        self.endepochs = endepochs
        self.system = system
        self.software = software
        self.sw_version = sw_version
        self.zr_a = zr_a
        self.zr_b = zr_b
        self.kr_a = kr_a
        self.kr_b = kr_b
        self.simulated = simulated


class OdimHowRadarDset(OdimGroup):

    """
    Classe che implementa il sottogruppo "how" di gruppo "dataset<n>" di ODIM OPERA v.2.1
    di un dato polare, con specifiche per dati radar per l'elevazione <n>-esima.
    (Es: implementa gruppo "dataset1/how" se inizializzo l'istanza con le
         specifiche radar del gruppo "how" per la prima elevazione del volume
         radar acquisito.)

    Nei volumi polari il gruppo how corrispondente ad un'elevazione contiene
    sia gli attributi di un'istanza di questa classe che quelli di un'istanza
    della classe simcradarlib.odim.odim_utils.OdimHowPolarDset.

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:
    - beamwidth   --Optional[float] = None    : The radar’s half-power beamwidth (degrees)
    - wavelength  --Optional[float] = None    : Wavelength in cm
    - rpm         --Optional[float] = None    : Antenna speed in revolutions per minute,
                                                positive for clockwise scanning, negative
                                                for counter-clockwise scanning
    - pulsewidth  --Optional[float] = None    : Pulsewidth in µs
    - RXbandwidth --Optional[float] = None    : Bandwidth (MHz) that the receiver is set to
                                                when operating the radar with the above mentioned
                                                pulsewidth
    - lowprf      --Optional[float] = None    : Low pulse repetition frequency in Hz
    - highprf     --Optional[float] = None    : High pulse repetition frequency in Hz
    - TXloss      --Optional[float] = None    : Total loss in dB in the transmission chain, defined
                                                as the losses that occur between the signal generator
                                                and the feed horn
    - RXloss      --Optional[float] = None    : Total loss in dB in the receiving chain, defined as
                                                the losses that occur between the feed and the receiver
    - radomeloss  --Optional[float] = None    : One-way dry radome loss in dB
    - antgain     --Optional[float] = None    : Antenna gain in dB
    - beamwH      --Optional[float] = None    : Horizontal half-power (-3 dB) beamwidth in degrees
                                                (if horizontal and vertical beamwidths are different)
    - beamwV      --Optional[float] = None    : Vertical half-power (-3 dB) beamwidth in degrees
                                                (if horizontal and vertical beamwidths are different)
    - gasattn     --Optional[float] = None    : Gaseous specific attenuation in dB/km assumed by the radar
                                                processor (zero if no gaseous attenuation is assumed)
    - radconstH   --Optional[float] = None    : Radar constant in dB for the horizontal channel
                                                (Appendix A, OPERA-ODIM_H5-v2.1.pdf)
    - radconstV   --Optional[float] = None    : Radar constant in dB for the vertical channel.
                                                (Appendix A, OPERA-ODIM_H5-v2.1.pdf)
    - nomTXpower  --Optional[float] = None    : Nominal transmitted peak power in kW
    - TXpower     --Optional[np.array] = None : Transmitted peak power in kW. The values given are average powers
                                                over all transmitted pulses in each azimuth gate. The number of
                                                values in this array corresponds with the value of "where/nrays"
                                                for that dataset.
    - NI          --Optional[float] = None    : Unambiguous velocity (Nyquist) interval (±m/s)
    - Vsamples    --Optional[float] = None    : Number of samples used for radial velocity measurements

    OdimHowRadarDset eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.

    _____________________________Esempio__________________________________
    Si può implementare il gruppo "dataset1/how" con le informazioni sulle modalità
    di acquisizione dati alla prima elevazione di un volume polare acquisito da SPC alle
    10:35 del 20/09/2022, creando l'istanza di OdimHowRadarDset:

    d1_how_radar = OdimHowRadarDset(    hierarchy="dataset1/how",
                                        beamwidth=0.9,
                                        wavelength=5.357142925262451,
                                        rpm=-1.6657347930235655,
                                        pulsewidth=0.5,
                                        RXbandwidth=2.0,
                                        lowprf=702,
                                        highprf=702,
                                        TXloss=2.72,
                                        RXloss=3.74,
                                        radomeloss=None,
                                        antgain=46.0,
                                        beamwH=0.9,
                                        beamwV=0.9,
                                        gasattn=0.017,
                                        radconstH=None, radconstV=None,
                                        nomTXpower=280.0,
                                        NI=18.80357166767120,
                                        Vsamples=50
                                    )
    """

    def __init__(
        self,
        hierarchy: str,
        beamwidth: Optional[float] = None,
        wavelength: Optional[float] = None,
        rpm: Optional[float] = None,
        pulsewidth: Optional[float] = None,
        RXbandwidth: Optional[float] = None,
        lowprf: Optional[float] = None,
        highprf: Optional[float] = None,
        TXloss: Optional[float] = None,
        RXloss: Optional[float] = None,
        radomeloss: Optional[float] = None,
        antgain: Optional[float] = None,
        beamwH: Optional[float] = None,
        beamwV: Optional[float] = None,
        gasattn: Optional[float] = None,
        radconstH: Optional[float] = None,
        radconstV: Optional[float] = None,
        nomTXpower: Optional[float] = None,
        TXpower: Optional[np.array] = None,
        NI: Optional[float] = None,
        Vsamples: Optional[float] = None,
    ):

        super().__init__(hierarchy)
        self.beamwidth = beamwidth
        self.wavelength = wavelength
        self.rpm = rpm
        self.pulsewidth = pulsewidth
        self.RXbandwidth = RXbandwidth
        self.lowprf = lowprf
        self.highprf = highprf
        self.TXloss = TXloss
        self.RXloss = RXloss
        self.radomeloss = radomeloss
        self.antgain = antgain
        self.beamwH = beamwH
        self.beamwV = beamwV
        self.gasattn = gasattn
        self.radconstH = radconstH
        self.radconstV = radconstV
        self.nomTXpower = nomTXpower
        self.TXpower = TXpower
        self.NI = NI
        self.Vsamples = Vsamples


class OdimHowPolarDset(OdimGroup):

    """
    Classe che implementa il sottogruppo "how" di un gruppo "dataset<n>" con specifiche polari
    per l'elevazione <n>-esima, per un file ODIM OPERA v.2.1, di un dato polare, cioè
    vol['what'].attrs['object']='PVOL' o 'SCAN'.
    (Es: implementa gruppo "dataset1/how" se inizializzo l'istanza con le
         specifiche polari del gruppo "how" per la prima elevazione del volume
         radar acquisito.)

    Nei volumi radar il gruppo "how" contiene sia gli attributi
    di classe simcradarlib.odim.odim_utils.OdimHowRadarDset sia gli attributi di questa
    classe, i cui valori però sono array tranne per 'azmethod' e 'binmethod'.

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:

    -hierarchy: str,
    -azmethod    --Optional[str] = None      : How raw data in azimuth are processed, see
                                               Table 12 of OPERA-ODIM_H5-v2.1.pdf.
    -binmethod   --Optional[str] = None      : How raw data in range are processed, see
                                               Table 12 of OPERA-ODIM_H5-v2.1.pdf.
    -elangles    --Optional[np.array] = None : Elevation angles (degrees above the horizon).
                                               The number of values in this array corresponds
                                               with the value of where/nrays for that dataset.
    -startazA    --Optional[np.array] = None : Azimuthal start angles (degrees) used for each
                                               azimuth gate in a scan. The number of values in
                                               this array corresponds with the value of
                                               "where/nrays" for that dataset.
    -stopazA     --Optional[np.array] = None : Azimuthal stop angles (degrees) used for each
                                               azimuth gate in a scan. The number of values in
                                               this array corresponds with the value of
                                               "where/nrays" for that dataset.
    -startazT    --Optional[np.array] = None : Acquisition start times for each azimuth gate in
                                               the sector or scan, in seconds past the 1970 epoch.
                                               The number of values in this array corresponds
                                               with the value of "where/nrays" for that dataset.
    -stopazT     --Optional[np.array] = None : Acquisition stop times for each azimuth gate in the
                                               sector or scan, in seconds past the 1970 epoch.
                                               The number of values in this array corresponds
                                               with the value of "where/nrays" for that dataset.

    OdimHowPolarDset eredita i metodi di classe di simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.

    ____________________________________Esempio_______________________________________
    Si può implementare il gruppo "dataset1/how" con le informazioni polari
    sulle modalità di acquisizione dati alla prima elevazione di un volume polare
    acquisito da SPC alle 10:35 del 20/09/2022, creando l'istanza di OdimHowPolarDset:

    d1_how_polar = OdimHowPolarDset(    hierarchy="dataset1/how",
                                        azmethod=None,
                                        binmethod=None,
                                        elangles=np.ndarray,
                                        startazA=np.ndarray,
                                        stopazA=np.ndarray,
                                        startazT=np.ndarray,
                                        stopazT=np.ndarray
                                    )
    con np.ndarray.shape=(nrays,) per tutti gli array passati sopra.
    """

    def __init__(
        self,
        hierarchy: str,
        azmethod: Optional[str] = None,
        binmethod: Optional[str] = None,
        elangles: Optional[np.array] = None,
        startazA: Optional[np.array] = None,
        stopazA: Optional[np.array] = None,
        startazT: Optional[np.array] = None,
        stopazT: Optional[np.array] = None,
    ):

        super().__init__(hierarchy)
        self.azmethod = azmethod
        self.binmethod = binmethod
        self.elangles = elangles
        self.startazA = startazA
        self.stopazA = stopazA
        self.startazT = startazT
        self.stopazT = stopazT


class OdimHowCartesianImageDset(OdimGroup):

    """
    Classe che implementa il sottogruppo "how" di un gruppo "dataset" di un file
    ODIM OPERA v.2.1, con le specifiche per mappe cartesiane 2D e Compositi cartesiani 2D
    ( cioè vol['what'].attrs['object']='IMAGE' o vol['what'].attrs['object']='COMP').

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:

    -angles         --Optional[np.array] = None   : Elevation angles in ascending order,
                                                    used to generate the product.
    -arotation      --Optional[np.array] = None   : Antenna rotation speed. The shape of this
                                                    array is ("dataset<n>/how/elangles",).
    -camethod       --Optional[str] = None        : How cartesian data are processed,
                                                    see Table 12 of OPERA-ODIM_H5-v2.1.pdf.
    -nodes          --Optional[list] = None       : Radar nodes (Table 9, OPERA-ODIM_H5-v2.1.pdf).
    -ACCnum         --Optional[int] = None        : Number of images used in precipitation
                                                    accumulation.

    OdimHowCartesianImageDset eredita i metodi di classe di
    simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.
    """

    def __init__(
        self,
        hierarchy: str,
        angles: Optional[np.array] = None,
        arotation: Optional[np.array] = None,
        camethod: Optional[str] = None,
        nodes: Optional[list] = None,
        ACCnum: Optional[int] = None,
    ):

        super().__init__(hierarchy)
        self.angles = angles
        self.arotation = arotation
        self.camethod = camethod
        self.nodes = nodes
        self.ACCnum = ACCnum


class OdimHowVertProfileDset(OdimGroup):
    """
    Classe che implementa il sottogruppo "how" di un gruppo "dataset" di
    ODIM OPERA v. 2.1 per profili verticali, aventi
    vol['what'].attrs['object']='VP'.

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:

    -hierarchy: str,
    -minrange    --Optional[float] = None  : Minimum range at which data is
                                             used when generating profile (km)
    -maxrange    --Optional[float] = None  : Maximum range at which data is
                                             used when generating profile (km)
    -dealiased   --Optional[bool] = None   : “True” if data has been dealiased,
                                             “False” if not

    OdimHowVertProfileDset eredita i metodi di classe di
    simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.
    """

    def __init__(
        self,
        hierarchy: str,
        minrange: Optional[float] = None,
        maxrange: Optional[float] = None,
        dealiased: Optional[bool] = None,
    ):

        super().__init__(hierarchy)
        self.minrange = minrange
        self.maxrange = maxrange
        self.dealiased = dealiased


class OdimWhatDset(OdimGroup):
    """
    Classe che implementa il sottogruppo "what" in un gruppo
    di un file ODIM OPERA v. 2.1 di volume polare
    al livello gerarchico "dataset<n>/data<m>/what",
    quindi corrispondente alle informazioni sulla grandezza
    radar <m>-esima, storata durante la scansione alla
    elevazione <n>-esima del volume polare.

    Classe figlia di simcradarlib.odim.odim_utils.OdimGroup con attributi dell'istanza:

    -product            --str (default=None): Table14 OPERA-ODIM_H5-v2.1.pdf
    -prodpar            --str (default=None): Table15 (solo per prodotti cartesiani)
    -quantity           --str (default=None): Table16 OPERA-ODIM_H5-v2.1.pdf
    -startdate          --str (default=None): [Starting YYYYMMDD]
    -starttime          --str (default=None): [Starting HHmmss]
    -enddate            --str (default=None): [Ending YYYYMMDD]
    -endtime            --str (default=None): [Ending HHmmss]
    -gain               --float (default=1.0): Coefficient ’a’ in y=ax+b used to convert to unit
    -offset             --float (default=0.0): Coefficient ’b’ in y=ax+b used to convert to unit
    -nodata             --float (default=None):Raw value used to denote areas void of data
    -undetect           --float (default=None):Raw value used to denote areas below
                                               the measurement detection threshold

    OdimWhatDset eredita i metodi di classe di
    simcradarlib.odim.odim_utils.OdimGroup:
    .odim_create(self, hf: h5py._hl.files.File):
        crea il gruppo nel file hdf aperto da h5py.
    .odim_setattrs(self, hf: h5py._hl.files.File, attrslist: list):
        assegna a al gruppo gli attributi della lista attrslist se presenti
        tra gli attributi dell'istanza.

    _____________________________Esempio__________________________________
    Si può implementare il gruppo "dataset1/data1/what" con le informazioni sulla prima
    grandezza storata alla prima elevazione del volume polare acquisito da SPC alle
    10:35 del 20/09/2022, creando l'istanza di OdimWhatDset come di seguito.
    Supponendo che la prima grandezza storata è la varianza della velocità radiale:

    d1_data1_what = OdimWhatDset(   hierarchy="dataset1/data1/what",
                                    quantity="WRAD",
                                    gain=0.0002891744952648878,
                                    offset=0.0,
                                    nodata=65535.0,
                                    undetect=0.0
                                    )
    """

    def __init__(
        self,
        hierarchy: str,
        product: Optional[str] = None,
        prodpar: Optional[str] = None,
        quantity: Optional[str] = None,
        startdate: Optional[str] = None,
        starttime: Optional[str] = None,
        enddate: Optional[str] = None,
        endtime: Optional[str] = None,
        gain: float = 1.0,
        offset: float = 0.0,
        nodata: Optional[float] = None,
        undetect: Optional[float] = None,
    ):

        super().__init__(hierarchy)
        self.product = product
        self.prodpar = prodpar
        self.quantity = quantity
        self.startdate = startdate
        self.starttime = starttime
        self.enddate = enddate
        self.endtime = endtime
        self.gain = gain
        self.offset = offset
        self.nodata = nodata
        self.undetect = undetect
