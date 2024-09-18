[![Build Status](https://simc.arpae.it/moncic-ci/simcradarlib/rocky8.png)](https://simc.arpae.it/moncic-ci/simcradarlib/)
[![Build Status](https://simc.arpae.it/moncic-ci/simcradarlib/rocky9.png)](https://simc.arpae.it/moncic-ci/simcradarlib/)
[![Build Status](https://simc.arpae.it/moncic-ci/simcradarlib/fedora38.png)](https://simc.arpae.it/moncic-ci/simcradarlib/)
[![Build Status](https://simc.arpae.it/moncic-ci/simcradarlib/fedora40.png)](https://simc.arpae.it/moncic-ci/simcradarlib/)
[![Build Status](https://copr.fedorainfracloud.org/coprs/simc/stable/package/simcradarlib/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/simc/stable/package/simcradarlib/)

# simcradarlib

## Introduzione

La libreria simcradarlib contiene utilities per le procedure radar di Arpae-SIMC operative e di sviluppo
e nasce dall'esigenza di un porting da IDL e R a Python delle procedure e librere radar attualmente
richiamate dalle procedure operative e di sviluppo.

## Descrizione generale

La prima release della libreria contiene tre moduli, indicati di seguito.
Per la documentazione dettagliata dei singoli metodi e classi implementati nei sottomoduli si rimanda
alla documentazione nel codice disponibile in forma 'docstring'.

1. io_utils :
   
   contiene sottomoduli con classi e funzioni per la lettura di file netCDF, ZLR e BUFR e per la scrittura
   di file netCDF e BUFR e per la scrittura di campi 2D georeferenziati in formato ODIM OPERA v.2.1 .
   Elenco dei sottomoduli, classi e funzioni presenti:
   - simcradarlib.io_utils.structure_class
   - simcradarlib.io_utils.structure_class.StructureBase
   - simcradarlib.io_utils.structure_class.StructVariable
   - simcradarlib.io_utils.structure_class.StructCoords
   - simcradarlib.io_utils.structure_class.StructGrid
   - simcradarlib.io_utils.structure_class.StructProjection
   - simcradarlib.io_utils.structure_class.StructProduct
   - simcradarlib.io_utils.structure_class.StructTime
   - simcradarlib.io_utils.structure_class.StructSource
   - simcradarlib.io_utils.structure_class.RadarProduct
   - simcradarlib.io_utils.read_rad2d_nc
   - simcradarlib.io_utils.read_rad2d_nc.readnc_to_struct
   - simcradarlib.io_utils.read_rad2d_zlr
   - simcradarlib.io_utils.read_rad2d_zlr.read_zlr
   - simcradarlib.io_utils.rad_var_class
   - simcradarlib.io_utils.rad_var_class.VarPr
   - simcradarlib.io_utils.rad_var_class.VarZ60
   - simcradarlib.io_utils.rad_var_class.VarCumPrr
   - simcradarlib.io_utils.rad_var_class.VarZdr
   - simcradarlib.io_utils.rad_var_class.VarVn16
   - simcradarlib.io_utils.rad_var_class.VarVn49
   - simcradarlib.io_utils.rad_var_class.VarSv
   - simcradarlib.io_utils.rad_var_class.VarQc
   - simcradarlib.io_utils.rad_var_class.VarPrmm
   - simcradarlib.io_utils.rad_var_class.VarCumPrmm
   - simcradarlib.io_utils.rad_var_class.VarZ
   - simcradarlib.io_utils.rad_var_class.VarTh
   - simcradarlib.io_utils.rad_var_class.VarDbzh
   - simcradarlib.io_utils.rad_var_class.Vrad
   - simcradarlib.io_utils.rad_var_class.Wrad
   - simcradarlib.io_utils.rad_var_class.Rhohv
   - simcradarlib.io_utils.rad_var_class.Phidp
   - simcradarlib.io_utils.rad_var_class.Hght
   - simcradarlib.io_utils.rad_var_class.DbzV
   - simcradarlib.io_utils.rad_var_class.Poh
   - simcradarlib.io_utils.rad_var_class.Vil
   - simcradarlib.io_utils.rad_var_class.ClassConv
   - simcradarlib.io_utils.rad_var_class.Snr
   - simcradarlib.io_utils.rad_var_class.Class
   - simcradarlib.io_utils.rad_var_class.VilDensity
   - simcradarlib.io_utils.rad_var_class.VarRate
   - simcradarlib.io_utils.rad_var_class.VarAcrr
   - simcradarlib.io_utils.rad_var_class.VarClassId
   - simcradarlib.io_utils.general_radar_utils
   - simcradarlib.io_utils.general_radar_utils.get_reader
   - simcradarlib.io_utils.general_radar_utils.unzip_to_nc
   - simcradarlib.io_utils.general_radar_utils.get_meta_for_pysteps_from_macro
   - simcradarlib.io_utils.general_radar_utils.dpc_utm_grid_from_meta_pysteps
   - simcradarlib.io_utils.exporters
   - simcradarlib.io_utils.exporters.ExportableVar
   - simcradarlib.io_utils.bufr_class
   - simcradarlib.io_utils.bufr_class.Bufr

2. log_utils :
   
   contiene utilities per ottenere informazioni sull'esecuzione di processi ( lanciati da uno script o
   in una parte dello script principale)

   Elenco dei sottomoduli, classi e funzioni presenti:
   - simcradarlib.log_utils
   - simcradarlib.log_utils.log_exec_process
   - simcradarlib.log_utils.log_exec_process.log_exec_process.log_endprocess_info
   - simcradarlib.log_utils.log_exec_process.log_exec_process.log_subprocess_info

3. odim :
   
   contiene utilities per la lettura di file ODIM OPERA v.2.1 di prodotti radar e per la scrittura di campi
   2D georeferenziati (come la POH) e volumi polari in formato ODIM OPERA v.2.1.
   Elenco dei sottomoduli, classi e funzioni presenti:
   - simcradarlib.odim
   - simcradarlib.odim.odim_utils
   - simcradarlib.odim.odim_utils.OdimDset
   - simcradarlib.odim.odim_utils.OdimDset8bImage
   - simcradarlib.odim.odim_utils.OdimGroup
   - simcradarlib.odim.odim_utils.OdimWhat
   - simcradarlib.odim.odim_utils.OdimWherePolar
   - simcradarlib.odim.odim_utils.OdimWherePolarDset
   - simcradarlib.odim.odim_utils.OdimWhereSector
   - simcradarlib.odim.odim_utils.OdimWhereGeoimage
   - simcradarlib.odim.odim_utils.OdimWhereCross
   - simcradarlib.odim.odim_utils.OdimWhereCrossSection
   - simcradarlib.odim.odim_utils.OdimWhereRhi
   - simcradarlib.odim.odim_utils.OdimWhereVertProfile
   - simcradarlib.odim.odim_utils.OdimHow
   - simcradarlib.odim.odim_utils.OdimHowRadarDset
   - simcradarlib.odim.odim_utils.OdimHowPolarDset
   - simcradarlib.odim.odim_utils.OdimHowCartesianImageDset
   - simcradarlib.odim.odim_utils.OdimHowVertProfileDset
   - simcradarlib.odim.odim_utils.OdimWhatDset
   - simcradarlib.odim.odim_utils.odim_pvol
   - simcradarlib.odim.odim_utils.odim_pvol.OdimHierarchyPvol
   - simcradarlib.odim.odim_utils.odim_image

4. geo_utils :

   contiene utilities per la georeferenziazione di dati radar.
   Elenco dei sottomoduli, classi e funzioni presenti:
   - simcradarlib.geo_utils
   - simcradarlib.geo_utils.georef
   - simcradarlib.geo_utils.georef.bin_altitude
   - simcradarlib.geo_utils.georef.site_distance
   - simcradarlib.geo_utils.georef.get_earth_radius
   - simcradarlib.geo_utils.georef.spherical_to_xyz

5. visualization :

   contiene utilities per la visualizzazione di prodotti e dati radar.
   Elenco dei sottomoduli, classi e funzioni presenti:
   - simcradarlib.visualization
   - simcradarlib.visualization.plot_ppi
   - simcradarlib.visualization.plot_ppi.plot_ppi_curvilinear
   - simcradarlib.visualization.plot_ppi.plot_ppi_from_vol

## Sviluppi futuri
Lo sviluppo della libreria proseguirà nell'ottica di completare il porting delle routine esistenti usate
dalle procedure operative in Python.

E' in corso la scrittura di un manuale di documentazione e guida all'uso della libreria come documento
drive e verranno resi disponibili Notebooks di esempio.

## Licenza

`simcradarlib` è rilasciato sotto licenza GPLv3, ad eccezione di
`simcradarlib.geo_utils`, che usa codice della libreria
[`wradlib`](https://wradlib.org/), rilasciata sotto licenza MIT (si veda il
modulo per maggiori informazioni sulla licenza).
