USE mundiales;

-- Validacion de muestra: solo tablas que cambian en los 3 dias
-- Dia 1 y 2: partidos
-- Dia 3: selecciones
-- Adicional: tablas LOG relacionadas

SELECT 'partidos_2026' AS tabla;
SELECT
    p.id_partido,
    p.numero_partido,
    p.goles_local,
    p.goles_visitante,
    p.fecha
FROM partidos p
JOIN mundiales m ON m.id_mundial = p.id_mundial
WHERE m.anio = 2026
ORDER BY p.numero_partido
LIMIT 20;

SELECT 'selecciones' AS tabla;
SELECT id_seleccion, nombre
FROM selecciones
ORDER BY id_seleccion
LIMIT 20;

SELECT 'log_ejecucion' AS tabla;
SELECT id_log, fecha_evento, dia_carga, evento, detalle
FROM log_ejecucion
ORDER BY id_log DESC
LIMIT 20;

SELECT 'log_fragmentacion' AS tabla;
SELECT id_log, fecha_evento, dia_carga, tabla, table_rows, data_length, index_length, data_free
FROM log_fragmentacion
ORDER BY id_log DESC
LIMIT 20;

SELECT 'log_partidos' AS tabla;
SELECT id_log, fecha_evento, dia_carga, operacion, id_entidad, detalle_antes, detalle_despues
FROM log_partidos
ORDER BY id_log DESC
LIMIT 20;

SELECT 'log_selecciones' AS tabla;
SELECT id_log, fecha_evento, dia_carga, operacion, id_entidad, detalle_antes, detalle_despues
FROM log_selecciones
ORDER BY id_log DESC
LIMIT 20;
