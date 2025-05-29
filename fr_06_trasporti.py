#!/usr/bin/env python3

# con questo script si importano le tratte stradali e ferroviarie
# si potebbe valutare anche di fare con la viabilità secondaria
# si rasterizza e si creano i diversi buffer

# !!! Attenzione!  i layer in ingresso devono contenere linee ed essere topolgicamente corretti
# !!! Prima di importare le reti bisogna eliminare le aree in galleria



import grass.script as gs
import os

 
def rete():
# mi sposto nel mapset mappe_di_base
    gs.run_command('g.mapset', mapset='mappe_di_base', flags='c')

# importo il file con la rete stradale e quello con la rete ferroviaria

    gs.run_command('v.import', input='/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/rete_trasporti/ferrovia_pulito.shp', output='ferrovia', overwrite=True)
    gs.run_command('v.import', input='/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/rete_trasporti/strade_pulito.shp', output='rete_stradale', overwrite=True)

# voglio accertarmi che il file della rete stradale che ho importato copra almeno tutta la mia regione di lavoro
# uso ilcomando g.region per ottenere le informazioni sulla mia regione
    info_regione=gs.parse_command('g.region', flags='g')
# definisco come variabili i valori estremi in direzione NSWE della mia regione
    regione_N = float(info_regione['n'])
    regione_S = float(info_regione['s'])
    regione_W = float(info_regione['w'])
    regione_E = float(info_regione['e'])
    # print(regione_E) 

# uso il comando v.info per ottenere informazioni sul dataset della rete stradale
    info_rete_stradale=gs.parse_command('v.info', map='rete_stradale', flags='g')
# definisco come variabili i valori estremi in direzione NSWE del dataset delle frane
    rete_stradale_N = float(info_rete_stradale['north'])
    rete_stradale_S = float(info_rete_stradale['south'])
    rete_stradale_W = float(info_rete_stradale['west'])
    rete_stradale_E = float(info_rete_stradale['east'])

# se la regione di lavoro è più piccola del dataset della rete stradale
    if regione_N < rete_stradale_N and regione_S > rete_stradale_S and regione_W > rete_stradale_W and regione_E < rete_stradale_E:
        print('dataset rete stradale ritagliato alla regione')
# ritaglia la rete stradale sull'area di lavoro
        gs.run_command('v.overlay', ainput='rete_stradale', binput='area_di_lavoro', operator='and', output='rete_stradale_tagliato')
# e dopo butta via il dataset originale
        gs.run_command('g.remove', type='vector', name='rete_stradale', flags='f')
# in caso contrario butta via direttamente il dataset perché è troppo piccolo
    else: 
        gs.run_command('g.remove', type='vector', name='rete_stradale', flags='f')
        print("l'estensione del dataset è inferiore alla regione di lavoro")

# faccio lo stesso lavoro per il dataset delle ferrovie
# uso il comando v.info per ottenere informazioni sul dataset delle ferrovie
    info_ferrovia=gs.parse_command('v.info', map='ferrovia', flags='g')
# definisco come variabili i valori estremi in direzione NSWE del dataset delle ferrovie
    ferrovia_N = float(info_ferrovia['north'])
    ferrovia_S = float(info_ferrovia['south'])
    ferrovia_W = float(info_ferrovia['west'])
    ferrovia_E = float(info_ferrovia['east'])

# se la regione di lavoro è più piccola del dataset delle ferrovie
    if regione_N < ferrovia_N and regione_S > ferrovia_S and regione_W > ferrovia_W and regione_E < ferrovia_E:
        print('dataset ferrovia ritagliato alla regione')
# ritaglia le frane sull'area di lavoro
        gs.run_command('v.overlay', ainput='ferrovia', binput='area_di_lavoro', operator='and', output='ferrovia_tagliato')
# e dopo butta via il dataset originale
        gs.run_command('g.remove', type='vector', name='ferrovia', flags='f')
# in caso contrario butta via direttamente il dataset perché è troppo piccolo ed è un campione statistico distribuito male
    else: 
        gs.run_command('g.remove', type='vector', name='ferrovia', flags='f')
        print("l'estensione del dataset è inferiore alla regione di lavoro")


def main():
    rete()
# unisco i layer dalla rete stradale e ferroviaria
# in questa versione base non mi porto dietro la tabella degli attributi perché assegno le stesse fasce di buffer a ciascun tipo di strada
    gs.run_command('v.patch', input='rete_stradale_tagliato@mappe_di_base,ferrovia_tagliato@mappe_di_base', output='rete_trasporti', overwrite=True)
# trasformo la rete in raster
    gs.run_command('v.to.rast', input='rete_trasporti@mappe_di_base', type='line', output='trasporti', use='value', value=1, overwrite=True)
# elimino le mappe vettoriali di lavoro    
    gs.run_command('g.remove', type='vector', name='ferrovia_tagliato,rete_stradale_tagliato,rete_trasporti', flags='f')
# mi trasferisco nel mapset mappe_reclass
    gs.run_command('g.mapset', mapset='mappe_reclass', flags='c')
# qui inserisco le fasce di buffer
    gs.run_command('r.buffer', input='trasporti@mappe_di_base', output='trasporti_rec', distances='50,100,150,200', overwrite=True)
# includo l'asse stradale nella classe 1
    gs.mapcalc('{r} = if({a}<3, 1, if({a}<4, 2, if({a}<5, 3, 4)))'.format(r='trasporti_reclass', a='trasporti_rec'), overwrite = True)
# elimino la mappa di lavoro trasperti_rec
    gs.run_command('g.remove', type='raster', name='trasporti_rec', flags='f')
#   assegno il valore 5 (o comunque il valore più alto) alla classe oltre i 200 m
    gs.run_command('r.null', map='trasporti_reclass', null=5)


if __name__ == '__main__':
    main()
