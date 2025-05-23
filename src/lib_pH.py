#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 16:09:59 2024

@author ori: Clathi
"""

import serial
import serial.tools.list_ports
import os
import glob
import csv
import time
from datetime import datetime
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score


T4 = np.array([[0, 4.01], [5, 4.00], [10, 4.00], 
      [15, 4.00], [20, 4.00], [25, 4.01], 
      [30, 4.02], [35, 4.03], [40, 4.04], 
      [45, 4.05], [50, 4.06], [55, 4.08], 
      [60, 4.09], [65, 4.11], [70, 4.12], 
      [75, 4.14], [80, 4.16], [85, 4.17], 
      [90, 4.19], [95, 4.20]])


T7 = np.array([[0, 7.13], [5, 7.10], [10, 7.07], 
      [15, 7.05], [20, 7.03], [25, 7.01], 
      [30, 7.00], [35, 6.99], [40, 6.98], 
      [45, 6.98], [50, 6.98], [55, 6.98], 
      [60, 6.98], [65, 6.99], [70, 6.99], 
      [75, 7.00], [80, 7.01], [85, 7.02], 
      [90, 7.03], [95, 7.04]])

T10 = np.array([[0, 10.32], [5, 10.25], [10, 10.18], 
      [15, 10.12], [20, 10.06], [25, 10.01], 
      [30, 9.96], [35, 9.92], [40, 9.88], 
      [45, 9.85], [50, 9.82], [55, 9.79], 
      [60, 9.77], [65, 9.76], [70, 9.75], 
      [75, 9.74], [80, 9.74], [85, 9.74], 
      [90, 9.75], [95, 9.76]])


x_T4 = T4[:,0]
y_T4 = T4[:,1]
x_T7 = T7[:,0]
y_T7 = T7[:,1]
x_T10 = T10[:,0]
y_T10 = T10[:,1]
f4 = interpolate.interp1d(x_T4, y_T4)
f7 = interpolate.interp1d(x_T7, y_T7)
f10 = interpolate.interp1d(x_T10, y_T10)


#######################################################
#
# ACCES ARDUINO
#
#######################################################


def port_connexion(br = 9600 , portIN = '') :
    """
    Établit la connexion au port série.

    Parameters
    ----------
    br : int
        Flux de données en baud.
    portIN : string
        Identifiant du port série sur lequel le script doit lire des données.

    Returns
    -------
    port : string
        Identifiant du port série sur lequel le script doit lire des données.
    s : serial.tools.list_ports_common.ListPortInfo / string
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié. En cas d'échec de connexion, 's' sera une chaîne de caractères "erreur".

    """

    arduino_list=['85035323234351504260','85035323234351E09062','75439313737351402252','8503532323435130F142','75330303934351B05162']

    if portIN == '' :
        ports = list(serial.tools.list_ports.comports())
    else :
        ports = [portIN]  
    i = 0 
    conn = False
    while conn == False :
        try :
            port = ports[i] 
            if portIN == '' and (port.manufacturer == 'Arduino (www.arduino.cc)' or port.serial_number in arduino_list ):
                port = port.device
                port = (port).replace('cu','tty')
                s = serial.Serial(port=port, baudrate=br, timeout=5) 
                conn = True  
                print('Connexion établie avec le port', port)
            else :
                s = serial.Serial(port=port, baudrate=br, timeout=5)
                conn = True
                print('Connexion établie avec le port', port)
        except :
            i += 1
            if i >= len(ports) :
                print("/!\ Port de connexion non détecté. Merci de rétablir la connexion non établie : connexion au processeur dans les réglages avant utilisation.")
                s = 'error' 
                portIN = '' 
                conn = True
            pass     
    return port , s


def fn_settings(portIN , s , br , nb_inter , time_inter) :
    """
    Configuration des paramètres modifiables par l'utilisateur.

    Parameters
    ----------
    portIN : string
        Identifiant du port série sur lequel le script doit lire des données.
    s : serial.tools.list_ports_common.ListPortInfo
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié.
    br : int
        Flux de données en baud.
    nb_inter : int
        Nombre de valeurs utilisées pour constituer une mesure (une mesure correspond à la moyenne de toutes les valeurs prélevées).
    time_inter : float
        Temps d'intervalle entre chaque prélèvement de valeur au sein d'une mesure.

    Returns
    -------
    portIN : string
        Identifiant du port série sur lequel le script doit lire des données.
    s : serial.tools.list_ports_common.ListPortInfo
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié.
    br : int 
        Flux de données en baud.
    nb_inter : int
        Nombre de valeurs utilisées pour constituer une mesure (une mesure correspond à la moyenne de toutes les valeurs prélevées).
    time_inter : float
        Temps d'intervalle entre chaque prélèvement de valeur au sein d'une mesure.

    """
    
    print("Configurer le port de connexion : P \nChanger le flux (baudrate) : B \nChanger le temps et la fréquence de mesure : T")
    setting = input('>>> ')
    if setting == 'P' or setting == 'p':
        print('Saisissez le chemin du port (pour tester toutes les connexions périphériques de l\'ordinateur, laissez le champ vide)')
        port_name = input('>>> ')
        try :
            portIN , s = port_connexion(br, port_name)
        except Exception as inst :
            print("/!\ Echec de l'opération.")
            print('Erreur :',inst)
            pass
    elif setting == 'B' or setting == 'b' :
        try :
            br = int(input('Saisissez le nouveau baudrate : '))
            portIN , s = port_connexion(br, portIN)
            print('Paramètre enregistré.')
        except :
            print('/!\ Saisie invalide.')
            pass
    elif setting == 'T' or setting == 't' :
        try :
            time_measurement = float(input('Saisissez la durée d\'une mesure (sec) : '))
            nb_inter = int(input('Saisissez le nombres de valeurs composant une mesure : '))
            time_inter = time_measurement / nb_inter
            print("Une mesure comprend désormais ",nb_inter," valeurs, espacées entre elles de ",time_inter," secondes.\n")
        except :
            print('/!\ Saisie invalide.')
            pass
    else :
        print('/!\ Saisie invalide.')
    return portIN , s, br , nb_inter , time_inter





#######################################################
#
# FONCTIONS DE CALIBRATION
#
#######################################################

def Calibration(buffers = [7, 4], n = 200, port_test = ''):
    """Calibre la sonde pH pour 2 et 3 tampons (7, 4 et 10) en 100 mesures. Corrige les valeurs obtenues en fonction de la température.

    Parameters
    ----------
    buffers : list, liste
        DESCRIPTION. The default is [7, 4].
    n : int, nombre de mesures
        DESCRIPTION. The default is 100.

    Returns
    -------
    model : list, liste
        DESCRIPTION. Les paramètres a et b de la courbe de calibration, a correspond au coefficient directeur et b à l'ordonnée à l'origine.

    """
    EM4 = []
    EM7 = []
    EM10 = []
    voltage_values = []
    errorvoltage_values = []
    T = time.asctime()

    if port_test == '':
        port_test = serial.Serial(port = '/dev/ttyACM0', baudrate = 9600, timeout = 5) #Ouverture du port RS-232

    for i in range(len(buffers)):
    
        input('Prêt pour calibration pH%s ?' %(buffers[i]))
        print('Patientez 1 min le temps que la sonde se stabilise')
        
        # time.sleep(60)
        
        print('Les mesures commencent')
        
        
        t0 = time.time()
        t = 0
        temp_sol = []
        #
        # Principe on mesure pendant 60s puis on calcule la T moyenne et on s'en sert pour en déduire
        # les PH des solutions tampons
        #
        while t < 60:
            t = time.time()-t0
            try:
                line = port_test.readline().decode()
                data = line.strip('\r\n').split(';')
                print("%4.2f; %4.2f; %4.2f" % (t, float(data[0]), float(data[1])), end="\r")
                temp_sol.append(float(data[0]))
            except:
                # mauvaise mesure
                pass
        temperature = np.mean(np.array(temp_sol))
        
        print(f"La température relevée est de {temperature}")
        if buffers[i] == 4:
            y=np.round(f4(temperature),2)
        if buffers[i] == 7:
            y=np.round(f7(temperature),2)
        if buffers[i] == 10:
            y=np.round(f10(temperature),2)
        
        buffers[i] = y
        
        f = open('CALIB/fichier_calibration_pH%s %s.csv' %(buffers[i], T), 'w')
        t0 = time.time()
        
        for k in range(n):
            try:
                t = time.time()-t0
                line = port_test.readline().decode()
                data = line.strip('\r\n').split(';')
                st = "%4.2f; %4.2f; %4.2f" % (t, float(data[0]), float(data[1]))
                print(st,end='\r')
                f.write(st + '\n')
            except:
                pass
        f.close()
        
        f = open('CALIB/fichier_calibration_pH%s %s.csv' %(buffers[i], T), 'r')
        csv_reader = csv.reader(f, delimiter=';')
        L = []
        t = []
        for row in csv_reader:
            L.append(float(row[2]))
            t.append(float(row[0]))

        moyenne = np.mean(L)
        ecart_type = np.std(L)
        
        for m in range(len(L)):
        
            ecart_moyenne = (L[m]-moyenne)
            if np.round(buffers[i]) == 4.0:
                EM4.append(ecart_moyenne)
            if np.round(buffers[i]) == 7.0:
                EM7.append(ecart_moyenne)
            if np.round(buffers[i]) == 10.0:
                EM10.append(ecart_moyenne)

        voltage_values.append(moyenne)
        errorvoltage_values.append(ecart_type)

        f.close()

    model = np.polyfit(voltage_values, buffers, 1)
    print('Les paramètres a et b de notre regression linéaire sont', model)
    predict = np.poly1d(model)
    r2_score(buffers, predict(voltage_values))
    r2 = np.round(r2_score(buffers, predict(voltage_values)),5)
    R2 = 'r2 =', r2
    print(R2)
    equation = f'y = {model[0]}x + {model[1]}'

    res = input("Voulez-vous visualiser la calibration (O/N) ?")
    if res in ['O','o','y','Y']:
        plot_calib(voltage_values, buffers, errorbuffers_values, errorvoltage_values, t, EM4, EM7, EM10, predict, equation, R2)

    if r2 < 0.95:
        print('La calibration ne semble pas précise')
        x = input('Voulez-vous recalibrer le pH mètre ? (Oui: 1/Non: 2) ')
        if x == '1':
            if calib3 :
                Calibration(buffers = [7, 4, 10], n = 100)
            else :
                Calibration()
        if x == '2':
            print('Vous pouvez à présent mesurer')
    return model

def Calibration_existante():
    """Calibre la sonde pH pour 3 tampons (7, 4 et 10) à partir d'une calibration déjà existante, et présente dans le même répertoire que ce programme.

    Returns
    -------
    model : list, liste
        DESCRIPTION. Les paramètres a et b de la courbe de calibration, a correspond au coefficient directeur et b à l'ordonnée à l'origine.

    """

    # liste des fichiers disponibles
    # comme la calib existante demande une calibration à 10 on ne fait que la liste des pH10 existants
    #
    cali_dispo = sorted(glob.glob('./CALIB/*pH10*.csv'), key=os.path.getmtime)
    print("Calibrations disponibles:")
    for i in range(len(cali_dispo)):
        print("%i - %s" % (i, cali_dispo[i]))
    res = input("Choisissez votre calibration en entrant son numéro d'ordre: ")

    print(cali_dispo[int(res)][-28:-4])

    cali_chosen = glob.glob('./CALIB/*%s.csv' % (cali_dispo[int(res)][-28:-4]))
    # 
    
    buffers = np.zeros(3)
    for f in cali_chosen :
        print(f)
        if 'pH4' in f:
            x_calib_existante4 = f
            try:
                f2 = f.split('pH')[1]
                buffer_val = float(f2.split(' ')[0])
                buffers[1] = buffer_val
            except:
                buffers.append[4]
        elif 'pH7' in f:
            x_calib_existante7 = f
            try:
                f2 = f.split('pH')[1]
                buffer_val = float(f2.split(' ')[0])
                buffers[0] = buffer_val
            except:
                buffers.append(7)
        elif 'pH10' in f:
            x_calib_existante10 = f
            try:
                f2 = f.split('pH')[1]
                buffer_val = float(f2.split(' ')[0])
                buffers[2] = buffer_val
            except:
                buffer.append(10)
    
    # buffers = [7, 4, 10]
    EM4 = []
    EM7 = []
    EM10 = []
    voltage_values = []
    errorvoltage_values = []
    errorbuffers_values = [0.01, 0.01, 0.01]
    
    c4 = open(x_calib_existante4, 'r')
    c7 = open(x_calib_existante7, 'r')
    c10 = open(x_calib_existante10, 'r')

    ###############################
    csv_reader7 = csv.reader(c7, delimiter=';')
    L = []
    t = []
    for row in csv_reader7:
        L.append(float(row[2]))
        t.append(float(row[0]))
    moyenne = np.mean(L)
    ecart_type = np.std(L)
    for m in range(len(L)):
        ecart_moyenne = (L[m]-moyenne)
        EM7.append(ecart_moyenne)
    voltage_values.append(moyenne)
    errorvoltage_values.append(ecart_type)
    c7.close()
    
    ###############################
    csv_reader4 = csv.reader(c4, delimiter=';')
    L = []
    t = []
    for row in csv_reader4:
        L.append(float(row[2]))
        t.append(float(row[0]))
    
    moyenne = np.mean(L)
    ecart_type = np.std(L)
    
    for m in range(len(L)):
        ecart_moyenne = (L[m]-moyenne)
        EM4.append(ecart_moyenne)
    voltage_values.append(moyenne)
    errorvoltage_values.append(ecart_type)
    c4.close()
    
    ###############################
    csv_reader10 = csv.reader(c10, delimiter=';')
    L = []
    t = []
    for row in csv_reader10:
        L.append(float(row[2]))
        t.append(float(row[0]))

    moyenne = np.mean(L)
    ecart_type = np.std(L)
    
    for m in range(len(L)):
        ecart_moyenne = (L[m]-moyenne)
        EM10.append(ecart_moyenne)
    
    voltage_values.append(moyenne)
    errorvoltage_values.append(ecart_type)
    c10.close() 

    ###############################
    model = np.polyfit(voltage_values, buffers, 1)
    print('Les paramètres a et b de notre regression linéaire sont', model)
    predict = np.poly1d(model)

    r2_score(buffers, predict(voltage_values))
    r2 = np.round(r2_score(buffers, predict(voltage_values)),5)
    R2 = 'r2 =', r2
    print(R2)
    equation = 'y = %5.3f x + %5.3f' % (model[0],model[1])
    plot_calib(voltage_values, buffers, errorbuffers_values, errorvoltage_values, t, EM4, EM7, EM10, predict, equation, R2)

    
    return model

def default_Calibration():
    """Calibration par défaut de la sonde pH, effectuée en laboratoire.

    Returns
    -------
    model : list, liste
        DESCRIPTION. Les paramètres a et b de la courbe de calibration par défaut, a correspond au coefficient directeur et b à l'ordonnée à l'origine.

    """
    pH10 = 590.782
    pH7 = 368.935
    pH4 = 137.475
    dpH10 = 0.41288739384970324
    dpH7 = 0.4906882920959089
    dpH4 = 0.9483538369195328

    pH = [ 4, 7,  10]
    voltage_values = [pH4, pH7, pH10]
    model = np.polyfit(voltage_values, pH, 1)
    print('Les paramètres a et b de notre regression linéaire sont', model)
    predict = np.poly1d(model)
    voltage_mesure = 600
    predict(voltage_mesure)
    print('Pour un voltage de %s le pH prédit est de' %(voltage_mesure),predict(voltage_mesure))
    R2 = np.round(r2_score(pH, predict(voltage_values)),5)
    print(R2)
    
    fig,ax=plt.subplots(1)
    ax.plot(voltage_values, pH, 'o', color='C0')
    errorvoltage_values = [dpH4, dpH7, dpH10]
    errorpH_values = [0.01, 0.01, 0.01]    
    ax.errorbar(voltage_values, pH, errorpH_values, errorvoltage_values, 'o', ecolor = 'C0')
    
    R2 = 'r2 = %5.3f'% (R2)
    equation_default = 'y = %5.3f x + %5.3f' % (model[0], model[1])

    x_lin_reg = range(0, 1023)
    y_lin_reg = predict(x_lin_reg)
    ax.plot(x_lin_reg, y_lin_reg, color = 'C1')
    ax.text(0.05, 0.95, equation_default, transform=plt.gca().transAxes, fontsize=12)
    ax.text(0.10, 0.90, R2, transform=plt.gca().transAxes, fontsize=12)
    ax.set_title("Calibration par défaut")
    plt.show()
    return model


#######################################################
#
# FONCTIONS DE MESURE/CALCUL DE PH
#
#######################################################

def indiv_measure(port_test, model, n=10):
    """_summary_

    Parameters
    ----------
    model : _type_
        _description_
    n : int, optional
        _description_, by default 10

    Returns
    -------
    tuple contenant les moyennes et écart types de température, voltage et ph de la solution
    """

    temp_sol = []
    v_sol = []
    i=0
    while i <= n:
        try:
            line = port_test.readline().decode()
            # print(line.strip("\r\n"))
            data = line.strip("\r\n").split(";")
            temp_sol.append(float(data[0]))
            v_sol.append(float(data[1]))
            i+=1
        except:
            pass
            
    temp_sol = np.array(temp_sol)
    v_sol = np.array(v_sol)
    ph_sol = v_sol*model[0] + model[1]
    
    return (np.mean(temp_sol), np.std(temp_sol), np.mean(v_sol), np.std(v_sol), np.mean(ph_sol), np.std(ph_sol))

def measure(model, n_stab=20, port_test = '', n=10):
    """Mesure le pH en se basant sur une calibration et renvoie l'évolution des écart-type au cours du temps.

    effectue n mesure individuelles 

    Parameters
    ----------
    model: list, liste
        Calibration utilisée. Par défaut les paramètres de courbe de calibration est a = 75.55116667 et b = -163.1275.
    n : int, nombre d'acquisitions pour une mesure
        DESCRIPTION. The default is 10.
    n_stab: int, nombre de mesures utilisées dans le calcul de stabilité
    port_test = "", string, port com ouvert

    """

    pH_values = []
    voltage_values = []
    errorvoltage_values = []
    T = time.asctime()
    L = []

    
    print('Les mesures commencent')
    if port_test == '':
        port_test = serial.Serial(port = '/dev/ttyACM0', baudrate = 9600, timeout = 5) #Ouverture du port RS-232


    f = open('DATA/fichier_mesure %s.csv' %(T), 'w')
    f.write("#t, t_sol, st_sol, v_sol, sv_sol, ph_sol, sph_sol, stabilite\n")
    t0 = time.time()
    continuer = True
    count = 0

    # test de stabilité sur n_stab séries de mesures
    stab = -1*np.ones(n_stab)
    stcount = 0
    while continuer:
        
    
        t = time.time()-t0
        t_sol, st_sol, v_sol, sv_sol, ph_sol, stph_sol = indiv_measure(port_test, model,n)

        # calcule la stabilité sur les dix denières valeurs de ph moyen
        stab[stcount] = np.mean(ph_sol)
        stcount +=1 

        if stcount == n_stab: # pas encore n_stab valeurs
            stcount=0 # une fois arrivé à 10 on réinitialise le compteur => on remplace les plus anciennes valeurs

        stabilite = np.std(stab)
            
        st = " Temps: %4.2f\n Température: %4.2f +/- %4.2f\n Voltage: %4.2f +/- %4.2f\n PH: %4.2f +/- %4.2f\n Stabilité: %4.2f\n " % (t, t_sol, st_sol, v_sol, sv_sol, ph_sol, stph_sol, stabilite) 
        print(st)
        st = "%4.2f;%4.2f;%4.2f;%4.2f;%4.2f;%4.2f;%4.2f;%4.2f\n" % (t, t_sol, st_sol, v_sol, sv_sol, ph_sol, stph_sol, stabilite) 
        f.write(st)
        
        count += 1
        if count % 20 == 0 :
            res = input("Continuer les mesures (O/N) ? ")
            if res == 'N':
                continuer = False
                
    
    f.close()
    res =input("Voulez-vous visualiser graphiquement les mesures (O/N) ? ")
    if res in ['o','O','y','Y']:
        plot_mes(T)


#######################################################
#
# FONCTIONS GRAPHIQUES
#
#######################################################

def plot_mes(T):
    """Représentation graphique des séries de mesures

    Parameters
    ----------
    T : str
        date du fichier
    """

    t, mT, sT, mV, sV, mpH, spH, stabilite = np.loadtxt('DATA/fichier_mesure %s.csv' %(T), delimiter=";",unpack=True)
    
    fig,ax = plt.subplots(2, figsize=(7,15))
    ax[0].plot(t,mpH, label = 'pH')
    ax[0].errorbar(t,mpH, yerr=spH, marker = 'o', color='C0')
    ax[0].set_ylabel('pH')
    ax[0].set_xlabel('Temps (s)')
    ax1 = ax[0].twinx()
    ax1.plot(t,mT, color='C1', label='Température')
    ax1.set_ylabel('Température (°C)')
    ax[0].set_title('Evolution temporelle des mesures de pH et température')
    ax[0].legend()
    
    
    ax[1].hist(mpH)
    ax[1].set_title('Histogramme des mesures de pH')
    ax[1].legend()
    
    plt.show()
    


def plot_calib(voltage_values, buffers, errorbuffers_values, errorvoltage_values, t, EM4, EM7, EM10, predict, equation, R2):
    """Représentation graphique des calibrations

    Parameters
    ----------
    voltage_values : _type_
        valeurs de voltages de l'arduino
    buffers : _type_
        valeurs des tampons
    errorbuffers_values : _type_
        incertitudes sur les tampons
    errorvoltage_values : _type_
        incertitude sur les voltages
    t : _type_
        temps
    EM4 : _type_
        _description_
    EM7 : _type_
        _description_
    EM10 : _type_
        _description_
    predict : _type_
        fonction de prédiction pH=f(V)
    equation : _type_
        equation de la calibration
    R2 : _type_
        R2 de la calibration
    """

    fig,ax = plt.subplots(2, figsize=(7,15))
    ax[0].scatter(voltage_values, buffers, marker = 'd')
    ax[0].errorbar(voltage_values, buffers, errorbuffers_values, errorvoltage_values, ecolor = 'black')
    x_lin_reg = range(0, 900)
    y_lin_reg = predict(x_lin_reg)
    ax[0].plot(x_lin_reg, y_lin_reg, c = 'r')
    ax[0].text(0.05, 0.95, equation, transform=plt.gca().transAxes, fontsize=12)
    ax[0].text(0.10, 0.90, R2, transform=plt.gca().transAxes, fontsize=12)
    ax[0].set_title('Droite de calibration')
    plt.legend()
    
    ax[1].plot(t,EM4, label = 'écart à la moyenne pH4')
    ax[1].plot(t,EM7, label = 'écart à la moyenne pH7')
    if len(EM10)>0:
        ax[1].plot(t,EM10, label = 'écart à la moyenne pH10')
    ax[1].set_title('Evolution de l\'écart-type des mesures')
    plt.legend()
 
 
    plt.show()

def graph():
    """Fait un graphique 
    ph =f(t) et T=f(t) avec barres d'erreurs  
    à partir d'un fichier de mesures
    sélectionné dans le dossier ./DATA

    propose la sauvegarde du fichier dans le dossier ./FIGURES au format pdf
    """

    mes_dispo = sorted(glob.glob('./DATA/*.csv'), key=os.path.getmtime)
    print("fichiers disponibles:")
    for i in range(len(mes_dispo)):
        print("%i - %s" % (i, mes_dispo[i]))
    res = input("Choisissez votre fichier en entrant son numéro d'ordre: ")

    try:
        data_name = mes_dispo[int(res)]
        t, t_sol, st_sol, v_sol, sv_sol, ph_sol, sph_sol, stabilite = np.loadtxt(data_name,delimiter=';',unpack=True)

        fig,ax = plt.subplots(1)
        
        ax.errorbar(t,ph_sol,yerr=2*sph_sol,fmt='o-', color='C0')
        ax1 = ax.twinx()
        ax1.errorbar(t,t_sol,yerr=2*st_sol,fmt='o-', color='C1')
        ax.set_xlabel("temps (s)")
        ax.set_ylabel("pH", color='C0')
        ax1.set_ylabel("température ($^\circ$C)", color='C1')
        plt.show()
        plt.pause(0.001)
        res = input("sauver (O/N) ? ")
        if res in ["O","o","Y","y"]:
            plot_name = data_name[:-3]+'pdf'
            plot_name = "./FIGURES/"+plot_name.strip('./DATA/')
            print(plot_name)
            plt.savefig(plot_name, bbox_inches='tight')
            
    except:
        print("problème dans l'ouverture du fichier ou la réalisation du graphique")

#######################################################
#
# clathi unused
#
#######################################################


def pH_sensor(nb_inter , time_inter , s) :
    """
    Mesure du voltage du pH-mètre et de la température.

    Parameters
    ----------
    nb_inter : int
        Nombre de valeurs utilisées pour constituer une mesure (une mesure correspond à la moyenne de toutes les valeurs prélevées).
    time_inter : float
        Temps d'intervalle entre chaque prélèvement de valeur au sein d'une mesure.
    s : serial.tools.list_ports_common.ListPortInfo
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié.

    Returns
    -------
    list_pH : list
        valeurs de voltages liées au pH et utilisées pour une mesure.
    list_temperatures : list
        valeurs de températures utilisées pour une mesure.

    """
    
    try :
        s.close()
        s.open()
        time.sleep(1)
    except :
        pass

    list_temperatures ,list_pH = [] , []
    err = 0 
    progression , restant = '' , int(nb_inter)
    for i in range(nb_inter) :
        try :
            values = s.readline().decode()
            values = values.split(";")
            temperature = float(values[0])
            list_temperatures.append(temperature)
            pH = float(values[1])
            list_pH.append(pH)
            progression += '*'
        except :
            err += 1
            progression += '!'
        restant -= 1
        barre = progression + restant * ' '
                    
        print(f'\r[{barre}]',flush=True, end='')
        time.sleep(time_inter) ## Time interval
    print('\n',err,f'problème(s) de lecture sur {nb_inter} mesures.\n')
    if err == nb_inter : 
        print('/!\ Un problème systématique semble empêcher la mesure. Veuillez vérifier la connexion à l\'appareil dans les paramètres.')
    return list_pH , list_temperatures   


def measurement(a , b , nb_inter , time_inter, s) :
    """
    Mesure unique ou en série et enregistrement éventuel des données.

    Parameters
    ----------
    a : float
        Pente de régression linéaire entre pH et voltage mesuré.
    b : float
        Ordonnée à l'origine de régression linéaire entre pH et voltage mesuré.
    nb_inter : int
        Nombre de valeurs utilisées pour constituer une mesure (une mesure correspond à la moyenne de toutes les valeurs prélevées).
    time_inter : float
        Temps d'intervalle entre chaque prélèvement de valeur au sein d'une mesure.
    s : serial.tools.list_ports_common.ListPortInfo
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié.

    Returns
    -------
    None.

    """
    
    print('Voulez-vous enregistrer les données (format csv) ? (y/n)')
    data_rec = input('>>> ')
    valid = False
    while valid == False :
        try :
            nb_mesure = int(input("Nombre de mesures à effectuer : "))
            valid = True
        except :
            print('/!\ Saisie invalide, veuillez saisir un nombre entier.')  
    if nb_mesure != 1 :
        valid = False
        while valid == False :
            try :
                time_mesure = float(input("Intervalle de temps entre deux mesures (en sec) : "))
            except :
                time_mesure = -9999
                pass
            if time_mesure-time_inter*nb_inter >= 0:
                valid = True
            else:
                print(f"/!\ L'intervalle doit être supérieur ou égal à {time_inter*nb_inter} sec.")  
    LIST_DATES = []
    LIST_TEMP , LIST_TEMPSTD = [] , []
    LIST_PH , LIST_PHSTD = [] , []
    for mesure in range(nb_mesure) :     
        LIST_DATES.append(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
        list_pH , list_temperatures = pH_sensor(nb_inter,time_inter,s)
        list_pH = np.array(list_pH)
        a , b = float(a) , float(b)
        list_pH = a*list_pH + b
        pH , pHstd = np.mean(list_pH) , np.std(list_pH)
        temp , tempstd = np.mean(list_temperatures) , np.std(list_temperatures)
        temp , tempstd = np.round(temp,2) , np.round(tempstd,4)
        pH , pHstd = np.round(pH,2) , np.round(pHstd,4)
        LIST_TEMP.append(temp)
        LIST_TEMPSTD.append(tempstd)
        LIST_PH.append(pH)
        LIST_PHSTD.append(pHstd)
        print(f'mesure nº{mesure+1}/{nb_mesure},',LIST_DATES[-1])
        print(f'   Température : {temp} °C \n   pH moyen : {pH} (écart-type : {pHstd})\n')
        if nb_mesure != 1 :
            time.sleep(time_mesure-time_inter*nb_inter)
    data = np.array([LIST_DATES , LIST_PH , LIST_PHSTD , LIST_TEMP , LIST_TEMPSTD]).T
    if data_rec == 'y' or data_rec == 'Y' :
        np.savetxt('mesure_pH_' + datetime.now().strftime("%m-%d-%Y_%Hh%Mm%Ss") 
                   + '.csv', data, delimiter=',', fmt='%s',
                   header= 'Date de mesure,pH,écart-type pH,Température,écart-type température')
    return 



def pH_temp_adjust(pH , temp) :
    """
    Ajustement du pH étalon en fonction de la température par interpolation linéaire.

    Parameters
    ----------
    pH : int
        pH de la solution étalon.
    temp : float
        température mesurée de la solution.

    Returns
    -------
    pH_adjusted : float
        pH interpolé en fonction de correspondances entre pH et températures connues.

    """
    
    ## tables of values | source : HANNA intruments, Buffer solutions | uncertainties : ± 0.01 pH @ 25°C
    TEMPERATURES = np.arange(0,100,5)
    pH_4  = np.array([4.01,4.00,4.00,4.00,4.00,4.01,4.02,4.03,4.04,4.05,4.06,4.08,4.09,4.11,4.12,4.14,4.16,4.17,4.19,4.20])
    pH_7  = np.array([7.13,7.10,7.07,7.05,7.03,7.01,7.00,6.99,6.98,6.98,6.98,6.98,6.98,6.99,6.99,7.00,7.01,7.02,7.03,7.04])
    pH_10 = np.array([10.32,10.25,10.18,10.12,10.06,10.01,9.96,9.92,9.88,9.85,9.82,9.79,9.77,9.76,9.75,9.74,9.74,9.74,9.75,9.76])  
    if pH == 4:
        pH_adjusted = np.interp(temp,TEMPERATURES,pH_4)
    elif pH == 7:
        pH_adjusted = np.interp(temp,TEMPERATURES,pH_7)
    elif pH == 10:
        pH_adjusted = np.interp(temp,TEMPERATURES,pH_10)
    
    return pH_adjusted


