from simcradarlib.odim.odim_utils import (
    OdimDset,
    OdimWhat,
    OdimWherePolar,
    OdimWherePolarDset,
    OdimHow,
    OdimHowRadarDset,
    OdimHowPolarDset,
    OdimWhatDset,
)
from simcradarlib.io_utils.structure_class import StructBase
import h5py
import numpy as np
from typing import List, Union, Optional


class OdimHierarchyPvol(StructBase):

    """
    Implementa la gerarchia di un file HDF per dato polare (es: volume radar)
    compatibilmente con le specifiche ODIM OPERA v.2.1.

    Le classi utilizzate per implementare gli oggetti del file ODIM
    sono implementate in simcradarlib.odim.odim_utils .
    Sono le classi OdimWhat, OdimWhere, OdimHow, OdimWhatDset,
    OdimWherePolarDset, OdimHowRadarDset, OdimHowPolarDset.

    Classe figlia di simcradarlib.io_utils.structure_class.StructBase
    con attributi dell'istanza (assegnati tramite il metodo di classe
    OdimHierarchyPvol.setistance() descritto successivamente):

    -root_what:             --OdimWhat        : istanza della classe OdimWhat che
                                                implementa il gruppo "what" del root.
    -root_where:            --OdimWherePolar  : istanza della classe OdimWherePolar
                                                che implementa il gruppo "where" del root
    -root_how:              --OdimHow         : istanza della classe OdimHow che
                                                implementa il gruppo "how" del root.
    -n_group_dataset        --int             : numero di gruppi "dataset<n>" a livello
                                                gerarchico direttamente inferiore
                                                al root, corrispondenti alle n elevazioni
                                                nel caso di dati di volume polare radar.
                                                Se il radar effettua scansioni a 4 elevazioni,
                                                allora n_group_dataset=4 ed esistono i gruppi
                                                "dataset1","dataset2","dataset3","dataset4".
    -n_datasets             --int             : numero di dataset da storare. Deve essere pari
                                                al numero di grandezze storate durante ogni
                                                scansione. 
                                                Se vengono storate "DBZH" e "VRAD" allora
                                                n_datasets=2 ed esistono i dataset
                                                "dataset<n>/data1/data" e "dataset<n>/data2/data",
                                                per le n elevazioni a cui il radar scansiona
                                                l'atmosfera.
                                                Se il numero di grandezze storate
                                                è diverso per diverse elevazioni, n_datasets
                                                è il numero più grande.
    -group_datasets_what    --list            : lista costituita da istanze di
                                                classe OdimWhatDset, che rappresentano
                                                i gruppi "dataset<n>/what" di ciasuna
                                                delle n elevazioni a cui il radar scansiona
                                                un volume di atmosfera.
                                                (es: "dataset1/what").
                                                Il numero di elementi della lista deve essere
                                                pari all'attributo di istanza 'n_group_dataset'.
    -group_datases_where    --list            : lista di  istanze di classe OdimWherePolarDset,
                                                che rappresentano i gruppi "dataset<n>/where" per
                                                ciascuna delle n elevazioni a cui il radar scansiona.
                                                (es: "dataset1/where").
                                                Il numero di elementi della lista deve essere
                                                pari all'attributo dell'istanza 'n_group_dataset'.
    -group_datases_how_radar --list           : lista di istanze di classe OdimHowRadarDset, che
                                                rappresentano i gruppi "dataset<n>/how"
                                                (es: "dataset1/how") con attributi specifici
                                                del radar, per ciascuna elevazione <n>-esima a
                                                cui il radar scansiona l'atmosfera.
                                                Il numero di elementi della lista deve essere
                                                pari all'attributo di istanza 'n_group_dataset'.
    -group_datases_how_polar --list           : lista di istanze di classe OdimHowPolarDset,
                                                che rappresentano i gruppi "dataset<n>/how"
                                                (es: "dataset1/how") con attributi specifici
                                                del dato polare, per ciascuna delle n elevazioni.
                                                Il numero di elementi della lista deve essere
                                                essere pari all'attributo di istanza 'n_group_dataset'.

    -datasets               --list[np.ndarray]: Lista di lunghezza = n_group_dataset quindi ha tanti
                                                elementi quante sono le elevazioni; l'elemento <n>-esimo
                                                è la concatenazione delle matrici di dati delle varie
                                                grandezze storate all'elevazione <n>-esima.
                                                Quindi ogni elemento della lista è un np.ndarray
                                                di shape=(n_datasets,nrays,nbins) con
                                                            -n_datasets=attributo dell'istanza che
                                                             indica il numero di grandezze storate.
                                                            -nrays=numero di raggi nel PPI.
                                                            -nbins=numero di bins nel raggio per
                                                             l'elevazione <n>-esima.
                                                                 Esempio:
                                                Nel caso sia storata solo DBZH a 2 elevazioni, allora
                                                l'istanza di OdimHierarchyPvol ha attributo 'datasets'
                                                dato da una lista di 2 elementi, ognuno pari a un np.ndarray
                                                con shape=(1,nrays,nbins) con nbins che dipende dall'elevazione.
                                                --->        istanza.datasets=[ array_datasets_1elev,
                                                                               array_datasets_2elev ]
                                                            con
                                                            array_datasets_1elev.shape=(1,400,849)
                                                            array_datasets_1elev.shape=(1,400,660)
                                                            se nrays=400, nbins=849 alla prima elevazione
                                                            e nbins=660 alla seconda elevazione.

    -group_datasets_data_what --np.ndarray    : lista di lunghezza = n_group_dataset, quindi ha tanti
                                                elementi quante sono le elevazioni; l' elemento <n>-esimo
                                                è un array che contiene i gruppi "dataset<n>/data<m>/what"
                                                per tutte le m grandezze storate durante la scansione radar.
                                                Si noti che il numero di grandezze storate m = n_datasets.
                                                Quindi ogni elemento della lista è l'array di istanze di classe
                                                OdimWhatDset, che implementano i gruppi "dataset<n>/data<m>/what".
                                                                       Esempio:
                                                Nel caso siano storate 2 grandezze a 3 elevazioni:
                                                n_datasets=2
                                                n_group_datasets=3
                                                group_datasets_data_what=[ np.array([OdimWhatDset,OdimWhatDset]),
                                                                           np.array([OdimWhatDset,OdimWhatDset]),
                                                                           np.array([OdimWhatDset,OdimWhatDset])
                                                                         ]
                                                               che implementano
                                                   [ np.array( "dataset1/data1/what","dataset1/data2/what"] ),
                                                     np.array( "dataset2/data1/what","dataset2/data2/what"] )
                                                     np.array( "dataset3/data1/what","dataset3/data2/what"] )
                                                   ]

    -elangles                 --list[float]   : lista degli angoli di elevazione del volume radar.
                                                La lunghezza della lista deve essere pari all'attributo
                                                'n_group_datasets'.
    -varsnames                --list[str]     : lista dei nomi delle variabili radar storate in oggetti dataset
                                                di h5py nell'ODIM. (es: dataset1/data1/data contiene dati di
                                                WRAD alla 1° elevazione). La lunghezza della lista deve essere
                                                pari all'attributo 'n_datasets'.
                                                Se il numero di variabili storate è diverso per diverse
                                                elevazioni, allora varsnames le contiene comunque tutte, anche
                                                se ad un'elevazione possono non essere tutte storate.
                                                Ad esempio nei nostri volumi processati con AddCleanerQuantities
                                                la grandezza Z_VD, cioè la differenza di Z sulla verticale tra 2
                                                elevazioni, non è presente per l'ultima elevazione.

    GERARCHIA ODIM DATO POLARE:
    con dset_order=[1..,n_group_dataset]
        data_order=[1..,n_datasets]
    root:
        |___dataset<dset_order> (group):
        |   |_________________ what (group):
        |   |                        +attrs:
        |   |                              - {attributi di classe OdimWhatDset}
        |   |_________________ data<data_order> (group):
        |                      |                data (dataset)
        |                      |______________________ what (group):
        |                                                    +attrs:
        |                                                          - {attributi di classe
        |                                                             OdimWhatDset}
        |
        |
        |___what (group):
        |         +attrs:
        |              -date    (mandatory odim v.2.1)
        |              -time    (mandatory odim v.2.1)
        |              -version (mandatory odim v.2.1)
        |              -object  (mandatory odim v.2.1)
        |              -source  (mandatory odim v.2.1)
        |___where (group):
        |          +attrs:
        |              -lon     (mandatory odim v.2.1)
        |              -lat     (mandatory odim v.2.1)
        |              -height  (mandatory odim v.2.1)
        |___how   (group):
        |          +attrs:
        |              - {attributi di classe OdimHowPolarDset
        |                 e di classe OdimHowRadarDset}

    # Modifiche:
    29-04-2024: correzione nel metodo get_data_by_elangle per tener conto che nei volumi
    processati da AddCleanerQuantities, la grandezza "Z_VD" è presente a tutte le elevazioni
    tranne l'ultima.
    """

    root_what: OdimWhat
    root_where: OdimWherePolar
    root_how: OdimHow
    n_group_dataset: int
    n_datasets: int
    group_datasets_what: List[OdimWhatDset]
    group_datasets_where: List[OdimWherePolarDset]
    group_datasets_how_radar: List[OdimHowRadarDset]
    group_datasets_how_polar: List[OdimHowPolarDset]
    datasets: List[np.ndarray]
    group_datasets_data_what: List[np.ndarray]
    elangles: List[Optional[float]]
    varsnames: List[str]

    def __init__(
        self,
    ):
        super().__init__()

    def setistance(
        self,
        root_what: OdimWhat,
        root_where: OdimWherePolar,
        root_how: OdimHow,
        n_group_dataset: int,
        n_datasets: int,
        group_datasets_what=List[OdimWhatDset],
        group_datasets_where=List[OdimWherePolarDset],
        group_datasets_how_radar=List[OdimHowRadarDset],
        group_datasets_how_polar=List[OdimHowPolarDset],
        datasets=List[np.ndarray],
        group_datasets_data_what=List[np.ndarray],
    ) -> None:
        """
        Metodo di istanza della classe OdimHierarchyPvol
        per assegnare ad un'istanza di tale classe, già
        creata, gli attributi di istanza, documentati
        nell'__init__ di OdimHierarchyPvol.

        INPUT: (dettagli nella documentazione di OdimHierarchyPvol)

        -root_what                 --OdimWhat
        -root_where                --OdimWhere
        -root_how                  --OdimHow
        -n_group_dataset           --int
        -n_datasets                --int
        -group_datasets_what       --list[OdimWhatDset]
        -group_datasets_where      --list[OdimWherePolarDset]
        -group_datasets_how_radar  --list[OdimHowRadarDset]
        -group_datasets_how_polar  --list[OdimHowPolarDset]
        -datasets                  --list[np.ndarray]
        -group_datasets_data_what  --list[np.ndarray]

        Gli attributi di istanza di OdimHierarchyPvol 'elangles' e 'varsnames'
        non sono assegnati in quanto parametri in input al metodo setistance,
        ma vengono calcolati dal metodo e assegnati poi all'istanza.

        Questo metodo permette di riempire la struttura gerarchica del volume
        polare implementato da un'istanza della classe. E' utile in lettura.
        Infatti è richiamato dal metodo di classe read_odim.
        """

        self.root_what = root_what
        self.root_where = root_where
        self.root_how = root_how
        self.n_group_dataset = n_group_dataset
        self.n_datasets = n_datasets
        self.datasets = datasets
        self.group_datasets_what = group_datasets_what
        self.group_datasets_where = group_datasets_where
        self.group_datasets_how_radar = group_datasets_how_radar
        self.group_datasets_how_polar = group_datasets_how_polar
        self.group_datasets_data_what = group_datasets_data_what

        assert self.datasets.__len__() == self.n_group_dataset
        assert self.group_datasets_data_what.__len__() == self.n_group_dataset

        self.elangles = [self.group_datasets_where[i].elangle for i in range(self.n_group_dataset)]
        #self.varsnames = [self.group_datasets_data_what[0][i].quantity for i in range(self.n_datasets)]

    def get_group_by_elangle(
        self, elangle: float, namegroup: str
    ) -> Union[OdimWhat, OdimHow, OdimWhatDset, OdimWherePolarDset, OdimHowRadarDset, OdimWherePolar, OdimHowPolarDset]:

        """
        Metodo di istanza della classe OdimHierarchyPvol per accedere ad un
        gruppo della gerarchia ODIM, corrispondente all' elevazione
        del volume definita dall'angolo di elevazione 'elangle'.

        INPUT:
        -elangle                 --float : angolo di elevazione
        -namegroup               --str   : nome dell'attributo dell'istanza OdimHierarchyPvol
                                           il quale implementa il gruppo a cui voglio
                                           accedere tra
                                                -'group_datasets_what'
                                                 (per accedere al sottogruppo "what" di un gruppo
                                                 "dataset<n>" per l'elevazione <n>-esima).
                                                -'group_datasets_where'
                                                  (per accedere al sottogruppo "where" di un gruppo
                                                 "dataset<n>" per l'elevazione <n>-esima).
                                                -'group_datasets_how_radar'
                                                  (per accedere al sottogruppo "how" con le specifiche
                                                  radar di un gruppo "dataset<n>" per l'elevazione
                                                  <n>-esima).
                                                -'group_datasets_how_polar'
                                                  (per accedere al sottogruppo "how" con le specifiche
                                                  polari di un gruppo "dataset<n>" per l'elevazione
                                                  <n>-esima).
                                                -'group_datasets_data_what'
                                                  (per accedere al sottogruppo "what" di un gruppo
                                                  "dataset<n>/data<m>" per l'elevazione
                                                  <n>-esima e la grandezza radar <m>-esima).
                                            (non possono essere i gruppi root come 'root_what'
                                            perchè deve essere un gruppo corrispondente ad un'elevazione)

        OUTPUT:
                            --Union[ OdimWhat, OdimHow, OdimWhatDset, OdimWherePolarDset,
                                     OdimHowRadarDset, OdimWherePolar, OdimHowPolarDset ]:

                                L'output è il contenuto dell'attributo dell'istanza di OdimHierarchyPvol,
                                il quale contiene l'istanza della classe di simcradarlib.odim.odim_utils
                                che implementa il gruppo a cui voglio accedere, per l'elevazione scelta.

        __________________________________________Esempio__________________________________________
        Per accedere all'istanza della classe OdimWhat che implementa il sottogruppo 'what' per la
        prima elevazione cioè vol['dataset1/what'], passare in input:

                       elangle=0.5, nomegroup="group_datasets_what"

                                       cioè

            odim_pvol = OdimHierarchyPvol()
            what_dset1 = odim_pvol.get_group_by_elangle(
                                                         elangle=0.5,
                                                         nomegroup="group_datasets_what"
                                                       )
        __________________________________________________________________________________________
        """

        return self.__dict__[namegroup][self.elangles.index(elangle)]

    def get_data_by_elangle(self, elangle: float, quantity: str) -> np.ndarray:

        """
        Metodo di istanza della classe OdimHierarchyPvol che restituisce la matrice di
        dati di una grandezza radar storata nel volume ODIM per una data elevazione.

        INPUT:
        -elangle           --float : angolo di elevazione
        -quantity          --str   : nome della grandezza radar di cui voglio leggere
                                     i dati. La stringa passata deve corrispondere al
                                     contenuto dell'attributo "quantity" del gruppo
                                     "dataset<n>/data<m>/what", dove <n> indica l'indice
                                     dell'elevazione a cui corrisponde 'elangle' e <m> è
                                     l'indice della grandezza storata che voglio leggere.
        OUPUT:
                            --np.ndarray:
                                     array 2D di dati della grandezza radar scelta,
                                     acquisiti all'elevazione scelta 'elangle'.

        ____________________________________Esempio__________________________________
        Per accedere ai dati di riflettività alla prima elevazione si passa in input
        'elangle'=0.5 e quantity='DBZH':

               odim_pvol=OdimHierarchyPvol()
               z_data_1elev = odim_pvol.get_data_by_elangle(elangle=0.5,quantity="DBZH")
        _____________________________________________________________________________
        """

        # try:
        varsnames_elangle = self.varsnames.copy()
        if elangle==max(self.elangles) and "Z_VD" in varsnames_elangle:
            varsnames_elangle.remove("Z_VD")
        indexq = varsnames_elangle.index(quantity)
        # except ValueError:
        # indexq = self.varsnames.index(quantity.encode("utf-8"))

        raw = self.datasets[self.elangles.index(elangle)][indexq]
        offset = self.group_datasets_data_what[self.elangles.index(elangle)][indexq].offset
        gain = self.group_datasets_data_what[self.elangles.index(elangle)][indexq].gain
        data = raw * gain + offset
        return data

    def get_attrs_from_odimgroup(
        self,
        attrs_list: list,
        hgroup: h5py._hl.group.Group,
        out_cont: Union[
            OdimDset,
            OdimWhat,
            OdimHow,
            OdimWhatDset,
            OdimWherePolarDset,
            OdimHowRadarDset,
            OdimWherePolar,
            OdimHowPolarDset,
        ],
    ) -> None:

        """
        Metodo di istanza della classe OdimHierarchyPvol, chiamato dal
        metodo read_odim (sotto), per la lettura di attributi di gruppi
        o dataset di un file ODIM.

        INPUT:
        -attrs_list    --list : Lista di attributi da leggere nel file ODIM.
                                Possono essere attributi di un oggetto gruppo
                                o di un dataset.
        -hgroup        --h5py._hl.group.Group :
                                oggetto Group di h5py corrispondente al
                                gruppo ODIM di cui voglio leggere gli attributi.
        -out_cont      --Union[ simcradarlib.odim.odim_utils.OdimDset,
                                simcradarlib.odim.odim_utils.OdimWhat,
                                simcradarlib.odim.odim_utils.OdimHow,
                                simcradarlib.odim.odim_utils.OdimWhatDset,
                                simcradarlib.odim.odim_utils.OdimWherePolarDset,
                                simcradarlib.odim.odim_utils.OdimHowRadarDset,
                                simcradarlib.odim.odim_utils.OdimWherePolar,
                                simcradarlib.odim.odim_utils.OdimHowPolarDset ]:
                                istanza della classe che implementa il gruppo o
                                il dataset di cui ho letto gli attributi nel file
                                ODIM.

        PROCESSING:
        Itera sugli elementi di attrs_list verificando che siano attributi per
        il gruppo 'hgroup' del file ODIM che sto leggendo e, se esistono, assegna
        gli attributi trovati all'oggetto out_cont, istanza della classe in
        simcradarlib.odim.odim_utils che implementa quel gruppo/dataset.
        Tale istanza, rappresentativa del gruppo o dataset di cui sono stati letti
        gli attributi dal file ODIM, è un attributo dell'istanza di classe OdimHierarchyPvol
        che voglio riempire di contenuti.
        """

        for att in attrs_list:
            if att in hgroup.attrs.keys():
                val_att = hgroup.attrs.__getitem__(att)
                if type(val_att)==np.bytes_:
                    out_cont.__setattr__(att, val_att.decode())
                else:
                    out_cont.__setattr__(att, val_att)

    def export_odim(self, out_filename: str) -> None:

        """
        Metodo di istanza della classe OdimHierarchyPvol che scrive un volume
        radar o dato di tipo polare (cioè vol['what'].attrs['quantity']='PVOL' o
        vol['what'].attrs['quantity']='SCAN') in formato ODIM OPERA v.2.1.

        Il contenuto scritto nel file ODIM in output è l'insieme dei gruppi e
        relativi attributi storati negli attributi dell'istanza di OdimHierarchyPvol,
        sulla quale invoco tale metodo.
        Per maggiori dettagli guardare lo script di esempio in
        documentazione/esempio_export_odim.py .

        INPUT:

        -out_filename   --str : filename del file ODIM in output.
        """

        hf = h5py.File(out_filename, "w")
        self.root_what.odim_create(hf)
        self.root_what.odim_setattrs(hf, ["object", "version", "date", "time", "source"])

        self.root_where.odim_create(hf)
        self.root_where.odim_setattrs(hf, ["lon", "lat", "height"])

        self.root_how.odim_create(hf)
        self.root_how.odim_setattrs(hf, ["task", "startepochs", "system", "software", "sw_version", "simulated"])

        for i_group, num_group in enumerate(np.arange(1, self.n_group_dataset, 1)):

            g_dset_what = self.group_datasets_what[i_group]
            g_dset_what.odim_create(hf)
            g_dset_what.odim_setattrs(hf, ["product", "startdate", "starttime", "enddate", "endtime"])

            g_dset_where = self.group_datasets_where[i_group]
            g_dset_where.odim_create(hf)
            g_dset_where.odim_setattrs(hf, ["elangle", "nbins", "rstart", "rscale", "nrays", "a1gate"])

            g_dset_how = self.group_datasets_how_polar[i_group]
            g_dset_how.odim_create(hf)
            g_dset_how.odim_setattrs(hf, ["elangles", "startazA", "stopazA", "startazT", "stopazT"])
            g_dset_how_radar = self.group_datasets_how_radar[i_group]
            g_dset_how_radar.odim_setattrs(
                hf,
                [
                    "beamwidth",
                    "wavelength",
                    "rpm",
                    "pulsewidth",
                    "RXbandwidth",
                    "lowprf",
                    "highprf",
                    "TXloss",
                    "RXloss",
                    "radomeloss",
                    "antgain",
                    "beamwH",
                    "beamwV",
                    "gasattn",
                    "nomTXpower",
                    "NI",
                    "Vsamples",
                ],
            )

            for i_dset, num_dset in enumerate(np.arange(1, self.n_datasets, 1)):
                if i_dset<self.datasets[i_group].__len__():
                    dset_i = OdimDset(self.datasets[i_group][i_dset], f"dataset{num_group}/data{num_dset}/data")
                    dset_i.odim_create(hf)
                    if i_dset<self.group_datasets_data_what[i_group].__len__():
                        dseti_what = self.group_datasets_data_what[i_group][i_dset]
                        dseti_what.odim_create(hf)
                        dseti_what.odim_setattrs(hf, ["quantity", "gain", "nodata", "offset", "undetect"])

        hf.close()
        return None

    def read_odim(self, filename: str) -> None:

        """
        Metodo di istanza della classe OdimHierarchyPvol che legge un file ODIM OPERA v.2.1
        di volume radar o dato di tipo polare (cioè vol['what'].attrs['quantity']='PVOL' o
        vol['what'].attrs['quantity']='SCAN').

        Il contenuto del file ODIM letto viene assegnato agli attributi dell'istanza di
        OdimHierarchyPvol, sulla quale invoco tale metodo.

        INPUT:
        - filename    --str : filename del file ODIM da leggere
        """

        hr = h5py.File(filename, "r")

        gd_what_list = []
        gd_where_list = []
        gd_how_polar_list = []
        gd_how_radar_list = []
        gd_datadset_list_total = []
        gd_data_what_list_total = []
        root_what = OdimWhat(
            hierarchy="what",
            obj=hr["what"].attrs["object"].decode(),
            version=hr["what"].attrs["version"].decode(),
            date=hr["what"].attrs["date"].decode(),
            time=hr["what"].attrs["time"].decode(),
            source=hr["what"].attrs["source"].decode(),
        )
        root_where = OdimWherePolar(
            "where", hr["where"].attrs["lon"], hr["where"].attrs["lat"], hr["where"].attrs["height"]
        )
        attrs_howroot = ["task", "startepochs", "system", "software", "sw_version", "simulated"]
        root_how = OdimHow("how")
        self.get_attrs_from_odimgroup(attrs_howroot, hr["how"], root_how)

        nmax_datasets=0
        allquantities=[]
        # poi itero sui dataset
        group_dataset_names = [k for k in hr.keys() if "dataset" in k]
        for gdname in group_dataset_names:

            dg_what = OdimWhatDset(hierarchy=f"{gdname}/what")
            attrs_ = ["product", "startdate", "starttime", "enddate", "endtime"]
            self.get_attrs_from_odimgroup(attrs_, hr[f"{gdname}/what"], dg_what)

            dg_where = OdimWherePolarDset(f"{gdname}/where", None, None, None, None, None, None)
            attrs_ = ["elangle", "nbins", "rstart", "rscale", "nrays", "a1gate"]
            self.get_attrs_from_odimgroup(attrs_, hr[f"{gdname}/where"], dg_where)

            dg_how_radar = OdimHowRadarDset(f"{gdname}/how")
            attrs_ = [
                "beamwidth",
                "wavelength",
                "rpm",
                "pulsewidth",
                "RXbandwidth",
                "lowprf",
                "highprf",
                "TXloss",
                "RXloss",
                "radomeloss",
                "antgain",
                "beamwH",
                "beamwV",
                "gasattn",
                "nomTXpower",
                "NI",
                "Vsamples",
            ]
            self.get_attrs_from_odimgroup(attrs_, hr[f"{gdname}/how"], dg_how_radar)

            dg_how_polar = OdimHowPolarDset(f"{gdname}/how")
            attrs_ = ["elangles", "startazA", "stopazA", "startazT", "stopazT"]
            for att in attrs_:
                try:
                    dg_how_polar.__setattr__(att, hr[f"{gdname}/how"].attrs.__getitem__(att))
                except KeyError:
                    if att in hr[f"{gdname}/how"].keys():
                        dg_how_polar.__setattr__(att, hr[f"{gdname}/how"][att][:])

            gd_what_list.append(dg_what)
            gd_where_list.append(dg_where)
            gd_how_polar_list.append(dg_how_polar)
            gd_how_radar_list.append(dg_how_radar)
            # leggo i dataset e i gruppi what dei dataset gd_datadset_list
            gd_data_what_list = []
            gd_datadset_list = []
            dataset_names = [dd for dd in hr[f"{gdname}"].keys() if "data" in dd]
            nmax_datasets=max(nmax_datasets,len(dataset_names))
            for d in dataset_names:
                gd_datadset_list.append(hr[f"{gdname}/{d}/data"][:])
                whatd = hr[f"{gdname}/{d}/what"]
                quantity = whatd.attrs["quantity"]
                if type(quantity)==np.bytes_ : quantity = quantity.decode()
                d_what = OdimWhatDset(
                    hierarchy=f"{gdname}/{d}/what",
                    quantity=quantity, #whatd.attrs["quantity"],
                    gain=whatd.attrs["gain"],
                    offset=whatd.attrs["offset"],
                    nodata=whatd.attrs["nodata"],
                    undetect=whatd.attrs["undetect"],
                )
                gd_data_what_list.append(d_what)
                if quantity not in allquantities:
                    allquantities.append(quantity)

            gd_data_what_list_total.append(np.array(gd_data_what_list))
            gd_datadset_list_total.append(np.vstack([[d] for d in gd_datadset_list]))

        hr.close()

        # poi costruisco ODIM_HIERARCHY_PVOL()
        self.setistance(
            root_what=root_what,
            root_where=root_where,
            root_how=root_how,
            n_group_dataset=len(group_dataset_names),
            n_datasets=nmax_datasets,
            group_datasets_what=gd_what_list,
            group_datasets_where=gd_where_list,
            group_datasets_how_radar=gd_how_radar_list,
            group_datasets_how_polar=gd_how_polar_list,
            datasets=gd_datadset_list_total,
            group_datasets_data_what=gd_data_what_list_total,
        )
        self.varsnames=allquantities

        return None
