# SAFE-M-PH: un pH-mètre low cost pour l'enseignement

* [Introduction](##introduction)
* [L'appareil](##appareil)
* [Scripts](##arduino-scripts)
* [Programme python](##python)

## Introduction <a class="anchor" id="introduction"></a>

* Ce programme permet de contrôler un ph-mètre arduino équipé d'une sonde de température PT100.
* Il résulte d'un travail collectif effectué par des étudiants de Licence 3 de l'Institut de physique du globe de Paris
* Il est distribué sous la licence créative common CC-by-SA 4.0


## L'appareil <a class="anchor" id="appareil"></a>

![](./Docs/compo.png)

Le principe de l'appareil reprend les spécification de DFROBOT https://wiki.dfrobot.com/PH_meter%28SKU__SEN0161%29 .
Deux ajouts sont effectués afin d'améliorer la précision:

* une sonde de température PT100 a été ajoutée afin de corriger, partiellement, de l'effet de la température;
* la calibration du pH mètre est effectuée et contrôlée par le programme Python.

Les sondes pH sont reliées à l'arduino via un amplificateur de signal muni d'un portard permettant de régler la gamme de tension. Tous les pH-mètre ont été réglé afin de pouvoir mesurer des solutions avec des pH d'au moins 2. à cette fin la vis de règlage est ajustée afin que l'électrode plongée dans une solution tampon de pH = 2 donne un voltage de 240 mV environ.

Le montage est effectué au moyen d'une carte PCB dessinée avec Fritzing 
![](./Fritzing/circuit.png)


## Script Arduino <a class="anchor" id="arduino-scripts"></a>

Le script arduino est simple et consiste uniquement à demander à l'appareil d'effectuer des mesures à une fréquence de 10Hz et les envoyer sur le port série. les mesures sont, d'une part, une mesure du voltage renvoyé par l'éléctrode pH et, d'autre part, une mesure de température renvoyée par la sonde PT100

## Programme Python <a class="anchor" id="python-and-sql"></a>

La récupération, au moyen du port série, et l'analyse des données est effectuée au moyen d'un programme python. Pour fonctionner le programme nécessite, en plus des librairies standard l'installation des librairies suivantes: numpy, scipy, matplotlib, sklearn.

Pour des raisons de simplicité le script fonctionne en mode terminal, pas d'interface utilisateur graphique donc, et offre des choix à l'étudiant.