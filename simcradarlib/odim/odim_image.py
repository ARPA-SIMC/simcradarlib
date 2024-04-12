from simcradarlib.odim.odim_utils import (
    OdimDset8bImage,
    OdimWhat,
    OdimWhereGeoimage,
    OdimHow,
    OdimWhatDset,
)
from simcradarlib.io_utils.structure_class import StructBase
import h5py
from typing import Union


class OdimHierarchyImage(StructBase):

    """
    Implementa la gerarchia di un file HDF per una mappa georeferenziata 2D,
    compatibilmente con specifiche ODIM OPERA v.2.1.
    (es: mappa POH; vale per HDF con vol['what'].attrs['object']='IMAGE' o
    vol['what'].attrs['object']='COMP')

    Le classi utilizzate per implementare gli oggetti del file ODIM
    sono implementate in simcradarlib.odim.odim_utils .
    Sono le classi OdimWhat, OdimDset8bImage, OdimWhereGeoimage, OdimHow,
    OdimWhatDset.

    Classe figlia di simcradarlib.io_utils.structure_class.StructBase con
    attributi dell'istanza:

    -root_what:             --OdimWhat        : istanza della classe OdimWhat che
                                                implementa il gruppo "what" del root.
    -root_where:          --OdimWhereGeoimage : istanza della classe OdimWhereGeoimage
                                                che implementa il gruppo "where" del root.
    -root_how:              --OdimHow         : istanza della classe OdimHow che
                                                implementa il gruppo "how" del root.
    -group_dataset_what     --OdimWhatDset    : istanza della classe OdimWhatDset,
                                                che implementa il gruppo "dataset1/what".
    -dataset                --np.ndarray      : istanza della classe OdimDset8bImage,
                                                che implementa il dataset del file ODIM.
                                                L' attributo 'data' di tale istanza di
                                                OdimDset8bImage deve contenere l'array
                                                2D dei dati dell'immagine.
    -group_data_what        --OdimWhatDset    : istanza della classe OdimWhatDset che
                                                implementa il gruppo "dataset1/data1/what".

    GERARCHIA ODIM DATO 'GEOGRAPHICAL IMAGE':
    root:
        |___dataset1 (group):
        |   |_________________ what (group):
        |   |                        +attrs:
        |   |                              - {attributi di classe OdimWhatDset}
        |   |_________________ data1 (group):
        |                      |                data (dataset):
        |                      |                        +attrs:
        |                      |                             -CLASS='IMAGE'
        |                      |                             -IMAGE_VERSION='2.1'
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
        |              -{attributi di classe OdimWhereGeoimage}
        |___how   (group):
        |          +attrs:
        |              - {attributi di classe OdimHow}
    """

    root_what: OdimWhat
    root_where: OdimWhereGeoimage
    root_how: OdimHow
    group_dataset_what: OdimWhatDset
    dataset: OdimDset8bImage
    group_data_what: OdimWhatDset

    def __init__(
        self,
    ):
        super().__init__()

    def setistance(
        self,
        root_what: OdimWhat,
        root_where: OdimWhereGeoimage,
        root_how: OdimHow,
        group_dataset_what: OdimWhatDset,
        dataset: OdimDset8bImage,
        group_data_what: OdimWhatDset,
    ) -> None:
        """
        Metodo di istanza della classe OdimHierarchyImage per
        assegnare ad un'istanza, già creata, di tale classe,
        gli attributi di istanza per tale classe (per dettagli
        consultare documentazione della classe OdimHierarchyImage).

        INPUT:
        -root_what                 --OdimWhat
        -root_where                --OdimWhereGeoimage
        -root_how                  --OdimHow
        -group_dataset_what        --OdimWhatDset
        -dataset                   --OdimDset8bImage
        -group_data_what           --OdimWhatDset
        """

        self.root_what = root_what
        self.root_where = root_where
        self.root_how = root_how
        self.dataset = dataset
        self.group_data_what = group_data_what
        self.group_dataset_what = group_dataset_what

        # verifico che la matrice dei dati sia 2D
        assert self.dataset.data.shape.__len__() == 2

    def get_attrs_from_odimgroup(
        self,
        attrs_list: list,
        hgroup: h5py._hl.group.Group,
        out_cont: Union[OdimDset8bImage, OdimWhat, OdimHow, OdimWhereGeoimage, OdimWhatDset],
    ) -> None:

        """
        Metodo di istanza della classe OdimHierarchyImage, chiamato dal metodo
        simcradarlib.odim.odim_utils.OdimHierarchyImage.read_odim, per
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
        Itera sugli elementi di attrs_list verificando che siano attributi per
        il gruppo 'hgroup' del file ODIM che sto leggendo e, se esistono, assegna
        gli attributi trovati all'oggetto out_cont, istanza della classe del modulo
        simcradarlib.odim.odim_utils la quale implementa quel gruppo o dataset.
        Tale istanza, rappresentativa del gruppo o dataset di cui sono stati letti
        gli attributi dal file ODIM, viene assegnata al valore dell' attributo
        dell'istanza di classe OdimHierarchyImage che deve essere riempito di contenuti.
        """

        for att in attrs_list:
            if att in hgroup.attrs.keys():
                out_cont.__setattr__(att, hgroup.attrs.__getitem__(att))

        return None

    def export_odim(self, out_filename: str) -> None:

        """
        Metodo di istanza della classe OdimHierarchyImage che scrive una
        mappa 2D di dati georeferenziati (tale che vol['what'].attrs['quantity']='IMAGE')
        in formato ODIM OPERA v.2.1.

        Il contenuto del file ODIM che viene scritto è l'insieme degli attributi
        dell'istanza della classe OdimHierarchyImage, su cui viene invocato tale
        metodo.

        INPUT:
        -out_filename   --str : filename del file ODIM in output.
        """

        hf = h5py.File(out_filename, "w")
        self.root_what.odim_create(hf)
        self.root_what.odim_setattrs(hf, ["object", "version", "date", "time", "source"])

        self.root_where.odim_create(hf)
        self.root_where.odim_setattrs(
            hf,
            [
                "projdef",
                "xsize",
                "ysize",
                "xscale",
                "LL_lon",
                "LL_lat",
                "UL_lon",
                "UL_lat",
                "UR_lon",
                "UR_lat",
                "LR_lon",
                "LR_lat",
            ],
        )
        self.root_how.odim_create(hf)
        self.root_how.odim_setattrs(hf, ["task", "startepochs", "system", "software", "sw_version", "endepochs"])

        g_dset_what = self.group_dataset_what
        g_dset_what.odim_create(hf)
        g_dset_what.odim_setattrs(hf, ["product", "startdate", "starttime", "enddate", "endtime"])

        dset = OdimDset8bImage(self.dataset.data, "dataset1/data1/data")
        dset.odim_create(hf)
        dset.odim_setattrs(hf, ["CLASS", "IMAGE_VERSION"])
        dset_what = self.group_data_what
        dset_what.odim_create(hf)
        dset_what.odim_setattrs(hf, ["quantity", "gain", "nodata", "offset", "undetect"])

        hf.close()
        return None

    def read_odim(self, filename: str) -> None:

        """
        Metodo di istanza della classe OdimHierarchyImage che legge un file
        ODIM OPERA v.2.1 di una  mappa 2D di dati georeferenziati
        (vol['what'].attrs['quantity']='IMAGE').

        Il contenuto del file ODIM letto viene assegnato ai vari attributi
        dell'istanza della classe OdimHierarchyImage su cui viene invocato
        tale metodo. Alcuni attributi sono istanze di classi del modulo
        simcradarlib.odim.odim_utils le quali implementano gli oggetti del
        file ODIM.

        INPUT:
        - filename    --str : filename del file odim da leggere
        """

        hr = h5py.File(filename, "r")
        root_what = OdimWhat(
            hierarchy="what",
            obj=hr["what"].attrs["object"],
            version=hr["what"].attrs["version"],
            date=hr["what"].attrs["date"],
            time=hr["what"].attrs["time"],
            source=hr["what"].attrs["source"],
        )
        root_where = OdimWhereGeoimage("where")
        attrswhere = [
            "projdef",
            "xsize",
            "ysize",
            "xscale",
            "yscale",
            "LL_lon",
            "LL_lat",
            "UL_lon",
            "UL_lat",
            "UR_lon",
            "UR_lat",
            "LR_lon",
            "LR_lat",
        ]

        self.get_attrs_from_odimgroup(attrswhere, hr["where"], root_where)
        try:
            attrs_howroot = ["task", "startepochs", "endepochs", "system", "software", "sw_version", "simulated"]
            root_how = OdimHow("how")
            self.get_attrs_from_odimgroup(attrs_howroot, hr["how"], root_how)
        except Exception:
            pass

        # ho un solo dataset per l'unica mappa salvata che leggo
        dataset_what = OdimWhatDset(hierarchy="dataset1/what")
        attrs_ = ["product", "startdate", "starttime", "enddate", "endtime"]
        self.get_attrs_from_odimgroup(attrs_, hr["dataset1/what"], dataset_what)

        data_what = OdimWhatDset(hierarchy="dataset1/data1/what")
        attrs_ = ["quantity", "gain", "nodata", "offset", "undetect"]
        self.get_attrs_from_odimgroup(attrs_, hr["dataset1/data1/what"], data_what)

        data = hr["dataset1/data1/data"][:]
        dataset = OdimDset8bImage(data, "dataset1/data1/data")
        self.get_attrs_from_odimgroup(["CLASS", "IMAGE_VERSION"], hr["dataset1/data1/data"], dataset)
        hr.close()

        self.setistance(root_what, root_where, root_how, dataset_what, dataset, data_what)

        return None
