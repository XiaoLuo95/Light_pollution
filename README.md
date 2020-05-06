# README

Para el correcto funcionamiento del script, hacen falta tener instalados los paquetes siguientes:

* requests
* time
* numpy
* re
* sys
* math
* pandas
* collections
* Geopy.distance

Situado en el fichero, para ejecutar el script:

*data file example: __UPM.txt__* 

### Desde Python3 Shell:

```python
>>> import subprocess
>>> subprocess.run('python3 light_pollution.py {data file}', shell=True)
```

### Desde Terminal

```
python3 light_pollution.py {data file}
```

#### Como fuentes de contaminación lumínica se tienen en cuenta:
* municipios
* minas
* fábricas
* invernaderos
* centros comerciales