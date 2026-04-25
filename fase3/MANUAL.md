# Proyecto Fase 3 — Mundiales de Fútbol en MongoDB

## Universidad de San Carlos de Guatemala
## Facultad de Ingenieria
## Escuela de Ciencias y Sistemas
## Sistemas de Bases de Datos 2

Seccion: B
Grupo: 17

### Integrantes:

- Engel Emilio Coc Raxjal - 202200314
- Harold Alejandro Sanchez Hernandez - 202200100
- Juan Esteban Chacon Trampe - 202300431



## 1. Objetivo del proyecto

El enunciado pide:

* extraer y cargar información de los mundiales en una base **NoSQL**,
* entregar scripts de creación/carga/índices,
* implementar un método que reciba el **año del mundial** y muestre toda la información relacionada,
* e implementar otro método que reciba el **país** y muestre su historial, partidos, grupo, resultados, años de participación y si fue sede. 

---

## 2. Arquitectura que se decidió

Se trabajó con **dos colecciones principales**:

* `mundiales`
* `selecciones`

La idea del README fue correcta: separar la consulta por **año** y la consulta por **país** para que cada una lea directamente un documento ya “preparado”, sin joins ni búsquedas pesadas en tiempo de ejecución.  

### 2.1 Colección `mundiales`

Se usa para responder el inciso del **año del mundial**.
Cada documento representa una edición del torneo e incluye:

* información general del mundial,
* partidos,
* grupos,
* posiciones finales,
* goleadores,
* premios,
* tarjetas,
* planteles. 

### 2.2 Colección `selecciones`

Se usa para responder el inciso del **país**.
Cada documento representa una selección nacional e incluye:

* estadísticas históricas acumuladas,
* años como sede,
* participaciones por mundial,
* grupo de cada participación,
* partidos,
* plantel,
* estadísticas de jugadores.  

---

## 3. Flujo general de trabajo

El flujo quedó así:

1. **CSV crudos** en `./output/`
2. `transformar_mongo.py`

   * limpia datos,
   * unifica nombres,
   * agrupa e incrusta información,
   * genera `output_mongo/mundiales.json`
   * genera `output_mongo/selecciones.json`
3. `cargar_mongo.py`

   * inserta los JSON en MongoDB,
   * recrea las colecciones,
   * crea índices.
4. Métodos Python:

   * `metodo_info_mundial(...)`
   * `metodo_info_pais(...)`
5. Ejecución por consola mediante:

   * `cli_consultas.py`

---

## 4. Preparación del entorno

Según el README, el entorno se levanta con Docker, se crea un entorno virtual y se instalan `pymongo` y `pandas`. Luego se transforma, se carga y se consulta. 

### 4.1 Levantar MongoDB

```bash
docker-compose up -d
```

### 4.2 Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4.3 Instalar dependencias

```bash
pip install pymongo pandas
```

### 4.4 Transformar

```bash
python transformar_mongo.py
```

### 4.5 Cargar

```bash
python cargar_mongo.py
```

---

## 5. Conexión a MongoDB

La base quedó configurada así:

* Host: `127.0.0.1:27017`
* Usuario: `mundiales_user`
* Password: `mundiales1234`
* Database: `mundiales` 

### URI completa

```text
mongodb://mundiales_user:mundiales1234@127.0.0.1:27017/mundiales?authSource=admin
```

También se puede usar en MongoDB Compass. El README ya traía esa guía.

---

## 6. Qué hace `transformar_mongo.py`

Este script es el núcleo de la transformación: toma CSV relacionales y los convierte en documentos JSON listos para MongoDB.

### 6.1 Entradas que consume

Lee archivos desde `./output/` y espera principalmente:

* `mundiales.csv`
* `selecciones.csv`
* `partidos.csv`
* `grupos.csv`
* `posiciones_finales.csv`
* `goleadores.csv`
* `premios.csv`
* `tarjetas.csv`
* `planteles.csv`
* `jugadores_por_mundial.csv`
* `partido_goles.csv`
* `partido_jugadores.csv`

Si falta un CSV secundario, el script sigue cuando puede. Si faltan CSV base (`mundiales`, `selecciones`, `partidos`), se detiene.

### 6.2 Limpieza y tipado de datos

Antes de agrupar, aplica limpieza para dejar datos consistentes:

* detección automática del separador CSV (coma o punto y coma),
* normalización de nombres de columnas a minúscula,
* tratamiento de valores vacíos (`""`, `nan`, `NULL`, `-`, etc.),
* conversión de enteros y decimales,
* normalización de texto,
* conversión de altura a centímetros.

Esto evita que un mismo campo llegue con tipos distintos al documento final.

### 6.3 Unificación de nombres históricos

Usa `ALIASES` y `canonical()` para mapear variaciones históricas a un único nombre canónico (por ejemplo, nombres antiguos de selecciones).

Además, el script recorre datos de partidos/grupos/posiciones para detectar selecciones que no estén en `selecciones.csv` y las agrega automáticamente para no perder historial.

### 6.4 Derivación de subcampeones

No depende solo de los valores de `selecciones.csv` para subcampeonatos. También calcula:

* subcampeón por mundial (`posicion == 2` en `posiciones_finales`),
* años de subcampeonato por selección.

Con eso corrige inconsistencias de origen y deja `subcampeon_anios` y `subcampeon_veces` coherentes.

### 6.5 Estructuras intermedias (índices en memoria)

Construye mapas para armar documentos eficientes:

* índice de mundiales (`anio` -> metadatos del torneo),
* índice de selecciones (`nombre` -> estadísticas históricas),
* goles por partido (por slug de URL),
* alineaciones por partido (local/visitante),
* agrupaciones por año de grupos, posiciones, goleadores, premios y tarjetas,
* agrupaciones por año+selección de planteles y estadísticas de jugadores.

Estas estructuras permiten incrustar información relacionada sin hacer joins en MongoDB.

### 6.6 Construcción de documentos finales

Genera dos listas de documentos:

* `docs_mundiales`
* `docs_selecciones`

`docs_mundiales` guarda por edición: resumen del torneo, partidos con goles y alineaciones, grupos, posiciones finales, goleadores, premios, tarjetas y planteles.

`docs_selecciones` guarda por país: estadísticas históricas, años como sede y participaciones. Cada participación incluye:

* `anio`
* `fue_sede`
* `fue_campeon`
* `fue_subcampeon`
* `grupo`
* `posicion_final`
* `etapa_final`
* `partidos`
* `plantel`
* `estadisticas_jugadores`

### 6.7 Salidas que produce

Escribe en `./output_mongo/`:

* `mundiales.json`
* `selecciones.json`

Esos dos archivos son la entrada directa del script de carga (`cargar_mongo.py`).

---

## 7. Qué hace `cargar_mongo.py`

Este script toma los JSON generados por la transformación y los publica en MongoDB, dejando la base lista para consultas.

### 7.1 Conexión y validación de servicio

Primero crea cliente Mongo con la URI configurada y ejecuta un `ping`.

Si no hay conexión, muestra error claro y recomienda levantar Docker (`docker-compose up -d`).

### 7.2 Carga de colecciones (proceso completo)

Para cada colección (`mundiales`, `selecciones`) realiza:

* lectura del archivo JSON correspondiente en `./output_mongo/`,
* validación de existencia del archivo,
* validación de que no esté vacío,
* limpieza de la colección destino,
* inserción masiva con `insert_many`.

Este enfoque hace la carga idempotente: ejecutar nuevamente deja el mismo estado final de datos.

### 7.3 Índices creados y para qué sirven

Después de insertar, crea índices para acelerar filtros usados por la CLI.

#### En `mundiales`

* `anio` (único): búsqueda directa de una edición.
* `partidos.local`: filtros de partidos por selección local.
* `partidos.visitante`: filtros de partidos por selección visitante.
* `partidos.etapa`: filtros por fase (grupos, final, etc.).
* `partidos.fecha`: filtros por día de partido.
* `grupos.grupo`: filtros por grupo (A, B, C...).
* `grupos.seleccion`: consulta de selección dentro de grupos.

#### En `selecciones`

* `nombre` (único): búsqueda exacta por país.
* índice de texto en `nombre`: búsqueda parcial/flexible.
* `participaciones.anio`: filtro de historial por año.
* `participaciones.partidos.local`: localización de partidos donde la selección fue local.
* `participaciones.partidos.visitante`: localización de partidos donde fue visitante.

### 7.4 Resultado final de este script

Al terminar, Mongo queda con:

* colecciones reconstruidas,
* datos cargados desde JSON,
* índices listos para consultas rápidas desde `metodos_consultas.py` y `cli_consultas.py`.

En resumen: `transformar_mongo.py` modela la data y `cargar_mongo.py` la publica con rendimiento de consulta.

---

## 8. Métodos implementados

Se implementaron dos métodos en Python para cumplir literalmente lo que pide el proyecto.

### 8.1 `metodo_info_mundial(anio, grupo=None, pais=None, fecha=None)`

Consulta la colección `mundiales`.

#### Parámetros

* `anio`: obligatorio
* `grupo`: opcional
* `pais`: opcional
* `fecha`: opcional

#### Qué devuelve

* información general del mundial
* grupos
* partidos
* posiciones finales
* goleadores
* premios
* tarjetas
* planteles

#### Uso

```bash
python3 cli_consultas.py mundial 2022
python3 cli_consultas.py mundial 2022 --grupo A
python3 cli_consultas.py mundial 2022 --pais Argentina
python3 cli_consultas.py mundial 2022 --fecha 18-Dec-2022
```

---

### 8.2 `metodo_info_pais(pais, anio=None, fase=None)`

Consulta la colección `selecciones`.

#### Parámetros

* `pais`: obligatorio
* `anio`: opcional
* `fase`: opcional

#### Qué devuelve

* información histórica de la selección
* veces campeón
* veces subcampeón
* años de participación
* si fue sede
* participaciones por año
* grupo
* partidos
* plantel
* estadísticas de jugadores

#### Uso

```bash
python3 cli_consultas.py pais Argentina
python3 cli_consultas.py pais Argentina --anio 2022
python3 cli_consultas.py pais Alemania --fase Final
python3 cli_consultas.py pais Francia --anio 1998 --fase Grupo
```

---

## 9. Problemas encontrados y cómo se corrigieron

## 9.1 Error por tipado `str | None`

### Problema

En Python menor a 3.10 falló esta sintaxis:

```python
value: str | None
```

### Solución

Se cambió a:

```python
from typing import Optional
```

y luego:

```python
value: Optional[str]
```

---

## 9.2 Error en `_resultado_desde_partido`

### Problema

Algunas consultas por país daban:

```text
TypeError: '>' not supported between instances of 'NoneType' and 'NoneType'
```

### Causa

Había partidos con `goles_local` o `goles_visitante` en `None`.

### Solución

Se modificó `_resultado_desde_partido()` para devolver:

* `"Sin resultado registrado"` si faltaba marcador.

---

## 9.3 Información de más en `metodo_info_mundial`

### Problema

Al filtrar por fecha o grupo, seguían apareciendo planteles, posiciones o tarjetas que no correspondían al subconjunto filtrado.

### Causa

Los filtros se aplicaban solo sobre `partidos`, pero no sobre los demás arreglos del documento.

### Solución

Se reescribió la lógica:

1. filtrar `partidos`
2. detectar las selecciones realmente involucradas
3. recortar:

   * `grupos`
   * `planteles`
   * `tarjetas`
   * `goleadores`
   * `posiciones_finales`

Así la salida quedó consistente.

---

## 9.4 Caso `--grupo B --pais España`

### Problema

La consulta:

```bash
python3 cli_consultas.py mundial 2010 --grupo B --pais España
```

daba resultados vacíos en `partidos` y `grupos`, pero seguía mostrando cosas de España.

### Explicación

Los filtros funcionan como intersección:

* mundial 2010
* grupo B
* España

Como España no pertenece a ese grupo, el subconjunto correcto es vacío.

### Solución

Si no hay partidos para la combinación de filtros:

* se vacían también los demás arreglos dependientes,
* y se agrega un mensaje:

  * `"No hay resultados para la combinación de filtros indicada"`

---

## 9.5 Información de más en `metodo_info_pais`

### Problema

Al filtrar por fase, seguía apareciendo información de grupo o plantel que no tenía relación directa con esa fase.

### Solución

Se ajustó el método para que:

* `anio` filtre participaciones
* `fase` filtre partidos dentro de cada participación
* si la fase no es de grupos, `grupo` se oculte
* si no hay partidos para esa fase, la participación quede vacía de forma consistente

---

## 9.6 Subcampeonatos incorrectos

### Problema

En algunas selecciones:

* `subcampeon_veces` era incorrecto
* `subcampeon_anios` incluía años donde el país fue campeón

### Causa

La información original de `selecciones.csv` no era confiable para subcampeonatos.

### Solución

Se corrigió `transformar_mongo.py` para derivar los subcampeonatos desde `posiciones_finales` usando `posicion == 2`, igual que ya se hacía para detectar el subcampeón de cada mundial. 

Se agregó:

* `build_subcampeon_anios_por_seleccion(df_pos)`
* nueva lógica en `build_index_selecciones(...)`

Con eso:

* `subcampeon_anios` queda correcto
* `subcampeon_veces` se calcula como la longitud de esa lista

---

## 10. CLI de ejecución

Se creó `cli_consultas.py` para no tener que modificar archivos cada vez.

### Ventaja

Permite ejecutar ambos métodos directamente desde la consola con parámetros.

### Ejemplos

```bash
python3 cli_consultas.py mundial 2022
python3 cli_consultas.py mundial 2022 --pais Argentina
python3 cli_consultas.py mundial 2022 --fecha 18-Dec-2022

python3 cli_consultas.py pais Brasil
python3 cli_consultas.py pais Argentina --anio 2022
python3 cli_consultas.py pais Alemania --fase Final
```

También se dejó opción `--json` para imprimir el resultado completo en formato JSON.

---

## 11. Uso en MongoDB Compass

Compass se usa para:

* verificar que las colecciones existen
* inspeccionar documentos
* hacer filtros simples
* demostrar la estructura del proyecto

### Colecciones

* `mundiales`
* `selecciones`

### Ejemplos de filtro en Compass

#### Mundial 2022

```json
{ "anio": 2022 }
```

#### Selección Argentina

```json
{ "nombre": "Argentina" }
```

#### Búsqueda parcial

```json
{ "nombre": { "$regex": "Arg", "$options": "i" } }
```

---

## 12. Archivos importantes del proyecto

### Datos y transformación

* `transformar_mongo.py`
* `output_mongo/mundiales.json`
* `output_mongo/selecciones.json`

### Carga

* `cargar_mongo.py`

### Métodos

* `metodos_consultas.py`

### Interfaz por consola

* `cli_consultas.py`

### Documentación base

* `README.md`
* `Enunciado proyecto 3.pdf`

---

## 13. Orden correcto para ejecutar todo

```bash
docker-compose up -d
source venv/bin/activate
pip install pymongo pandas
python transformar_mongo.py
python cargar_mongo.py
python3 cli_consultas.py mundial 2022
python3 cli_consultas.py pais Argentina
```



