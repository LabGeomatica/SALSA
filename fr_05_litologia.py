#!/usr/bin/env python3

import grass.script as gs
import os

# Dati necessari:
# la mappa della litologia elaborata dal CNR IRPI
# https://www.cnr.it/it/comunicato-stampa/11583/una-nuova-carta-litologica-digitale-per-lo-studio-della-geologia-italiana
# https://essd.copernicus.org/articles/14/4129/2022/
# dataset scaricabile all'indirizzo https://doi.pangaea.de/10.1594/PANGAEA.935673

# Da sistemare al 27/03/2025:
# Bisognerebbe impacchettare la mappa modificata insieme allo script

def main():
# mi trasporto nel mapset "mappe_di_base" e se non esiste lo creo
    gs.run_command('g.mapset', mapset='mappe_di_base', flags='c')
# importo la mappa della litologia restringendo l'importazione solo alle feature che ricadono almeno in parte entro la regione di lavoro
# la mappa originale (litology_italy.gpkg) è raggruppata, quindi l'importazione prende tutta l'Italia mettendoci moltro tempo e su PC non molto potenti si pianta
# per superare questo problema la mappa è stata creata in QGIS una copia non raggruppata (litology_italy_single_parts.gpkg) e si importa questa
    gs.run_command('v.import', extent='region', input='/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/litology_italy_single_parts.gpkg', output='lito_italy')
# mi trasporto nel mapset "mappe_reclass"
    gs.run_command('g.mapset', mapset='mappe_reclass', flags='c')
# trasformo la mappa importata in raster, che viene automaticamente tagliato sulla maschera
    gs.run_command('v.to.rast', input='lito_italy', output='litologia_reclass', use='attr', attribute_column='cat_')

if __name__ == '__main__':
    main()



