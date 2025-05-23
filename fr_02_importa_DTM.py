#!/usr/bin/env python3

# Questo script mi serve per:
# importare il DTM
# se necessario ricampionarlo 

# I dati che devo immettere sono:
# nome e percorso DTM con risoluzione uguale o superiore a quella di lavoro

# Cose da risolvere al 12/3/2025:
# impostare la risoluzione del DTM direttamente da quella della regione
# come si fa nel caso di risoluzione ns molto diversa da ew?
# come si fa ad impostare un intervallo di valori da mandare a null?


import os
import grass.script as gs

def main():
# mi trasporto nel mapset "mappe_di_base" e se non esiste lo creo
# in teoria dovrei già esserci
    gs.run_command('g.mapset', mapset='mappe_di_base', flags='c')
# importo il DTM con r.import, così se è in un sistema di coordinate diverso viene riproiettato
# scegliere il file del DTM da usare e inserire il percorso completo
    gs.run_command('r.import', input= '/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/dtm_liguria_20m.tif', outpu='DTM', overwrite=True)
# faccio r.info sul DTM per ottenere i valori della risoluzione
# flags='g' significa scrivi le informazioni in un formato che possa esser letto in uno script
    info_DTM = gs.parse_command('r.info', map='DTM', flags='g')
# prendo la risoluzione Nord Sud e la trasformo in una variabile
    DTM_nsres = float(info_DTM['nsres'])
    DTM_ewres = float(info_DTM['ewres'])
# impostare la risoluzione scelta per la regione di lavoro + 1 per considerare anche il valore massimo
# sarebbe bello riferirsi direttamente alla risoluzione della regione senza dovere mettere il valore manualmente
# ATTENZIONE! COME FARE NEL CASO DI DTM CON RISOLUZIONE NS MOLTO DIVERSA DA RISOLUZIONE EW?
    if DTM_ewres < 19 and DTM_nsres < 19:  # ATTENZIONE! per adesso ho considerato come risoluzione di lavoro 20, ma bisogna pescare la risoluzione della regione + o - 1
        print('DTM da ricampionare!')
# elimino i valori che spesso si trovano a rappresentare i nulli
# ho messo una lista dei più comuni, ma come si fa se nel DTM si usa un'altra regola?
        gs.run_command('r.null', map='DTM', setnull= '-999, -9999, -32767')
        gs.run_command('r.resamp.stats', input='DTM', output='DTM_ok')
        gs.run_command('g.remove', type='raster', name='DTM', flags='f')
    elif DTM_ewres > 21 and DTM_nsres > 21:
        gs.run_command('g.remove', type='raster', name='DTM', flags='f')
        print('risoluzione troppo bassa')
        print('DTM rimosso')
    else: 
        gs.run_command('g.rename', raster='DTM,DTM_ok')
        print('questo DTM è quello che mi serve')

if __name__ == '__main__':
    main()
