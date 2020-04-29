# README

Para el correcto funcionamiento del script, hacen falta tener instalados los paquetes siguientes:

* requests
* time
* math
* pandas
* collections
* Geopy.distance



Situado en el fichero, para ejecutar el script:

### Desde Python3 Shell:

```python
>>> exec(open("light_pollution.py").read())
```

### Desde Terminal

```
python3 light_pollution.py
```



Hacen falta introducir, ignorando los paréntesis: 

* Latitud de punto de referencia: **xx(º) xx(') xx()'') N**
* Longitud de punto de referencia: **xx(º) xx(') xx('') W/E**

* Radio de búsqueda en kilómetro
* Ángulo central de búsqueda
* Apertura de ángulo, igualmente distribuido en ambos lados del ángulo central

