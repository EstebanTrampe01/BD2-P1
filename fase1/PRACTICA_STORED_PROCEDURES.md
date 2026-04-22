# Guía práctica: Stored Procedures en MySQL

## ¿Qué es un Stored Procedure (SP)?
Un **Stored Procedure** es un programa SQL guardado en la base de datos que:
- Ejecuta múltiples consultas en una sola llamada.
- Mejora rendimiento (no necesita enviar código desde la aplicación).
- Encapsula lógica compleja en la BD.
- Facilita reutilización.

En este proyecto hay **2 SPs**:

### 1. **sp_info_mundial** — Información de un Mundial
- Devuelve ficha del mundial, tabla de grupos, partidos, posiciones finales y goleadores.
- **Parámetros**: año (obligatorio), grupo (opcional), selección (opcional), fecha (opcional).

### 2. **sp_info_pais** — Carrera histórica de un país
- Devuelve estadísticas generales, posiciones finales, fase de grupos y todos sus partidos.
- **Parámetros**: país (obligatorio), año (opcional), solo_fase (opcional).

---

## Paso 1: Crear los SPs en MySQL

Desde `fase1/`, conéctate a MySQL y ejecuta los archivos:

```bash
mysql -h 127.0.0.1 -u mundiales_user -p mundiales < stored/sp1.sql
mysql -h 127.0.0.1 -u mundiales_user -p mundiales < stored/sp2.sql
```

O directamente en MySQL CLI:

```sql
USE mundiales;
SOURCE stored/sp1.sql;
SOURCE stored/sp2.sql;
```

Valida creación:

```sql
SHOW PROCEDURE STATUS WHERE Db = 'mundiales';
```

Deberías ver `sp_info_mundial` y `sp_info_pais`.

---

## Paso 2: Llamar un SP — Sintaxis básica

```sql
CALL sp_info_mundial (2022, NULL, NULL, NULL);
CALL sp_info_pais ('Brasil', NULL, NULL);
```

---

## Paso 3: Ejemplos prácticos por caso de uso

### **CASO 1: Consultando sp_info_mundial**

#### A) Ficha completa del Mundial 2022
```sql
CALL sp_info_mundial(2022, NULL, NULL, NULL);
```
**Qué devuelve:**
- Resumen: sede, campeón, selecciones, partidos, goles.
- Tabla de grupos (todos).
- Todos los partidos.
- Posiciones finales.
- Top goleadores.

#### B) Solo el Grupo A del 2022
```sql
CALL sp_info_mundial(2022, 'A', NULL, NULL);
```
**Qué devuelve:**
- Resumen del mundial.
- Tabla de grupos (solo grupo A).
- Partidos del grupo A.
- Posiciones finales.
- Goleadores.

#### C) Partidos de Argentina en el 2022
```sql
CALL sp_info_mundial(2022, NULL, 'Argentina', NULL);
```
**Qué devuelve:**
- Resumen del mundial.
- Tabla de grupos donde juega Argentina.
- Todos los paridos donde participa Argentina.
- Posiciones finales.
- Goleadores de Argentina.

#### D) Partidos de una fecha específica del 2022
```sql
CALL sp_info_mundial(2022, NULL, NULL, '2022-11-21');
```
**Qué devuelve:**
- Resumen del mundial.
- Tabla de grupos.
- Partidos del 21-11-2022.
- Posiciones finales.
- Goleadores.

#### E) Combinado: Grupo A + Selecciones que comiencen con 'A'
```sql
CALL sp_info_mundial(2022, 'A', 'A', NULL);
```
**Qué devuelve:**
- Todos los datos, pero filtrados por grupo A y selecciones como 'Argentina', 'Australia', etc.

---

### **CASO 2: Consultando sp_info_pais**

#### A) Carrera histórica de Brasil (todos los mundiales)
```sql
CALL sp_info_pais('Brasil', NULL, NULL);
```
**Qué devuelve:**
- Ficha histórica: mundiales jugados, campeones, subcampeones, estadísticas totales.
- Tabla: años en que participó, posición final en cada uno.
- Mundiales organizados por Brasil.
- Desempeño en fase de grupos por año.
- Todos los partidos jugados en toda su historia.

#### B) Solo el desempeño de Brasil en 2002
```sql
CALL sp_info_pais('Brasil', 2002, NULL);
```
**Qué devuelve:**
- Ficha histórica (global, no filtrada).
- Mundiales 2002 (posición final en ese año).
- Mundiales como sede.
- Fase de grupos en 2002.
- Todos los partidos de Brasil en 2002.

#### C) Solo los partidos de Francia en Finales
```sql
CALL sp_info_pais('Francia', NULL, 'Final');
```
**Qué devuelve:**
- Ficha histórica de Francia.
- Todos sus mundiales.
- Mundiales como sede.
- Fase de grupos.
- Solo partidos de Francia clasificados como "Final" (ej: Final, Semifinal).

#### D) Argentina solo en 1986
```sql
CALL sp_info_pais('Argentina', 1986, NULL);
```
**Qué devuelve:**
- Ficha histórica (global).
- Participación de Argentina en 1986 (posición final).
- Mundiales como sede (si aplica).
- Fase de grupos en 1986.
- Partidos de Argentina en 1986.

#### E) Búsqueda parcial: "Alem"
```sql
CALL sp_info_pais('Alem', NULL, NULL);
```
**Qué devuelve:**
- Todo sobre Alemania (el SP busca con LIKE, así que "Alem" coincide).

---

## Paso 4: Ejercicios propuestos (Lo que probablemente te pidieron)

### Ejercicio 1: Ficha del Mundial 2018
```sql
CALL sp_info_mundial(2018, NULL, NULL, NULL);
```
**Análisis**:
- ¿Cuántas selecciones jugaron?
- ¿Cuántos goles se anotaron en total?
- ¿Quién fue el campeón?
- ¿Quién fue el top goleador?

### Ejercicio 2: Partidos de Bélgica en el 2018
```sql
CALL sp_info_mundial(2018, NULL, 'Bélgica', NULL);
```
**Análisis**:
- ¿En qué grupo estuvo Bélgica?
- ¿Ganó todos sus partidos de grupo?
- ¿Hasta qué fase llegó?

### Ejercicio 3: Carrera histórica completa de Alemania
```sql
CALL sp_info_pais('Alemania', NULL, NULL);
```
**Análisis**:
- ¿Cuántos mundiales jugó?
- ¿Ganó alguna vez? ¿Cuántas?
- ¿Fue subcampeona?
- ¿Organizó algún mundial?
- ¿En qué fase quedó en la mayoría de mundiales?

### Ejercicio 4: Semifinales de Italia (todas las épocas)
```sql
CALL sp_info_pais('Italia', NULL, 'Semifinal');
```
**Análisis**:
- ¿Cuántas veces jugó semifinales?
- ¿Ganó alguna semifinal?

### Ejercicio 5: España en el 2010
```sql
CALL sp_info_pais('España', 2010, NULL);
```
**Análisis**:
- ¿Con qué equipo (grupo) jugó?
- ¿Cuántos partidos jugó?
- ¿Quién fue campeón ese año?

---

## Paso 5: Salida de los SPs

Los SPs devuelven **múltiples result sets** (varias tablas seguidas):

Por ejemplo, `CALL sp_info_mundial(2022, NULL, NULL, NULL)` devuelve:

1. **Tabla 1:** Resumen del mundial
2. **Tabla 2:** Tabla de grupos
3. **Tabla 3:** Partidos y goles
4. **Tabla 4:** Posiciones finales
5. **Tabla 5:** Goleadores

En muchas herramientas (MySQL Workbench, phpMyAdmin, VSCode), verás tabs o secciones para cada resultado.

---

## Paso 6: Capturar salida en variables (si necesitas programar)

Si llamas desde Python o aplicación:

```python
cn.cursor.callproc('sp_info_mundial', (2022, None, None, None))
for result_set in cn.cursor.fetchall():
    print(result_set)
# Avanzar a próximo result set
cn.cursor.nextset()
```

---

## Paso 7: Casos comunes de evaluación

Si te pidieron hacer consultas "sobre los stored procedures", probablemente sea:

1. **Test básico**: Llamar ambos SPs sin parámetros y capturar salida.
2. **Filtros**: Llamar con diferentes parámetros (año, país, grupo).
3. **Validación**: Verificar que la información no tenga inconsistencias.
4. **Análisis**: Responder preguntas como "¿Cuál fue el top goleador de 2014?" usando la salida del SP.

### Ejemplo de lo que pueden pedir:

> "Ejecuta `sp_info_mundial` para el año 2014, filtra solo al grupo D, y di:
> - Tabla de posiciones finales
> - Partidos que se jugaron
> - Goleadores no del grupo D"

---

## Paso 8: Chequeo rápido de integridad

Antes de entregar, valida:

```sql
-- ¿Existen los SPs?
SHOW PROCEDURE STATUS WHERE Db = 'mundiales';

-- ¿Devuelven resultados?
CALL sp_info_mundial(2022, NULL, NULL, NULL);

-- ¿Sin errores?
CALL sp_info_pais('Brasil', NULL, NULL);
```

---

## Resumen rápido de qué hace cada SP

| SP | Entrada | Salida | Uso |
|---|---------|--------|-----|
| `sp_info_mundial` | Año (+ filtros opcionales) | Ficha mundial, grupos, partidos, goleadores | Consultar un mundial específico |
| `sp_info_pais` | País (+ filtros opcionales) | Histórico país, participaciones, partidos | Consultar carrera histórica de un país |

---

## Tips de debugging

Si algo no funciona:

1. **Error "Procedure not found"**: Verificar que ejecutaste `sp1.sql` y `sp2.sql`.
2. **Resultados vacíos**: Verificar que el año o país existe en la BD (`SELECT * FROM mundiales; SELECT * FROM selecciones;`).
3. **Búsqueda de país falla**: El SP usa `LIKE`, así que "Bras" encuentra "Brasil". Intenta con strings cortos.

---

## Conclusión

Los SPs simplifican consultas complejas. Con estos dos, puedes investigar:
- Cualquier mundial en detalle.
- La historia completa de cualquier país.
- Estadísticas de jugadores, goles, fases.

Lo que probablemente te pidieron es **llamarlos con diferentes parámetros y analizar la salida** para responder preguntas sobre mundiales de fútbol.

¡A practicar! 🚀
