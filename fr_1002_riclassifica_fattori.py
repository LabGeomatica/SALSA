#!/usr/bin/env python3

import grass.script as gs
import os



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


# RICORDATI! 

def main():
    input_path = '/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work'
# richiamo la funzione crea_mapaset definita qui sopra e creo un mapset per ogni tipo di frana    
    crea_mapset()  
    
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


# Elenco le mappe raster nella cartella mappe_reclass escludendo MASK
    raster_list = gs.parse_command('g.list', type='raster', mapset='mappe_reclass', exclude='MASK')
    #print(f"il mapset mappe_reclass contiene: {raster_list}")

# Ciclo attraverso le cartelle e i file nella cartella input_path
# per tutti i mapset nella mia lista "mapset_frane"
    for mapset in mapset_frane:
# mi sposto nel mapset
        gs.run_command('g.mapset', mapset=mapset, flags='c')
# uso il metodo os.walk() per accedere al contenuto tutte le cartelle, sottocartelle e flie nel mio input_path
        for root, dirs, files in os.walk(input_path):
# per tutti i file
            for file in files:
# Verifico che il file sia un file .txt
                if file.endswith('.txt'):
# definisco il nome della sottocartella e del file
                    nome_cartella = os.path.basename(root)
                    nome_file = file
  
                    #print(f'cartella:{nome_cartella}, file:{nome_file}')
# definisco nome e percorso del file che userò come regole per il comando r.reclass
                    file_regole = os.path.join(input_path, nome_cartella, nome_file)
                    print(f"File regole trovato: {file_regole}")

# per tutti i raster nella mia raster_list (cioè tutti i raster nel mapset "mappe_reclass"
                    for raster in raster_list: 
# definisco la variabile match_name
# cioè creo un nome da associare al file di regole
                        match_name=f"{mapset}_{raster}.txt"
                        # print(f"controllo se {file} corrisponde a {match_name}")
# se il nome del file di regole corrisponde al march_name
                        if file==match_name:
                            print(f"il file {file} corrisponde a {raster}!")
# riclassifica la mappa corrispondente
# salvala nel mapset corrispondente al tipo di frana
# aggiungi _2 al nome della mappa
                            gs.run_command('r.reclass', input=raster, output=f'{raster}_2@{mapset}', rules=file_regole)



if __name__ == '__main__':
    main()








