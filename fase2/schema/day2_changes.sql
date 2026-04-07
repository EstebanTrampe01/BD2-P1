USE mundiales;

-- Dia 2: segunda simulacion de resultados (2026)
START TRANSACTION;

SET @dia := 2;

INSERT INTO log_ejecucion (dia_carga, evento, detalle)
VALUES (@dia, 'INICIO_CAMBIOS', 'Dia 2 - Simulacion adicional de resultados en partidos 2026');

DROP TEMPORARY TABLE IF EXISTS tmp_day2_before;
CREATE TEMPORARY TABLE tmp_day2_before AS
SELECT
    p.id_partido,
    p.numero_partido,
    p.goles_local AS goles_local_before,
    p.goles_visitante AS goles_visitante_before
FROM partidos p
JOIN mundiales m ON m.id_mundial = p.id_mundial
WHERE m.anio = 2026
  AND p.numero_partido IN (15, 16, 17, 19, 20, 21, 22, 24, 27, 28);

UPDATE partidos p
JOIN mundiales m ON m.id_mundial = p.id_mundial
SET
    goles_local = CASE p.numero_partido
        WHEN 15 THEN 1
        WHEN 16 THEN 0
        WHEN 17 THEN 2
        WHEN 19 THEN 3
        WHEN 20 THEN 1
        WHEN 21 THEN 2
        WHEN 22 THEN 2
        WHEN 24 THEN 1
        WHEN 27 THEN 0
        WHEN 28 THEN 1
        ELSE goles_local
    END,
    goles_visitante = CASE p.numero_partido
        WHEN 15 THEN 1
        WHEN 16 THEN 1
        WHEN 17 THEN 2
        WHEN 19 THEN 1
        WHEN 20 THEN 0
        WHEN 21 THEN 2
        WHEN 22 THEN 0
        WHEN 24 THEN 1
        WHEN 27 THEN 0
        WHEN 28 THEN 2
        ELSE goles_visitante
    END
WHERE m.anio = 2026
  AND p.numero_partido IN (15, 16, 17, 19, 20, 21, 22, 24, 27, 28);

INSERT INTO log_partidos (dia_carga, operacion, id_entidad, detalle_antes, detalle_despues)
SELECT
    @dia,
    'UPDATE',
    CAST(p.id_partido AS CHAR),
    JSON_OBJECT(
        'goles_local', b.goles_local_before,
        'goles_visitante', b.goles_visitante_before
    ),
    JSON_OBJECT(
        'goles_local', p.goles_local,
        'goles_visitante', p.goles_visitante
    )
FROM partidos p
JOIN tmp_day2_before b ON b.id_partido = p.id_partido;

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
  AND table_name IN ('partidos', 'partido_jugadores', 'partido_goles', 'selecciones');

INSERT INTO log_ejecucion (dia_carga, evento, detalle)
VALUES (@dia, 'FIN_CAMBIOS', 'Dia 2 aplicado correctamente');

COMMIT;

SELECT p.id_partido, p.numero_partido, p.goles_local, p.goles_visitante
FROM partidos p
JOIN mundiales m ON m.id_mundial = p.id_mundial
WHERE m.anio = 2026
  AND p.numero_partido IN (15, 16, 17, 19, 20, 21, 22, 24, 27, 28)
ORDER BY p.id_partido;
