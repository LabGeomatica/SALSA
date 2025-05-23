#!/usr/bin/env python3

import grass.script as gs
import os


def main():
     input_path=('/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work')
    # mi sposto nel mapset mappe_reclass
     gs.run_command('g.mapset', mapset='mappe_reclass')
     gs.run_command('g.mapsets', mapset='frane', operation='add', format='plain')   
# elenco tutte le mappe raster che stanno nel mapset mappe_reclass
# escludo la mappa MASK perché è la maschera e resta così come è
     rasters=gs.parse_command('g.list', type='raster', mapset='mappe_reclass', exclude='MASK', )
# creo una lista che chiamo raster_list che contiene le mappe che ho elencato sopra
     raster_list = [raster for raster in rasters]
     # print(raster_list)
# elenco tutte le mappe raster che stanno nel mapset frane
     tipi_frane=gs.parse_command('g.list', type='raster', mapset='frane', exclude='MASK', )
# creo una lista che chiamo lista_frane che contiene le mappe che ho elencato sopra
     lista_frane = [tipo for tipo in tipi_frane]

# per ogni mappa della lista tipi_frane
     for tipo in lista_frane:
# definisco la variabile "cartella" che avrà come percorso l'input_path e come nome il tipo di frana
        cartella = os.path.join(input_path, tipo)
# creo una cartella per ogni tipo di frana
        os.makedirs(cartella, mode=0o777, exist_ok=True)

# per ogni mappa della lista raster_list        
        for raster in raster_list:
# creo un file con estensione .csv nella mia cartella di lavoro
# gli definisco il percorso che è l'unione del mio input_path + il nome della mappa raster.csv
# f significa che inserisco una variabile tra {} all'interno di una stringa di testo, in questo caso il nome di ciascuna mappa raster per avere il nome delle mappe in uscita
         file_path = os.path.join(cartella, f"{tipo}_{raster}.csv")
# uso il comando r.stats per crearmi per ogni mappa un file .csv nella mia cartella 
         gs.run_command('r.stats', input=f"{tipo},{raster}", output=file_path, flags='nc')


if __name__ == '__main__':
    main()
