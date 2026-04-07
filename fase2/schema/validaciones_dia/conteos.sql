USE mundiales;

-- Validacion general de SELECT COUNT(*) por cada tabla

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
