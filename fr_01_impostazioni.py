#!/usr/bin/env python3

# Questo script mi serve per:
# impostare la regione sull'estensione della mia area di lavoro
# creare una cartella in cui tenere tutti i vari file per reclass, statistiche e simili
# impostare la risoluzione di lavoro

# I dati che devo immettere sono:
# nome e percorso del file vettoriale con i confini dell'area di lavoro
# risoluzione di lavoro

# Cose da risolvere al 12/3/2025:
# come creare la cartella direttamente nel GIS_database
# come definirla in modo da non dover mettere ogni volta che si usa il percorso completo

import os
import grass.script as gs

def mapset():
# collego il mapset appena creato al mapset mappe_di_base per recuperare la mappa dell'area di lavoro
    gs.run_command('g.mapsets', mapset='mappe_di_base', operation='add', format='plain')   
 # imposto la regione sulla mappa vettoriale dell'area di lavoro e scelgo la risoluzione #   
    gs.run_command('g.region', vector='area_di_lavoro@mappe_di_base', res=20)
# imposto la maschera usando la mappa vettoriale della mia area di lavoro
    gs.run_command('r.mask', vector= 'area_di_lavoro@mappe_di_base')




def cartella_di_lavoro():
# creo una cartella di lavoro dove si salvano tutti i vari file e poi per report, file di reclass e simili metterò sempre il suo percorso
# sarebbe meglio che questa cartella fosse creata dentro il GIS_database o comunque in un posto univoco e dove difficilmente ci si può pasticciare
# dentro la cartella di lavoro creo già la cartella "reclass" dove mi andrò a salvare i txt per riclassificare le mappe con statistica bivariata

# definisco come variabile il percorso della cartella
    input_path=('/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work')
# faccio lo stesso per la sottocartella cartella "reclass"
    output_path=('/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work/reclass')
# con exist_ok=True impongo che se la cartella esiste già venga riutilizzata
    os.makedirs(input_path, mode=511, exist_ok=True)
    os.makedirs(output_path, mode=511, exist_ok=True)
    
# associo alla funzione cartella_di_lavoro() il valore di input_path
    return input_path







def main():
# mi trasporto nel mapset "mappe_di_base" e se non esiste lo creo
    gs.run_command('g.mapset', mapset='mappe_di_base', flags='c')
# importo la mappa vettoriale dell'area di lavoro
# uso v.import così se è necessario la riproietta nel mio sistema di coordinate
# attenzione a mettere il percorso completo corretto
# su windows e linux gli / sono diversi!!!!
    gs.run_command('v.import', input='/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/prov_savona/prov_savona.shp', output = 'area_di_lavoro')        
    mapset()
    cartella_di_lavoro()


if __name__ == '__main__':
    main()



#   queste righe commentate sono per creare la maschera da un raster. A quanto pare nelle ultime versioni di GRASS la maschera si può creare anche da un vettore
#   gs.run_command('v.to.rast', input='area_di_lavoro', output='area_di_lavoro_rast', use='value', value=1)
#   gs.run_command('r.mask', raster = 'area_di_lavoro_rast')

