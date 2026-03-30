# Documentación técnica del scraping (sitio de mundiales)

## 1. Objetivo de este documento

Este documento explica, con detalle operativo, cómo se obtuvo la data del sitio de mundiales y cómo se estructuró la salida en CSV crudo (`output/`) para luego pasar al proceso de transformación y carga a base de datos.

Su propósito es complementar `TrasformacionCarga.md` con foco específico en la fase de **extracción** (scraping), incluyendo:

1. Qué herramientas se usaron y por qué.
2. Cómo fue la lógica de navegación y parseo.
3. Qué datos se extrajeron por entidad.
4. Qué problemas de calidad aparecen en el crudo y por qué son esperables.
5. Qué decisiones técnicas se tomaron para tener un scraping robusto y reproducible.


## 2. Alcance del scraping

Fuente objetivo:

- `https://www.losmundialesdefutbol.com/mundiales.php`

Alcance funcional implementado:

- Recorrer páginas históricas de mundiales y secciones relacionadas.
- Extraer datos a nivel de dominio futbolístico (mundial, selección, jugador, partido, etc.).
- Guardar salida en archivos CSV crudos separados por entidad (carpeta `output/`).

Salida cruda producida (13 CSV):

- `output/mundiales.csv`
- `output/selecciones.csv`
- `output/jugadores.csv`
- `output/partidos.csv`
- `output/grupos.csv`
- `output/posiciones_finales.csv`
- `output/goleadores.csv`
- `output/premios.csv`
- `output/tarjetas.csv`
- `output/jugadores_por_mundial.csv`
- `output/planteles.csv`
- `output/partido_jugadores.csv`
- `output/partido_goles.csv`


## 3. Herramientas utilizadas y justificación

En la implementación del scraping se trabajó con un enfoque tipo crawler estructurado (Scrapy) y parseo HTML flexible:

- **Scrapy**
  - Controla el ciclo request/response, cola de URLs y seguimiento de enlaces.
  - Permite separar claramente: spider (extracción) y pipeline (persistencia CSV).
  - Facilita reintentos y control de ritmo para no saturar el sitio.

- **BeautifulSoup (bs4)**
  - Útil cuando el HTML real tiene variaciones entre páginas o tablas con estructura irregular.
  - Permite parseo semántico por nodos y no solo selectores rígidos.

- **Regex (`re`)**
  - Clasificación de tipos de URL (ej. páginas de resultados, jugadores, premios, etc.).
  - Extracción de patrones puntuales (años, rutas, valores compactos en texto).

- **CSV (`csv.DictWriter`)**
  - Salida tabular simple, compatible y auditable por equipo.
  - Permite revisión manual rápida de datos antes del ETL.

Por qué este stack fue apropiado:

- El sitio mezcla tablas históricas, páginas de detalle y enlaces con rutas relativas.
- Se necesitaba cobertura amplia (muchas páginas) + tolerancia a HTML heterogéneo.
- El proyecto académico requería trazabilidad clara: `web -> output (crudo) -> output_db (limpio) -> MySQL`.


## 4. Arquitectura lógica del scraping

La arquitectura operativa de extracción siguió este patrón:

1. **Punto de entrada**
   - Página raíz de mundiales con enlaces a secciones históricas y detalles.

2. **Descubrimiento de enlaces**
   - Recolección de enlaces internos relevantes.
   - Filtro por dominio objetivo y rutas útiles (`/mundiales/`, `/partidos/`, `/jugadores/`, etc.).

3. **Clasificación de páginas**
   - Cada URL detectada se clasifica por tipo para enviar al parser correcto.
   - Ejemplos de tipo: mundial, resultados, grupos, goleadores, premios, jugador, partido, plantel.

4. **Parseo especializado por tipo**
   - Cada tipo de página tiene su lógica específica de extracción.
   - Resultado: objetos de datos (items) con esquema homogéneo por entidad.

5. **Persistencia CSV por entidad**
   - Pipeline enruta cada item al CSV correspondiente.
   - Se escribe encabezado una sola vez por archivo.

6. **Salida cruda consolidada**
   - Carpeta `output/` contiene la data extraída sin normalización fuerte.


## 5. Lógica de navegación y cobertura

### 5.1 Estrategia de cobertura

La estrategia se diseñó para maximizar cobertura histórica con mínimo riesgo de bloqueo:

- Navegación por enlaces internos desde páginas de mundiales.
- Seguimiento controlado de páginas de detalle (partidos, jugadores, planteles).
- Exclusión de enlaces externos/no relevantes.

### 5.2 Control de ritmo y comportamiento responsable

Buenas prácticas aplicadas durante extracción:

- Respetar `robots.txt` cuando corresponde.
- Reducir concurrencia por dominio.
- Agregar `download_delay` para evitar ráfagas agresivas.
- Reintentos en errores transitorios de red/servidor.
- Auto-throttle para adaptar velocidad según latencia.

Objetivo: tener scraping estable, reproducible y ético, minimizando ruido operativo.


## 6. Diseño de salida cruda (`output/`)

### 6.1 Principio de diseño

El `output/` no intenta ser base normalizada. Es una capa **raw/staging** con:

- Datos cercanos al origen web.
- Tipos aún heterogéneos (fechas texto, booleanos como "Si/No", etc.).
- Campos de trazabilidad (`url`, `fecha_scraping`) útiles para auditoría.

Esto permite:

- Repetir transformaciones sin re-scrapear.
- Depurar extracción antes de modelado relacional.
- Conservar evidencia del dato original.

### 6.2 Campos típicos presentes en el crudo

Dependiendo del CSV, se observan patrones como:

- Identificadores lógicos (año, nombre de selección, nombre de jugador).
- URLs relativas y absolutas (ej. `../partidos/...` y `https://.../partidos/...`).
- Fechas en texto (`20-Nov-2022`, `9 de junio de 1978`).
- Números con ruido textual (`+3`, `104 (0 ya jugados)`).
- Valores faltantes representados como `""`, `-`, `None`, `nan`.


## 7. Qué extrae cada entidad (visión de negocio)

### 7.1 `mundiales.csv`

- Año del mundial.
- Selección organizadora.
- Selección campeona.
- Totales del torneo (selecciones, partidos, goles, promedio).

Uso posterior: base para `id_mundial` y relaciones históricas.

### 7.2 `selecciones.csv`

- Nombre de selección.
- Estadísticas históricas agregadas (participaciones, partidos, goles, etc.).
- Información de títulos en formato textual multivalorado (en crudo).

Uso posterior: catálogo maestro de selecciones + insumo para explotar títulos.

### 7.3 `jugadores.csv`

- Identidad del jugador (nombre, nombre completo).
- URL de jugador (clave natural de scraping).
- Datos biográficos y deportivos (fecha, posición, selección, altura, estadísticas).

Uso posterior: catálogo maestro de jugadores y mapeo `url_jugador -> id_jugador`.

### 7.4 `partidos.csv`

- Año/mundial.
- Fecha, etapa, selecciones local/visitante.
- Goles local/visitante.
- URL del partido.

Uso posterior: catálogo de partidos y mapeo `url_partido -> id_partido`.

### 7.5 `grupos.csv` y `posiciones_finales.csv`

- Tablas de clasificación por mundial y selección.
- Posición, puntos, GF/GC, diferencia, etc.

Uso posterior: análisis de rendimiento por fase y resultados finales.

### 7.6 `goleadores.csv`, `tarjetas.csv`, `premios.csv`

- Métricas individuales por mundial.
- Eventos disciplinarios.
- Premios por edición (con casos pendientes o no definidos en fuente).

Uso posterior: estadísticas de rendimiento y reconocimientos.

### 7.7 `jugadores_por_mundial.csv`, `planteles.csv`

- Participación de jugador por mundial.
- Planteles por selección y edición.

Uso posterior: análisis de convocatoria, minutos y desempeño por torneo.

### 7.8 `partido_jugadores.csv`, `partido_goles.csv`

- Detalle granular por partido:
  - quién jugó,
  - rol/camiseta/minutos,
  - quién anotó, minuto y tipo de gol.

Uso posterior: capa de detalle para consultas finas y SP avanzados.


## 8. Problemas típicos detectados en el crudo (esperables)

Durante la extracción, los siguientes problemas son normales por naturaleza del HTML/fuente:

- URLs con dos formatos (relativo/absoluto) para la misma entidad.
- Campos numéricos mezclados con texto explicativo.
- Fechas en formatos múltiples (español y abreviaturas en inglés).
- Ausencia de dato en torneos futuros o secciones incompletas.
- Filas no estrictamente de jugador (p.ej. entrenador en plantel).

Estos casos no invalidan scraping; se corrigen en la fase ETL de normalización.


## 9. Decisiones técnicas relevantes tomadas en scraping

1. **Separar scraping de transformación**
   - El scraper entrega raw (`output/`) sin forzar tipos complejos.
   - La limpieza fuerte queda para `transformar_output.py`.

2. **Conservar `url` y `fecha_scraping` en crudo**
   - Útil para trazabilidad y depuración.
   - En modelo final se centralizan metadatos y se usan IDs internos.

3. **CSV por entidad, no un mega CSV**
   - Facilita validación por dominio.
   - Reduce acoplamiento entre parsers.

4. **Normalización de URL en transformación (no en scraping duro)**
   - Se evita romper extracción por cambios menores de ruta.

5. **Repetibilidad**
   - El flujo permite rehacer `output_db` y recargar BD sin reescrapear.


## 10. Flujo operativo recomendado (de punta a punta)

Orden sugerido para reproducir el proceso completo:

1. Ejecutar scraping para regenerar `output/` (si se requiere actualización de fuente).
2. Ejecutar transformación:
   - `venv/bin/python transformar_output.py`
3. Levantar BD en Docker:
   - `docker compose up -d`
4. Cargar datos normalizados:
   - `venv/bin/python cargar_bd.py`
5. Validar conteos e integridad referencial en MySQL.


## 11. Controles de calidad recomendados para la fase de scraping

Antes de transformar, revisar en `output/`:

- Que existan los 13 CSV esperados.
- Que cada CSV tenga encabezado correcto y no esté vacío sin razón.
- Que las columnas `url_partido`/`url_jugador` estén presentes donde aplique.
- Que no haya caracteres de codificación dañados (UTF-8).

Checks rápidos útiles:

- Conteo de filas por CSV.
- Muestras aleatorias de URLs.
- Verificación de fechas en columnas críticas.
- Detección de filas con separadores anómalos.


## 12. Riesgos y mitigaciones

### Riesgo 1: Cambios de estructura HTML

- **Impacto**: parseos incompletos o columnas vacías.
- **Mitigación**: parsers por tipo de página + validación por CSV + fallback por nombre/URL en ETL.

### Riesgo 2: Inconsistencia de URLs

- **Impacto**: fallas de mapeo a IDs en detalle.
- **Mitigación**: normalizar claves URL al basename en transformación.

### Riesgo 3: Valores sin dato en páginas futuras

- **Impacto**: nulos en campos de premios/partidos/jugadores.
- **Mitigación**: mantener `NULL` controlado y documentado; no inventar datos.


## 13. Estado actual del scraping en el proyecto

Estado funcional observado:

- `output/` disponible con 13 CSV crudos.
- Estructura suficiente para transformar a `output_db`.
- Flujo completo reproducible con scripts actuales del repo.

Nota técnica:

- El foco operativo actual del repositorio está en transformación/carga (`transformar_output.py`, `cargar_bd.py`).
- La extracción cruda ya está materializada en `output/` y documentada aquí para trazabilidad del proceso completo.


## 14. Conclusión

El proceso de scraping se diseñó para priorizar cobertura histórica, trazabilidad y estabilidad operativa:

- Extrae datos de múltiples tipos de página del sitio de mundiales.
- Conserva una capa cruda auditable (`output/`).
- Alimenta de forma consistente la etapa de normalización (`output_db`) y la carga SQL.

Con este enfoque, el proyecto mantiene separación de responsabilidades clara:

- **Scraping**: obtener y persistir raw.
- **Transformación**: limpiar, mapear y normalizar.
- **Carga BD**: insertar respetando PK/FK y tipos SQL.

Eso permite explicar, reproducir y defender técnicamente todo el pipeline de datos en la presentación del proyecto.
