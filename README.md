#  README

Basado en python3, para el correcto funcionamiento del script, hacen falta tener instalados los paquetes siguientes:

* re
* sys
* math
* time
* numpy
* pandas
* argparse
* requests
* collections
* Geopy.distance

<br>

### Diagrama ilustrativo:

<image src="https://github.com/XiaoLuo95/Light_pollution/blob/master/images/threshold.png" width="775" height="500">

Los ángulos de búsqueda se calculan con:

* [-t] threshold percentil (0.0-1.0)
* [-T] threshold en magnitud real
* [-o] introduciendo manualmente los ángulos

**¡Ojo! Son mutuamente incompatibles**

<br>

Situado en el fichero, para ejecutar el script:

*data file example: __UPM.txt__* 

### Desde Python3 Shell:

```python
>>> import subprocess
>>> subprocess.run('python3 main.py {arguments (see Help)}', shell=True)
```

### Desde Terminal

```
python3 main.py {arguments (see Help)}
```

### Help
```
usage: main.py [-h] [-t THRESHOLD_PERCENT] [-T THRESHOLD_MAG]
               [-o OPENING OPENING] [-d DISTANCE] [-c CLOUDINESS_ANGLE]
               [-u UPDATE] -f FILE -s SOURCE
optional arguments:
  -h, --help            show this help message and exit
  -t THRESHOLD_PERCENT, --threshold_percent THRESHOLD_PERCENT
                        percentage of magnitude from minimum to consider.
                        Default 0.3. Incompatible with {-T, -o}. [0.00-1.00]
  -T THRESHOLD_MAG, --threshold_mag THRESHOLD_MAG
                        maximum magnitude under consideration. Incompatible
                        with {-t, -o}.
  -o OPENING OPENING, --opening OPENING OPENING
                        angle opening's lower and upper bound, separated by
                        whitespace. Incompatible with {-t, -T}. [0-359.99]
                        [0-359.99]
  -d DISTANCE, --distance DISTANCE
                        radius in km within to search, default 200.
  -c CLOUDINESS_ANGLE, --cloudiness_angle CLOUDINESS_ANGLE
                        Only supported for tas. Angle opening w.r.t. each
                        original angle from tas to be considered as same, in
                        order to calculate the cloudiness to each place.
                        Default 1º. [0-12]
  -u UPDATE, --update UPDATE
                        default False. If set as True, the script will proceed
                        to update the list of light pollution sources in
                        Spain.
required arguments:
  -f FILE, --file FILE  file containing measurement data
  -s SOURCE, --source SOURCE
                        data source type: sqm/tas
```

<br>

#### Como fuentes de contaminación lumínica se tienen en cuenta:

* municipios
* minas
* fábricas
* invernaderos
* centros comerciales
