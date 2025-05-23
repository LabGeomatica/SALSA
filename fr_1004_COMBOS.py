#!/usr/bin/env python3

import grass.script as gs
import os
import re
import itertools
import csv
import pandas as pd
from itertools import combinations

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


def installare_estensione():

# mi serve l'estensione r.edm.eval
# chissà se su windows funzionerà?
# controllo se l'estensione r.edm.eval è già installata in locale
    info_estensioni = gs.parse_command('g.extension', flags='a', operation='add')
    print(f'queste sono le estensioni installate: {info_estensioni}')

# se l'estensione è nella lista delle estensioni già installate
    if 'r.edm.eval' in info_estensioni:
        print('eureka!')

# se non c'è la installa
    else:
        gs.run_command('g.extension', extension ='r.edm.eval', operation='add')



def main():
    input_path='/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work'

# definisco la variabile mapset_frane come il riusltato della funzione "per_tutti_i_tipi()" che ho richiamato ora
    mapset_frane=per_tutti_i_tipi()
    print(mapset_frane)

    installare_estensione()
             

# per ogni mapset della lista mapset_frane creo la lista di tutti i fattori predisponenti contenuti e la chiamo lista_fattori

# per ogni mapset nella lista mapset_frane
    for mapset in mapset_frane:
# mi trasferisco nel mapset
        gs.run_command('g.mapset', mapset={mapset})
# creo la lista mappe_nel_mapset
# questa lista contiene tutte le mappe, ma devo escludere la MASK e la mappa logit
# non posso usare exclude= perché dovrei usare una forma f'logit_{mapset}' ma grass.script non la legge 
        mappe_nel_mapset= gs.parse_command('g.list', type='raster', mapset={mapset})
# creo una nuova lista che chiamo lista_fattori che filtra le mappe diverse da MASK e quella con la forma (f'logit_{mapset}'       
        lista_fattori = [
            mappa for mappa in mappe_nel_mapset
            if mappa != 'MASK' and not mappa.startswith(f'logit_{mapset}') and not mappa.startswith(f'est_') and not mappa.startswith(f'susc_')
            ]
              
        print(f"nel mapset {mapset}: ci sono le mappe {lista_fattori}")

# definisco il percorso alle sottocartelle

        dir_path=os.path.join(input_path, mapset)

        if os.path.isdir(dir_path):

#            print(dir_path)


# Creo una lista vuota che chiamo combinazioni
            combinazioni = []

# per tutti gli elementi che stanno nella lista, dalla posizione 1 all'ultimo
            for i in range(1, len(lista_fattori)+1):
                elementi = [list(x) for x in itertools.combinations(lista_fattori, i)]
                combinazioni.extend(elementi)        


# creo un file .csv che mi riassuma le AIC di tutte le combinazioni
            csv_path = f'{dir_path}/report_AIC.csv'
# lo metto in modalità scrittura e lo definisco come csvfile
            with open(csv_path, 'w', newline='') as csvfile:
# questa linea è per aggiungere righe al file .csv
                writer = csv.writer(csvfile)
# questa per mettere le intestazioni di colonna
                writer.writerow(['ID', 'AIC', 'Fattori'])  

# creo una lista vuota 
                risultati = []  # per trovare il minimo AIC alla fine


                for i, combo in enumerate(combinazioni):
# In questo modo l'ID inizia da 1 e non da 0
                    id = i + 1  

#                    print(f"ID: {id}, Combinazione: {combo}")



# questo per poter cercare dentro ogni file il test AIC e il corrispondente valore
# non salvo nessuna mappa ma solo i report

                    output_file = f'{dir_path}/report_{id}.txt'
        
                    with open(output_file, 'w') as f:   
        
                        gs.run_command('r.regression.multi', mapx= combo, mapy=f'logit_{mapset}', output=output_file, overwrite=True)


                    with open(output_file, 'r') as f:
                        output = f.read()

# cerco in ogni file la stringa AIC=....
                    match = re.search(r"AIC\s*=\s*([0-9.]+)", output)
                    if match:
                        aic = float(match.group(1))

# estraggo l'AIC e gli altri parametri che voglio salvare nel file .csv
                # print(f'{id}, AIC: {aic}, Fattori: {combo}')

# considero che non ci sia il caso in cui non ho un'AIC perché altrimenti non sarei arrivata qui
#           else:
#               print("AIC non trovato")
#               aic = None

# aggiungo i dati nel CSV
# da qualche problema di formattazione, ma si riesce a capire (c'è qualche virgola di troppo)
                        writer.writerow([id,aic,','.join(combo)])

# Leggi il file CSV 
            df = pd.read_csv(csv_path)

# Trova la riga con il valore minimo della colonna 'AIC'
            min_aic_row = df.loc[df['AIC'].idxmin()]

# Estrai il valore della colonna 'Fattori'
            fattori_min_aic = min_aic_row['Fattori']

            print("Fattori con AIC minimo:", fattori_min_aic)

            gs.run_command('r.regression.multi', mapx= fattori_min_aic, mapy=f'logit_{mapset}', estimates=f'est_{mapset}', overwrite=True)



# In questa parte uso l'addon r.edm.eval per valutare l'affidabilità del modello
# salvo il grafico nella sottocartella di ciascun tipo di frana
# salvo il valore dell'AUC
# il comando r.edm.eval riporta i risultati in un formato del cavolo, quindi li devo prima salvare come file e poi leggerli dal file

# creo un file di lavoro in ciascuna sottocartella

        output_file=f'{dir_path}/AUC_output.txt'
        
# metto il file in modalità di scrittura 
# e lo definisco come f
        with open(output_file, 'w') as f:

# lancio il comando r.edm.eval
            gs.parse_command('r.edm.eval', reference=f"{mapset}@frane", prediction=f"est_{mapset}", figure=f"{dir_path}/AUC_{mapset}.jpg",stdout=f, stderr=f, overwrite=True)



# Leggo il contenuto del file
        with open(output_file, 'r') as f:
            output = f.read()

# Estraggo dal file l'AUC con regex
# faccio una query nel file
        match = re.search(r"AUC\s*=\s*([0-9.]+)", output)
        if match:
            auc = float(match.group(1))
            print("AUC:", auc)
#        else:
#            print("AUC non trovato")




if __name__ == '__main__':
    main()
