import numpy as np
from typing import Optional, Iterable, Any, Union
from datetime import datetime

"""
Sono definite le classi usate per la lettura delle variabili del file ncdf, bufr in modo da ottenere
le relative info e i dati in una struttura analoga a quella di IDL.
Sostituisce il define_structure.pro
"""


class StructBase:

    """Classe genitore di tutte le classi che implementano le sottostrutture con le
    informazioni di una variabile e delle classi che implementano una variabile.

    E' la classe base da cui ereditano quasi tutte le classi definite nella libreria,
    in quanto non ha parametri per il costruttore ma solo metodi per l'assegnazione
    di attributi e l'ispezione degli attributi di istanza.
    """

    def __init__(self):

        pass

    def addparams(self, newparam: Union[Iterable[str], str], value: Union[Iterable[Any], Any]) -> None:

        """
        Metodo d'istanza, che assegna un attributo o una lista di attributi all'istanza della
        classe StructBase.
        Tutte le classi figlie di StructBase ereditano questa funzione chiamando il super()
        nel loro __init__ .

        INPUT:
        - newparam --Union[iterable[str],str] : stringa del nome dell'attributo da assegnare o
                                                lista di stringhe dei nomi degli attributi
                                                se si vuole assegnare una lista di attributi
                                                all'istanza della classe StructBase.
        - value    --Union[Iterable[Any],Any] : attributo o lista degli attributi da assegnare
                                                all'istanza della classe StructBase; il type di
                                                ciascun attributo può essere qualsiasi
                                                (float,int,object,str..).
        es: istanza=StructBase()
            istanza.addparams(newparams="attributo1",value=0)
            istanza.addparams(newparams=["attr1","attr2"],value=[0,1])
        """

        if type(newparam) == str:
            setattr(self, newparam, value)
        elif type(newparam) == list:
            for k, v in zip(newparam, value):
                self.__dict__[k] = v

        return None

    def struct_getitem(self, param: str) -> Any:
        """
        Metodo di istanza della classe StructBase che restituisce il valore dell'attributo
        param se l'istanza lo possiede, None altrimenti.

        INPUT:
        - param --str : nome dell'attributo dell'istanza di cui voglio conoscere il valore.

        OUTPUT:
                --Optional[Any] : il valore dell'attributo, se l'istanza lo possiede,
                                  None altrimenti.

        es: istanza=StructBase()
            istanza.addparams(newparams="attributo1",value=0)
            attributo1 = istanza.struct_getitem("attributo1")

            e attributo1 sarà uguale a 0 in questo caso.
        """

        if param in self.__dict__.keys():
            return self.__dict__[param]
        return None

    def struct_hasitem(self, param: str) -> bool:
        """
        Metodo di istanza della classe StructBase che restituisce True se l'istanza
        possiede l'attributo param, False altrimenti.

        INPUT:
        - param --str  : nome dell'attributo di cui verificare l'esistenza per l'istanza.

        OUTPUT:
                --bool : True se l'istanza ha l'attributo di nome 'param', False altrimenti.

        es: istanza=StructBase()
            istanza.addparams(newparams="attributo1",value=0)
            istanza.struct_hasitem("attributo1") --> l'output è True
        """
        if param in self.__dict__.keys():
            return True
        return False


class StructVariable(StructBase):

    accum_time_h: Optional[float] = None

    __doc__ =  """
    Classe figlia di StructBase con attributi dell'istanza:

    -name                   --str    (default=None)  : nome della variabile.
    -long_name              --str    (default=None)  : nome esteso della variabile.
    -standard_name          --str    (default=None)  : nome standard della variabile, netCDF compliant.
    -units                  --str    (default=None)  : unità fisiche della variabile letta.
    -min_val                --float  (default=None)  : valore minimo variabile.
    -max_val                --float  (default=None)  : valore massimo variabile.
    -missing                --float  (default=None)  : valore degli out of range/dato mancante.
    -undetect               --float  (default=None)  : valore sottosoglia, assegnato ai punti in cui il valore
                                                       rilevato<min_val.
    -color_table            --str    (default=None)  : filename del file txt con livelli e colori per la grafica.

    e attributo di classe
    -accum_time_h           --float  (default=None)  : tempo di cumulata (0 se campo istantaneo). Questo
                                                       attributo è implementato come attributo di classe.
    ** Nelle strutture per le informazioni sulla variabile ottenute dalle routine IDL erano presenti anche i
       seguenti attributi, che qui possono essere aggiunti tramite il metodo add_params ereditato da
       simcradarlib.io_utils.structure_class.StructBase:
    -offset                 --float  (default=0.)    : valore offset (se il campo va compresso,residuo da idl)
    -scale_factor           --float  (default=0.)    : valore scale_factor (se il campo va compresso,residuo da idl)
    -nbyte
    -val_compresso
    -tab_id

    Metodo di classe:
    - set_cls_by_name( varname : Optional[str]):
      metodo che prende in input il nome della variabile radar da implementare come struttura e
      restituisce in output la classe che implementa tale variabile, identificandola come quella
      con l'attributo 'name' pari al parametro in input 'varname' tra tutte le classi figlie di
      StructVariable, implementate in simcradarlib.io_utils.rad_var_class .
      
    
    Metodo d'istanza:
    - set_var_by_name( varname : Optional[str] = None)-> None:
      metodo che prende in input il nome della variabile radar da implementare come struttura e
      assegna agli attributi dell'istanza i valori dei corrispondenti attributi per la classe
      che implementa tale variabile radar, identificata come quella avente l'attributo 'name'
      pari al parametro in input 'varname' tra tutte le classi figlie di StructVariable,
      implementate in simcradarlib.io_utils.rad_var_class .
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
        color_table: Optional[str] = None,
    ):

        super().__init__()
        self.name = name
        self.long_name = long_name
        self.standard_name = standard_name
        self.units = units
        self.min_val = min_val
        self.max_val = max_val
        self.missing = missing
        self.undetect = undetect
        self.color_table = color_table

    @classmethod
    def set_cls_by_name(cls, varname: Optional[str] = None):
        """
        metodo di classe della classe simcradarlib.io_utils.structure_class.StructVariable
        che prende in input 'varname', cioè il nome della variabile radar da implementare,
        e restituisce in output la classe figlia di StructVariable che implementa quella
        particolare variabile radar, purchè sia passato il parametro in input 'varname'.
        Se tale parametro 'varname' non è passato in input, di default vale None e viene
        restituito None.

        INPUT:
        varname    --str : nome della variabile radar da implementare; tale stringa
                           deve coincidere con l'attributo 'name' atteso per l'istanza
                           della classe figlia di StructVariable la quale implementa
                           tale variabile tra tutte le classi figlie implementate in
                           simcradarlib.io_utils.rad_var_class .
        OUTPUT:
        outcls     --Optional[ Union[ simcradarlib.io_utils.rad_var_class.VarPr,
                                      simcradarlib.io_utils.rad_var_class.VarZ60,
                                      simcradarlib.io_utils.rad_var_class.VarCumPrr,
                                      simcradarlib.io_utils.rad_var_class.VarZdr,
                                      simcradarlib.io_utils.rad_var_class.VarVn16,
                                      simcradarlib.io_utils.rad_var_class.VarVn49,
                                      simcradarlib.io_utils.rad_var_class.VarSv,
                                      simcradarlib.io_utils.rad_var_class.VarQc,
                                      simcradarlib.io_utils.rad_var_class.VarPrmm,
                                      simcradarlib.io_utils.rad_var_class.VarCumPrmm,
                                      simcradarlib.io_utils.rad_var_class.VarZ,
                                      simcradarlib.io_utils.rad_var_class.VarTh,
                                      simcradarlib.io_utils.rad_var_class.VarDbzh,
                                      simcradarlib.io_utils.rad_var_class.VarVrad,
                                      simcradarlib.io_utils.rad_var_class.VarWrad,
                                      simcradarlib.io_utils.rad_var_class.VarRhohv ]
                             ] :
                            classe figlia di StructVariable che implementa la variabile
                            radar desiderata, identificata come quella che ha attributo
                            'name' pari al parametro in input varname.
        """
        outcls = None
        if varname is not None:
            subclasses = list(cls.__subclasses__()).copy()
            for subcls in subclasses:
                outcls = subcls()
                if outcls.name == varname:
                    break
        return outcls

    def set_var_by_name(self, varname: Optional[str]) -> None:
        """
        metodo di istanza della classe simcradarlib.io_utils.structure_class.StructVariable
        che prende in input il nome della variabile radar da implementare e assegna agli
        attributi dell'istanza di StructVariable i valori dei corrispondenti attributi per
        la classe figlia di StructVariable la quale implementa quella variabile, avente
        come attributo 'name' il parametro in input 'varname'.
        Se il parametro 'varname' non è passato in input, vale None di default e non
        vengono modificati i valori degli attributi dell'istanza.

        (Per far questo, la classe figlia di StructVariable che implementa la variabile
        desiderata viene identificata invocando il metodo di classe set_cls_by_name() e
        poi gli attributi vengono assegnati con addparams, ereditato da StructBase)

        INPUT:
        varname    --str : nome della variabile radar da implementare; tale stringa
                           deve coincidere con l'attributo 'name' atteso per l'istanza
                           della classe figlia di StructVariable la quale implementa
                           tale variabile tra tutte le classi figlie implementate in
                           simcradarlib.io_utils.rad_var_class .
        OUTPUT:
                  --None

        __________________________________________________________________________________________
        Esempio:
        Creo l'istanza della classe StructVariable senza specificare parametri in input

        >>myvar=simcradarlib.io_utils.structure_class.StructVariable()
        >>myvar.__dict__.items()
        dict_items([('name', None), ('long_name', None), ('standard_name', None), ('units', None),
        ('min_val', None), ('max_val', None), ('missing', None), ('undetect', None),
        ('color_table', None)])

        e successivamente invoco il metodo set_var_by_name() passando in input il varname="Z_60" per
        implementare la riflettività

        >>myvar.set_var_by_name("Z_60")
        >>myvar.__dict__.items()
        dict_items([('name', 'Z_60'), ('long_name', 'Radar reflectivity factor'), ('standard_name',
        None), ('units', 'dBZ'), ('min_val', -19.69), ('max_val', 60.0), ('missing', -20.0),
        ('undetect', -19.69), ('color_table', 'RGB_Z.txt')])
        _________________________________________________________________________________________
        """
        if varname is not None:
            clsvar = self.set_cls_by_name(varname)
            self.addparams(newparam=list(clsvar.__dict__.keys()), value=list(clsvar.__dict__.values()))

        return


class StructCoords(StructBase):

    __doc__ =  """
    Classe figlia di StructBase con attributi dell'istanza:

    -name                   --str          (default=None)  : nome del tipo di coordinata.
    -long_name              --str          (default=None)  : nome esteso della variabile coordinata.
    -units                  --str          (default=None)  : unità fisiche della variabile coordinata.
    -vals                   --np.ndarray   (default=None)  : valori delle coordinate su un asse di grigliato 2D.
                                                             Tale np.ndarray ha shape pari al numero di punti
                                                             griglia sull'asse considerato.
                                                             Es: se il grigliato ha nx punti griglia in orizzontale
                                                                 e ny punti griglia in verticale, la struttura
                                                                 StructCoords delle coordinate orizzontali
                                                                 avrà StructCoords.vals.shape=(nx,)
                                                                 mentre per le coordinate verticali
                                                                 StructCoords.vals.shape=(ny,).
    """

    def __init__(
        self,
        name: Optional[str] = None,
        long_name: Optional[str] = None,
        units: Optional[str] = None,
        vals: Optional[np.ndarray] = None,
    ):

        super().__init__()
        self.name = name
        self.long_name = long_name
        self.units = units
        self.vals = vals


class StructGrid(StructBase):

    # nx:Optional[int] = None
    # ny:Optional[int] = None
    nx: int
    ny: int
    name: str

    __doc__ = """
    Classe figlia di StructBase con attributi dell'istanza:

    -limiti            --np.ndarray((4,))  (default=None)  : array contenente le coordinate degli estremi
                                                             del grigliato in ordine [ y_min, x_min, y_max, x_max].
    -dx                     --float        (default=None)  : passo griglia sull'asse x.
    -dy                     --float        (default=None)  : passo griglia sull'asse y.
    -units_dx               --str          (default=None)  : unità di misura del passo griglia sull'asse x.
    -units_dy               --str          (default=None)  : unità di misura del passo griglia sull'asse y.
    -name                   --str          (default=None)  : nome dell'area (residuo IDL). Questo attributo è
                                                             implementato come attributo di classe.

    Tramite il modulo numero_punti_griglia() si può aggiungere agli attributi dell'istanza :
    -nx                     --int          : numero punti griglia della griglia sull'asse x.
    -ny                     --int          : numero punti griglia della griglia sull'asse y.
    """

    def __init__(
        self,
        limiti: np.ndarray = np.array([None, None, None, None]),
        dx: Optional[float] = None,
        dy: Optional[float] = None,
        units_dx: Optional[str] = None,
        units_dy: Optional[str] = None,
    ):

        super().__init__()
        self.limiti = limiti
        self.dx = dx
        self.dy = dy
        self.units_dx = units_dx
        self.units_dy = units_dy

    def numero_punti_griglia(self) -> None:
        """
        Metodo di istanza della classe StructGrid che calcola il numero di celle sull'asse
        x e y della griglia usata e li aggiunge agli attributi dell'istanza della classe.
        """

        # nx = int(round((self.limiti[3] - self.limiti[1]) / self.dx, 1)) + 1
        # ny = int(round((self.limiti[2] - self.limiti[0]) / self.dy, 1)) + 1
        nx = int(round((self.limiti[3] - self.limiti[1]) / self.dx)) + 1
        ny = int(round((self.limiti[2] - self.limiti[0]) / self.dy)) + 1
        setattr(self, "nx", nx)
        setattr(self, "ny", ny)

        return None


class StructProjection(StructBase):

    proj_id: Optional[int] = None
    projection_index: Optional[int] = None
    projection_name: str = "None"
    grid_mapping_name: str = "None"
    long_name: str = "None"
    stand_par1: Optional[float] = 0.0
    semimajor_axis: Optional[float] = None
    semiminor_axis: Optional[float] = None
    x_offset: Optional[float] = None
    y_offset: Optional[float] = None

    __doc__ = """
    Classe figlia di StructBase con attributi dell'istanza:

    -center_longitude        --np.float64       (default=None)  : longitudine del centro di proiezione.
    -center_latitude         --np.float64       (default=None)  : latitudine del centro di proiezione.
    -proj_name               --str              (default=None)  : descrizione testuale del tipo di proiezione usata.
    -earth_radius            --float64          (default=None)  : raggio terrestre usato ( residuo IDL).
    """

    def __init__(
        self,
        center_longitude: Optional[float] = None,
        center_latitude: Optional[float] = None,
        proj_name: Optional[str] = None,
        earth_radius: Optional[float] = None,
    ):

        super().__init__()
        self.center_longitude = center_longitude
        self.center_latitude = center_latitude
        self.proj_name = proj_name
        self.earth_radius = earth_radius


class StructProduct(StructBase):

    __doc__ = """
    Classe figlia di StructBase con attributi dell'istanza:

    -name                 --str     (default=None)  : nome del tipo di prodotto.
    -long_name            --str     (default=None)  : descrizione del tipo di prodotto.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        long_name: Optional[str] = None,
        # proj_id: Optional[int] = None,
    ):

        super().__init__()
        self.name = name
        self.long_name = long_name
        # self.proj_id = proj_id


class StructTime(StructBase):

    __doc__ = """
    Classe figlia di StructBase con attributi dell'istanza:

    -date_time_validita   --datetime  (default=None)  : oggetto datetime.datetime che rappresenta
                                                        la dataora di validità dei dati.
    -date_time_emissione  --datetime  (default=None)  : oggetto datetime.datetime che rappresenta
                                                        la dataora di emissione dei dati.
    -acc_time             --int       (default=None)  : tempo di cumulata se il campo non è istantaneo
                                                        ma cumulato. Nell'implementazione attuale il
                                                        tempo di cumulata letto da un file netCDF non è
                                                        assegnato a questo attributo, ma all'attributo
                                                        accum_time_h di StructVariable, attenendosi alle
                                                        precedenti routine IDL.
    -acc_time_unit        --str       (default=None)  : unità del tempo di cumulazione. Es: "hours".
    """

    def __init__(
        self,
        date_time_validita: Optional[datetime] = None,
        acc_time: Optional[int] = None,
        acc_time_unit: Optional[str] = None,
        date_time_emissione: Union[Optional[datetime], str] = "Unknown",
    ):

        super().__init__()
        self.date_time_emissione = date_time_emissione
        self.date_time_validita = date_time_validita
        self.acc_time = acc_time
        self.acc_time_unit = acc_time_unit


class StructSource(StructBase):

    __doc__ = """
    Classe figlia di StructBase con attributi dell'istanza:

    -name_source   --str  (default="Unknown") : nome della sorgente dei dati.
                                                (Es: per le ZLR è il nickname del radar).
    -name_file     --str  (default=None)      : nome del file sorgente dei dati (residuo IDL).
    -commento      --str  (default=None)      : commento opzionale sulla sorgente dati
                                                (residuo IDL).
    -quality_file  --str  (default=None)      : nome di file della qualità dei dati se esiste
                                                (ad es per le ZLR, per ogni file YYYYmmddHHMM.ZLR
                                                 esiste quello della qualità dei dati corrispondente
                                                 YYYYmmddHHMM.qual_ZLR ).
    """

    emission_center: Optional[str] = None

    def __init__(
        self,
        name_source: Optional[str] = "Unknown",
        name_file: Optional[str] = None,
        commento: Optional[str] = None,
        quality_file: Optional[str] = None,
    ):

        super().__init__()
        self.name_source = name_source
        self.name_file = name_file
        self.quality_file = quality_file
        self.commento = commento


class RadarProduct(StructProduct):

    __doc__ = """
    Classe figlia di StructProduct per implementare i prodotti radar e
    sostituisce la tabella /autofs/radar/radar/file_x_idl/tabelle/prodotti.txt
    e /autofs/radar/radar/idl/general_utilities/read_prod_tab.pro.

    Attributi dell'istanza (ereditati da StructProduct):

    - name       --str : nome del tipo di prodotto.
    - long_name  --str : nome esteso del tipo di prodotto.

    Quindi non è mantenuto 'tab_id' che era presente in prodotti.txt.

    Se viene creata l'istanza di classe RadarProduct senza specificare long_name
    nell'inizializzazione, tale attributo viene settato pari al valore della chiave
    corrispondente all'attributo 'name' nel dizionario 'dict_radprods', definito
    nel costruttore come variabile di istanza.

    dict_radprods = {
            "SRI": "Surface Radar Rainfall Intensity",
            "SRT": "Surface Radar Rainfall Accumulation",
            "CAPPI": "Constant Altitude PPI",
            "MAX": "Maximum Vertical Projection",
            "PPI": "Plan Position Indicator",
            "LBM": "Lowest Beam Map Reflectivity",
            "BEAM": "Radar Beam",
            "RHI": "Range-Height Indicator",
            "XSEC": "Vertical Section",
            "ETOP": "Echo Top",
            "HSP": "HVMI horizontal panel",  # HVIM??
            "VSP": "HVIM vertical panel",
            "VIL": "Vertical Integrated Liquid Water",
            "CLASS_CONV": "Convective-stratiform classification",
            "POH_ARPA": "Probability of hail",
            "VID": "Vil density - hail size",
            "SURF": "Surface field",
            "COMP": "Cartesian composite image",
            "RR": "Accumulation",
        }

    Es: istanza = RadarProduct(name="RR")
        --> istanza.long_name = "Accumulation"

        perchè dict_radprods["RR"] = "Accumulation"
    """

    def __init__(self, name: str = "None", long_name: str = "None"):
        super().__init__(name, long_name)
        self.name = name
        self.long_name = long_name

        dict_radprods = {
            "SRI": "Surface Radar Rainfall Intensity",
            "SRT": "Surface Radar Rainfall Accumulation",
            "CAPPI": "Constant Altitude PPI",
            "MAX": "Maximum Vertical Projection",
            "PPI": "Plan Position Indicator",
            "LBM": "Lowest Beam Map Reflectivity",
            "BEAM": "Radar Beam",
            "RHI": "Range-Height Indicator",
            "XSEC": "Vertical Section",
            "ETOP": "Echo Top",
            "HSP": "HVMI horizontal panel",  # HVIM??
            "VSP": "HVIM vertical panel",
            "VIL": "Vertical Integrated Liquid Water",
            "CLASS_CONV": "Convective-stratiform classification",
            "POH_ARPA": "Probability of hail",
            "VID": "Vil density - hail size",
            "SURF": "Surface field",
            "COMP": "Cartesian composite image",
            "RR": "Accumulation",
        }
        if self.name != "None" and self.long_name == "None" and self.name in dict_radprods.keys():
            self.long_name = dict_radprods[self.name]
