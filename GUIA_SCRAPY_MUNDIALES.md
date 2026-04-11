# Guia tecnica del scraper de mundiales

Este documento explica como se construyo y como se usa el flujo de scraping en `fase1/`, desde la extraccion con Scrapy hasta la carga final a MySQL.

## 1) Objetivo del proyecto

El flujo busca:

1. Recorrer `losmundialesdefutbol.com` con un crawler controlado.
2. Extraer datos estructurados de mundiales, selecciones, jugadores, partidos, goles, premios, grupos y tarjetas.
3. Guardar una salida cruda en CSV (`output/`).
4. Transformar esa salida a un modelo normalizado para BD (`output_db/`).
5. Cargar CSVs normalizados en MySQL (contenedor Docker).

## 2) Arquitectura general (como se hizo)

El proceso se implemento en 3 etapas:

- Etapa A - Scrapy:
  - Spider principal: `fase1/mundiales_scraper/spiders/mundiales.py`
  - Tipado de datos (items): `fase1/mundiales_scraper/items.py`
  - Escritura de CSV por tipo: `fase1/mundiales_scraper/pipelines.py`
  - Config de crawling: `fase1/mundiales_scraper/settings.py`

- Etapa B - Transformacion:
  - Script: `fase1/transformar_output.py`
  - Convierte datos crudos en tablas con IDs y llaves foraneas para el schema final.

- Etapa C - Carga a BD:
  - Script: `fase1/cargar_bd.py`
  - Inserta `output_db/*.csv` en tablas MySQL.

## 3) Requisitos y entorno

## Python

Dependencias detectadas por imports del proyecto:

- `scrapy`
- `beautifulsoup4`
- `lxml`
- `pandas`
- `mysql-connector-python`

Instalacion sugerida:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install scrapy beautifulsoup4 lxml pandas mysql-connector-python
```

## Base de datos (Docker)

Definida en `fase1/docker-compose.yml`:

- Servicio: `mysql:8.0`
- DB: `mundiales`
- User: `mundiales_user`
- Password: `mundiales1234`
- Puerto: `3306`

Levantar BD:

```bash
cd fase1
docker compose up -d
```

## 4) Flujo de ejecucion completo

Desde `fase1/`:

```bash
# 1) Ejecutar spider
scrapy crawl mundiales

# 2) Transformar salida cruda a salida normalizada
python3 transformar_output.py

# 3) Cargar a MySQL
python3 cargar_bd.py
```

Notas:

- `scrapy.cfg` esta en `fase1/scrapy.cfg`, por eso conviene correr Scrapy dentro de `fase1/`.
- El pipeline escribe por defecto a `fase1/output/`.
- La transformacion escribe a `fase1/output_db/`.

## 5) Que hace cada archivo Python

### `fase1/mundiales_scraper/spiders/mundiales.py`

Es el nucleo del crawler.

- Clasifica URLs por patron (`mundial`, `resultados`, `premios`, `jugador`, etc.).
- En `parse()` enruta cada respuesta al parser especifico segun tipo de URL.
- Ejecuta parseadores especializados:
  - `_parse_mundial`
  - `_parse_resultados`
  - `_parse_posiciones_finales`
  - `_parse_goleadores_completo`
  - `_parse_premios`
  - `_parse_grupo`
  - `_parse_tarjetas`
  - `_parse_partido`
  - `_parse_plantel`
  - `_parse_seleccion`
  - `_parse_jugador`
  - `_parse_jugador_por_mundial`
- Sigue enlaces internos con `_seguir_enlaces()` filtrando:
  - dominio
  - extensiones no utiles (imagenes, css, js, pdf, etc.)
  - fragmentos externos/redes

Implementacion clave:

- Se usa `BeautifulSoup` sobre `response.text` para parseo flexible del HTML.
- Se extrae `fecha_scraping` por registro.
- Se normalizan textos con helper `limpiar()`.

### `fase1/mundiales_scraper/items.py`

Define el contrato de datos de Scrapy (uno por entidad):

- `MundialItem`
- `SeleccionItem`
- `JugadorItem`
- `JugadorMundialItem`
- `GoleadorMundialItem`
- `PartidoItem`
- `PosicionFinalItem`
- `PremioItem`
- `GrupoItem`
- `TarjetaItem`
- `PartidoJugadorItem`
- `PartidoGolItem`
- `PlantelItem`

Estos items desacoplan extraccion (spider) de persistencia (pipeline).

### `fase1/mundiales_scraper/pipelines.py`

Implementa `CsvPipeline`.

- Crea `output/` si no existe.
- Abre un archivo CSV por tipo de item.
- Escribe headers solo si el archivo esta vacio.
- Hace `flush()` en cada escritura para evitar perdida de datos ante cortes.
- Ignora campos extra con `extrasaction="ignore"`.

Resultado: 13 CSVs de salida cruda (`mundiales.csv`, `jugadores.csv`, `partidos.csv`, etc.).

### `fase1/mundiales_scraper/settings.py`

Configura estrategia y politicas del crawler.

Puntos importantes:

- `ROBOTSTXT_OBEY = True`
- `CONCURRENT_REQUESTS_PER_DOMAIN = 1`
- `DOWNLOAD_DELAY = 1.5`
- `AUTOTHROTTLE_ENABLED = True`
- `DEPTH_LIMIT = 5`
- Cola FIFO + `DEPTH_PRIORITY = 1` para recorrido mas uniforme por niveles.
- Pipeline activo: `mundiales_scraper.pipelines.CsvPipeline`.

### `fase1/mundiales_scraper/middlewares.py`

Archivo de plantilla de Scrapy. En este proyecto no contiene logica personalizada activa.

### `fase1/mundiales_scraper/__init__.py`

Paquete Python del proyecto Scrapy (vacio).

### `fase1/mundiales_scraper/spiders/__init__.py`

Archivo de paquete para modulo de spiders (plantilla).

### `fase1/transformar_output.py`

Convierte CSV crudo a modelo normalizado de BD.

Responsabilidades principales:

- Detectar separador y leer CSVs base.
- Construir mapas de IDs:
  - seleccion
  - jugador
  - mundial
  - partido
- Normalizar claves de URL (`/jugadores/...`, `/partidos/...`).
- Limpiar tipos:
  - enteros
  - decimales
  - alturas a cm
  - IDs con formato `18.0`
- Transformar cada tabla con funciones dedicadas (`transformar_*`).
- Exportar CSVs limpios en `output_db/`.
- Guardar mapas auxiliares `_mapa_*.csv` para trazabilidad.

Funciones de transformacion clave:

- `transformar_mundiales`
- `transformar_selecciones`
- `transformar_seleccion_titulos`
- `transformar_jugadores`
- `transformar_jugador_camisetas`
- `transformar_partidos`
- `transformar_grupos`
- `transformar_posiciones_finales`
- `transformar_goleadores`
- `transformar_premios`
- `transformar_tarjetas`
- `transformar_jugadores_por_mundial`
- `transformar_planteles`
- `transformar_partido_jugadores`
- `transformar_partido_goles`

### `fase1/cargar_bd.py`

Carga `output_db/` en MySQL.

- Conecta con credenciales del proyecto.
- Ejecuta `TRUNCATE` en orden seguro (con `FOREIGN_KEY_CHECKS` temporalmente en 0).
- Carga tabla por tabla con `executemany`.
- Normaliza valores antes de insertar:
  - vacios a `NULL`
  - fechas a formato ISO
  - numericos embebidos en texto
- Informa columnas extra/faltantes por CSV.

### `fase2/cargar_bd.py`

Es una copia funcional del cargador de `fase1/` para el flujo de fase 2.

## 6) Salidas generadas

## Salida cruda (`fase1/output/`)

Archivos por entidad extraida, con columnas cercanas al HTML original.

## Salida normalizada (`fase1/output_db/`)

Archivos alineados al schema relacional (IDs, FKs y tipos limpios), listos para insercion.

Tambien se generan:

- `_mapa_jugadores.csv`
- `_mapa_partidos.csv`
- `_mapa_selecciones.csv`
- `_mapa_mundiales.csv`

## 7) Decisiones tecnicas relevantes

- Se prefirio un crawler unico multi-parser para centralizar navegacion y reglas.
- Se uso `DEPTH_LIMIT` + FIFO/BFS para mejorar cobertura de ramas menos profundas.
- Se desacoplo extraccion y carga a BD mediante etapa intermedia de transformacion.
- Se conservaron URLs originales para trazabilidad y reconstruccion de mapeos.

## 8) Validacion basica recomendada

Despues de correr el flujo:

1. Verificar que existan CSVs en `fase1/output/` y `fase1/output_db/`.
2. Revisar logs de `[AVISO]` en transformacion/carga.
3. Consultar conteos en MySQL por tabla para confirmar volumen esperado.

## 9) Comandos utiles de operacion

Desde `fase1/`:

```bash
# Ejecutar spider con logs mas detallados
scrapy crawl mundiales -s LOG_LEVEL=DEBUG

# Ejecutar solo transformacion
python3 transformar_output.py

# Ejecutar solo carga
python3 cargar_bd.py
```

---

Si se desea extender el scraper, el punto natural es agregar un nuevo parser en `spiders/mundiales.py`, su `Item` en `items.py`, su salida en `pipelines.py` y su transformacion en `transformar_output.py`.
