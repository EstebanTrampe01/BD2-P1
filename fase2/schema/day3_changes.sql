USE mundiales;

-- Dia 3: convertir nombres de paises a MAYUSCULAS
START TRANSACTION;

SET @dia := 3;

INSERT INTO log_ejecucion (dia_carga, evento, detalle)
VALUES (@dia, 'INICIO_CAMBIOS', 'Dia 3 - Actualizacion de nombres de selecciones a MAYUSCULAS');

DROP TEMPORARY TABLE IF EXISTS tmp_day3_before;
CREATE TEMPORARY TABLE tmp_day3_before AS
SELECT
    id_seleccion,
    nombre AS nombre_before
FROM selecciones
WHERE nombre IS NOT NULL
  AND nombre <> UPPER(nombre);

UPDATE selecciones
SET nombre = UPPER(nombre)
WHERE nombre IS NOT NULL
  AND nombre <> UPPER(nombre);

INSERT INTO log_selecciones (dia_carga, operacion, id_entidad, detalle_antes, detalle_despues)
SELECT
    @dia,
    'UPDATE',
    CAST(s.id_seleccion AS CHAR),
    JSON_OBJECT('nombre', b.nombre_before),
    JSON_OBJECT('nombre', s.nombre)
FROM selecciones s
JOIN tmp_day3_before b ON b.id_seleccion = s.id_seleccion;

INSERT INTO log_fragmentacion (dia_carga, tabla, engine, table_rows, data_length, index_length, data_free)
SELECT
    @dia,
    table_name,
    engine,
    table_rows,
    data_length,
    index_length,
    data_free
FROM information_schema.tables
WHERE table_schema = 'mundiales'
  AND table_name IN ('selecciones', 'partidos', 'grupos', 'posiciones_finales');

INSERT INTO log_ejecucion (dia_carga, evento, detalle)
VALUES (@dia, 'FIN_CAMBIOS', 'Dia 3 aplicado correctamente');

COMMIT;

SELECT id_seleccion, nombre
FROM selecciones
ORDER BY id_seleccion
LIMIT 20;
