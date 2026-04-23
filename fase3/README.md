

## Levantar MongoDB con Docker

```bash
# 1. Levantar Docker
docker-compose up -d

#Crear el entorno virtual
python3 -m venv venv

# Activar el entorno
source venv/bin/activate

#  Instalar dependencias
pip install pymongo pandas

# Transformar (CSVs deben estar en ./output/)
python transformar_mongo.py

#  Cargar a MongoDB
python cargar_mongo.py

# Consultar(faltan arreglarlas)
python consultas.py
```

- **MongoDB** disponible en `localhost:27017`
- **Mongo Express** (UI web) en `http://localhost:8081`
- **MongoDB Compass** vayan en ` mongodb://mundiales_user:mundiales1234@127.0.0.1:27017/mundiales?authSource=admin`


- SUGERENCIA: usen MongoDB Compass es como dbaver solo que para mongo directamente ya que dbaver no esta disponible el nosql a no ser que pagen xd



## Credenciales Docker

| Parámetro | Valor           |
|-----------|-----------------|
| Host      | 127.0.0.1:27017 |
| Usuario   | mundiales_user  |
| Password  | mundiales1234   |
| Database  | mundiales       |






## Explicacion del docker por si tiene dudas












### 1. Mongo Express (Interfaz Web)
Esta es la forma mas rapida de ver los datos sin instalar nada extra, los pasos son estos:


- Ir al : http://localhost:8081.

- hay una lista de la db, clic en "mundiales"

- Dentro de "mundiales" hay  dos colecciones: mundiales y selecciones

- clic en "View" en la coleccion mundiales, se veran los documentos y se puede expandir los arreglos de partidos para ver como quedaron incrustados.

- Pero es mejor MongoDB Compass es mas porfecional(potente) por asi decirlo, lo malo es que hay que instalarlo

### 2. MongoDB Compass (Interfaz Gráfica)


- Abrir MongoDB Compass 


- En la pantalla de conexion, pega esta URI:`mongodb://mundiales_user:mundiales1234@localhost:27017/mundiales?authSource=admin`
- mongodb://mundiales_user:mundiales1234@localhost:27017/mundiales?authSource=admin

- Una vez conectado, selecciona la base de datos mundiales a la izquierda

- Pestaña Documents: aqui estan los JSON aparte se veran los campos como partidos tienen un icono de flecha, al hacer clic, se despliegan todos los partidos de ese mundial

- Pestaña Schema: clic en "Analyze Schema" Compass para mostrar graficamente quw tipos de datos hay y que porcentaje de documentos tienen ciertos campos(podira servir para la docu)

- para poder hacer consultas simples es ir a documents en doonde dice filtrer ahi colocar lo que se va a buscar y luego precionar find ( eso solo para consultas normales y simples ).

## Por si tienen duda 
 la base de datos tiene dos colecciones independientes, mundiales y selecciones, para cumplir con el requisito de que las consultas sean instantaneas y evitar procesos pesados de busqueda en tiempo de ejecucion, entonces la coleccion mundiales funciona como un registro de eventos, donde cada documento contiene toda la "foto" de un año especifico (incluyendo partidos, grupos y alineaciones incrustadas), la ideal es para responder al inciso C del proyecto, por otro lado, la coleccion selecciones actua como una "biografia" historica de cada pais almacenando su trayectoria completa, participaciones y los años en que fue sede, lo cual resuelve directamente el inciso D. Dividirlos de esta manera nos permite usar indices unicos en campos clave como el año y el nombre del pais, asegurando que no importa que tan grande sea nuestra data (como tenemos demasiados datos revicen el output_mongo para ver porque se los digo jaja), la respuesta siempre sea inmediata al no tener que realizar Joins entre tablas


- **Coleccion mundiales**: Sirve para consultas por año, ya que contiene el detalle tecnico de los torneos: quien gano, resultados de partidos, goleadores y planteles de esa edicion especíiica

- **Coleccion selecciones**: Sirve para consultas por pais, contiene el historial global: cuantas veces ha participado, posiciones historicas y su récord como sede del mundial

- **razon**: Para maximizar el rendimiento como no tenemos la informacin ya masticada en la coleccion correcta, MongoDB solo tiene que leer un documento para darnos toda la respuesta por eso su rapidez.

-->De todas formas ustede revisen y si hay que cambiar algo se cambiá.


# metodos
para usar los metodos solo entran a la carpeta scripts

modifican los parametros que necesiten tomando en cuenta que:

## en **consulta_mundial.py** 

- anio → obligatorio
- grupo → opcional, por ejemplo "A"
- pais → opcional, por ejemplo "Argentina"
- fecha → opcional,por ejemplo "18-Dec-2022" o "13-Jul-1930"
```bash
metodo_info_mundial(2010, grupo="B", pais="España")
```
para ejecutarlo unicamente 

```bash
python3 consulta_mundial.py
```

y devuelve un diccionario con:
- info_general
- grupos
- partidos
- posiciones_finales
- goleadores
- premios
- tarjetas
- planteles



## en **consulta_pais.py** 

- pais → obligatorio
- anio → opcional
- fase → opcional, por ejemplo "Final", "Grupo", "Semis", "Octavos"

```bash
metodo_info_pais("Brasil", anio=2014)
```
para ejecutarlo unicamente 

```bash
python3 consulta_pais.py
```
devuelve un diccionario con:
- info_historica
- participaciones
- Dentro de info_historica va:
- años de participación
- si fue campeón
- si fue subcampeón
- sedes
- estadísticas históricas
