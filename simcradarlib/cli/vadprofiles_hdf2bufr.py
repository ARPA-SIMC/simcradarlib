#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os, re, argparse
import numpy as np
from datetime import datetime
from simcradarlib.odim.odim_vprof import OdimHierarchyProfile
import dballe

def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument( "-i", "--input_file", dest="inputfile",
                         required=True, help="HDF5 input file, required" )
    parser.add_argument( "-o", "--output_file", dest="outputfile",
                         required=False, help="BUFR output file, optional" )
    args = parser.parse_args()

    if args.outputfile:
        bufr_data = str(args.outputfile)
    else:
        bufr_data = os.path.splitext(os.path.basename(args.inputfile))[0] + ".bufr"

    print(f"Output file: {bufr_data}")
    
    # Apro e leggo il contenuto del file del profilo di vento
    profile = OdimHierarchyProfile()
    profile.read_vp_odim(args.inputfile)

    #print(profile.root_where.__dict__)
    #print(profile.root_what.__dict__)
    #print(profile.root_how.__dict__)
    
    MAX_LEVELS = 256  # il template BUFR usato non gestisce più di 256 livelli
    #RMS_THRESHOLD = 90.0 # colonna 3 (rms): scarta righe >= 90

    # Inizializzo messaggio dballe
    msg = dballe.Message("temp")

    # Anagrafica stazione
    source = profile.root_what.source.decode("utf-8")
    try:
        print(f"Scrittura anagrafica")
        match = re.search(r'WMO:(\d{2})(\d{3})', source)
        blocco  = match.group(1)
        station = match.group(2)
        print(f"Blocco: {blocco}, Stazione: {station}")

        msg.set_named("height_station", dballe.var("B07030", profile.root_where.height))
        msg.set_named("block", dballe.var("B01001", blocco))
        # Per coerenza con i dati storici, la stazione viene scritta solo
        # se si tratta di SPC (WMO)
        if station == 144:
            msg.set_named("station", dballe.var("B01002", station))
        msg.set_named("latitude", dballe.var("B05001", profile.root_where.lat))
        msg.set_named("longitude", dballe.var("B06001", profile.root_where.lon))
        print(profile.root_where.lat, profile.root_where.lon, profile.root_where.height)
    except Exception as e:
        print(f"Problemi in scrittura anagrafica: {e}")
        exit(3)

    # Date/time
    try:
        print(f"Scrittura date/time")
        #print(profile.root_what.date.decode("utf-8"))
        #print(profile.root_what.time.decode("utf-8"))
        dt = datetime.strptime(profile.root_what.date.decode("utf-8"), "%Y%m%d")
        msg.set_named("year",   dballe.var("B04001", dt.year))
        msg.set_named("month",  dballe.var("B04002", dt.month))
        msg.set_named("day",    dballe.var("B04003", dt.day))
        dt = datetime.strptime(profile.root_what.time.decode("utf-8"), "%H%M%S")
        msg.set_named("hour",   dballe.var("B04004", dt.hour))
        msg.set_named("minute", dballe.var("B04005", dt.minute))
        msg.set_named("second", dballe.var("B04006", dt.second))
    except Exception as e:
        print(f"Problemi in scrittura date/time: {e}")
        exit(4)

    # Tipo di strumento di misura
    msg.set_named("meas_equip_type", dballe.var("B02003", 3))
    
    # Dati profilo
    # Colonne matrice: intensità(0), direzione(1), velocità_vert(2), rms(3),
    #                  NULL(4), NULL(5), azimuth(6), altezza(7)
    count_row = 0
    
    ff_data = profile.get_quantity("ff")
    ff_what = profile.get_what_by_quantity("ff")
    ff_nodata   = float(ff_what.nodata)
    ff_undetect = float(ff_what.undetect)
    #print(ff_data)
    #print(ff_nodata, ff_undetect)

    dd_data = profile.get_quantity("dd")
    dd_what = profile.get_what_by_quantity("dd")
    dd_nodata   = float(dd_what.nodata)
    dd_undetect = float(dd_what.undetect)
    #print(dd_data)
    #print(dd_nodata, dd_undetect)

    if (ff_data.shape != dd_data.shape):
        print(f"Intensità e direzione del vento hanno dimensioni diverse, esco.")
        exit(5)

    # Dati livelli verticali
    try:
        print(f"Scrittura livelli verticali")
        minh    = profile.root_where.minheight
        maxh    = profile.root_where.maxheight
        dh      = profile.root_where.interval
        heights = np.arange(minh + profile.root_where.height + dh/2,
                            maxh + profile.root_where.height + dh  ,
                            dh)
        #print(heights)
    except Exception as e:
        print(f"Problemi sui livelli verticali: {e}")
        exit(6)
      
    for i in range(0,len(ff_data)):
        level  = dballe.Level(102, int(heights[i] * 1000.))
        trange = dballe.Trange(254, 0, 0)
        # B11002 = wind speed (intensità)
        val = float(ff_data[i])
        if val in (ff_nodata, ff_undetect):
            val = None
        msg.set(level, trange, dballe.var("B11002", val))
        # B11001 = wind direction (direzione)
        val = float(dd_data[i])
        if val in (dd_nodata, dd_undetect):
            val = None
        msg.set(level, trange, dballe.var("B11001", val))
        
        count_row += 1
        if count_row == MAX_LEVELS:
            break

    print(f"Esportazione in bufr")    
    exporter = dballe.Exporter("BUFR", template_name="temp-radar")
    bufr_bytes = exporter.to_binary([msg])
    with open(bufr_data, "wb") as f:
        f.write(bufr_bytes)

if __name__ == '__main__':
    # Questo serve per eseguirla con python -m simcradarlib.cli.vadprofiles_hdf2bufr, ma una volta installata la
    # libreria puoi lanciarla con simcradarlib-vadprofiles_hdf2bufr (possiamo cambiare il nome se vuoi).
    run_cli()
