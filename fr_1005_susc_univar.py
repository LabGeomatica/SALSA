#!/usr/bin/env python3

import grass.script as gs
import os

# questa parte serve per elaborare le mappe di suscettibilità per ogni tipo di frana
# confrontarle con la mappa delle frane con r.univar
# salvare il risultato di r.univar in un file .csv

# ad oggi (12 maggio 2025) la calibrazione è svolta con il 100% delle frane



# con questa funzione stabilisco che l'operazione va ripetuta per tutti i tipi di frane
# cioè per ciascun mapset dedicato ad un tipo di frana

def per_tutti_i_tipi():
# Elenco i mapset presenti nella location
# per avere una lista dei mapset in una location si usa g.mapset -l
    location = gs.parse_command('g.mapset', flags='l')
# trasformo il risultato in una lista, ma questa risulta aggregata, quindi composta da una frase
    mapset_aggregati = [mapset for mapset in location]
# divido la frase formando una lista di singole parole, cioè dei nomi dei mapset
    lista_mapset = mapset_aggregati[0].split()

# tolgo dalla lista i mapset che non riguardano le frane
# creo un sottoinsieme della lista che contiene i mpaset da non considerare
    da_rimuovere = ["frane", "mappe_di_base", "mappe_reclass", "PERMANENT"]
# creo una lista che contiene tutti i mapset che non sono nella lista da non considerare
    mapset_frane = [item for item in lista_mapset if item not in da_rimuovere]
    # print(mapset_frane)

# la variabile mapeset_frane è il risultato di questa funzione
    return mapset_frane


def main():
    input_path='/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work'

# definisco la variabile mapset_frane come il risultato della funzione "per_tutti_i_tipi()" che ho richiamato ora
    mapset_frane=per_tutti_i_tipi()
    print(mapset_frane)

# per ogni mapset nella lista mapset_frane
    for mapset in mapset_frane:
# mi trasferisco nel mapset
        gs.run_command('g.mapset', mapset={mapset})
# creo la lista mappe_nel_mapset

        mappe_nel_mapset= gs.parse_command('g.list', type='raster', mapset={mapset})
#       print(f"in {mapset} ci sono le mappe {mappe_nel_mapset}")
# scorro tutte le mappe del mapset
        for mappa in mappe_nel_mapset:
# quando trovo la mappa dei valori attesi cioè le mappe che ho creato con r.regfression.multi e che iniziano con est
            if mappa == (f'est_{mapset}'):
# tramite l'inverso della funzione di logit calcolo i valori di probabilità
# cioè la suscettibilità al dissesto
                gs.mapcalc('{r} = exp({a}) / (1 + exp({a}))'.format(r='susc_' + mapset, a=mappa), overwrite = True)
                print(f'ho creato la mappa susc_{mapset}')
            
# definisco come variabile il percorso per ogni sottocartella nella cartella di lavoro
            dir_path=os.path.join(input_path, mapset)

# questo è un controllo per vedere se il percorso punta alle sottocartelle giuste
            #if os.path.isdir(dir_path):
                #print(dir_path)


        #for mappa in mappe_nel_mapset:
            if mappa == (f'susc_{mapset}'):
                print(f'questa è la mia mappa di suscettibilità: susc_{mapset}')
                gs.parse_command('r.univar', map=mappa, zones=f'{mapset}@frane', flags='t', separator='comma', overwrite=True, output=f'{dir_path}/{mapset}_univar.csv')


if __name__ == '__main__':
    main()


