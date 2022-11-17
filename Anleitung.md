# Anleitung

**Autor**: Leo Halbritter - Studentischer Mitarbeiter TU Wien

## Voraussetzungen

Um die Modelle lokal auszuführen, sind die folgenden Tools notwendig:

- [Anaconda 3](https://www.anaconda.com)

### Windows

Ist die Anaconda Installation abgeschlossen muss nun unter Windows die *Anaconda Prompt* ausgeführt werden. In dieser kann ganz normal über den *cd \<path\>* Befehl in den Projekt-Ordner *hydraulics-models* navigiert werden. Das sollte dann in etwa so aussehen:

<img src="C:\Users\halbritter\AppData\Roaming\Typora\typora-user-images\image-20221117114354560.png" alt="image-20221117114354560" style="zoom: 80%;" />

### Linux

Unter Linux kann das normale Terminal gestartet werden und die *Anaconda Umgebung base* sollte automatisch aktiv sein.

### Umgebung installieren

In dem Projekt-Ordner sollte ein File mit dem Namen *environment.yml* zur Verfügung stehen. Die Umgebung *hydraulics* lässt sich einfach mit dem Befehl `conda env create -f environment.yml` installieren. Nach korrekter Ausführung sollte nun über den Befehl `conda activate hydraulics` die neue Umgebung aktiviert werden können. Ob das ganze erfolgreich war ist sichtbar anhand des Umgebungsnamen ganz links. Zeigt dieser *(hydraulics)* an, war die Installation erfolgreich.

![image-20221117115018544](C:\Users\halbritter\AppData\Roaming\Typora\typora-user-images\image-20221117115018544.png)

## Benutzung

Die Modelle sind als Hilfestellung für Lehrveranstaltungen mit Laborbetrieb gedacht. Sie sollen den Laborbetrieb simulieren. Um die Modelle lokal zu benutzen muss vorerst die unter **Voraussetzungen** erklärte Installation durchgeführt werden und dann folgende Schritte in dem Anaconda Fenster abgelaufen werden:

- **Umgebung aktivieren**: `conda activate hydraulics`
- **Zum Projekt-Ordner navigieren**: `cd pfad/zu/projekt/hydraulics_models`
- **Applikation starten**: `voila --enable_nbextensions=True`

Der letzte Schritt startet mit der Applikation auch den Standard-Browser des Systems. Es sollte nun eine Seite angezeigt werden, die drei Ordner mit den Namen:

- *ElasticAngle_Model* - Hier kann das Mechanik-Modell zum elastischen, starren Winkel simuliert werden
- *Pipe_Model* - Hier kann das Hydraulik-Modell zu einer reibungslosen Röhre simuliert werden
- *Tank_Model* - Hier kann das Hydraulik-Modell zu einem Wassertank mit Löchern simuliert werden

In jedem dieser Ordner befindet sich jeweils ein ".ipynb" File, welches jeweils ein Modell simuliert. Ein Klick auf eines der Files startet die jeweilige Simulation.

### Pipe Model

