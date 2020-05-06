# README

Para el correcto funcionamiento del script, hacen falta tener instalados los paquetes siguientes:

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

Situado en el fichero, para ejecutar el script:

*data file example: __UPM.txt__* 

### Desde Python3 Shell:

```python
>>> import subprocess
>>> subprocess.run('python3 light_pollution.py {data} {threshold} {-s source: sqm/tas} {OPTIONAL opening {angle_lower angle_upper}} {OPTIONAL distance}', shell=True)
```

### Desde Terminal

```
python3 light_pollution.py {data} {threshold} {-s source: sqm/tas} {OPTIONAL opening {angle_lower angle_upper}} {OPTIONAL distance}
```

### Help
```
usage: light_pollution.py [-h] [-o OPENING OPENING] [-d DISTANCE] -s SOURCE
                          data threshold
positional arguments:
  data                  file containing measurement data
  threshold             percentage of magnitude from minimum under
                        consideration [0.00-1.00]
optional arguments:
  -h, --help            show this help message and exit
  -o OPENING OPENING, --opening OPENING OPENING
                        angle opening's lower and upper bound, separated by
                        whitespace [0-360]
  -d DISTANCE, --distance DISTANCE
                        radius in km within to search, default 200
  -s SOURCE, --source SOURCE
                        data source type: sqm/tas
```

#### Como fuentes de contaminación lumínica se tienen en cuenta:
* municipios
* minas
* fábricas
* invernaderos
* centros comerciales