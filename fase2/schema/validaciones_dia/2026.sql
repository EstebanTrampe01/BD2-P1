Use mundiales;

-- Conteo de partidos 2026 ya simulados con ambos goles

SELECT
    m.anio,
    COUNT(*) AS partidos_2026_total,
    SUM(CASE WHEN p.goles_local IS NOT NULL AND p.goles_visitante IS NOT NULL THEN 1 ELSE 0 END) AS partidos_con_marcador
FROM partidos p
JOIN mundiales m ON m.id_mundial = p.id_mundial
WHERE m.anio = 2026
GROUP BY m.anio;