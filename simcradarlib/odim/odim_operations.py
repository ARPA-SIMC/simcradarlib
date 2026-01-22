import h5py
import numpy as np
from netCDF4 import num2date, date2num
from datetime import datetime

def formatstr(mystring : str):
    """
    Codifica la stringa in input nella forma in cui devono essere scritti gli
    attributi di un file ODIM compliant.
    """
    lenstr1 = int(len(mystring) +1)
    #versione commentata funzionava solo su fedora 40
    #ascii_type = h5py.string_dtype('ascii', lenstr1)
    #return np.array( mystring.encode('latin-1'), dtype=ascii_type)
    return np.array( mystring.encode('latin-1'),f'S{lenstr1}')

def odim_to_odimcompliant(f : str, pt : str):
    """
    Converte file odim v.2.4 di prodotto Datamet in formato compliant con gli standard ODIM e
    con le procedure idl e C++ operative al 22/1/2026 ad Arpae.
    Si usa su file ODIM di prodotti che siano mappe 2D.
    
    INPUT:
    f    --str : filename del prodotto in formato ODIM da convertire.
    pt   --str : stringa indicativa del tipo di prodotto.
                 Se pt=='ETOP' o pt=='ETM', l'attributo quantity del
                 gruppo dataset1/what e del gruppo dataset1/data1/what
                 viene settato a 'HGHT'.
    
    PROCESSING:
    Il file ODIM viene aperto in modalità sovrascrittura tramite h5py.
    Sovrascrive l'attributo globale 'Conventions' con la versione 2.1 per cui
    erano disposte le procedure operative al 22/1/2026, le quali lo controllano.
    Si verifica che l'attributo 'object' dei gruppi 'dataset1/data1/what'
    e 'what' sia 'IMAGE'.
    Si sovrascrive l'attributo 'quantity' dei gruppi 'dataset1/what' e 
    'dataset1/data1/what' se il tipo di prodotto indicato da pt in input
    è 'ETOP' o 'ETM' ponendolo a 'HGHT'.
    Se non esistono gli attributi 'gain' e 'offset' per il gruppo
    'dataset1/data1/what', si creano e si settano a 1.0 e 0.0 rispettivamente.
    Si sovrascrive l'orario nell'attributo 'time' del gruppo 'what' in modo
    che sia compliant.
    Si calcolano i secondi dal 1970-1-1 e si attribuiscono all'attributo 'startepochs'
    del gruppo 'how'.
    
    Il file odim viene chiuso e le modifiche vengono salvate.

    OUTPUT:
    None
    """
    h = h5py.File(f,'r+')
    h.attrs['Conventions']=formatstr('ODIM_H5/V2_1')
    h['what'].attrs['object'] = formatstr('IMAGE')
    h['dataset1/data1/what'].attrs['object'] = formatstr('IMAGE')
    if( pt=='ETM' or 'ETOP' in pt):
        h['dataset1/what'].attrs['quantity'] = formatstr( 'HGHT')
        h['dataset1/data1/what'].attrs['quantity'] = formatstr( 'HGHT')
        #data=h['dataset1/data1/data'][:]
        #data[data>0] *= 1000
        #h['dataset1/data1/data'][:]=data
    if 'gain' not in h['dataset1/data1/what'].attrs:
        h['dataset1/data1/what'].attrs['gain'] = 1.0
    if 'offset' not in h['dataset1/data1/what'].attrs:
        h['dataset1/data1/what'].attrs['offset'] = 0.0
    time0 = datetime.strptime(h['what'].attrs['time'].decode('utf-8'),'%H%M%S').strftime('%H%M%S')
    h['what'].attrs['time'] = formatstr( time0)
    t = datetime.strptime(h['what'].attrs['date'].decode('utf-8')+h['what'].attrs['time'].decode('utf-8'),'%Y%m%d%H%M%S')
    #print(f"time={t}")
    #grp = h.create_group('how', track_order=True)
    #if 'startepochs' not in h['how'].attrs.keys():
    h['how'].attrs['startepochs'] = date2num(t, 'seconds since 1970-01-01')
    #print(f"startepochs={date2num(t, 'seconds since 1970-01-01')}")
    #grp.attrs['startepochs'] = date2num(t, 'seconds since 1970-01-01')
    h.close()

    return
