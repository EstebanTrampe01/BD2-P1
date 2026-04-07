USE mundiales;

-- Validacion de integridad referencial despues de restaurar

SELECT 'fk_nulas_criticas' AS check_name,
       (
           (SELECT COUNT(*) FROM grupos WHERE id_mundial IS NULL OR id_seleccion IS NULL) +
           (SELECT COUNT(*) FROM posiciones_finales WHERE id_mundial IS NULL OR id_seleccion IS NULL) +
           (SELECT COUNT(*) FROM goleadores WHERE id_mundial IS NULL OR id_jugador IS NULL) +
           (SELECT COUNT(*) FROM tarjetas WHERE id_mundial IS NULL OR id_jugador IS NULL) +
           (SELECT COUNT(*) FROM jugadores_por_mundial WHERE id_mundial IS NULL OR id_jugador IS NULL) +
           (SELECT COUNT(*) FROM planteles WHERE id_mundial IS NULL OR id_seleccion IS NULL OR id_jugador IS NULL) +
           (SELECT COUNT(*) FROM partido_jugadores WHERE id_partido IS NULL OR id_jugador IS NULL) +
           (SELECT COUNT(*) FROM partido_goles WHERE id_partido IS NULL OR id_mundial IS NULL)
       ) AS issues;

SELECT 'huerfanos_criticos' AS check_name,
       (
           (SELECT COUNT(*) FROM partido_jugadores pj LEFT JOIN partidos p ON p.id_partido = pj.id_partido WHERE p.id_partido IS NULL) +
           (SELECT COUNT(*) FROM partido_jugadores pj LEFT JOIN jugadores j ON j.id_jugador = pj.id_jugador WHERE j.id_jugador IS NULL) +
           (SELECT COUNT(*) FROM partido_goles pg LEFT JOIN partidos p ON p.id_partido = pg.id_partido WHERE p.id_partido IS NULL) +
           (SELECT COUNT(*) FROM partido_goles pg LEFT JOIN jugadores j ON j.id_jugador = pg.id_jugador WHERE pg.id_jugador IS NOT NULL AND j.id_jugador IS NULL)
       ) AS issues;
