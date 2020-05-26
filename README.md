#  README

Este proyecto tiene como objetivo de que, partiendo de mediciones de contaminación lumínica en un determinado punto geográfico, sacar datos sobre posibles fuentes de contaminación en aquellas direcciones en que ésta sea más fuerte. Adicionalmente, genera mapa interactivo con información de dichas fuentes.

Los datos de fuentes de contaminación lumínica son almacenados de forma local para acelerar el proceso. Para actualizar dichos datos, procede a usar opcion "-u" en el comando.

<br>

Basado en python3, para el correcto funcionamiento del script, hacen falta tener instalados los paquetes siguientes:

* re
* sys
* math
* time
* folium
* numpy
* pandas
* argparse
* requests
* collections
* geopy.distance

<br>

## Lógica del proyecto

<image src="https://github.com/XiaoLuo95/Light_pollution/blob/master/images/logic.png" width="775" height="580">

<br>

## Diagrama ilustrativo:

<image src="https://github.com/XiaoLuo95/Light_pollution/blob/master/images/threshold.png" width="775" height="500">

Los ángulos de búsqueda se calculan con:

* [-t] threshold percentil (0.0-1.0)
* [-T] threshold en magnitud real
* [-o] introduciendo manualmente los ángulos

**¡Ojo! Son mutuamente incompatibles**

La opción "single" sólo soporta para threshold percentil y en magnitud real

<br>

## Mapa:

### Modo genérico (auto cluster)

<image src="https://github.com/XiaoLuo95/Light_pollution/blob/master/images/map_generical.png" width="600" height="500">

<image src="https://github.com/XiaoLuo95/Light_pollution/blob/master/images/map_generical_zoomed.png" width="600" height="500">

<br>

### Modo detallado

<image src="https://github.com/XiaoLuo95/Light_pollution/blob/master/images/map_detailed.png" width="600" height="500">

<br>



## Algoritmo personalizado:

Si el usuario desee, puede crear sus propios algoritmos para sustituir "filetype_angles.py" y "filter_algorithm.py".

<br>

#### filetype_angles.py OUTPUT:

angle_min: lista de cotas inferiores de ángulos

angle_max: lista de cotas superiores de ángulos

[tas] m10: pandas dataframe de direcciones originales de m10 de tas, con "Mag"(magnitud), "Azi"(ángulo azimutal) y "Cloudiness"(nubosidad)

**Ejemplo:**

Tres ángulos: [30º-60º], [120º-150º] y [210º-270º], deben devolver:

* angle_min: [30, 120, 210]
* angle_max: [60, 150, 270]

<br>

#### filter_algorithm.py OUTPUT:

result: pandas dataframe con columnas siguientes:

* Nombre
* Tipo
* Provincia
* Poblacion
* Distancia
* Dirección
* lon
* lat
* [tas] Nubosidad

<br>

## Uso:

Situado en el fichero, para ejecutar el script:

*data file example: __UPM.txt__* 

### Desde Python3 Shell:

```python
>>> import subprocess
>>> subprocess.run('python3 main.py {arguments (see Help)}', shell=True)
```

### Desde Terminal (recomendado)

```
python3 main.py {arguments (see Help)}
```

### Help
```
usage: main.py [-h] [-t THRESHOLD_PERCENT] [-T THRESHOLD_MAG]
               [-o OPENING OPENING] [-d DISTANCE] [-c CLOUDINESS_ANGLE]
               [-S SINGLE] [-u UPDATE] -f FILE -s SOURCE
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
                        radius in km within to search, default 120.
  -c CLOUDINESS_ANGLE, --cloudiness_angle CLOUDINESS_ANGLE
                        Only supported for tas. Angle opening w.r.t. each
                        original angle from tas to be considered as same, in
                        order to calculate the cloudiness to each place.
                        Default 1º. [0-12]
  -S SINGLE, --single SINGLE
                        Default False. Angle opening for single valley of
                        lowest value. Compatible with percentile and magnitude
                        thresholds
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

<br>

## Ejemplos de uso:

* Actualizar de fuente de datos (aprox. 90s)

  _**Por motivo de prevenir posible misuso de otras funcionalidades, por favor, use ésta funcionalidad junto con cualesquier argumentos requeridos**_

  ```
  python3 main.py -f file -s source -u True
  ```

* Fuente SQM, análisis automático con threshold en 30%, en radio de 200km

  ```
  python3 main.py -f file -s sqm -t 0.3 -d 200
  ```

* Fuente TAS, análisis automático con threshold real de 19.86, valle único del mínimo, apertura de ángulo de 2.5º para considerar nubosidad con respecto a direcciones originales

  ```
  python3 main.py -f file -s tas -T 19.86 -s True -c 2.5
  ```

* Fuente TAS, fuentes de contaminación entre ángulos [330º-0º], en radio de 50km

  ```
  python3 main.py -f file -s tas -o 330 0
  ```

  