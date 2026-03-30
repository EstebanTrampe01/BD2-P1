# Stored Procedures

## 1. Introducción

Los procedimientos permiten consultar la información desde dos perspectivas complementarias:

- **`sp_info_mundial`**  Vista por edición del torneo: año, grupos, partidos, goleadores, premios
- **`sp_info_pais`**  Vista por selección (historial completo, sedes, participaciones, estadísticas)

Ambos procedimientos soportan parámetros opcionales de filtrado para acotar los resultados a una búsqueda específica sin necesidad de construir consultas SQL ad hoc.

## 2. Esquema de la Base de Datos

Los procedimientos se apoyan en las siguientes tablas principales:

| Tabla                  | Descripción                                                                                                                                               |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `selecciones`           | Catálogo de selecciones nacionales con estadísticas históricas acumuladas                                                                                 |
| `mundiales`             | Una fila por edición del torneo (año, sede, campeón, totales)                                                                                             |
| `partidos`              | Cada partido jugado: fecha, etapa, local, visitante, marcador                                                                                             |
| `grupos`                | Posiciones en la fase de grupos por selección y mundial                                                                                                  |
| `posiciones_finales`    | Clasificación general de todas las selecciones al cierre del torneo                                                                                      |
| `goleadores`            | Ranking de goleadores por mundial con posición y promedio                                                                                                 |
| `partido_goles`         | Detalle gol a gol: jugador, minuto, tipo (normal/penal/autogol)                                                                                          |
| `jugadores`             | Catálogo de jugadores con datos biográficos y carrera                                                                                                    |
| `jugadores_por_mundial` | Participación de cada jugador en un mundial (titular, goles, tarjetas)                                                                                   |
| `premios`               | Premios individuales y colectivos por mundial                                                                                                            |
| `tarjetas`              | Tarjetas amarillas y rojas por jugador y mundial                                                                                                          |
| `seleccion_titulos`     | Registro de campeonatos y subcampeonatos por selección                                                                                                    |

## 3. Procedimiento: `sp_info_mundial`

### 3.1 Descripción general

Consulta toda la información de una edición específica del Mundial de Fútbol identificada por su año. Devuelve hasta siete conjuntos de resultados ordenados desde la ficha general del torneo hasta el detalle de disciplina.

- **Propósito**: Obtener una vista completa y detallada de una edición del torneo.
- **Perspectiva**: Por año de celebración del mundial.
- **Resultados**: 7 conjuntos de datos (result sets) en una sola llamada.

### 3.2 Firma del procedimiento

```sql
CALL sp_info_mundial(p_anio, p_grupo, p_seleccion, p_fecha);
````

### 3.3 Parámetros de entrada

| Parámetro     | Tipo           | Requerido | Descripción / Comportamiento con NULL                                         |
| ------------- | -------------- | --------- | ----------------------------------------------------------------------------- |
| `p_anio`      | `SMALLINT`     | REQUERIDO | Año de celebración del mundial. Es el único parámetro obligatorio.            |
| `p_grupo`     | `VARCHAR(5)`   | OPCIONAL  | Letra del grupo a filtrar (A, B, C…). Se convierte a mayúsculas internamente. |
| `p_seleccion` | `VARCHAR(100)` | OPCIONAL  | Nombre parcial de la selección. Usa búsqueda `LIKE %valor%`.                  |
| `p_fecha`     | `DATE`         | OPCIONAL  | Fecha exacta de partido en formato `YYYY-MM-DD`.                              |

**AVISO**: Si `p_anio` no coincide con ningún mundial registrado, el procedimiento retorna un único result set con un mensaje de advertencia y no ejecuta las consultas restantes.

### 3.4 Conjuntos de resultados

| Sección                     | Descripción                                                                                                      | Filtros activos                     |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| **Ficha General**        | Año, sede, campeón, selecciones participantes, total de partidos, goles y promedio de goles por partido.         | Ninguno                             |
|  **Tabla de Grupos**      | Posición de cada selección dentro de su grupo con PJ, PG, PE, PP, GF, GC, Dif, Pts e indicador de clasificación. | `p_grupo`, `p_seleccion`            |
| **Partidos y Resultados** | Listado de partidos con fecha, etapa, marcador, ganador y detalle de cada gol (jugador, minuto, tipo).           | `p_grupo`, `p_seleccion`, `p_fecha` |
| **Posiciones Finales**   | Clasificación general de todas las selecciones al cierre del torneo con estadísticas completas.                  | `p_seleccion`                       |
| **Goleadores Top 10**    | Mejores anotadores con posición en el ranking, goles, partidos disputados y promedio por partido.                | `p_seleccion`                       |
| **Premios**              | Premios individuales y colectivos del torneo (Balón de Oro, Bota de Oro, Guante de Oro, etc.).                   | Ninguno                             |
| **Disciplina Top 10**    | Jugadores con más tarjetas; separadas por amarillas, rojas directas y rojas por doble amarilla.                  | `p_seleccion`                       |



### 3.5 Lógica interna destacada

* **Resolución del `id_mundial`**: Al inicio, el SP realiza un `SELECT … INTO` sobre la tabla `mundiales` con el filtro `anio = p_anio`. Si el valor retornado es `NULL`, se produce un mensaje de advertencia y no se ejecuta el bloque `ELSE`.
* **Filtro de grupo en partidos**: El parámetro `p_grupo` compara la columna `etapa` con los patrones '%Grupo X%' y '%Group X%' (español e inglés), garantizando compatibilidad con datos de distintas fuentes.
* **Detalle de goles con `GROUP_CONCAT`**: Se usa `GROUP_CONCAT(… ORDER BY pg.minuto SEPARATOR ' | ')` para consolidar en una sola celda todos los goles del partido, incluyendo nombre del anotador, minuto y tipo (P para penal y AG para autogol).
* **Determinación del ganador**: La columna `Resultado` usa una expresión `CASE` sobre `goles_local` vs `goles_visitante` para retornar el nombre de la selección ganadora o la cadena 'Empate'.

### 3.6 Ejemplos de uso

* Consulta completa del mundial:

  ```sql
  CALL sp_info_mundial(2014, NULL, NULL, NULL);
  ```

* Solo el Grupo A de un mundial:

  ```sql
  CALL sp_info_mundial(2018, 'A', NULL, NULL);
  ```

* Partidos de una selección:

  ```sql
  CALL sp_info_mundial(2022, NULL, 'Argentina', NULL);
  ```

* Partidos de una fecha específica:

  ```sql
  CALL sp_info_mundial(2014, NULL, NULL, '2014-07-13');
  ```

* Combinación de grupo y selección:

  ```sql
  CALL sp_info_mundial(2010, 'B', 'España', NULL);
  ```

---

## 4. Procedimiento: `sp_info_pais`

### 4.1 Descripción general

Consulta el historial completo de una selección nacional a lo largo de todos los mundiales en que participó. Acepta búsqueda parcial por nombre: escribir 'Méx' es suficiente para encontrar 'México'.

* **Propósito**: Obtener toda la trayectoria histórica de un país en los mundiales.
* **Perspectiva**: Por selección nacional (una o todas las ediciones).
* **Resultados**: 10 conjuntos de datos en una sola llamada.

### 4.2 Firma del procedimiento

```sql
CALL sp_info_pais(p_seleccion, p_anio, p_solo_fase);
```

### 4.3 Parámetros de entrada

| Parámetro     | Tipo           | Requerido | Descripción / Comportamiento con NULL                                                                            |
| ------------- | -------------- | --------- | ---------------------------------------------------------------------------------------------------------------- |
| `p_seleccion` | `VARCHAR(100)` | REQUERIDO | Nombre completo o parcial del país. Búsqueda `LIKE %valor%`, no distingue mayúsculas.                            |
| `p_anio`      | `SMALLINT`     | OPCIONAL  | Año del mundial a consultar. Aplica el filtro a todos los result sets.                                           |
| `p_solo_fase` | `VARCHAR(100)` | OPCIONAL  | Texto parcial del nombre de la etapa: 'Final', 'Grupo', 'Semifinal', etc. Solo afecta el result set de partidos. |

**AVISO**: La búsqueda parcial toma la primera coincidencia en orden alfabético. Se recomienda usar nombres lo suficientemente específicos para evitar ambigüedad.

### 4.4 Conjuntos de resultados

| Sección                         | Descripción                                                                                                    | Filtros activos         |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------- | ----------------------- |
| **Ficha Histórica Global**   | Mundiales jugados, veces campeón/subcampeón, totales PJ/PG/PE/PP/GF/GC y % de efectividad.                     | Ninguno                 |
| **Participaciones por Año**  | Por cada edición: posición final, fase alcanzada, estadísticas del torneo, y distinción si fue sede o campeón. | `p_anio`                |
| **Mundiales como Sede**     | Ediciones en que el país fue organizador: campeón de esa edición, partidos totales, goles y promedio.          | `p_anio`                |
| **Fase de Grupos**           | Posición en la tabla de cada grupo con PJ/PG/PE/PP/GF/GC/Dif/Pts e indicador de clasificación.                 | `p_anio`                |
| **Partidos y Resultados**     | Todos los partidos con resultado desde la perspectiva del país (Victoria/Empate/Derrota) y detalle de goles.   | `p_anio`, `p_solo_fase` |
| **Títulos y Subcampeonatos** | Lista de mundiales en que fue campeón o subcampeón.                                                            | `p_anio`                |
| **Goleadores del País**      | Jugadores que aparecen en el ranking oficial de goleadores de cada edición.                                    | `p_anio`                |
| **Premios**                 | Premios individuales o colectivos obtenidos por la selección o sus jugadores.                                  | `p_anio`                |
| **Disciplina**               | Tarjetas amarillas y rojas de jugadores, ordenadas por gravedad descendente.                                   | `p_anio`                |
| **Resumen por Mundial**      | Cuadro consolidado por edición: partidos totales, victorias, empates, derrotas, goles a favor y en contra.     | `p_anio`                |

### 4.5 Lógica interna destacada

* **Búsqueda parcial del país**: El SP usa `LIKE CONCAT('%', p_seleccion, '%')` con `ORDER BY nombre LIMIT 1` para resolver el país.
* **Resultado desde la perspectiva del país**: La columna `Resultado` evalúa `p.id_local` vs `v_id_seleccion` para saber si el país jugó como local o visitante.
* **Cálculo del % de efectividad**: Se usa `NULLIF` para proteger la operación de división por cero.

### 4.6 Ejemplos de uso

* **Historial completo**:

  ```sql
  CALL sp_info_pais('Brasil', NULL, NULL);
  ```

* **Un mundial específico**:

  ```sql
  CALL sp_info_pais('Argentina', 2022, NULL);
  ```

* **Solo finales**:

  ```sql
  CALL sp_info_pais('Alemania', NULL, 'Final');
  ```

* **Solo fase de grupos**:

  ```sql
  CALL sp_info_pais('Uruguay', NULL, 'Grupo');
  ```

* **Búsqueda parcial**:

  ```sql
  CALL sp_info_pais('Méx', NULL, NULL);
  ```

* **País + edición + fase**:

  ```sql
  CALL sp_info_pais('Francia', 1998, 'Semifinal');
  ```

## 5. Comportamiento ante Errores y Casos Especiales

| Situación                                   | Comportamiento                         | Mensaje / Efecto                                |
| ------------------------------------------- | -------------------------------------- | ----------------------------------------------- |
| **Mundial no encontrado (sp_info_mundial)** | Retorna 1 result set con aviso         | No se encontró información para el Mundial YYYY |
| **País no encontrado (sp_info_pais)**       | Retorna 1 result set con aviso         | No se encontró ningún país que coincida con …   |
| **País sin sede registrada**                | 0 filas en sección 3 de `sp_info_pais` | Sección vacía, sin error de ejecución           |
| **País sin títulos**                        | 0 filas en sección 6 de `sp_info_pais` | Sección vacía, sin error de ejecución           |
| **Partido sin goles registrados**           | `GROUP_CONCAT` retorna NULL            | Columna 'Goles detalle' aparece vacía           |
| **División por cero en efectividad**        | `NULLIF` protege la operación          | Retorna NULL en lugar de lanzar error           |
| **Búsqueda de país ambigua**                | Se toma la 1 coincidencia alfabética  | Usar nombre más específico para precisión       |

algunos casos **puntuales** son por ejemplo:
 el mundial de **1950** en el cual no se realizó una final sino que hubo una fase preliminar donde los 13 participantes se dividían en cuatro grupos para enfrentarse todos contra todos en una vez. Los ganadores de cada grupo (Brasil, España, Suecia y Uruguay) pasaban después a una liguilla de cuatro bajo el mismo sistema, de la que saldría el campeón además de los mundiales de **2002** y **2026** que tienen como sede a varios países. 
## 6. Referencia Rápida de Llamadas

### 6.1 `sp_info_mundial`

* **Todo el mundial**:

  ```sql
  CALL sp_info_mundial(2014, NULL, NULL, NULL);
  ```

* **Solo un grupo**:

  ```sql
  CALL sp_info_mundial(2018, 'B', NULL, NULL);
  ```

* **Partidos de una selección**:

  ```sql
  CALL sp_info_mundial(2022, NULL, 'Argentina', NULL);
  ```

* **Partidos de una fecha**:

  ```sql
  CALL sp_info_mundial(2014, NULL, NULL, '2014-07-13');
  ```

* **Grupo + selección**:

  ```sql
  CALL sp_info_mundial(2010, 'A', 'España', NULL);
  ```

* **Selección + fecha**:

  ```sql
  CALL sp_info_mundial(2018, NULL, 'Francia', '2018-07-15');
  ```

### 6.2 `sp_info_pais`

* **Historial completo**:

  ```sql
  CALL sp_info_pais('Brasil', NULL, NULL);
  ```

* **Un mundial específico**:

  ```sql
  CALL sp_info_pais('Argentina', 2022, NULL);
  ```

* **Solo finales**:

  ```sql
  CALL sp_info_pais('Alemania', NULL, 'Final');
  ```

* **Solo fase de grupos**:

  ```sql
  CALL sp_info_pais('Uruguay', NULL, 'Grupo');
  ```

* **Búsqueda parcial**:

  ```sql
  CALL sp_info_pais('Méx', NULL, NULL);
  ```

* **País + edición + fase**:

  ```sql
  CALL sp_info_pais('Francia', 1998, 'Semifinal');
  ```

## 7. Requisitos e Instalación

### 7.1 Requisitos previos

* **Motor**: MySQL 8.0 o superior
* **Base de datos**: mundiales con esquema y datos ya cargados
* **Privilegios**: `CREATE ROUTINE` y `EXECUTE` sobre la base de datos mundiales

### 7.2 Pasos de instalación

1. **Seleccionar la base de datos**:

   ```sql
   USE mundiales;
   ```

2. **Instalar el procedimiento de mundiales**:

   ```sql
   SOURCE sp_info_mundial.sql;
   ```

3. **Instalar el procedimiento de países**:

   ```sql
   SOURCE sp_info_pais.sql;
   ```

4. **Verificar la instalación**:

   ```sql
   SHOW PROCEDURE STATUS WHERE Db = 'mundiales';
   ```

### 7.3 Desinstalación

```sql
DROP PROCEDURE IF EXISTS sp_info_mundial;
DROP PROCEDURE IF EXISTS sp_info_pais;
```


