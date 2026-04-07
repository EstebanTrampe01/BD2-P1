USE mundiales;

SELECT
  id_log,
  fecha_evento AS fecha_utc,
  DATE_SUB(fecha_evento, INTERVAL 6 HOUR) AS fecha_local_cst,
  dia_carga,
  evento
FROM log_ejecucion
ORDER BY id_log DESC