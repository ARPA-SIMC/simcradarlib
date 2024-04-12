from simcradarlib.io_utils.structure_class import (
    StructTime,
    StructGrid,
    StructProjection,
    StructSource,
    StructVariable,
    RadarProduct,
)
from simcradarlib.io_utils.rad_var_class import VarZ, VarPrmm, VarCumPrmm
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Optional, Union, Tuple, Dict, Any
import logging
import pyproj
import sys

module_logger = logging.getLogger(__name__)


class Bufr:

    """
    Classe per leggere dati in formato BUFR dai files decodificati
    tramite decbufr (idea: aggiungere anche il metodo per la scrittura).

    Attributi di classe:
    source           --StructSource : istanza della classe StructSource per
                                      implementare la struttura con info sulla
                                      provenienza dei dati scritti in un BUFR.
    product          --RadarProduct : istanza della classe RadarProduct per
                                      implementare la struttura con info sul
                                      tipo di prodotto dei dati del BUFR.
    projection   --StructProjection : istanza della classe StructProjection per
                                      implementare la struttura con info sulla
                                      proiezione dei dati del BUFR.
    grid             --StructGrid   : istanza della classe StructGrid per
                                      implementare la struttura con info sul
                                      grigliato dei dati BUFR.
    variabile      --StructVariable : istanza della classe StructVariable per
                                      implementare la struttura con info sulla
                                       variabile relativa ai dati del BUFR.
    time               --StructTime : istanza della classe StructTime per
                                      implementare la struttura con info temporali.
    """

    source: StructSource
    product: RadarProduct
    projection: StructProjection
    grid: StructGrid
    variabile: Union[StructVariable, VarZ, VarPrmm, VarCumPrmm]
    time: StructTime

    def __init__(self):

        pass

    def _check_emptyfield(self, substring: str) -> Optional[str]:

        """
        Metodo che restituisce None se la stringa in input, substring,
        è vuota, altrimenti restituisce substring.

        INPUT:
        - substring   --str : stringa in input.
        OUTPUT:
                      --Union[str,None]: substring se subtring non vuota
                                         altrimenti None.

        Questo metodo è invocato dal metodo di istanza della classe Bufr get_octect()
        per ricostruire gli ottetti nel file di metadati di un BUFR in lettura.
        """

        if substring == "":
            return None
        else:
            return substring

    def get_octect(self, line: str) -> list:

        """
        Metodo che prende in input una riga del file testo dei metadati
        ottenuto dal decbufr (nomebufr.txt) e crea la lista di 8 componenti
        relative ai metadati. Le componenti che corrispondono a campi vuoti vengono
        settati a None tramite il metodo _check_emptyfield (sopra)

        INPUT:
        - line           --str : riga del file di metadati in output alla decodifica
                                 del bufr tramite script C decbufr.
                                 Tale riga è una stringa, contenente 8 componenti
                                 (sottostringhe) sui metadati.
        OUTPUT:
        - octect         --list : lista avente le seguenti 8 componenti
                                  [f_, x_, y_, value, id5, id6, id7, descriptor]

        dove f_,x_,y_ rappresentano il descrittore BUFR, che può essere di diversi tipi:
        (***********************inizio source documentazione Mistral***************************)

        - Element descriptor: f_=0, x_=classe del descrittore, y_=entry within a class x_
                              (Tabella B)
        - Replica di numero predefinito di descrittori:
                               f_=1, x_=numero di descrittori da replicare, y_=numero di repliche
                               (y_=0 guarda documentazione)
        - Operator descriptor: f_=2, x_=identifica operatore, y_=valore per controllo sull'uso dell'
                                operatore. (Tabella C)
        - Sequence descriptor: f_=3, x_ e y_ indicano rispettivamente la classe del descrittore e
                               l'entry della classe come per Element descriptor (in questo caso però
                               si identificano gli elementi di Tabella D)
        Nel caso di dati prodotti da centri di emissioni locali che necessitano di una rappresentazione
        non definita nella Tabelle B, si riserva una parte delle tabelle B e D ad uso locale.

        Nota: f_ è rappresentato come numero a 2bits, x_ come numero a 6bits, y_ come numero a 8bits
        (********************************fine source documentazione***********************)

        In particolare in questa implementazione:
        f_ = primi 2 caratteri della stringa line in input.
        y_ = sottostringa dal 3° al 5° carattere di line.
        x_= sottostringa dal 6° al 9° carattere di line.
        value = sottostringa dal 10° al 23° carattere di line tranne quando (f_=='3',x_=='21',y_=='193')
        id5 = sottostringa dal 24° al 27° carattere di line tranne quando (f_=='3',x_=='21',y_=='193')
        id6 = sottostringa dal 28° al 32° carattere di line tranne quando (f_=='3',x_=='21',y_=='193')
        id7 = sottostringa dal 33° al 35° carattere di line tranne quando (f_=='3',x_=='21',y_=='193')
        descriptor = sottostringa dal 36° carattere di line tranne quando (f_=='3',x_=='21',y_=='193')

        infatti quando (f_=='3',x_=='21',y_=='193') la sottostringa successiva a 'f_ x_ y_' contiene il nome
        del file di metadati in input e settiamo le componenti id5,id6,id7 della lista octect a None, la
        componente value pari al resto della sottostringa e la componente descriptor='namefile'.
        """

        f_ = line[:2].strip()
        x_ = line[2:5].strip()  # 6bit
        y_ = line[5:9].strip()  # 8bit
        if f_ == "3" and x_ == "21" and y_ == "193":
            value = line[9:].strip()
            id5 = ""
            id6 = ""
            id7 = ""
            descriptor = "namefile"
        else:
            value = line[9:23].strip()
            id5 = line[23:27].strip()
            id6 = line[27:32].strip()
            id7 = line[32:35].strip()
            descriptor = line[35:].strip()

        octect = [f_, x_, y_, value, id5, id6, id7, descriptor]
        return [self._check_emptyfield(o) for o in octect]

    def read_meta(self, fname_meta: str) -> pd.DataFrame:

        """
        Metodo che legge il file di metadati decodificato dal BUFR tramite decbufr e
        restituisce un oggetto DataFrame di pandas, con le info sui metadati del BUFR.

        INPUT:
        - fname_meta    --str : nome del file di testo con i metadati del file BUFR
                                (ottenuto dalla decodifica tramite decbufr, es:
                                nomebufr.txt).

        OUTPUT:
        - df            --pd.DataFrame : oggetto DataFrame di pandas, avente colonne
                                         ["F", "X", "Y", "value", "id5", "id6", "id7", "descriptor"].
                                         Ciascuna riga del DataFrame ha 8 elementi ( uno per ogni
                                         colonna) i quali sono l'ottetto corrispondente ad una riga
                                         del file di metadati (nomebufr.dat ottenuto con decbufr).
                                         L'ottetto di descrittori su ciascuna riga del file dei metadati
                                         è letta tramite il metodo di istanza della classe Bufr
                                         simcradarlib.io_utils.bufr_class.Bufr.get_octect .
                                         Ciascun ottetto viene inserito come nuova riga del DataFrame
                                         'df'.

                                         In particolare per ogni riga, nella colonna "F" viene
                                         inserito il valore del descrittore f_, documentato in
                                         simcradarlib.io_utils.bufr_class.Bufr._check_emptyfield,
                                         di ciascun ottetto del file dei metadati.
                                         Analogamente la colonna "X" contiene i valori del descrittore
                                         x_ , la colonna "Y" i valori del descrittore y_, le
                                         colonna "id5" "id6 "id7" contengono rispettivamente i valori
                                         delle sottostringhe dal 24° al 27°, dal 28° al 32°,
                                         dal 33° al 35° carattere di ciascuna riga del file dei
                                         metadati. La colonna "descriptor" contiene i valori dalla
                                         36° carattere di ogni riga del file dei metadati.
                                         Per maggiori dettagli (e eccezioni) consultare la
                                         documentazione del metodo
                                         simcradarlib.io_utils.bufr_class.Bufr._check_emptyfield .
        """

        with open(fname_meta) as file:
            lines = [line for line in file]

        dfb = []
        for line in lines:
            dfb.append(self.get_octect(line))
        df = pd.DataFrame(dfb, columns=["F", "X", "Y", "value", "id5", "id6", "id7", "descriptor"])

        return df

    def get_acc_time_from_meta(self) -> int:

        """
        Metodo che legge nell'oggetto DataFrame di pandas,
        in cui sono storati i metadati del file BUFR,
        il tempo di cumulata se il campo è una cumulata.
        Se il campo è istantaneo o la lettura di acc_time fallisce,
        restituisce l'intero acc_time=0 di default.

        L'oggetto DataFrame di pandas in cui sono storati i metadati del file BUFR
        è ottenuto in output dal metodo simcradarlib.io_utils.bufr_class.read_meta().
        Quando viene invocato il metodo di istanza
        simcradarlib.io_utils.bufr_class.read_bufr() per leggere il BUFR, tale
        DataFrame viene assegnato all'attributo di istanza 'meta'.
        (Per questo nel codice si accede ad esso tramite self.meta)

        OUTPUT:
        acc_time        --int : intero corrispondente al tempo di cumulata in ore se il
                                campo è cumulato, 0 altrimenti.

        """

        index_timesignificance = self.meta.loc[
            (self.meta.F == "0") & (self.meta.X == "8") & (self.meta.Y == "21")
        ].index.values
        acc_time = 0
        if index_timesignificance.__len__() > 0 and float(self.meta.iloc[index_timesignificance[0]].value) == 3.0:
            try:
                ind_t = self.meta.loc[(self.meta.F == "0") & (self.meta.X == "4") & (self.meta.Y == "23")].index.values[
                    0
                ]
                acc_time -= int(24 * float(self.meta.iloc[ind_t].value))
            except (IndexError, KeyError, TypeError):
                module_logger.warning("Non trovo time period per descrittori F=0,X=4,Y=23")
            try:
                ind_t2 = self.meta.loc[
                    (self.meta.F == "0") & (self.meta.X == "4") & (self.meta.Y == "24")
                ].index.values[0]
                acc_time -= int(float(self.meta.iloc[ind_t2].value))
            except (IndexError, KeyError, TypeError):
                module_logger.warning("Non trovo time period per descrittori F=0,X=4,Y=24")
        return int(acc_time)

    def get_datetime_from_meta(self) -> Optional[datetime]:

        """
        Metodo che legge le informazioni temporali nell'oggetto DataFrame di pandas,
        in cui sono storati i metadati del BUFR, e restituisce l'oggetto datetime
        corrispondente, con la data di validità del campo.

        L'oggetto DataFrame di pandas in cui sono storati i metadati del file BUFR
        è ottenuto in output dal metodo simcradarlib.io_utils.bufr_class.read_meta().
        Quando viene invocato il metodo di istanza
        simcradarlib.io_utils.bufr_class.read_bufr() per leggere il BUFR, tale
        DataFrame viene assegnato all'attributo di istanza 'meta'.
        (Per questo nel codice si accede ad esso tramite self.meta)

        OUTPUT:
        - dt            --datetime : oggetto datetime.datetime contenente la dataora di
                                     validità dei dati nel file BUFR.
        """

        year, month, day, hour, minutes = (-99, -99, -99, -99, -99)
        try:
            index_year = self.meta.loc[
                (self.meta.F == "3") & (self.meta.X == "1") & (self.meta.Y == "11")
            ].index.values[0]
            year = int(float(self.meta.iloc[index_year].value))
        except IndexError:
            module_logger.error("Non trovo YEAR (F=3,X=1,Y=11)")

        try:
            subdf = self.meta.iloc[index_year + 1]
            if subdf.F is None and subdf.X is None and subdf.Y is None:
                month = int(float(subdf.value))
            subdf = self.meta.iloc[index_year + 2]
            if subdf.F is None and subdf.X is None and subdf.Y is None:
                day = int(float(subdf.value))
        except IndexError:
            module_logger.error("Mese e giorno non estratti")

        try:
            index_hour = self.meta.loc[
                (self.meta.F == "3") & (self.meta.X == "1") & (self.meta.Y == "12")
            ].index.values[0]
            hour = int(float(self.meta.iloc[index_hour].value))
            subdf = self.meta.iloc[index_hour + 1]
            if subdf.F is None and subdf.X is None and subdf.Y is None:
                minutes = int(float(subdf.value))
        except IndexError:
            module_logger.exception("non trovo campi 'hour,minutes'")

        try:
            year = year if year != -99.0 else 0
            month = month if month != -99.0 else 0
            day = day if day != -99.0 else 0
            hour = hour if hour != -99.0 else 0
            minutes = minutes if minutes != -99.0 else 0

            dt = datetime(year, month, day, hour, minutes)
        except ValueError:
            module_logger.exception("non sono stati letti i campi Y,m,d,H,M")
            dt = None
        return dt

    def get_source_product_from_meta(self) -> Tuple[StructSource, RadarProduct]:

        """
        Metodo che a partire dall'oggetto DataFrame di pandas,
        in cui sono storati i metadati del BUFR, crea un'istanza
        della classe simcradarlib.io_utils.structure_class.StructSource,
        con le informazioni sulla provenienza dei dati, ed un'istanza
        della classe simcradarlib.io_utils.structure_class.RadarProduct,
        con informazioni sul prodotto.

        L'oggetto DataFrame di pandas in cui sono storati i metadati del file BUFR
        è ottenuto in output dal metodo simcradarlib.io_utils.bufr_class.read_meta().
        Quando viene invocato il metodo di istanza
        simcradarlib.io_utils.bufr_class.read_bufr() per leggere il BUFR, tale
        DataFrame viene assegnato all'attributo di istanza 'meta'.
        (Per questo nel codice si accede ad esso tramite self.meta)

        Se la lettura dei metadati sul 'source' fallisce, restituisce
        l'istanza della classe StructSource con valori di default per gli attributi
        di classe (non sarà presente 'emission_center' tra gli attributi).
        Analogamente per l'istanza di RadarProduct.

        OUTPUT:
        -(source_struct, prod_struct)     --Tuple[StructSource, RadarProduct]:
                        tupla di due elementi, rispettivamente un'istanza della classe
                        simcradarlib.io_utils.structure_class.StructSource, con le
                        informazioni sulla provenienza dei dati, ed un'istanza della
                        classe simcradarlib.io_utils.structure_class.RadarProduct,
                        con le informazioni sul tipo di prodotto dei dati nel file BUFR.

                        In particolare, l'istanza di StructSource creata ha attributi:

                        - name_source       --str : nome della sorgente dati
                                                    (es:
                                                    'GAT', 'SPC' per Arpae,
                                                    'Bric della Croce,Monte Settepani'
                                                    per ArpaP,
                                                    'Mosaico radar nazionale' per DPC
                                                     ).
                        - emission_center   --str : nome del centro emissione del BUFR
                                                    (es: "Arpae Emilia-Romagna",
                                                    "Arpa Piemonte","DPC").
                        - name_file         --str : nome del file BUFR.

        NB: Differenze rispetto ad IDL:
        1.  L'attributo 'name_source' non era presente in IDL.
            In questa implementazione, per i BUFR di Arpa Piemonte
            l'attributo 'name_source' vale "Bric della Croce,Monte Settepani",
            per i BUFR di Arpae Emilia-Romagna 'name_souce' vale "SPC" per
            i BUFR di Z di SPC e vale "GAT" per i BUFR di Z di "GAT",
            mentre per i BUFR del DPC vale "Mosaico radar nazionale".
            Questa scelta dei valori di 'name_source' è stata fatta in corso
            di implementazione della libreria ma si può cambiare.
        2.  L'attributo 'emission_center' in IDL aveva valori diversi:
            In particolare:
            in IDL 'emission_center' = "ER" per i BUFR di Arpae Emilia-Romagna,
            mentre in questa implementazione vale "Arpae Emilia-Romagna".
            Per i BUFR di Arpa Piemonte, in IDL 'emission_center' valeva
            "PIEM", mentre in questa implementazione vale "Arpa Piemonte".
            Per i BUFR del DPC, 'emission_center' è invece rimasto uguale
            e vale "DPC".
            Questo potrebbe al più provocare conflitti con la grafica radar di
            Arpae-SIMC (in teoria no).
        """

        source_struct = StructSource()
        prod_struct = RadarProduct()
        try:
            index_ = self.meta.loc[self.meta.descriptor == "namefile"].index.values[0]
            namefile = self.meta.iloc[index_].value.split(".")[0]
            if "EMRO" in namefile:
                radar = namefile.split("_")[3].strip("@")
                source_struct.name_source = radar  # come per netcdf
                source_struct.addparams("emission_center", "Arpae Emilia-Romagna")  # idl era ER
                prod = namefile.split("_")[4].strip("@")
                prod = "LBM" if prod == "CZ" else prod
            elif "PIEM" in namefile:
                source_struct.name_source = "Bric della Croce,Monte Settepani"  # o TORINO? me lo invento
                source_struct.addparams("emission_center", "Arpa Piemonte")  # idl era PIEM
                prod = namefile.split("_")[4].strip("@")
            elif "ROMA" in namefile:
                source_struct.name_source = "Mosaico radar nazionale"  # me lo invento
                source_struct.addparams("emission_center", "DPC")  # idl era DPC
                prod = namefile.split("_")[2].strip("@")
            else:
                pass

            source_struct.name_file = f"{namefile}.BUFR"

        except Exception:
            module_logger.exception("lettura source fallita")
        try:
            prod = "SRI" if prod == "SR" else prod
            prod_struct = RadarProduct(prod)
        except Exception:
            module_logger.exception("lettura product fallita")

        return source_struct, prod_struct

    def get_projection_from_meta(self) -> StructProjection:

        """
        Metodo che legge i dati sulla proiezione dal DataFrame pandas in cui sono storati i metadati
        del BUFR e crea l'istanza della classe simcradarlib.io_utils.structure_class.StructProjection.

        L'oggetto DataFrame di pandas in cui sono storati i metadati del file BUFR è ottenuto in output
        dal metodo simcradarlib.io_utils.bufr_class.read_meta().
        Quando viene invocato il metodo di istanza simcradarlib.io_utils.bufr_class.read_bufr() per leggere il
        BUFR, tale DataFrame viene assegnato all'attributo di istanza 'meta' (per questo nel codice si accede
        ad esso tramite self.meta).

        OUTPUT:
        - proj_struct    --StructProjection :
                                      istanza della classe
                                      simcradarlib.io_utils.structure_class.StructProjection,
                                      avente attributi:

                                      center_longitude   --Optional[float] = None :
                                                             longitudine del centro di proiezione.
                                      center_latitude    --Optional[float] = None :
                                                             latitudine del centro di proiezione.
                                      semimajor_axis     --Union[float,int]= 0.0  :
                                                             semiasse maggiore dell'ellipsoide della proiezione.
                                      semiminor_axis     --Union[float,int]= 0.0  :
                                                             semiasse minore dell'ellipsoide della proiezione.
                                      x_offset           --Union[float,int]= 0.0  :
                                                             valore x del centro del grigliato (UTM)
                                                             (nella documentazione IDL è però indicato come
                                                             lower left corner dell'output).
                                      y_offset           --Union[float,int]= 0.0  :
                                                             valore y del centro del grigliato (UTM)
                                                             (nella documentazione IDL è però indicato come
                                                             lower left corner dell'output).
                                      standard_par1      --Union[float,int]= 0.0  :
                                                             latitudine in gradi del primo parallelo standard
                                                             su cui la scala è corretta. Il valore deve essere
                                                             compreso tra -90 e 90 gradi. NB: per proiezioni
                                                             Albers Equal Area and Lambert Conformal Conic,
                                                             standard_par1 e standard_par2 non devono avere
                                                             valori uguali e opposti (da documentazione IDL
                                                             di MAP_PROJ_INIT).
                                      standard_par2      --Union[float,int]= 0.0  :
                                                             latitudine in gradi del secondo parallelo standard
                                                             su cui la scala è corretta. Il valore deve essere
                                                             compreso tra -90 e 90 gradi. NB: per proiezioni
                                                             Albers Equal Area and Lambert Conformal Conic,
                                                             standard_par1 e standard_par2 non devono avere
                                                             valori uguali e opposti (da documentazione IDL
                                                             di MAP_PROJ_INIT).
                                      proj_id            --Optional[int] = None   :
                                                             intero identificativo della proiezione
                                      proj_name          --Optional[str] = None   :
                                                             nome del tipo di proiezione
                                      earth_radius       --Optional[float] = None :
                                                             raggio terrestre
                                      pyprojstring       --str (solo per proj_id=6,9,101)  :
                                                             stringa della proiezione secondo standard di pyproj
                                      zone               --int (solo per proj_id=101): intero della zona (UTM),
                                                             compreso tra 1 e 60 per l'emisfero boreale.

        Se la lettura fallisce viene restituita l'istanza con attributi di classe settati ai valori di default.

        Differenze rispetto a IDL:
        1.  Per attinenza alle convenzioni Python PEP 8 sul name styling
            (https://peps.python.org/pep-0008/#naming-conventions), alcune variabili sono
            state rese 'lowercase' in questa implementazione, mentre in IDL erano 'UPPER_CASE'.
            Tali variabili sono:
            SEMIMAJOR_AXIS, SEMIMINOR_AXIS, STANDARD_PAR1, STANDARD_PAR2, ZONE.
        """

        proj_struct = StructProjection()
        try:
            index_clon = self.meta.loc[
                (self.meta.F == "0") & (self.meta.X == "29") & (self.meta.Y == "193")
            ].index.values[0]
            proj_struct.center_longitude = float(self.meta.iloc[index_clon].value)
        except IndexError:
            module_logger.warning("non leggo center longitude")

        try:
            index_clat = self.meta.loc[
                (self.meta.F == "0") & (self.meta.X == "29") & (self.meta.Y == "194")
            ].index.values[0]
            proj_struct.center_latitude = float(self.meta.iloc[index_clat].value)
        except IndexError:
            module_logger.warning("non leggo center latitude")

        try:
            index_ = self.meta.loc[(self.meta.F == "0") & (self.meta.X == "29") & (self.meta.Y == "199")].index.values[
                0
            ]
            proj_struct.addparams("semimajor_axis", float(self.meta.iloc[index_].value))
        except IndexError:
            module_logger.warning("non leggo semimajor axis, setto a 0")
            proj_struct.addparams("semimajor_axis", 0.0)

        try:
            index_ = self.meta.loc[(self.meta.F == "0") & (self.meta.X == "29") & (self.meta.Y == "200")].index.values[
                0
            ]
            proj_struct.addparams("semiminor_axis", float(self.meta.iloc[index_].value))
        except IndexError:
            module_logger.warning("non leggo semiminor axis, setto a 0")
            proj_struct.addparams("semiminor_axis", 0.0)

        try:
            index_ = self.meta.loc[(self.meta.F == "0") & (self.meta.X == "29") & (self.meta.Y == "195")].index.values[
                0
            ]
            # per il DPC (quando bufrnamefile contiene 'ROMA') x_offset = -x_offset
            xoffset = float(self.meta.iloc[index_].value)
            if self.source.emission_center == "DPC" and xoffset > 0:
                xoffset = -xoffset
            proj_struct.addparams("x_offset", xoffset)
        except IndexError:
            module_logger.warning("non leggo x_offset, setto a 0")
            proj_struct.addparams("x_offset", 0.0)

        try:
            index_ = self.meta.loc[(self.meta.F == "0") & (self.meta.X == "29") & (self.meta.Y == "196")].index.values[
                0
            ]
            proj_struct.addparams("y_offset", float(self.meta.iloc[index_].value))
        except IndexError:
            module_logger.warning("non leggo y_offset, setto a 0")
            proj_struct.addparams("y_offset", 0.0)

        try:
            index_ = self.meta.loc[(self.meta.F == "0") & (self.meta.X == "29") & (self.meta.Y == "197")].index.values[
                0
            ]
            proj_struct.addparams("standard_par1", float(self.meta.iloc[index_].value))
        except IndexError:
            module_logger.warning("non leggo standard_par1, setto a 0")
            proj_struct.addparams("standard_par1", 0.0)

        try:
            index_ = self.meta.loc[(self.meta.F == "0") & (self.meta.X == "29") & (self.meta.Y == "198")].index.values[
                0
            ]
            proj_struct.addparams("standard_par2", float(self.meta.iloc[index_].value))
        except IndexError:
            module_logger.warning("non leggo standard_par2, setto a 0")
            proj_struct.addparams("standard_par2", 0.0)

        try:
            # qui potrei anzichè usare  f,x,y=0,29,201 o 1 , potrei invece filtrare su descriptor='Projection type'
            index_ = self.meta.loc[(self.meta.F == "0") & (self.meta.X == "29") & (self.meta.Y == "201")].index.values
            if index_.__len__() > 0:
                index_ = index_[0]
            else:
                index_ = self.meta.loc[
                    (self.meta.F == "0") & (self.meta.X == "29") & (self.meta.Y == "1")
                ].index.values[0]

            proj_type_int = int(float(self.meta.iloc[index_].value))
            if proj_type_int == 0:
                # 0: Azimuthal Equidistant
                # proj_struct.proj_id = 6 # tolgo proj_id residuo idl
                if self.source.emission_center == "Arpae Emilia-Romagna":
                    proj_struct.projection_index = 0
                    if self.source.name_source == "GAT":
                        proj_struct.center_longitude = 10.4992
                        proj_struct.center_latitude = 44.7914
                    elif self.source.name_source == "SPC":
                        proj_struct.center_longitude = 11.6236
                        proj_struct.center_latitude = 44.6547
                    else:
                        module_logger.warning(
                            f"source_name non noto:{self.source.name_source}\n non setto center lon-lat"
                        )
                    # aggiungo proj_name,Earth radius come per zlr
                    # aggiungo anche pyprojstring
                    proj_struct.proj_name = "Cartesian lat-lon"
                    proj_struct.earth_radius = 6370.997
                    pyprojstring = f"+proj=eqc +lat_0={proj_struct.center_latitude:.4f} \
    +lon_0={proj_struct.center_longitude:.4f} +ellps=WGS84 +R={proj_struct.earth_radius:.4f}"
                    proj_struct.addparams("pyprojstring", pyprojstring)

            elif proj_type_int == 1:
                # 1 stereographic - 106 polar stereographic
                if proj_struct.center_latitude == 90.0:
                    # stereografica polare (idl)
                    # proj_struct.proj_id = 106 # tolgo proj_id residuo idl
                    proj_struct.proj_name = "Polar stereographic"
                    proj_struct.center_latitude = proj_struct.stand_par1
                else:
                    # stiamo utilizzando la stereografica normale non devo ridefinire i parametri
                    # proj_struct.proj_id = 1 # tolgo proj_id residuo idl
                    proj_struct.proj_name = "Stereographic"
            elif proj_type_int == 2:
                # proj_struct.proj_id = 104  # lambert conical # tolgo proj_id residuo idl
                proj_struct.proj_name = "Lambert Conformal Conic"
                # proj_struct.addparams(["STANDARD_PAR1","STANDARD_PAR2"],[stand_par1,stand_par2]) gia fatto
            elif proj_type_int == 3:
                # salto la parte che entra nel if keyword set = DPC
                if self.source.emission_center == "DPC":
                    # proj_struct.proj_id = 9 # tolgo proj_id residuo idl
                    # per il DPC utilizzo la proiezione mercatore e
                    # impongo il raggio della sfera visto che DATAMAT ha utilizzato questi parametri
                    if (proj_struct.semimajor_axis, proj_struct.semiminor_axis) == (0.0, 0.0):
                        proj_struct.semimajor_axis = 6370997.0
                        proj_struct.semiminor_axis = 6370997.0
                        proj_struct.earth_radius = 6370997.0
                    else:
                        proj_struct.earth_radius = proj_struct.semimajor_axis
                        # pyprojstring='+proj=tmerc +lat_0=42.0 +lon_0=12.5 +ellps=WGS84'
                    pyprojstring = f"+proj=tmerc +lat_0={proj_struct.center_latitude:.1f} \
    +lon_0={proj_struct.center_longitude:.1f} +ellps=WGS84"
                    proj_struct.addparams("pyprojstring", pyprojstring)
                    proj_struct.proj_name = "tmerc"  # =pyproj.Proj(pyprojstring).name

                elif self.source.emission_center == "Arpa Piemonte":
                    # piemonte codifica in UTM:
                    # proj_struct.proj_id = 101 #in lettura togliamo residui di idl
                    proj_struct.earth_radius = 6378388.0
                    proj_struct.proj_name = "UTM"
                    proj_struct.addparams(["semimajor_axis", "semiminor_axis", "zone"], [6378388.0, 6356911.94613, 32])
                    # per il piemonte calcolo anche parametri x_offset e y_offset che non vengono passati
                    pyprojstring = "+proj=utm +zone=32 +k_0=0.9996 +ellps=intl"
                    piem_proj = pyproj.Proj(pyprojstring)
                    proj_struct.addparams("pyprojstring", pyprojstring)
                    proj_struct.proj_name = piem_proj.name  # = 'utm'
                    # oppure posso scrivere proj_name'utm intl' (International 1909 (Hayford) )

                    index_ = self.meta.loc[
                        (self.meta.F == "3") & (self.meta.X == "1") & (self.meta.Y == "23")
                    ].index.values[0]
                    lat_nw = float(self.meta.iloc[index_].value)
                    lon_nw = round(float(self.meta.iloc[index_ + 1].value), 1)
                    xoffset, yoffset = piem_proj(lon_nw, lat_nw)
                    proj_struct.addparams(["x_offset", "y_offset"], [xoffset, yoffset])

                else:
                    # proj_struct.proj_id = 9 # tolgo proj_id residuo idl
                    proj_struct.proj_name = "Mercator"
            elif proj_type_int == 4:
                # proj_struct.proj_id = 6 # tolgo proj_id residuo idl
                proj_struct.proj_name = "Azimuthal Equidistant"
            elif proj_type_int == 5:
                # proj_struct.proj_id = 4 # tolgo proj_id residuo idl
                proj_struct.proj_name = "Lambert Azimuthal"
            else:
                module_logger.warning("proj_type_int non noto")

        except IndexError:
            module_logger.warning("non leggo descriptor 'Projection type'")

        except AttributeError:
            module_logger.exception("tentativo di accesso ad attributo inesistente")

        return proj_struct

    def get_grid_from_meta(self) -> StructGrid:

        """
        Metodo che legge le informazioni sul grigliato dei dati BUFR dall'oggetto
        DataFrame pandas in cui sono storati e crea istanza di classe
        simcradarlib.io_utils.structure_class.StructGrid.

        L'oggetto DataFrame di pandas in cui sono storati i metadati del file BUFR
        è ottenuto in output dal metodo simcradarlib.io_utils.bufr_class.read_meta().
        Quando viene invocato il metodo di istanza
        simcradarlib.io_utils.bufr_class.read_bufr() per leggere il BUFR, tale
        DataFrame viene assegnato all'attributo di istanza 'meta'.
        (Per questo nel codice si accede ad esso tramite self.meta)

        OUTPUT:
        - grid_struct      --StructGrid : istanza della classe
                                          simcradarlib.io_utils.structure_class.StructGrid.
        Differenze rispetto a IDL:
        In questa implementazione sono stati aggiunti gli attributi 'units_dx' e 'units_dy'
        in quanto attributi di istanza della classe StructGrid, che implementa la
        struttura con le informazioni sul grigliato.
        """

        grid_struct = StructGrid()
        try:
            grid_struct.addparams(
                "ny",
                int(
                    float(
                        self.meta.loc[
                            (self.meta.F == "0") & (self.meta.X == "30") & (self.meta.Y == "22")
                        ].value.values[0]
                    )
                ),
            )
            grid_struct.addparams(
                "nx",
                int(
                    float(
                        self.meta.loc[
                            (self.meta.F == "0") & (self.meta.X == "30") & (self.meta.Y == "21")
                        ].value.values[0]
                    )
                ),
            )
        except IndexError:
            module_logger.warning("non setto numero punti griglia nx e ny")

        try:
            grid_struct.dy = float(
                self.meta.loc[(self.meta.F == "0") & (self.meta.X == "6") & (self.meta.Y == "33")].value.values[0]
            )
            grid_struct.dx = float(
                self.meta.loc[(self.meta.F == "0") & (self.meta.X == "5") & (self.meta.Y == "33")].value.values[0]
            )
        except IndexError:
            module_logger.warning("non setto pixelsize orizzontale nè verticale")
        # chiedi se units_dx e units_dy sono sempre in m, direi di si perchè calcola tutto in utm
        grid_struct.units_dx = "meters"
        grid_struct.units_dy = "meters"

        # ------------------------------------------------------------------------------
        # per EMR e abruzzo quando sono in gnomonica calcolo x_offset e y_offset
        # non capisco perchè c'è questo pezzo visto che i bufr SPC e GAT hanno già xoffset e yoffset
        # si può togliere? e mettere solo myproj.x_offset ecc
        # per ora commentiamo
        # if self.projection.proj_id == 5 and self.source.emission_center == "Arpae Emilia Romagna":
        # x_offset = -grid_struct.nx * 0.5 * grid_struct.dx
        # y_offset = grid_struct.ny * 0.5 * grid_struct.dy
        # else:
        # x_offset, y_offset = (self.projection.x_offset, self.projection.y_offset)
        x_offset, y_offset = (self.projection.x_offset, self.projection.y_offset)

        grid_struct.limiti = np.array(
            [y_offset - grid_struct.ny * grid_struct.dy, x_offset, y_offset, x_offset + grid_struct.nx * grid_struct.dx]
        )

        # --------------------------------------------------------------------------------
        return grid_struct

    def get_var_levs_from_meta(
        self, fill_method: str
    ) -> Tuple[Union[StructVariable, VarZ, VarPrmm, VarCumPrmm], np.array]:

        """
        Metodo che legge informazioni sulla variabile dei dati nel BUFR dal DataFrame in cui sono storati
        e crea un'istanza della classe figlia di StructVariable implementata nel modulo
        simcradarlib.io_utils.rad_var_class .

        Viene inoltre ricavato l'array dei livelli, cioè le classi di valori possibili per la variabile.
        Infatti nei BUFR il campo dei dati non è trattato come un campo continuo ma come categorico,
        cioè si assume che il campo ammette nei singoli punti griglia un insieme finito di valori.

        I livelli vengono utilizzati nell'estrazione dei valori del campo di dati successivamente.

        L'oggetto DataFrame di pandas in cui sono storati i metadati del file BUFR è ottenuto in output
        dal metodo simcradarlib.io_utils.bufr_class.read_meta().
        Quando viene invocato il metodo di istanza simcradarlib.io_utils.bufr_class.read_bufr() per leggere
        il BUFR, tale DataFrame viene assegnato all'attributo di istanza 'meta'(per questo nel codice si
        accede ad esso tramite self.meta).

        ______________________________________Approfondimento:____________________________________________

        Questo approfondimento serve solo per avere un'idea di come sono i dati del campo in un BUFR.
        Dal file BUFR vengono letti i livelli con i quali si individua una sequenza :
        ad esempio se i livelli letti sono [l0, l1, l2, l3 ] allora si considera che l'asse dei valori
        è dato da:
                        l0               l1                 l2            l3
                         |_______________|__________________|_____________|

        che equivale a individuare 3 classi di valori, con estremi [l0,l1], [l1,l2], [l2,l3] rispettivamente.
        L'insieme finale di valori ammessi per il campo (chiamati anch'essi livelli, sarebbero i veri
        livelli finali) è ottenuto prendendo il minimo per ogni classe se fill_method='min', il massimo su
        ogni classe se fill_method='max' e la media degli estremi se fill_method='ave'.
        In questo esempio, se fill_method è
        - 'min' ---> livelli finali sono [l0,l1,l2]
        - 'max' ---> livelli finali sono [l1,l2,l3]
        - 'ave' ---> livelli finali sono [(l0+l1)/2,(l1+l2)/2,(l2+l3)/2]
        In realtà in questo insieme finale di livelli, il primo livello è sempre il 'lower_bound' letto
        dal file BUFR.
        __________________________________________________________________________________________________

        INPUT:
        - fill_method        --str: indica il criterio con cui costruire la lista dei livelli
                                    -'min' se i livelli sono definiti sul bottom della classe
                                    -'ave' se i livelli sono la media tra gli estremi della classe
                                    -'max' se i livelli sono definiti sul top della classe
                                    Il primo livello è sempre dato dal lower bound e viene letto dal BUFR.

        OUTPUT:
        - ( struct_var, levels):    --Tuple : tupla di due elementi che sono
                                              - struct_var   --Union[StructVariable,VarZ,VarPrmm,VarCumPrmm] :
                                                                    classe figlia di variabile che implementa
                                                                    il tipo di variabile dei dati BUFR.
                                              - levels       --np.array[float] :
                                                                    array dei livelli che identificano le classi
                                                                    di valori possibili per la variabile.
        """

        # le tabelle delle variabili radar usate in idl sono in
        # /autofs/radar/radar/file_x_idl/tabelle/

        index_z = self.meta.loc[(self.meta.F == "3") & (self.meta.X == "13") & (self.meta.Y == "9")].index.values
        index_rr = self.meta.loc[(self.meta.F == "3") & (self.meta.X == "13") & (self.meta.Y == "10")].index.values
        index_cum = self.meta.loc[(self.meta.F == "3") & (self.meta.X == "13") & (self.meta.Y == "11")].index.values
        index_cum2 = self.meta.loc[(self.meta.F == "0") & (self.meta.X == "13") & (self.meta.Y == "11")].index.values

        struct_var = StructVariable()
        if index_z.__len__() > 0:
            struct_var = VarZ()
            index_ = index_z[0]
        elif index_rr.__len__() > 0:
            struct_var = VarPrmm()
            index_ = index_rr[0]
        elif index_cum.__len__() > 0 or index_cum2.__len__() > 0:
            struct_var = VarCumPrmm()
            try:
                index_ = index_cum[0]
            except IndexError:
                index_ = index_cum2[0]
        else:
            raise Exception("Non ho capito cosa contiene il bufr. Esco")
            sys.exit()

        # leggo anche i livelli
        low_bounds = float(self.meta.iloc[index_].value)
        if self.source.emission_center == "DPC" and struct_var.name == "Z" and low_bounds == 0:
            low_bounds = -31  # patch per parare buco di Datamat
        if (self.meta.iloc[index_ + 1].F, self.meta.iloc[index_ + 1].X, self.meta.iloc[index_ + 1].Y) == (
            "1",
            "1",
            "0",
        ):
            index_ = index_ + 1

        # il numero di livelli è scritto nella riga dopo il primo record con descriptor=var.name
        nlev = max(0, int(float(self.meta.iloc[index_ + 1].value)))

        # prendo tutti i livelli in ordine crescente e se un livello è 'missing' non lo considero
        ind_levs = np.concatenate([np.array([index_]), range(index_ + 2, index_ + 2 + nlev)])
        levels = self.meta.iloc[ind_levs].value.values
        levels = levels[levels != "missing"].astype(float)
        # il primo elemento di levels è low_bound e verifico che gli altri siano +grandi
        levels[1:] = np.array([l for l in levels.astype(float) if l > low_bounds])
        levels[0] = low_bounds

        if fill_method == "min":
            # livelli sono definiti sul bottom della classe
            levels[1:] = levels[0:-1]
        elif fill_method == "ave":
            levels[1:] = np.array([np.mean(levels[i: i + 2]) for i in range(levels.__len__() - 1)])
        elif fill_method == "max":
            # levels[1:] = levels[1:] passo tanto non fa niente
            pass
        else:
            raise Exception("Parametro fill_method passato in modo scorretto. Esco")
            sys.exit()

        return struct_var, levels

    def read_bufr(
        self, fname_bufr_data: str, fname_bufr_meta: str, fill_method: str
    ) -> Tuple[
        Dict[
            str,
            Union[StructTime, StructGrid, StructProjection, StructSource, RadarProduct, VarZ, VarPrmm, VarCumPrmm, Any],
        ],
        Union[Any, np.array],
    ]:

        """
        Metodo che legge il file dei metadati e il file binario dei dati ottenuti dalla decodifica
        di un BUFR e restituisce una tupla. Il primo elemento è la macrostruttura dei metadati in
        formato dizionario, avente come chiavi ['TIME','GRID','PROJECTION','SOURCE','PRODUCT','VARIABILE']
        e valori corrispondenti le istanze delle classi implementate in simcradarlib.io_utils.structure_class,
        con attributi ricavati dal file dei metadati.
        Il secondo elemento è la matrice dei dati nel file binario decodificato, restituita in formato
        array.
        _____
        INPUT:
        fname_bufr_data       --str : nome del file binario dei dati ottenuto dalla decodifica del file BUFR
        fname_bufr_meta       --str : nome del file di metadati ottenuto dalla decodifica del file BUFR
        fill_method           --str : indica il metodo per la definizione dei livelli del BUFR; i
                                      valori possibili sono 'min', 'ave', 'max'
        ______                        (dettagli nella documentazione del metodo get_var_levs_from_meta).
        OUTPUT:
        macro                 --dict : dizionario avente come chiavi
                                       ['TIME','GRID','PROJECTION','SOURCE','PRODUCT','VARIABILE']
                                       e values le istanze delle classi implementate in
                                       simcradarlib.io_utils.structure_class, con attributi
                                       ricavati dal file dei metadati:

                                       - 'TIME'    : ha come value un'istanza della classe StructTime
                                                     con informazioni temporali.
                                       - 'GRID'    : ha come value un'istanza della classe StructGrid
                                                     e contiene le info sul grigliato.
                                       -'SOURCE'   : ha come value un'istanza della classe StructSource
                                                     e ha attributi contenenti le info sulla provenienza
                                                     dei dati.
                                       -'PRODUCT'  : ha come value un'istanza della classe RardarProduct
                                                     e ha attributi contenenti info sul tipo di prodotto.
                                       -'VARIABILE': ha come value un'istanza di classe implementata nel
                                                     modulo simcradarlib.io_utils.rad_var_class, con
                                                     attributi contenenti info sul tipo di variabile.
                                       -'PROJECTION': ha come value un'istanza di classe StructProjection
                                                      con attributi contenenti info sulla proiezione dei dati.
        out_field         --np.array : array dei dati letto dal file binario decodificato.
        """

        # ***********************************LETTURA METADATI**************************************
        df_meta = pd.DataFrame()
        try:
            # lettura del file bufrname.txt dei metadati dalla decodifica tramite decbufr
            df_meta = self.read_meta(fname_bufr_meta)
        except Exception:
            module_logger.exception("Non sono riuscito a leggere metadati")
        self.meta = df_meta

        self.time = StructTime()
        if self.meta.__len__() > 0:
            try:
                self.time.date_time_validita = self.get_datetime_from_meta()
                # non riempo attributi acc_time, acc_time_unit, date_time_emissione perchè non leggiamo
                # campi cumulati ma solo istantanei e non so la data di emissione
                self.time.acc_time = self.get_acc_time_from_meta()
                self.time.acc_time_unit = "hours"
            except Exception as e:
                module_logger.exception(f"Lettura time fallita:\n{e}")

            self.source, self.product = self.get_source_product_from_meta()
            self.projection = self.get_projection_from_meta()
            self.grid = self.get_grid_from_meta()
            self.variabile, self.levels = self.get_var_levs_from_meta(fill_method)
        else:
            module_logger.warning("Metadati vuoti!")
            self.levels = None

        # ***********************************LETTURA DATI**************************************
        if self.levels is not None:
            try:
                with open(fname_bufr_data, mode="rb") as binary:
                    lines_rb = [line for line in binary.read()]
            except Exception:
                module_logger.exception(f"Lettura file binario dei dati {fname_bufr_data} fallita")
            try:
                # cont = np.array(lines_rb).reshape((self.grid.nx, self.grid.ny))
                cont = np.array(lines_rb).reshape((self.grid.ny, self.grid.nx))
            except ValueError:
                module_logger.exception("Reshape non corretto della matrice binaria")
            except AttributeError:
                module_logger.exception(
                    "Reshape dei dati binari fallito: controlla \
                attributi nx e ny di grid"
                )

            ind_lev_idl = np.arange(0, self.levels.__len__(), 1)
            # out_field = np.ones(shape=(self.grid.nx, self.grid.ny))*self.variabile.missing
            out_field = np.ones(shape=(self.grid.ny, self.grid.nx)) * self.variabile.missing
            for idl in ind_lev_idl:
                # il valore della matrice in output è il livello corrispondente tra l'indice
                # del livello e il valore binario in quel pixel. Quindi se il primo elemento
                # della matrice binaria è 1, il valore in output in quel pixel è dato dal valore
                # del livello con indice 1 (self.levels[1])
                out_field[cont == idl] = self.levels[idl]

        macro = {
            "TIME": self.time,
            "GRID": self.grid,
            "SOURCE": self.source,
            "PRODUCT": self.product,
            "VARIABILE": self.variabile,
            "PROJECTION": self.projection,
        }
        return macro, out_field
