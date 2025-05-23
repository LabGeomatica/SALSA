#!/usr/bin/env python3

import grass.script as gs
import os
import pandas as pd
import csv


"""
# QUesto per il momento lo tolgo, ho provato ceh funziona

def crea_mapset():
# elenco tutte le mappe raster che stanno nel mapset frane
    tipi_frane=gs.parse_command('g.list', type='raster', mapset='frane', exclude='MASK', )
# creo una lista che chiamo lista_frane che contiene le mappe che ho elencato sopra
    lista_frane = [tipo for tipo in tipi_frane]
# per ogni mappa della lista tipi_frane
    for tipo in lista_frane:
# creo un mapset per ogni tipo di frana
        gs.run_command('g.mapset', mapset={tipo}, flags='c')
# collego il mapset appena creato al mapset mappe_di_base per recuperare la mappa dell'area di lavoro
        gs.run_command('g.mapsets', mapset='mappe_di_base,frane,mappe_reclass', operation='add', format='plain')   
 # imposto la regione sulla mappa vettoriale dell'area di lavoro e scelgo la risoluzione #   
        gs.run_command('g.region', vector='area_di_lavoro@mappe_di_base', res=20)
# imposto la maschera usando la mappa vettoriale della mia area di lavoro
        gs.run_command('r.mask', vector= 'area_di_lavoro@mappe_di_base', overwrite=True)


"""


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

    input_path = '/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work'

    # crea_mapset()

    mapset_frane=per_tutti_i_tipi()
    print(f"questi sono i mapset che userò: {mapset_frane}")

    
    for mapset in mapset_frane:
        dir_path=os.path.join(input_path, mapset)


# preva per vedere che il mio dir_path punti alle cartelle corrette
#        if os.path.isdir(dir_path):
#            print(dir_path)

# cerco in tutte le directory e i file nel mio percorso dir_path
        for root, dirs, files in os.walk(dir_path):

# per tutti i nomi di file tra i file che trovo
                for filename in files:
# se il nome finisce con .csv
                    if filename.endswith('.csv'):

# chiamo filepath il percorso di questi file unendo la root cioè la mia dir_pah e il nome del file
                        filepath = os.path.join(root, filename)
                        print(f"Leggo il file: {filepath}")

# trova ogni file .csv tramite il percorso, lo legge e lo ccarica come DataFrame
# header=None significa che la prima linea NON contiene le intestazioni di colonna, quindi il DataFrame che si va a creare NON avrà l'intestazione
# sep='\s+' significa che i vari spazi vuoti vanno considerati come separatori di campo
                        df = pd.read_csv(filepath, header=None, sep='\s+')
                        print(df)

                        celle_frana = df[df[0]==1]  # creo un nuovo DataFrame che contiene le righe di df per cui il valore riportato nella colonna 0 = 1 e lo chiamo celle_frana
# print(celle_frana)
                        celle_no_frana = df[df[0]==0]   # creo un nuovo DataFrame che contiene le righe di df per cui il valore riportato nella colonna 0 = 0 e lo chiamo celle_no_frana
# print(celle_no_frana)
                        celle = pd.merge(left=celle_frana, right=celle_no_frana, how='outer', on=1)   # creo un nuovo DataFrame che ha a sinistra le colonne del DataFrame Celle_frana e a destra quelle del DataFrame Celle_no_frana
# outer significa che il tipo di join che faccio non è un'intersezione
# è obbligatorio indicare almeno il parametro right, altrimenti non sa in che ordine "affiancare" i DataFrame
                        #print(celle)


                        celle["0_x"]=celle["0_x"].fillna(1).astype(int)   # qui ho sostituirto tutti i NaN della colonna 0_x (quella che indica con 1 se le celle sono in frana) con il valore 1 e ho stabilita che tutta la colonna fosse di tipo int (numeri interi)
                        celle["2_x"]=celle["2_x"].fillna(0).astype(int)   # qui ho sostituirto tutti i NaN della colonna 2_x (quella dove è riportato il numero delle celle) con il valore 0 e ho stabilita che tutta la colonna fosse di tipo int (numeri interi)
                        #print(celle)

                        celle["prob"]=celle['2_x']/(celle['2_x'] + celle['2_y'])*100  # aggiungo al DataFrame celle la colonna "prob" in cui si riporta la probabilità condizionata, cioè (numero celle in frana / numero (celle in frana + celle non in frana)) * 100
                        celle.sort_values(by='prob',inplace = True) # riordino le righe in ordine crescente secondo la probabilità condizionata e rendo questa nuova disposizione permanente con inplace=True
                        #print(celle)

                        celle_gnu = celle.reset_index() # creo il nuovo DataFrame celle_gnu che mi assegna un indice (in pratica il rownumber) per le classi riordinate
                        #print(celle_gnu)


# Inizializza un contatore per la colonna "classe_gnu"how is written python smallest number
                        last_index = 2  #how is written python smallest number

# impongo le condizioni per trovare il valore minimo di probabilità quando questa è > 0
# nel dataframe celle_gnu la colonna "prob" deve essere >0 e allo stesso tempo applico il metodo min()
                        valore_minimo_non_0 = celle_gnu[celle_gnu["prob"]>0]["prob"].min()

# creo la colonna vuota
                        classe_gnu_values = []
                        for index, row in celle_gnu.iterrows():
                            classe_gnu_values.append(10000)

#aggiungo colonna con valori vuoti
                        celle_gnu["classe_gnu"] = classe_gnu_values

# valore di partenza per ordinare la probabilità
# per valori di probabilità diversi da 0
                        startNum = 1

# primo giro, controllo se ci sono prob a 0
# nel caso metto 1 e imposto valore partenza a 2
                        for index, row in celle_gnu.iterrows():
                            if row["prob"] == 0:
# funzione loc usa indice delle righe come puntatore riga/colonna
# per impostare valore nel dataset)
                                celle_gnu.loc[index, "classe_gnu"] = 1

# reimposto valore partenza
                        startNum = 2

# secondo giro, tutti i valori di prob diversi da zero
# imposto valore di partenza e poi lo incremento
                        for index, row in celle_gnu.iterrows():
                            if row["prob"] != 0:
                                celle_gnu.loc[index, "classe_gnu"] = startNum
                                startNum = startNum+1

# aggiungo la colonna "regole" in cui è contenuto per tutte le righe un testo che riporta  valore vecchio "="  valore nuovo
                        celle_gnu["regole"] = celle_gnu[1].astype(str) + " = " + celle_gnu["classe_gnu"].astype(str)
                        print(celle_gnu)

# creo il percorso per i file .txt
# per prima cosa sostituisco l'estensione .csv con .txt
                        txt = os.path.basename(filename)
                        #print(txt)
                        txt = txt.replace(".csv", ".txt")
                        txt = txt.replace(".CSV", ".txt")
                        print(txt)

                        file_txt_path = os.path.join(dir_path,txt)
    
                        print(file_txt_path)

# esporto ol DataFrame in un file txt

                        with open(file_txt_path, 'w') as f:
# cancello il contenuto (è facoltativa perché ho già messo il parametro w)
                            f.truncate(0) 
# scelgo le colonne del dataframe che voglio portare nel txt
                            df_string = celle_gnu["regole"].to_string(header=False, index=False)
# copio nel file .txt le colonne che avevo selezionat
                            f.write(df_string)
# aggiungo le linee di chiusura per avere un file di reclass
                            f.writelines(["\n","*=*\n", "end"])





if __name__ == '__main__':
    main()
