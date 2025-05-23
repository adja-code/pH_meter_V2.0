#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 11:34:52 2024

@author: Thibault Chardon, Thomas Gauthier-Brouart, Caroline Lu, François Métivier, Clara Palmieri
"""

from lib_pH import *


if __name__ == '__main__':

    plt.ion()

    try:
        port, s = port_connexion()
        print("pH-mètre connecté  au port %s" % (port))
    except:
        print("Attention aucun arduino disponible")
    
    interface ="""
    ===========================================================================
    MENU PRINCIPAL
    ===========================================================================
    Que souhaitez-vous faire ?
    1 - Calibrer
    2 - Mesurer
    3 - Représenter graphiquement
    4 - Quitter
    ===========================================================================
    ? """

    new_calib = False
    continuer = True
    calib3 = False
    continuer_calib = True
    default_model = default_Calibration()
    while continuer:
        
        x = input (interface)
        
        if x == '1':
            
            while continuer_calib :
                interface_calib ="""
    ===========================================================================
    MENU CALIBRATION
    ==========================================================================
    Voulez - vous :
    1 - Calibrer avec deux tampons (pH 7 et 4) ?
    2 - Calibrer avec trois tampons (pH 7, 4 et 10) ?
    3 - Calibrer à partir d'une calibration déjà existante dans le répertoire
    4 - Quitter le menu calibration et retourner au menu principal
    ===========================================================================
    ? """
                x_calib = input(interface_calib)
                if x_calib == '1':
                    calib3 = False
                    errorbuffers_values = [0.01, 0.01]
                    model = Calibration(buffers = [7, 4], n = 300, port_test = s)
                    new_calib=True

                elif x_calib == '2':
                    calib3 = True
                    errorbuffers_values = [0.01, 0.01, 0.01]
                    model = Calibration(buffers = [7, 4, 10], n = 300, port_test = s)
                    new_calib=True

                elif x_calib == '3':
                    model = Calibration_existante()
                    new_calib = True

                elif x_calib == '4':
                    continuer_calib = False

        elif x == '2':
            y = input('Prêt à mesurer ?')
            if new_calib :
                measure(model, port_test = s)
            else : 
                measure(default_model, port_test = s)
        elif x == "3":
            graph()
        elif x == '4':
            continuer = False
    
    print('Fin du programme')

