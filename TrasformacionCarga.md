# Documentación del proyecto "Mundiales de Fútbol"

## 1. Visión general del flujo de datos

El proyecto se organiza en varias etapas bien separadas, desde los datos crudos obtenidos por scraping hasta su carga en una base de datos MySQL ejecutada en Docker.

Flujo completo:

1. **Datos crudos**: archivos CSV generados por el proceso de scraping y guardados en la carpeta `output/`.
2. **Transformación y normalización**: se ejecuta un script de transformación (basado en `cargar_datos.py` en modo "transformador") que toma los CSV de `output/`, limpia y normaliza la información y genera CSV "limpios" y consistentes en la carpeta `output_db/`.
3. **Carga a la base de datos**: el script `cargar_db.py` lee los CSV de `output_db/` y los inserta en la base de datos MySQL `mundiales`, respetando tipos de datos, claves primarias y foráneas.
4. **Infraestructura Docker**: el archivo `docker-compose.yml` levanta un contenedor MySQL 8.0 y ejecuta automáticamente el esquema SQL definido en `init/schema.sql`, creando todas las tablas necesarias.

La separación entre `output/` y `output_db/` es clave: `output/` contiene datos tal como vienen del scraping (heterogéneos, con formatos variados), mientras que `output_db/` contiene datos ya adaptados al esquema relacional pensado para análisis y consultas SQL.



## 2. Transformación de datos: de `output/` a `output_db/`

### 2.1. Objetivo de la transformación

Los CSV obtenidos del scraping no están listos para ser cargados directamente en una base de datos normalizada. Algunos problemas típicos que resuelve la transformación:

- Identificadores lógicos (como nombres de selecciones o años de mundiales) necesitan convertirse a **IDs numéricos** (llaves primarias auto-incrementales).
- URLs absolutas y relativas de jugadores o partidos deben unificarse en una **clave común** para poder usarse como referencia.
- Fechas en formato textual (por ejemplo, "9 de junio de 1978" o "20-Nov-2022") deben transformarse a formato estándar SQL `YYYY-MM-DD`.
- Valores especiales como `"nan"`, `"None"`, `"NULL"` o guiones `"-"` deben interpretarse como ausencia de dato (`NULL` en la base de datos).
- Columnas que agrupan información (como listas de años o números de camiseta separados por comas) se deben "explotar" en filas individuales.
- Asegurar que no haya filas que violen restricciones de integridad (por ejemplo, registros de planteles sin jugador asociado).

Para realizar esta limpieza y normalización se utiliza un script de transformación (basado en `cargar_datos.py` cuando se ejecuta en modo transformación) que:

- Lee todos los CSV de `output/`.
- Construye **diccionarios de mapeo** (mapas) para convertir campos lógicos a IDs numéricos.
- Aplica funciones de transformación específicas para cada tabla (selecciones, mundiales, jugadores, partidos, etc.).
- Escribe los resultados en nuevos CSV en la carpeta `output_db/`.

### 2.2. Construcción de diccionarios de mapeo

En la primera fase del proceso, el script construye varios mapas fundamentales:

- **Mapa de selecciones**: `nombre de selección → id_seleccion`.
  - Se recorre el archivo `selecciones.csv` de `output/` y se extraen todos los nombres de selecciones.
  - Cada nombre se limpia (`strip()`) y se asigna un ID numérico incremental, empezando por 1.
  - Esto permite que cualquier CSV que haga referencia a una selección por nombre pueda transformarla a `id_seleccion`.

- **Mapa de mundiales**: `año ("1930", "1934", ...) → id_mundial`.
  - Se toma el CSV `mundiales.csv` y se ordenan los años de manera creciente.
  - A cada año se le asigna un ID entero.
  - De esta forma, todos los CSV que referencian mundiales por año (como `mundial = 2022`) pueden traducirse al ID interno `id_mundial`.

- **Mapa de jugadores (por URL)**: `url normalizada → id_jugador`.
  - El archivo `jugadores.csv` trae una columna `url` que puede estar en forma absoluta (`https://www.../jugadores/miroslav_klose.php`) o relativa (`../jugadores/miroslav_klose.php`).
  - Se define una función `_normalizar_clave_url_jugador` que toma cualquier URL y se queda solo con el **nombre del archivo**, por ejemplo `"miroslav_klose.php"`.
  - Con esta clave normalizada se construye un mapa `clave_url → id_jugador`.
  - Esto permite unir información de distintas tablas (como goles o tarjetas) a un mismo jugador aunque las URLs estén escritas de forma distinta.

- **Mapa de jugadores por nombre**: `nombre → id_jugador`.
  - Para algunos CSV (como `partido_goles.csv`) no se dispone de la URL del jugador, solo del nombre.
  - Se recorre `jugadores.csv` y, usando el mapa anterior (por URL), se construye un mapa alternativo desde el **nombre del jugador** al `id_jugador`.
  - Este mapa se usa como solución de respaldo cuando no existe `url_jugador` en el CSV de origen.

- **Mapa de partidos**: `url_partido → id_partido`.
  - A partir de `partidos.csv`, se toma la columna `url_partido` (que suele tener rutas relativas como `../partidos/2022_catar_ecuador.php`).
  - Se limpia cada URL (por ejemplo, con `strip()`) y se asigna un ID numérico incremental a cada partido.
  - Este ID es el que se utilizará como clave primaria en la tabla `partidos` y como clave foránea en tablas como `partido_jugadores` y `partido_goles`.

Estos mapas también se exportan al final del proceso a archivos CSV de referencia en `output_db/`:

- `_mapa_jugadores.csv`
- `_mapa_mundiales.csv`
- `_mapa_partidos.csv`
- `_mapa_selecciones.csv`

De esta manera se conserva un registro explícito de cómo se asignaron los IDs numéricos a elementos lógicos del dominio.

### 2.3. Normalización y limpieza específica por tabla

Cada tipo de dato tiene una función de transformación dedicada que toma el DataFrame original de `output/` y produce un DataFrame ya adaptado al esquema de `schema.sql`. Algunas de las transformaciones más importantes son:

#### 2.3.1. Selecciones

- A partir de `selecciones.csv` se generan columnas como:
  - `id_seleccion` (usando el mapa de selecciones).
  - `nombre` (nombre limpio de la selección).
  - Estadísticas históricas: mundiales jugados, partidos, goles, etc.
- Se eliminan columnas que no son necesarias en el modelo relacional (por ejemplo, listas de años de campeonatos, que se transforman en otra tabla).

#### 2.3.2. Mundiales

- La columna `anio` se mapea a `id_mundial` usando el mapa de mundiales.
- Los campos `campeon` y `organizador` (que vienen como nombres de selecciones) se convierten en `id_campeon` e `id_organizador` usando el mapa de selecciones.
- Campos numéricos como `selecciones_participan`, `partidos`, `goles`, `promedio_gol` se mantienen o se limpian para asegurar que sean numéricamente válidos.

#### 2.3.3. Seleccion_titulos (campeonatos y subcampeonatos)

- No tiene CSV propio en `output/`; se genera a partir de `selecciones.csv`.
- Columnas como `campeon_anios` y `subcampeon_anios`, que traen listas de años separados por comas (ejemplo: `"1978, 1986"`), se "explotan" en filas individuales:
  - Para cada año se busca el `id_mundial` correspondiente.
  - Se inserta una fila con `tipo = 'campeon'` o `tipo = 'subcampeon'`.
- De este modo se crea una tabla relacional `seleccion_titulos` donde cada fila representa un título de campeón o subcampeón de una selección en un mundial concreto.

#### 2.3.4. Jugadores

- Se usa el mapa de jugadores por URL para generar `id_jugador`.
- Se almacena la `source_url` original como referencia.
- Se normalizan campos como:
  - `fecha_nacimiento` → se convierte a `YYYY-MM-DD`.
  - `altura` → si viene como `"1.70 m"`, se traduce a centímetros (`170`).
- Se asigna `id_seleccion_actual` usando el mapa de selecciones.

#### 2.3.5. Jugador_camisetas

- A partir de la columna `numeros_camiseta` en `jugadores.csv` (por ejemplo `"10,19"`), se generan varias filas en `jugador_camisetas`:
  - Cada número de camiseta se convierte en una fila con un `id_jugador_camiseta` propio.
  - `id_mundial` no siempre está disponible en el CSV de origen, por lo que puede quedar vacío.

#### 2.3.6. Partidos

- A partir de `partidos.csv` se generan:
  - `id_partido` (usando el mapa de partidos).
  - `source_url`, con la URL del partido.
  - `id_mundial` (mapeado desde el año del mundial).
  - `id_local` e `id_visitante` a partir de los nombres de las selecciones.
  - `fecha` en formato `YYYY-MM-DD`.

#### 2.3.7. Grupos, posiciones_finales, goleadores, premios, tarjetas, jugadores_por_mundial

- Estas tablas se construyen aplicando el mismo patrón:
  - Todo campo que hace referencia a selecciones, mundiales o jugadores se transforma a su ID numérico usando los mapas.
  - Campos numéricos se limpian y se convierten a enteros o decimales.
  - Campos de texto se limpian (`strip`) y se homogeneizan.
  - Los valores faltantes o especiales se convierten en `""` (vacío) en CSV, que más adelante se interpretarán como `NULL` al cargar en la base.

#### 2.3.8. Planteles

- Se generan columnas:
  - `id_mundial`, `id_seleccion`, `id_jugador` (usando los mapas respectivos).
  - `camiseta`, `posicion_grupo`, `fecha_nacimiento`, `altura_cm`, `club`.
- Un detalle importante es que la tabla `planteles` en el esquema exige `id_jugador NOT NULL`.
  - Algunos registros de la fuente representan al **entrenador**, y no traen `url_jugador`, por lo que no se les puede asignar un ID de jugador.
  - Para preservar la integridad referencial, se **filtran** todas las filas donde `id_jugador` esté vacío o sea nulo.

#### 2.3.9. Partido_jugadores y partido_goles

- En `partido_jugadores` se mapean:
  - `url_partido` → `id_partido`.
  - `url_jugador` → `id_jugador`.
  - `seleccion` → `id_seleccion`.
  - Además se trasladan `camiseta`, `posicion`, `rol`, minutos de entrada/salida y cantidad de goles.

- En `partido_goles`:
  - `url_partido` se convierte en `id_partido` usando el mapa de partidos.
  - Si existe `url_jugador` se usa para encontrar `id_jugador`; de lo contrario, se utiliza `jugador` (nombre) y el mapa por nombre.
  - `seleccion` se transforma en `id_seleccion`.
  - Se copian los campos `minuto` y `tipo_gol`.

  Es crucial que el formato de `url_partido` en los CSV de goles y el que se usó para construir el mapa de partidos coincidan; de lo contrario, `id_partido` podría quedar vacío, como se observó en algunas iteraciones del proyecto.

### 2.4. Escritura de CSV limpios en `output_db/`

Una vez transformados todos los DataFrames, el script guarda cada uno en la carpeta `output_db/` mediante una función auxiliar que simplemente hace `to_csv` con codificación UTF-8 y sin índice.

Al final del proceso de transformación se obtiene:

- Un CSV por cada tabla del modelo relacional (mundiales, selecciones, jugadores, partidos, grupos, etc.).
- Varios CSV de mapas (`_mapa_*.csv`) que documentan la correspondencia entre valores originales (años, nombres, URLs) y IDs numéricos.

Este diseño permite:

- Volver a cargar la base de datos desde cero en cualquier momento sin necesidad de repetir el scraping.
- Inspeccionar fácilmente los datos limpios antes de cargarlos.
- Depurar problemas de mapeo revisando los mapas auxiliares.



## 3. Carga de datos: de `output_db/` a MySQL con `cargar_db.py`

### 3.1. Propósito de `cargar_db.py`

El archivo `cargar_db.py` se encarga exclusivamente de la **carga** de los CSV ya transformados (ubicados en `output_db/`) a la base de datos MySQL `mundiales`.

Características principales:

- Usa `pandas` para leer los CSV de `output_db/`.
- Se conecta a MySQL usando `mysql-connector-python` con los parámetros definidos en `DB_CONFIG`.
- Inserta los datos en lotes (`LOTE = 500` filas por lote) para mejorar el rendimiento con tablas grandes.
- Tiene funciones de ayuda para convertir valores de texto a enteros, decimales, fechas y booleanos, manejando correctamente los valores vacíos.
- Define **una función de carga por tabla**, en un orden que respeta las dependencias de claves foráneas.

### 3.2. Configuración de conexión y utilidades

En la parte superior del archivo se define el diccionario `DB_CONFIG` con los mismos parámetros que se usan en Docker:

- `host`: `127.0.0.1`
- `port`: `3306`
- `database`: `mundiales`
- `user`: `mundiales_user`
- `password`: `mundiales1234`

También se define la carpeta de datos:

- `DIR_DATOS = "./output_db"`

Y el tamaño de lote para inserciones masivas:

- `LOTE = 500`

Las funciones de utilidad (`val`, `entero`, `decimal`, `fecha`, `booleano`) se encargan de:

- Interpretar cadenas vacías o marcadores especiales (`"nan"`, `"None"`, `"NULL"`) como `None` (que MySQL interpretará como `NULL`).
- Convertir textos a enteros (`entero`) y decimales (`decimal`) con manejo de errores.
- Parsear fechas a formato `YYYY-MM-DD` usando `pandas.to_datetime`.
- Convertir campos lógicos a 0/1 para columnas booleanas.

La función `insertar_lotes` recibe un cursor, un SQL parametrizado, una lista de filas y el nombre lógico de la tabla, e inserta las filas en bloques de tamaño `LOTE`, mostrando el progreso por pantalla.

### 3.3. Funciones de carga por tabla

Para cada tabla del esquema se define una función `cargar_<tabla>` que:

1. Recibe un cursor de base de datos y un DataFrame con los datos desde `output_db/`.
2. Construye la sentencia `INSERT INTO ... VALUES (...)` con los nombres de columnas tal como están en `schema.sql`.
3. Recorre el DataFrame fila a fila, aplica las funciones de conversión (`entero`, `decimal`, etc.) y acumula una lista de tuplas con los valores ya tipados.
4. Llama a `insertar_lotes` para ejecutar el `INSERT` en lotes.

Ejemplos de funciones:

- `cargar_selecciones`: inserta en la tabla `selecciones` los campos `id_seleccion`, `nombre`, `mundiales_jugados`, etc.
- `cargar_mundiales`: rellena `id_mundial`, `anio`, `id_organizador`, `id_campeon`, y estadísticas globales del mundial.
- `cargar_jugadores`: inserta todos los datos del jugador, incluidos `fecha_nacimiento`, `altura_cm` y estadísticas acumuladas.
- `cargar_partidos`: llena la tabla `partidos` con `id_partido`, `id_mundial`, `fecha`, `etapa`, IDs de selecciones local y visitante y los goles de cada uno.
- `cargar_partido_jugadores` y `cargar_partido_goles`: insertan el detalle de quién jugó cada partido y quién marcó cada gol, respetando las claves foráneas a `partidos`, `jugadores` y `selecciones`.

Este patrón de **una función por tabla** hace que el proceso sea fácil de mantener y extender: si en el futuro se añade una nueva tabla, basta con:

1. Añadir el CSV correspondiente a `output_db/`.
2. Escribir una nueva función `cargar_nueva_tabla` para construir e insertar las filas.
3. Invocar esa función en el flujo principal en el orden adecuado.

### 3.4. Orden de carga y respeto de claves foráneas

Aunque el fragmento principal del flujo de `cargar_db.py` no se mostró completo aquí, el patrón seguido es:

1. Conectar a la base de datos con `mysql.connector.connect(**DB_CONFIG)`.
2. Obtener un cursor.
3. (Opcional) Desactivar temporalmente las comprobaciones de claves foráneas y hacer `TRUNCATE` de las tablas para permitir recargar desde cero.
4. Cargar las tablas en un orden que respete las dependencias:
   - Primero tablas **maestras** sin dependencias fuertes (ej. `selecciones`, `mundiales`, `jugadores`).
   - Luego tablas que dependen de ellas (ej. `seleccion_titulos`, `jugador_camisetas`, `partidos`).
   - Después tablas intermedias y de detalle (`grupos`, `posiciones_finales`, `goleadores`, `premios`, `tarjetas`, `jugadores_por_mundial`, `planteles`).
   - Por último tablas con más FKs (`partido_jugadores`, `partido_goles`).
5. Confirmar la transacción con `conn.commit()`.
6. Cerrar la conexión.

Gracias a que los CSV de `output_db/` ya traen todos los IDs numéricos coherentes (id_mundial, id_seleccion, id_jugador, id_partido, etc.), la inserción respeta las restricciones de integridad definidas en `schema.sql`.



## 4. Infraestructura Docker y creación de tablas (`docker-compose.yml` y `schema.sql`)

### 4.1. `docker-compose.yml`

El archivo `docker-compose.yml` define un servicio `db` basado en la imagen oficial `mysql:8.0`. Los puntos clave de la configuración son:

- **Imagen y contenedor**:
  - `image: mysql:8.0`
  - `container_name: mundiales_db`

- **Credenciales y base de datos inicial**:
  - `MYSQL_ROOT_PASSWORD: root1234`
  - `MYSQL_DATABASE: mundiales`
  - `MYSQL_USER: mundiales_user`
  - `MYSQL_PASSWORD: mundiales1234`

  Estas variables de entorno le indican al contenedor que cree automáticamente:
  - La base de datos `mundiales`.
  - El usuario `mundiales_user` con la contraseña `mundiales1234`.

- **Puertos**:
  - `ports: - "3306:3306"`
  - Expone el puerto 3306 del contenedor en el puerto 3306 de la máquina host, permitiendo conectarse desde herramientas externas como DBeaver.

- **Volúmenes**:
  - `./init/schema.sql:/docker-entrypoint-initdb.d/schema.sql`
    - Monta el archivo de esquema en una ruta especial reconocida por MySQL Docker.
    - En el **primer arranque** del contenedor, MySQL ejecuta automáticamente todos los scripts `.sql` presentes en esa carpeta, por lo que `schema.sql` se ejecuta una única vez al inicio, creando toda la estructura de tablas.
  - `mundiales_data:/var/lib/mysql`
    - Volumen de datos persistente, donde MySQL guarda los archivos físicos de la base de datos. Esto permite que los datos sobrevivan a reinicios del contenedor.

- **Healthcheck**:
  - Se define un chequeo de salud que ejecuta `mysqladmin ping` contra el servidor.
  - Esto permite saber desde Docker si la base de datos está lista (`healthy`) antes de ejecutar procesos que dependan de ella.

### 4.2. `schema.sql`: creación de la base y tablas

El archivo `init/schema.sql` contiene todo el DDL (Data Definition Language) necesario para preparar la base `mundiales`:

1. **Creación de la base de datos**:
   - `CREATE DATABASE IF NOT EXISTS mundiales ...;`
   - `USE mundiales;`

2. **Creación de tablas**: se definen todas las tablas con sus columnas, tipos de datos, claves primarias y restricciones `NOT NULL` donde aplica. Algunas tablas importantes son:

   - `selecciones`: almacena información de cada selección (nombre, partidos jugados, goles, etc.).
   - `mundiales`: contiene un registro por mundial, con datos como año, organizador, campeón y estadísticas globales.
   - `jugadores`: información personal y estadística de cada jugador.
   - `partidos`: un registro por partido, con referencia al mundial, selecciones local y visitante, fecha y resultado.
   - `grupos`, `posiciones_finales`, `goleadores`, `premios`, `tarjetas`, `jugadores_por_mundial`, `planteles`, `partido_jugadores`, `partido_goles`.

3. **Claves foráneas**: en la segunda parte del archivo se añaden todas las `FOREIGN KEY` mediante sentencias `ALTER TABLE`, por ejemplo:

   - `mundiales.id_organizador` y `mundiales.id_campeon` referencian a `selecciones.id_seleccion`.
   - `partidos.id_mundial` referencia a `mundiales.id_mundial`.
   - `goleadores.id_jugador` referencia a `jugadores.id_jugador`.
   - `partido_jugadores.id_partido` referencia a `partidos.id_partido`.
   - `partido_goles.id_mundial`, `id_partido`, `id_jugador`, `id_seleccion` referencian a sus tablas maestras.

   Además se especifican comportamientos ante borrados y actualizaciones (`ON UPDATE CASCADE`, `ON DELETE CASCADE` o `SET NULL`) para preservar la consistencia lógica de los datos.

El resultado de ejecutar `schema.sql` es una base de datos completamente preparada para recibir los datos limpios producidos en `output_db/`.



## 5. ¿Por qué crear un nuevo directorio `output_db/`?

La decisión de introducir un segundo directorio `output_db/` separado de `output/` responde a varias necesidades prácticas y de diseño:

1. **Separación de responsabilidades**:
   - `output/`: contiene los datos **tal como salen del scraping**. Pueden cambiar si el sitio fuente cambia, si se corrige el scraper, etc.
   - `output_db/`: contiene los datos **adaptados al modelo relacional**. Aquí ya se espera que las columnas cumplan con los tipos, nombres y restricciones definidas en `schema.sql`.

2. **Reproducibilidad y depuración**:
   - Al mantener los CSV limpios en `output_db/`, es posible recargar la base de datos tantas veces como se necesite (por ejemplo, después de cambiar `cargar_db.py` o retocar el esquema) sin tener que repetir la fase de scraping.
   - Si se detectan inconsistencias (como IDs nulos o problemas de mapeo), se pueden inspeccionar los CSV intermedios y los mapas (`_mapa_*.csv`) para entender qué ocurrió.

3. **Estandarización y control de calidad**:
   - La fase de transformación aplica todas las reglas de negocio y normalización (unificación de URLs, limpieza de fechas, eliminación de filas inválidas, etc.).
   - De esta forma, el script de carga (`cargar_db.py`) puede asumir que los CSV de `output_db/` ya están en un formato compatible con la base, simplificando su lógica.

4. **Flexibilidad para análisis fuera de la BD**:
   - Los CSV de `output_db/` se pueden usar también directamente para análisis en herramientas como Python (pandas), R o incluso Excel/LibreOffice, sin necesidad de depender siempre de la base de datos.

En resumen, `output_db/` actúa como una **capa intermedia de datos curados** entre el scraping y la base de datos, lo que mejora la robustez, la trazabilidad y la facilidad de mantenimiento del proyecto.



## 6. Resumen del proceso extremo a extremo

1. El scraper genera CSV crudos y los coloca en `output/`.
2. Un script de transformación (inspirado en `cargar_datos.py` en su versión transformadora) lee `output/`, construye mapas de IDs y normaliza todas las tablas.
3. Los resultados limpios y consistentes se guardan en CSV dentro de `output_db/`, junto con mapas auxiliares `_mapa_*.csv`.
4. Se levanta el contenedor MySQL usando `docker-compose.yml`, que ejecuta automáticamente `init/schema.sql` para crear la base `mundiales` y todas sus tablas.
5. El script `cargar_db.py` se conecta a la base, lee los CSV de `output_db/` y los inserta en las tablas correspondientes en un orden que respeta las claves foráneas.
6. Finalmente, los datos quedan disponibles para consultas desde herramientas como DBeaver o la consola de MySQL, permitiendo análisis detallados sobre mundiales, selecciones, jugadores, partidos y goles.

Esta arquitectura modular (scraping → transformación → CSV limpios → carga a MySQL en Docker) hace que el proyecto sea fácil de entender, extender y mantener, y permite reejecutar cada etapa de manera independiente cuando cambian los datos o los requisitos de modelado.



## 7. Tecnologías usadas y justificación

### 7.1. Python como lenguaje principal

Se eligió **Python** para la etapa de transformación y carga por varias razones:

- Es un lenguaje muy utilizado en ciencia de datos y ETL (Extract, Transform, Load).
- Posee librerías maduras para trabajar con CSV y bases de datos.
- Facilita escribir scripts legibles y mantenibles para procesar grandes volúmenes de datos.

Los scripts clave del proyecto (`cargar_datos.py` en modo transformador y `cargar_db.py` para la carga) están escritos íntegramente en Python.

### 7.2. Uso de pandas en la transformación

La librería **pandas** se utiliza principalmente para:

- Leer los CSV de `output/` y `output_db/` en estructuras `DataFrame`, que permiten manipular columnas y filas de forma vectorizada.
- Aplicar transformaciones columna por columna (por ejemplo, mapear nombres de selecciones a `id_seleccion`, años de mundiales a `id_mundial`, etc.).
- Limpiar valores (reemplazar vacíos, normalizar textos, convertir tipos) usando funciones como `apply`, `astype`, o directamente operaciones sobre columnas.
- Exportar los resultados nuevamente a CSV mediante `DataFrame.to_csv`, que se usa para generar los archivos finales en `output_db/`.

Ejemplos concretos de dónde se aplica pandas:

- En el script de transformación (versión transformadora de `cargar_datos.py`), las funciones `transformar_*` reciben y devuelven `DataFrame` de pandas. Ahí se construyen las columnas finales de cada tabla (selecciones, mundiales, jugadores, partidos, etc.).
- En `cargar_db.py`, la función `leer` usa `pandas.read_csv` para cargar cada archivo de `output_db/` en memoria, y luego se recorre el `DataFrame` para construir las tuplas que se insertan en MySQL.

Gracias a pandas, se pueden expresar transformaciones complejas (como normalizar fechas, explotar listas de años o números de camiseta en varias filas, o mapear URLs a IDs) con pocas líneas de código, manteniendo claridad y reduciendo errores.

### 7.3. mysql-connector-python para la carga en BD

Para comunicar Python con MySQL se utilizó la librería **mysql-connector-python**:

- Permite abrir conexiones usando un diccionario de configuración (`DB_CONFIG`) coherente con los parámetros del contenedor Docker.
- Ofrece cursores con soporte para sentencias preparadas (`%s` como placeholders), lo que se aprovecha en las funciones `cargar_*` de `cargar_db.py`.
- Soporta inserciones masivas mediante `cursor.executemany`, que se usa dentro de la función `insertar_lotes` para enviar bloques de 500 filas por vez.

El uso combinado de pandas (para la parte de transformación y preparación de datos) y mysql-connector-python (para la escritura final en la base relacional) permite separar claramente las responsabilidades: pandas se encarga de la lógica de datos en memoria y el conector se encarga de la persistencia en MySQL
