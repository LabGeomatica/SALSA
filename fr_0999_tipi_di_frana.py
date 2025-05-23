#!/usr/bin/env python3

# DARE QUALCHE NOME PIU' SENSATO ALLA PARTE IN CUI SI CREA LA LISTA DI MAPPE VETTORIALI (LINEA 23 IN GIU')

# Al 26/03/2025
# servirebbe direttamente non caricare la mappa frana_1 (cioè quella dei crolli)
# ho provato a includere nel comando v.db.extract una condizione Where, ma la ignonra completamente
# al momento escludo le frane di tipo 1 dalla lista per creare nuovi mapset, ma è un sistema troppo macchinoso

import grass.script as gs
import os
from grass.script import db as grass


# questa funzione dovrebbe essere già definita nelle impostazioni

def mapset():
# collego il mapset appena creato al mapset mappe_di_base per recuperare la mappa dell'area di lavoro
    gs.run_command('g.mapsets', mapset='mappe_di_base', operation='add', format='plain')   
 # imposto la regione sulla mappa vettoriale dell'area di lavoro e scelgo la risoluzione #   
    gs.run_command('g.region', vector='area_di_lavoro@mappe_di_base', res=20)
# imposto la maschera usando la mappa vettoriale della mia area di lavoro
    gs.run_command('r.mask', vector= 'area_di_lavoro@mappe_di_base', overwrite=True)


def frane():
# mi sposto nel mapset "frane" e se non esiste lo creo
    gs.run_command('g.mapset', mapset='frane', flags='c')
    mapset()
# importo il file con le frane
# in questo caso ho scelto il file scaricato dall'IFFI frane_poly_opendataPolygon.shp
# i tipi di frane contenuti sono colamenti lenti, colamenti rapidi, scivolamenti, frane complesse, frane non determinate
# oltre a questi ci sono crolli/ribaltamente ed espansioni che non considero
    gs.run_command('v.import', input='/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/Frane_IFFI/frane_poly_opendataPolygon.shp', output='frane', overwrite=True)

# voglio accertarmi che il file delle frane che ho importato copra almeno tutta la mia regione di lavoro
# uso ilcomando g.region per ottenere le informazioni sulla mia regione
    info_regione=gs.parse_command('g.region', flags='g')
# definisco come variabili i valori estremi in direzione NSWE della mia regione
    regione_N = float(info_regione['n'])
    regione_S = float(info_regione['s'])
    regione_W = float(info_regione['w'])
    regione_E = float(info_regione['e'])
    # print(regione_E)"""  

# uso il comando v.info per ottenere informazioni sul dataset delle frane
    info_frane=gs.parse_command('v.info', map='frane', flags='g')
# definisco come variabili i valori estremi in direzione NSWE del dataset delle frane
    frane_N = float(info_frane['north'])
    frane_S = float(info_frane['south'])
    frane_W = float(info_frane['west'])
    frane_E = float(info_frane['east'])

# se la regione di lavoro è più piccola del dataset delle frane
    if regione_N < frane_N and regione_S > frane_S and regione_W > frane_W and regione_E < frane_E:
        print('dataset ritagliato alla regione')
# ritaglia le frane sull'area di lavoro
        gs.run_command('v.overlay', ainput='frane', binput='area_di_lavoro', operator='and', output='frane_area_lavoro')
# e dopo butta via il dataset originale
        gs.run_command('g.remove', type='vector', name='frane', flags='f')
# in caso contrario butta via direttamente il dataset perché è troppo piccolo ed è un campione statistico distribuito male
    else: 
        gs.run_command('g.remove', type='vector', name='frane', flags='f')
        print("l'estensione del dataset è inferiore alla regione di lavoro")



def main():
     input_path=('/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work')
# faccio lo stesso per la sottocartella cartella "reclass"
     output_path=('/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work/reclass')
# con exist_ok=True impongo che se la cartella esiste già venga riutilizzata
     os.makedirs(input_path, mode=511, exist_ok=True)
     os.makedirs(output_path, mode=511, exist_ok=True)


     frane()

# seleziono i valori singoli che trovo nella colonna "a_tipo_movim"   
# questa parte ".strip().split('\n')[1:] " significa che non considero la prima riga cioè l'intestazione della tabella
     tipi_frane=gs.read_command('v.db.select', map='frane_area_lavoro', format='plain', columns='DISTINCT a_tipo_movim').strip().split('\n')[1:]
# per ogni valore che ho selezionato:
     for tipo in tipi_frane:
# definisco il nome della mappa output
# f"frana_{tipo}" significa che voglio concatenare il testo "frana_" al valore per cui sto facendo tutta la procedura
        output_map=f"frana_{tipo}"
# con v.extract salvo una nuova mappa per ciascun tipo di frana
        gs.run_command('v.extract', input='frane_area_lavoro', output=output_map, where = f'a_tipo_movim={tipo}', overwrite=True)

# elenco tutte le mappe vettoriali che stanno nel map set frane
# escludo la mappa "area_di_lavoro"
# devo escludere i crolli/ribaltamenti (tipo 1) 
# escludo anche la mappa frane_area_lavoro perché dalle prova dà risultati peggiori e inoltre comprende i crolli che in questo lavoro non vengono considerati
# le mappe che escludo sono separate da , 
        vectors=gs.parse_command('g.list', type='vector', mapset='frane', exclude='frane_area_lavoro,frana_1')
# creo una lista che chiamo vector_list che contiene le mappe che ho elencato sopra
        vector_list = [vector for vector in vectors]
# per tutti i vettori nella lista che ho creato
# trasformo la mappa in raster    
     for vector in vector_list:
        output_rast=f"{vector}"
        gs.run_command('v.to.rast', input=vector, output=output_rast, use='value', value=1)

     frane_rast=gs.parse_command('g.list', type='raster', mapset='frane', exclude='MASK')
# creo una lista che chiamo vector_list che contiene le mappe che ho elencato sopra
     frane_rast_list = [frana for frana in frane_rast]
# per tutti i rater nella lista che ho creato
# assegno valore 0 ai nulli    
     for frana in frane_rast_list:
        gs.run_command('r.null', map=frana, null=0)


if __name__ == '__main__':
    main()

