USE mundiales;

-- Validacion general posterior a cada dia

SELECT 'selecciones' AS tabla, COUNT(*) AS total FROM selecciones
UNION ALL SELECT 'mundiales', COUNT(*) FROM mundiales
UNION ALL SELECT 'jugadores', COUNT(*) FROM jugadores
UNION ALL SELECT 'partidos', COUNT(*) FROM partidos
UNION ALL SELECT 'grupos', COUNT(*) FROM grupos
UNION ALL SELECT 'posiciones_finales', COUNT(*) FROM posiciones_finales
UNION ALL SELECT 'goleadores', COUNT(*) FROM goleadores
UNION ALL SELECT 'premios', COUNT(*) FROM premios
UNION ALL SELECT 'tarjetas', COUNT(*) FROM tarjetas
UNION ALL SELECT 'jugadores_por_mundial', COUNT(*) FROM jugadores_por_mundial
UNION ALL SELECT 'planteles', COUNT(*) FROM planteles
UNION ALL SELECT 'partido_jugadores', COUNT(*) FROM partido_jugadores
UNION ALL SELECT 'partido_goles', COUNT(*) FROM partido_goles;

-- Conteo de partidos 2026 ya simulados (con ambos goles no nulos)
SELECT
    m.anio,
    COUNT(*) AS partidos_2026_total,
    SUM(CASE WHEN p.goles_local IS NOT NULL AND p.goles_visitante IS NOT NULL THEN 1 ELSE 0 END) AS partidos_con_marcador
FROM partidos p
JOIN mundiales m ON m.id_mundial = p.id_mundial
WHERE m.anio = 2026
GROUP BY m.anio;

-- Muestra de partidos actualizados
SELECT
    p.id_partido,
    p.numero_partido,
    p.fecha,
    sl.nombre AS local,
    p.goles_local,
    p.goles_visitante,
    sv.nombre AS visitante
FROM partidos p
LEFT JOIN selecciones sl ON sl.id_seleccion = p.id_local
LEFT JOIN selecciones sv ON sv.id_seleccion = p.id_visitante
JOIN mundiales m ON m.id_mundial = p.id_mundial
WHERE m.anio = 2026
  AND p.numero_partido IN (1,4,5,7,8,9,10,11,13,14,15,16,17,19,20,21,22,24,27,28)
ORDER BY p.id_partido;

-- Ultimos eventos en bitacora de ejecucion
SELECT id_log, fecha_evento, dia_carga, evento, detalle
FROM log_ejecucion
ORDER BY id_log DESC
LIMIT 15;
