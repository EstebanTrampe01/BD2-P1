USE mundiales;

-- Dia 1: simular resultados de partidos del 2026
-- 14 partidos con resultados completos

START TRANSACTION;

SET @dia := 1;

INSERT INTO log_ejecucion (dia_carga, evento, detalle)
VALUES (@dia, 'INICIO_CAMBIOS', 'Dia 1 - Simulacion de resultados en partidos 2026');

DROP TEMPORARY TABLE IF EXISTS tmp_day1_before;
CREATE TEMPORARY TABLE tmp_day1_before AS
SELECT
    p.id_partido,
    p.numero_partido,
    p.goles_local AS goles_local_before,
    p.goles_visitante AS goles_visitante_before
FROM partidos p
JOIN mundiales m ON m.id_mundial = p.id_mundial
WHERE m.anio = 2026
  AND p.numero_partido IN (1, 4, 5, 7, 8, 9, 10, 11, 13, 14);

UPDATE partidos p
JOIN mundiales m ON m.id_mundial = p.id_mundial
SET
    goles_local = CASE p.numero_partido
        WHEN 1 THEN 2
        WHEN 4 THEN 1
        WHEN 5 THEN 3
        WHEN 7 THEN 0
        WHEN 8 THEN 2
        WHEN 9 THEN 4
        WHEN 10 THEN 1
        WHEN 11 THEN 2
        WHEN 13 THEN 2
        WHEN 14 THEN 1
        ELSE goles_local
    END,
    goles_visitante = CASE p.numero_partido
        WHEN 1 THEN 1
        WHEN 4 THEN 1
        WHEN 5 THEN 0
        WHEN 7 THEN 2
        WHEN 8 THEN 2
        WHEN 9 THEN 1
        WHEN 10 THEN 1
        WHEN 11 THEN 3
        WHEN 13 THEN 0
        WHEN 14 THEN 2
        ELSE goles_visitante
    END
WHERE m.anio = 2026
  AND p.numero_partido IN (1, 4, 5, 7, 8, 9, 10, 11, 13, 14);

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
JOIN tmp_day1_before b ON b.id_partido = p.id_partido;

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
VALUES (@dia, 'FIN_CAMBIOS', 'Dia 1 aplicado correctamente');

COMMIT;