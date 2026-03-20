# Mundiales de Fútbol — Guía de instalación y uso

## Estructura del proyecto

```
proyecto_mundiales/
├── docker-compose.yml      ← levanta MySQL
├── cargar_datos.py         ← librería interna (transformación y carga)
├── transformar_output.py   ← transforma output/ -> output_db/
├── cargar_bd.py            ← carga output_db/ -> MySQL
├── init/
│   └── schema.sql          ← schema normalizado (se ejecuta automáticamente)
├── output/                 ← CSVs crudos (scraping)
└── output_db/              ← CSVs limpios listos para la BD
```

---

## Paso 1 — Preparar entorno

1. Estar en la carpeta del proyecto:

    ```bash
    cd proyecto_mundiales
    ```

2. (Opcional) Activar entorno virtual si lo usas:

    ```bash
    source venv/bin/activate
    ```

3. Instalar dependencias Python:

    ```bash
    pip install pandas mysql-connector-python
    ```

> Nota: si tu sistema no tiene el comando `python`, usa `python3` en su lugar.

---

## Paso 2 — Levantar MySQL con Docker

```bash
docker compose up -d
```

Esto levanta MySQL en el puerto 3306 y ejecuta el schema automáticamente.

Esperar unos segundos y verificar que esté listo:

```bash
docker compose ps
# Estado debe ser: healthy
```

---

## Paso 3 — Transformar CSV crudos (output → output_db)

Los CSV originales deben estar en la carpeta `output/` con, al menos:

```
mundiales.csv
selecciones.csv
jugadores.csv
partidos.csv
grupos.csv
posiciones_finales.csv
goleadores.csv
premios.csv
tarjetas.csv
jugadores_por_mundial.csv
planteles.csv
partido_jugadores.csv
partido_goles.csv
```

Para generar los CSV limpios en `output_db/`:

```bash
python transformar_output.py
```

Este paso:

- Construye mapas de IDs (selecciones, jugadores, mundiales, partidos).
- Detecta selecciones históricas usadas en los datos (Yugoslavia, URSS, etc.) y las añade al catálogo para evitar `id_seleccion` en NULL.
- Normaliza URLs de jugadores (absolutas y relativas) para generar `id_jugador` coherentes.
- Limpia fechas, diferencias de gol y valores especiales como `"-"`, tratándolos como `NULL` donde corresponde.
- Filtra filas de planteles sin jugador real (entrenadores sin `url_jugador`).
- Genera todos los CSV finales en `output_db/` y los mapas de referencia `_mapa_*.csv`.

---

## Paso 4 — Cargar los datos en MySQL (output_db → BD)

Una vez generados los CSV en `output_db/`, ejecuta:

```bash
python cargar_bd.py
```

El script:

- Conecta a la base de datos `mundiales` definida en `docker-compose.yml`.
- Desactiva temporalmente `FOREIGN_KEY_CHECKS`, hace `TRUNCATE` de todas las tablas destino y vuelve a activarlos.
- Lee cada CSV de `output_db/` en un orden que respeta las claves foráneas.
- Normaliza valores problemáticos antes de insertarlos (fechas, textos con números, `"nan"`, `"null"`, `"-"`, etc.).
- Inserta todas las filas y muestra el número de registros cargados por tabla.
- Finaliza con el mensaje: `Carga completada en la base de datos.`

---

## Paso 5 — Verificar datos desde MySQL (CLI o DBeaver)

### Credenciales de conexión

| Campo    | Valor           |
|----------|-----------------|
| Host     | 127.0.0.1       |
| Puerto   | 3306            |
| Base     | mundiales       |
| Usuario  | mundiales_user  |
| Password | mundiales1234   |

### Conexión desde la línea de comandos

```bash
docker exec -it mundiales_db mysql -u mundiales_user -pmundiales1234 mundiales
```

Ejemplos de consultas básicas de verificación:

```sql
-- Tablas existentes
SHOW TABLES;

-- Conteos generales
SELECT COUNT(*) FROM selecciones;
SELECT COUNT(*) FROM mundiales;
SELECT COUNT(*) FROM jugadores;
SELECT COUNT(*) FROM partidos;

-- Comprobar que no hay claves foráneas nulas en tablas importantes
SELECT COUNT(*) FROM grupos WHERE id_seleccion IS NULL OR id_mundial IS NULL;
SELECT COUNT(*) FROM posiciones_finales WHERE id_seleccion IS NULL OR id_mundial IS NULL;
SELECT COUNT(*) FROM goleadores WHERE id_jugador IS NULL OR id_mundial IS NULL;
SELECT COUNT(*) FROM planteles WHERE id_jugador IS NULL OR id_mundial IS NULL;
```

Ejemplos de consultas de consistencia de negocio:

```sql
-- Top 10 goleadores históricos
SELECT j.nombre, g.goles, m.anio
FROM goleadores g
JOIN jugadores j  ON g.id_jugador = j.id_jugador
JOIN mundiales m  ON g.id_mundial = m.id_mundial
ORDER BY g.goles DESC
LIMIT 10;

-- Selecciones con más participaciones en mundiales
SELECT s.nombre, s.mundiales_jugados
FROM selecciones s
ORDER BY CAST(s.mundiales_jugados AS UNSIGNED) DESC
LIMIT 10;
```

---

## Conexión desde DBeaver

1. Abrir DBeaver y crear nueva conexión → elegir **MySQL**.
2. Rellenar los campos con las credenciales:
    - Host: `127.0.0.1`
    - Port: `3306`
    - Database: `mundiales`
    - User: `mundiales_user`
    - Password: `mundiales1234`
3. Probar conexión (**Test Connection**) y guardar.
4. En el panel izquierdo aparecerá la conexión; expandir **Schemas → mundiales** para ver las tablas.
5. Para consultar:
    - Clic derecho en la conexión → **SQL Editor → New SQL Script**.
    - Ejecutar las mismas consultas de verificación que arriba para revisar conteos y consistencia.

---

## Detener el contenedor

```bash
docker compose down
```

Para borrar también los datos:

```bash
docker compose down -v
```
