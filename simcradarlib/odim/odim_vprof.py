from simcradarlib.odim.odim_utils import (
    OdimRoot,
    OdimWhat,
    OdimWhereVertProfile,
    OdimHowVertProfile,
    OdimHow,
    OdimDset,
    OdimWhatDset,
)
from simcradarlib.io_utils.structure_class import StructBase
import h5py
from typing import Union


class OdimHierarchyProfile(StructBase):
    
    """
    Implementa la gerarchia di un file HDF per un profilo verticale
    compatibilmente con specifiche ODIM OPERA v.2.4
    (vol['what'].attrs['object']='VP')

    Le classi utilizzate per implementare gli oggetti del file ODIM
    sono implementate in simcradarlib.odim.odim_utils.

    Classe figlia di simcradarlib.io_utils.structure_class.StructBase con
    attributi dell'istanza:
    -root               --OdimRoot             : istanza della classe OdimRoot che
                                                 implementa root
    -root_what:         --OdimWhat             : istanza della classe OdimWhat che
                                                 implementa il gruppo "what" di root
    -root_where:        --OdimWhereVertProfile : istanza della classe OdimWhereVertProfile
                                                 che implementa il gruppo "where" di root
    -root_how:          --OdimHowVertProfile   : istanza della classe OdimHow che
                                                 implementa il gruppo "how" di root
    -group_dataset_what --OdimWhatDset         : istanza della classe OdimWhatDset,
                                                 che implementa il gruppo "dataset1/what"

    GERARCHIA ODIM 'VERTICAL PROFILE':
    root:
        |___dataset1 (group):
        |   |_________________ what (group):
        |   |                        +attrs:
        |   |                              - {attributi di classe OdimWhatDset}
        |   |_________________ data-n (group):
        |                      |________________ data (dataset)              
        |                      |________________ what (group):
        |                                             +attrs:
        |                                                 - {attributi di classe
        |                                                    OdimWhatDset}       
        |___what (group):
        |         +attrs:
        |              -date    (mandatory)
        |              -time    (mandatory)
        |              -version (mandatory)
        |              -object  (mandatory)
        |              -source  (mandatory)
        |___where (group):
        |          +attrs:
        |              -{attributi di classe OdimWhereVertProfile}
        |___how   (group):
        |          +attrs:
        |              - {attributi di classe OdimHowVertProfile}
    """
    root: OdimRoot
    root_what: OdimWhat
    root_where: OdimWhereVertProfile
    root_how: OdimHowVertProfile
    group_dataset_what: OdimWhatDset
    datasets: dict  # { "data1": {"data": OdimDset, "what": OdimWhatDset}, ... }

    def __init__(
        self,
    ):
        super().__init__()

    def setistance(
        self,
        root: OdimRoot,
        root_what: OdimWhat,
        root_where: OdimWhereVertProfile,
        root_how: OdimHowVertProfile,
        group_dataset_what: OdimWhatDset,
        datasets: dict, 
    ) -> None:
        """
        Metodo che assegna gli attributi a un'istanza già creata della classe.
        INPUT:
        -root                      --OdimRoot
        -root_what                 --OdimWhat
        -root_where                --OdimWhereVertProfile
        -root_how                  --OdimHowVertProfile
        -group_dataset_what        --OdimWhatDset
        -dataset           
        """
        self.root = root
        self.root_what = root_what
        self.root_where = root_where
        self.root_how = root_how
        self.group_dataset_what = group_dataset_what
        self.datasets = datasets
        
    def get_attrs_from_odimgroup(
        self,
        attrs_list: list,
        hgroup: h5py._hl.group.Group,
        out_cont: Union[OdimWhat, OdimHow, OdimWhereVertProfile, OdimHowVertProfile, OdimWhatDset],
    ) -> None:

        """
        Metodo di istanza della classe OdimHierarchyProfile, chiamato dal metodo
        simcradarlib.odim.odim_utils.OdimHierarchyProfile.read_odim, per
        la lettura di attributi di gruppi o dataset in un file ODIM.

        INPUT:
        -attrs_list    --list : Lista di attributi da leggere nel file ODIM.
                                Possono essere attributi di un oggetto gruppo
                                o di un oggetto dataset.
        -hgroup        --h5py._hl.group.Group :
                                oggetto Group di h5py corrispondente al
                                gruppo ODIM di cui voglio leggere gli attributi.
        -out_cont      --Union[ OdimDset8bImage, OdimWhat, OdimHow,
                                OdimWhereGeoimage, OdimWhatDset ]:
                                istanza della classe che implementa il gruppo o
                                il dataset di cui ho letto gli attributi nel file
                                ODIM. Tale classe è una di quelle implementate nel
                                modulo simcradarlib.odim.odim_utils.

        PROCESSING:
        Per ogni attributo in attrs_list, controlla se esiste nel gruppo hgroup del
        file ODIM. Se esiste, lo legge e lo assegna all'oggetto out_cont.
        Una volta riempito, out_cont viene assegnato all'attributo corrispondente
        dell'istanza di OdimHierarchyProfile
        """
        for att in attrs_list:
            if att in hgroup.attrs.keys():
                out_cont.__setattr__(att, hgroup.attrs.__getitem__(att))

        return None

    def get_quantity(self, quantity: str):
        # Metodo di istanza per la lettura del dato associato a "quantity"
        for content in self.datasets.values():
            if content["what"].quantity.decode() == quantity:
                return content["data"].data
        raise KeyError(f"Quantità '{quantity}' non trovata nei dataset.")
    
    def get_what_by_quantity(self, quantity: str):
        # Metodo di istanza per la lettura degli attributi "what" di "quantity"
        for content in self.datasets.values():
            if content["what"].quantity.decode() == quantity:
                return content["what"]
        raise KeyError(f"Quantità '{quantity}' non trovata.")

    def read_vp_odim(self, filename: str) -> None:
        """
        Metodo di istanza della classe OdimHierarchyProfile che legge un file
        ODIM HDF5 di una profilo verticale.
        (vol['what'].attrs['quantity']='VP').

        Il metodo legge il file ODIM e riempie gli attributi dell'istanza di
        OdimHierarchyProfile. Alcuni di questi attributi sono a loro volta
        oggetti di classi che rappresentano le strutture interne del file ODIM
        (gruppi, dataset, ecc.).

        INPUT:
        - filename    --str : filename del file odim da leggere
        """

        hr = h5py.File(filename, "r")
        root=OdimRoot(dict(hr.attrs))

        root_what = OdimWhat(
            hierarchy = "what",
            obj = hr["what"].attrs["object"],
            version = hr["what"].attrs["version"],
            date = hr["what"].attrs["date"],
            time = hr["what"].attrs["time"],
            source = hr["what"].attrs["source"],
        )
        root_where = OdimWhereVertProfile(
            hierarchy = "where",
            lon = hr["where"].attrs["lon"],
            lat = hr["where"].attrs["lat"],
            height = hr["where"].attrs["height"],
            levels = hr["where"].attrs["levels"],
            interval = hr["where"].attrs["interval"],
            minheight = hr["where"].attrs["minheight"],
            maxheight = hr["where"].attrs["maxheight"],
        )
        
        # Del gruppo how leggo solamente gli attributi che servono
        # per il profilo verticale
        root_how = OdimHowVertProfile(hierarchy="how")
        try:
            attrs_how = [
            "dealiased", "vpmethod"
            ]
            self.get_attrs_from_odimgroup(attrs_how, hr["how"], root_how)
        except Exception as e:
            print(f"Warning: gruppo 'how' non leggibile: {e}")
            pass

        # Leggo il dataset presente
        # Andrebbe inserito un controllo su eventuali altri dataset
        dataset_what = OdimWhatDset(hierarchy="dataset1/what")
        attrs_ = ["prodname", "product", "ptype"]
        self.get_attrs_from_odimgroup(attrs_, hr["dataset1/what"], dataset_what)

        # Leggi tutti i dataN presenti in dataset1
        datasets = {}
        n = 1
        while f"dataset1/data{n}" in hr:
            key = f"dataset1/data{n}"
            dw = OdimWhatDset(hierarchy=f"{key}/what")
            self.get_attrs_from_odimgroup(
                ["quantity", "gain", "nodata", "offset", "undetect"],
                hr[f"{key}/what"],
                dw
            )
            datasets[f"data{n}"] = {
                "data": OdimDset(hr[f"{key}/data"][:], f"{key}/data"),
                "what": dw,
            }
            n += 1
            
        hr.close()

        self.setistance(root, root_what, root_where, root_how, dataset_what, datasets)

        return None
