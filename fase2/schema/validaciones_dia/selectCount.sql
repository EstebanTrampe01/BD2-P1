USE mundiales;

-- Validacion: SELECT COUNT(*) por cada tabla del esquema

SELECT 'selecciones' AS tabla, COUNT(*) AS total FROM selecciones
UNION ALL SELECT 'mundiales', COUNT(*) FROM mundiales
UNION ALL SELECT 'seleccion_titulos', COUNT(*) FROM seleccion_titulos
UNION ALL SELECT 'jugadores', COUNT(*) FROM jugadores
UNION ALL SELECT 'jugador_camisetas', COUNT(*) FROM jugador_camisetas
UNION ALL SELECT 'partidos', COUNT(*) FROM partidos
UNION ALL SELECT 'grupos', COUNT(*) FROM grupos
UNION ALL SELECT 'posiciones_finales', COUNT(*) FROM posiciones_finales
UNION ALL SELECT 'goleadores', COUNT(*) FROM goleadores
UNION ALL SELECT 'premios', COUNT(*) FROM premios
UNION ALL SELECT 'tarjetas', COUNT(*) FROM tarjetas
UNION ALL SELECT 'jugadores_por_mundial', COUNT(*) FROM jugadores_por_mundial
UNION ALL SELECT 'planteles', COUNT(*) FROM planteles
UNION ALL SELECT 'partido_jugadores', COUNT(*) FROM partido_jugadores
UNION ALL SELECT 'partido_goles', COUNT(*) FROM partido_goles
UNION ALL SELECT 'scraping_runs', COUNT(*) FROM scraping_runs
UNION ALL SELECT 'scraping_metadata', COUNT(*) FROM scraping_metadata
UNION ALL SELECT 'log_ejecucion', COUNT(*) FROM log_ejecucion
UNION ALL SELECT 'log_fragmentacion', COUNT(*) FROM log_fragmentacion
UNION ALL SELECT 'log_mundiales', COUNT(*) FROM log_mundiales
UNION ALL SELECT 'log_selecciones', COUNT(*) FROM log_selecciones
UNION ALL SELECT 'log_jugadores', COUNT(*) FROM log_jugadores
UNION ALL SELECT 'log_seleccion_titulos', COUNT(*) FROM log_seleccion_titulos
UNION ALL SELECT 'log_jugador_camisetas', COUNT(*) FROM log_jugador_camisetas
UNION ALL SELECT 'log_partidos', COUNT(*) FROM log_partidos
UNION ALL SELECT 'log_grupos', COUNT(*) FROM log_grupos
UNION ALL SELECT 'log_posiciones_finales', COUNT(*) FROM log_posiciones_finales
UNION ALL SELECT 'log_goleadores', COUNT(*) FROM log_goleadores
UNION ALL SELECT 'log_premios', COUNT(*) FROM log_premios
UNION ALL SELECT 'log_tarjetas', COUNT(*) FROM log_tarjetas
UNION ALL SELECT 'log_jugadores_por_mundial', COUNT(*) FROM log_jugadores_por_mundial
UNION ALL SELECT 'log_planteles', COUNT(*) FROM log_planteles
UNION ALL SELECT 'log_partido_jugadores', COUNT(*) FROM log_partido_jugadores
UNION ALL SELECT 'log_partido_goles', COUNT(*) FROM log_partido_goles;
