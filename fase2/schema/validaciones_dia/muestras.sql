USE mundiales;

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