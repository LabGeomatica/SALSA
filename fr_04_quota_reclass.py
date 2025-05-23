#!/usr/bin/env python3

# dati richiesti:
# ampiezza classe di quota
# percorso cartella di lavoro


import os
import grass.script as gs


def classificazione(input_raster, ampiezza_classe):

    
# mi sposto nel mapset mappe_reclass e se non esiste lo creo
    gs.run_command('g.mapset', mapset='mappe_reclass', flags='c')
# con r.info recupero i principali dati sul DTM    
    info_quota=gs.parse_command('r.info', map=input_raster, flags='r')
# definisco come variabili il valore massimo e il vlaore minimo del DTM
    max=float(info_quota['max'])
    min=float(info_quota['min'])
# clacolo il range di valore, come la differenza tra max e min
    differenza=max-min
# divido il range di valori per l'ampiezza di ciascuna classe e trovo il numero di classi che devo fare     
# così in caso di valori che si dividono perfettamente
    if(differenza % ampiezza_classe) == 0:
        numero_classi = differenza/ampiezza_classe
# nel caso che la divisione abbiau n resto aggiungo 1 alla parte intera
    else:
        numero_classi=(differenza/ampiezza_classe) + 1
    numero_classi=int(numero_classi)
    # print(numero_classi)

# creo un file nuovo che poi userò per il reclass
    file_per_reclass=open('/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work/quota_rec', 'w')
    

# scrivo nel file le regole di reclass della quota
# faccio in modo che sia indipendente da quante classi ho e dall'ampiezza che scelgo per la classe
    for classe in range(numero_classi):
        file_per_reclass.writelines([f"{min + (ampiezza_classe*classe)} thru {ampiezza_classe*(classe + 1)}={classe +1} \n"])
# aggiungo le due linee di istruzioni in fondo al file di reclass 
    file_per_reclass.writelines(['*=*\n''end'])

def reclass(input_raster, regole):
# uso il comando r.reclass mettendo come file di regole quello che ho appena creato
    gs.run_command('r.reclass', input=input_raster, output='quota_rec', rules=regole)
# rendo indipendente la mappa riclassificata dal DTM originale
    gs.mapcalc('{r}={a}*1'.format(r='quota_reclass', a='quota_rec'))
    gs.run_command('g.remove', type='raster', name='quota_rec', flags='f')




def main():
# definisco le variabili che userò nelle mie funzioni
# se voglio cambiare l'ampiezza delle classi o il raster di input devo cambiarli solo qui
    input_raster = 'DTM_ok'  # Nome del raster di input
    ampiezza_classe=250
# stabilisco che il file con le regole di reclass sia salvato nellamia cartella work
    regole='/home/ilaria/Scrivania/prove_varie/impara_python/blocchi_per_frane/work/quota_rec'
    classificazione(input_raster, ampiezza_classe)
    reclass(input_raster, regole)
 

if __name__ == '__main__':
    main()
