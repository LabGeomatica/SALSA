#!/usr/bin/env python3

# in questo file creo dal DTM le mappe di pendenza, esposizione e accumulazione e le riclassifico
# per la pendenza ho provato anche r.reclass ma non mi convince molto perché la mappa risultante resta legata a quella originaria

# Cose da risolvere al 12/3/2025:
# mi conviene creare il mapset mappe_classificate o lascio tutto nelle mappe di base?
# c'è un modo di stabilire per le quote "ogni 250 m cambia classe"? In teoria potrei avere solo poche classi o arrivare alla cima dell'Everest
# si decide una logica nei nomi delle classi? (es. in ordine alfabetico...)
# le classi le stabilisco io una volta per tutte o do la possibilità di impostarle?
# potrebbe avere senso far scegliere diversi modi di stabilre le classi?


import grass.script as gs
import os

# funzione per impostare regione, risoluzione e maschera per un mapset nuovo

def mapset():
# collego il mapset appena creato al mapset mappe_di_base per recuperare la mappa dell'area di lavoro
    gs.run_command('g.mapsets', mapset='mappe_di_base', operation='add', format='plain')   
 # imposto la regione sulla mappa vettoriale dell'area di lavoro e scelgo la risoluzione #   
    gs.run_command('g.region', vector='area_di_lavoro@mappe_di_base', res=20)
# imposto la maschera usando la mappa vettoriale della mia area di lavoro
    gs.run_command('r.mask', vector= 'area_di_lavoro@mappe_di_base')


def main():
# mi trasporto nel mapset "mappe_di_base" e se non esiste lo creo
# in teoria dovrei già esserci
    gs.run_command('g.mapset', mapset='mappe_di_base', flags='c')
# calcolo pendenza ed esposizione
# la pendenza è calcolata in gradi
# l'esposizione è calcolata partendo da Nord in senso antiorario
# il parametro -e serve per stimare i valori di pendenza ed esposizione nelle aree di confine dove non è possibile calcolarli
# restano comunque alcune aree dove non sono calcolati, in corrispondenza di moli o struttture molto sottili (1 cella sola)
    gs.run_command('r.slope.aspect', elevation='DTM_ok', slope='pendenza', aspect='esposizione', flags ='e')
# calcolo l'accumulazione
# non metto la threshold perché non mi interessa l'estensione dei sottobacini
    gs.run_command('r.watershed', elevation='DTM_ok', accumulation='accumulazione')
# mi sposto nel mapset mappe_reclass e se non esiste lo creo
    gs.run_command('g.mapset', mapset='mappe_reclass', flags='c')
#imposto regione, risoluzione e maschera attraverso la funzione mapset()
    mapset()
# riclassifico la pendenza tramite t.mapcalc   
    gs.mapcalc('{r} = if({a}<5, 1, if({a}<10, 2, if({a}<15, 3, if({a}<20, 4, if({a}<25, 5, if({a}<30, 6, if({a}<35, 7, if({a}<40, 8, 9))))))))'.format(r='pendenza_reclass', a='pendenza'))
# riclassifico l'esposizione tramite r.mapcalc  
    gs.mapcalc('{r} = if({a}<45, 1, if({a}<135, 2, if({a}<225, 3, if({a}<315, 4, if({a}<360, 1, 0)))))'.format(r='esposizione_reclass', a='esposizione'))

# normalizzo l'accumulazione facendo il log del valore assoluto + 1    
    gs.mapcalc('{r} = log(abs({a})+1)'.format(r='log_abs_acc_1', a='accumulazione'))
# riclassifico l'accumulazione tramite r.mapcalc   
    gs.mapcalc('{r} = if({a}<1, 1, if({a}<2, 2, if({a}<3, 3, if({a}<4, 4, if({a}<5, 5, 6)))))'.format(r='accumulazone_reclass', a='log_abs_acc_1'))
# rimuovo la mappa di lavoro
    gs.run_command('g.remove', type='raster', name='log_abs_acc_1', flags='f')

if __name__ == '__main__':
    main()


# le righe commentate qui sotto sono per riclassificare la pendenza con r.reclass
# il file di regole è creato con lo script file_per_reclass.py
# non mi piace molto come soluzione perché il file riclassificato resta collegato all'originale
    # gs.run_command('r.reclass', input='pendenza', output='pendenza_reclass', rules='/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work/pendenza_rec')