#!/usr/bin/env python3

import grass.script as gs
import os
import pandas as pd
import csv


# Questa parte serve per dividere le mappe di suscettiblità in tre grandi classi


# con questa funzione stabilisco che l'operazione va ripetuta per tutti i tipi di frane
# cioè per ciascun mapset dedicato ad un tipo di frana
# è la stessa fatta nei blocchi precedenti, ma al momento resta così 
# quando si metteranno i blocchi insieme non sarà necessario ripeterla


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

# la variabile mapeset_frane è il risultato di questa funzione
    return mapset_frane


def main():
    input_path='/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work'
# definisco la variabile mapset_frane come il risultato della funzione "per_tutti_i_tipi()" che ho richiamato ora
    mapset_frane=per_tutti_i_tipi()
    print(mapset_frane)

# per ogni tipo di frana
    for mapset in mapset_frane:

# mi trasferisco nel mapset
        gs.run_command('g.mapset', mapset={mapset})

# definisco come variabile il percorso per ogni sottocartella nella cartella di lavoro
        dir_path=os.path.join(input_path, mapset)
        print(dir_path)

# importo come DataFrame il file che ha come percorso dir_path e come nome {mapset}_univar.csv
        df= pd.read_csv(f'{dir_path}/{mapset}_univar.csv')
#       print(df)


# individuo il limite inferiore della classe ad alta suscettibilità
# come il valore medio delle celle in frana
# che è riportato nella seconda linea all'ottava colonna dei file {mapset}_univar.csv

# estraggo dal DataFrame usando il metodo df.iloc() il valore medio delle celle in frana
# attenzione che in pYthon linee e colonne partono da 0, quindi è indicato con le coordinate 1,7

        limite_inf_classe_alta= df.iloc[1, 7]
        print(f'limite inferiore della classe alta = {limite_inf_classe_alta}')


# estraggo dal DataFrame usando il metodo df.iloc() il valore minimo di tutta l'area
# si trova alle coordinate 1,4 sempre partendo da 0 
        val_minimo = df.iloc[1,4]
        print(f"valore minimo di tutta l'area = {val_minimo}")

# calcolo il limite inferiore della classe a media suscettibilità
# come il valore a metà tra il minimo e il limite inferiore della classe ad alta suscettibilità
        limite_inf_classe_media = (limite_inf_classe_alta - val_minimo)/2 + val_minimo
        print(f'limite inferiore della classe media = {limite_inf_classe_media}')
        
        mappe_nel_mapset= gs.parse_command('g.list', type='raster', mapset={mapset})
#       print(f"in {mapset} ci sono le mappe {mappe_nel_mapset}")


# scorro tutte le mappe del mapset
        for mappa in mappe_nel_mapset:
# quando trovo la mappa della suscettibilità, che ho chiamato susc_{mapset}
            if mappa == (f'susc_{mapset}'):
# uso mapcalc per riclassificarla
                gs.mapcalc('{r} = if({a}<{b}, 1, if({a}<{c}, 2, 3))'.format(r='susc_reclass', a=f'susc_{mapset}@{mapset}', b=limite_inf_classe_media, c=limite_inf_classe_alta))


if __name__ == '__main__':
    main()
