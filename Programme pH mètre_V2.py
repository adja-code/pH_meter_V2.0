#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 11:34:52 2024

@author: Caroline Lu, Thomas Gauthier-Brouart, Thibault Chardon, Clara Palmieri, François Métivier
"""
from scipy import interpolate
import csv
import serial
import time
import numpy as np
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

def Calibration(buffers = [7, 4], n = 100):
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
    
    for i in range(len(buffers)):
    
        input('Prêt pour calibration pH%s ?' %(buffers[i]))
        print('Patientez 1 min le temps que la sonde se stabilise')
        
        # time.sleep(60)
        
        print('Les mesures commencent')
        
        port_test = serial.Serial(port = '/dev/ttyACM0', baudrate = 9600, timeout = 5) #Ouverture du port RS-232
        
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
                print(t,line, end="\r")
                data = line.strip('\r\n').split(';')
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
                line = port_test.readline().decode()
                st = str(time.time()-t0) + ';' + line
                print(st,end='\r')
                f.write(st)
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
        port_test.close()  

    model = np.polyfit(voltage_values, buffers, 1)
    print('Les paramètres a et b de notre regression linéaire sont', model)
    predict = np.poly1d(model)
    r2_score(buffers, predict(voltage_values))
    r2 = np.round(r2_score(buffers, predict(voltage_values)),5)
    R2 = 'r2 =', r2
    print(R2)
    equation = f'y = {model[0]}x + {model[1]}'

    res = input("Voulez-vous visualiser la calibration (O/N) ?")
    if res == O:
        plot_calib(voltage_values, buffers, errorbuffers_values, errorvoltage_values, t, EM4, EM7, EM10, predict)

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

    Parameters
    ----------
    Le nom du fichier à pH 7
    Le nom du fichier à pH 4
    Le nom du fichier à pH 10

    Returns
    -------
    model : list, liste
        DESCRIPTION. Les paramètres a et b de la courbe de calibration, a correspond au coefficient directeur et b à l'ordonnée à l'origine.

    """
    interface_calib_existante7 ="""
    ===========================================================================
    Veuillez renseigner le nom du fichier à pH7 : 
    ===========================================================================
    """
    x_calib_existante7 = input(interface_calib_existante7)
    interface_calib_existante4 ="""
    ===========================================================================
    Veuillez renseigner le nom du fichier à pH4 : 
    ===========================================================================
    """
    x_calib_existante4 = input(interface_calib_existante4)
    interface_calib_existante10 ="""
    ===========================================================================
    Veuillez renseigner le nom du fichier à pH10 : 
    ===========================================================================
    """
    x_calib_existante10 = input(interface_calib_existante10)
    
    buffers = [7, 4, 10]
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
    equation = f'y = {model[0]}x + {model[1]}'
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
    plt.show()
    return model


def measure(model, n = 100):
    """Mesure le pH en se basant sur une calibration et renvoie l'évolution des écart-type au cours du temps.

    Parameters
    ----------
    model: list, liste
        Calibration utilisée. Par défaut les paramètres de courbe de calibration est a = 75.55116667 et b = -163.1275.
    n : int, nombre de mesures
        DESCRIPTION. The default is 100.

    Returns
    -------
    pH_measure : float
        DESCRIPTION. La valeur du pH estimée.
    ecart_moyenne : plot
        DESCRIPTION. Evolution des écart à la moyenne au cours du temps.

    """

    pH_values = []
    voltage_values = []
    errorvoltage_values = []
    T = time.asctime()
    L = []

    
    print('Les mesures commencent')
    port_test = serial.Serial(port = '/dev/ttyACM0', baudrate = 9600, timeout = 5) #Ouverture du port RS-232


    f = open('DATA/fichier_mesure %s.csv' %(T), 'w')
    t0 = time.time()
    continuer = True
    count = 0

    # test de stabilité sur dix séries de mesures
    stab = np.zeros(10)
    stcount = np.zeros(10)
    while continuer:
        
        temp_sol = []
        v_sol = []
        i=0
        while i <= 10:
            try:
                line = port_test.readline().decode()
                data = line.strip("\r\n").split(";")
                temp_sol.append(float(data[0]))
                v_sol.append(float(data[1]))
                i+=1
            except:
                pass
            
        temp_sol = np.array(temp_sol)
        v_sol = np.array(v_sol)
        ph_sol = v_sol*model[0] + model[1]
        t = time.time()-t0

        # calcule la stabilité sur les dix denières valeurs de ph moyen
        stab[stcount] = np.mean(ph_sol)
        stcount +=1 
        if stcount < 10: # pas encore dix valeurs
            stabilite = -1
        else:
            stabilite = np.std(stab)
            stcount=0 # une fois arrivé à 10 on réinitialise le compteur => on remplace les plus anciennes valeurs

        st = " Temps: %4.2f\n Température: %4.2f +/- %4.2f\n Voltage: %4.2f +/- %4.2f\n PH: %4.2f +/- %4.2f\n Stabilité: %4.2f\n " % (t, np.mean(temp_sol), np.std(temp_sol), np.mean(v_sol), np.std(v_sol), np.mean(ph_sol), np.std(ph_sol),stabilite) 
        print(st)
        st = "%4.2f;%4.2f;%4.2f;%4.2f;%4.2f;%4.2f;%4.2f;%4.2f\n " % (t, np.mean(temp_sol), np.std(temp_sol), np.mean(v_sol), np.std(v_sol), np.mean(ph_sol), np.std(ph_sol),stabilite) 
        f.write(st)
        
        count += 1
        if count % 10 == 0 :
            res = input("Continuer les mesures (O/N) ? ")
            if res == 'N':
                continuer = False
                
    
    f.close()
    res =input("Voulez-vous visualiser graphiquement les mesures (O/N) ? ")
    if res in ['o','O','y','Y']:
        plot_mes(T)


def plot_mes(T):
    """Représentation graphique des séries de mesures

    Parameters
    ----------
    T : str
        date du fichier
    """

    t, mT, sT, mV, sV, mpH, spH, stabilite = np.loadtxt('DATA/fichier_mesure %s.csv' %(T), delimiter=";",unpack=True)
    
    fig,ax = plt.subplots(2)
    ax[0].plot(t,mpH, label = 'pH')
    ax[0].errorbar(t,mpH, yerr=spH, marker = 'o', color='C0')
    ax[0].set_ylabel('pH')
    ax[0].set_xlabel('Temps (s)')
    ax1 = ax[0].twinx()
    ax1.plot(t,mT, color='C1', label='Température')
    ax1.set_ylabel('Température (°C)')
    ax[0].title('Evolution temporelle des mesures de pH et température')
    ax[0].legend()
    
    
    ax[1].hist(mpH)
    ax[1].title('Histogramme des mesures de pH')
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

    fig,ax = plt.subplots(1)
    ax.scatter(voltage_values, buffers, marker = 'd')
    ax.errorbar(voltage_values, buffers, errorbuffers_values, errorvoltage_values, ecolor = 'black')
    x_lin_reg = range(0, 900)
    y_lin_reg = predict(x_lin_reg)
    ax.plot(x_lin_reg, y_lin_reg, c = 'r')
    ax.text(0.05, 0.95, equation, transform=plt.gca().transAxes, fontsize=12)
    ax.text(0.10, 0.90, R2, transform=plt.gca().transAxes, fontsize=12)
    
    
    fig2, ax2 = plt.subplots(1)
    ax2.plot(t,EM4, label = 'écart à la moyenne pH4')
    ax2.plot(t,EM7, label = 'écart à la moyenne pH7')
    if len(EM10)>0:
        ax2.plot(t,EM10, label = 'écart à la moyenne pH10')
    plt.title('Evolution de l\'écart-type des mesures')
    plt.legend()
 
 
    plt.show()


if __name__ == '__main__':
    
    interface ="""
    ===========================================================================
    BONJOUR
    ===========================================================================
    Que voulez-vous faire ?
    1 - Calibrer
    2 - Mesurer
    3 - Quitter
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
                Voulez - vous :
                1 - Calibrer avec deux tampons (pH 7 et 4) ?
                2 - Calibrer avec trois tampons (pH 7, 4 et 10) ?
                3 - Calibrer à partir d'une calibration déjà existante dans le répertoire
                4 - Quitter
                ===========================================================================
                ? """
                x_calib = input(interface_calib)
                if x_calib == '1':
                    calib3 = False
                    errorbuffers_values = [0.01, 0.01]
                    model = Calibration(buffers = [7, 4], n = 100)
                    y = input('Prêt à mesurer ?')
                    measure(model)
                    new_calib=True
                elif x_calib == '2':
                    calib3 = True
                    errorbuffers_values = [0.01, 0.01, 0.01]
                    model = Calibration(buffers = [7, 4, 10], n = 100)
                    y = input('Prêt à mesurer ?')
                    measure(model)
                    new_calib=True
                elif x_calib == '3':
                    model = Calibration_existante()
                    y = input('Prêt à mesurer ?')
                    measure(model)
                    new_calib = True
                elif x_calib == '4':
                    continuer_calib = False
        elif x == '2':
            y = input('Prêt à mesurer ?')
            if new_calib :
                measure(model)
            else : 
                measure(default_model)
        elif x == '3':
            continuer = False
    
    print('Fin du programme')

