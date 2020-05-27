#  README

Este proyecto tiene como objetivo de que, partiendo de mediciones de contaminación lumínica en un determinado punto geográfico, sacar datos sobre posibles fuentes de contaminación en aquellas direcciones en que ésta sea más fuerte. Adicionalmente, genera mapa interactivo con información de dichas fuentes.

Los datos de fuentes de contaminación lumínica son almacenados de forma local para acelerar el proceso. Para actualizar dichos datos, procede a usar opcion "-u" en el comando.

<br>

Basado en python3, para el correcto funcionamiento del script, hacen falta tener instalados los paquetes siguientes:

* re
* sys
* PIL
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

Vista general

<image src="https://github.com/XiaoLuo95/Light_pollution/blob/master/images/map_generical.png" width="600" height="500">

<br>

Vista ampliada con indicador

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
* uri
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
usage: main.py [-h] [-t] [-T] [-o] [-d] [-c] [-S] [-save]
               [-i] [-u] -f -s
optional arguments:
  -h, --help            show this help message and exit
  -t, --threshold_percent
                        percentage of magnitude from minimum to consider.
                        Default 0.3. Incompatible with {-T, -o}. [0.00-1.00]
  -T, --threshold_mag
                        maximum magnitude under consideration. Incompatible
                        with {-t, -o}.
  -o, --opening
                        angle opening's lower and upper bound, separated by
                        whitespace. Incompatible with {-t, -T}. [0-359.99]
                        [0-359.99]
  -d, --distance    radius in km within to search, default 120.
  -c, --cloudiness_angle
                        Only supported for tas. Angle opening w.r.t. each
                        original angle from tas to be considered as same, in
                        order to calculate the cloudiness to each place.
                        Default 1º. [0-12]
  -S, --single      Default False. Angle opening for single valley of
                        lowest value. Compatible with percentile and magnitude
                        thresholds
  -save, --save     Output file name. Will apply to both data and map
                        files. Default "result"
  -i, --indicator   Light pollution indicator image filename. If set, the
                        indicator will be included in the map generated.
  -u, --update      default False. If set as True, the script will proceed
                        to update the list of light pollution sources in
                        Spain.
required arguments:
  -f, --file        file containing measurement data
  -s, --source      data source type: sqm/tas
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

* Fuente SQM, análisis automático con threshold en 30%, en radio de 200km y guardar datos y mapa resultantes en "example"

  **_Se guardará los datos en "example.csv" y mapa en "example_map.html"_**

  ```
  python3 main.py -f file -s sqm -t 0.3 -d 200 -save example
  ```

* Fuente TAS, análisis automático con threshold real de 19.86, valle único del mínimo, apertura de ángulo de 2.5º para considerar nubosidad con respecto a direcciones originales

  ```
  python3 main.py -f file -s tas -T 19.86 -s True -c 2.5
  ```

* Fuente TAS, fuentes de contaminación entre ángulos [330º-0º], en radio de 50km

  ```
  python3 main.py -f file -s tas -o 330 0
  ```


* Fuente TAS, incluir imagen del indicador en el mapa

  ```
  python3 main.py -f file -s tas -i indicator.png
  ```

  