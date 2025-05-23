#!/usr/bin/env python3

import grass.script as gs
import os


def main():
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

# Elenco le mappe raster nella cartella mappe_reclass escludendo MASK
    lista_frane = gs.parse_command('g.list', type='raster', mapset='frane', exclude='MASK')
    #print(f"ecco le mappe di tutti i tipi di frane: {lista_frane}")
    for mapset in mapset_frane:
        gs.run_command('g.mapset', mapset={mapset})
        for frana in lista_frane:
            if frana==mapset:
                print(f"mapset {mapset}: {frana}")
                gs.mapcalc('{r} = (log({a} + 0.00000001) - log(1 - {a} + 0.00000001))'.format(r='logit_' + frana, a=frana), overwrite = True)
                # gs.run_command('g.copy', raster=f"{frana}@frane,{frana}")


if __name__ == '__main__':
    main()


