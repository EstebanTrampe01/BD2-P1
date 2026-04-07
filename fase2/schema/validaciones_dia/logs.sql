USE mundiales;

-- Ultimos eventos en bitacora de ejecucion
SELECT id_log, fecha_evento, dia_carga, evento, detalle
FROM log_ejecucion
ORDER BY id_log DESC
LIMIT 15;
