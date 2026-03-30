-- =============================================================================
-- Parámetros:
--   p_anio        SMALLINT  REQUIRED  Año del mundial  
--   p_grupo       VARCHAR   OPTIONAL  Letra del grupo  ej. 'A', 'B' …
--                                     NULL = todos los grupos
--   p_seleccion   VARCHAR   OPTIONAL  Nombre  de la selección
--                                     NULL = todas las selecciones
--   p_fecha       DATE      OPTIONAL  Fecha exacta de partido YYYY-MM-DD
--                                     NULL = todas las fechas
-- =============================================================================

USE mundiales;

DROP PROCEDURE IF EXISTS sp_info_mundial;

DELIMITER $$

CREATE PROCEDURE sp_info_mundial (
    IN p_anio       SMALLINT,
    IN p_grupo      VARCHAR(5),
    IN p_seleccion  VARCHAR(100),
    IN p_fecha      DATE
)
BEGIN

    /* ── Variables auxiliares ─────────────────────────────────────────────── */
    DECLARE v_id_mundial    INT UNSIGNED DEFAULT NULL;
    DECLARE v_campeon       VARCHAR(100) DEFAULT 'N/D';
    DECLARE v_organizador   VARCHAR(100) DEFAULT 'N/D';
    DECLARE v_selecciones   SMALLINT UNSIGNED DEFAULT 0;
    DECLARE v_partidos_tot  SMALLINT UNSIGNED DEFAULT 0;
    DECLARE v_goles_tot     SMALLINT UNSIGNED DEFAULT 0;
    DECLARE v_prom_gol      DECIMAL(4,2)      DEFAULT 0.00;

    /* ── 1. Obtener id_mundial ─────────────────────────────────────────────── */
    SELECT  m.id_mundial,
            COALESCE(sc.nombre, 'N/D'),
            COALESCE(so.nombre, 'N/D'),
            m.selecciones_participan,
            m.partidos,
            m.goles,
            m.promedio_gol
    INTO    v_id_mundial,
            v_campeon,
            v_organizador,
            v_selecciones,
            v_partidos_tot,
            v_goles_tot,
            v_prom_gol
    FROM    mundiales       m
    LEFT JOIN selecciones   sc ON sc.id_seleccion = m.id_campeon
    LEFT JOIN selecciones   so ON so.id_seleccion = m.id_organizador
    WHERE   m.anio = p_anio
    LIMIT 1;

    /* ── Validación ───────────────────────────────────────────────────────── */
    IF v_id_mundial IS NULL THEN
        SELECT CONCAT('No se encontró información para el Mundial ', p_anio,
                      '. Verifique el año ingresado.') AS mensaje;
    ELSE

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 1 — FICHA GENERAL DEL MUNDIAL
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        p_anio                          AS `MUNDIAL`,
        v_organizador                   AS `Sede/Organizador`,
        v_campeon                       AS `Campeón`,
        v_selecciones                   AS `Selecciones participantes`,
        v_partidos_tot                  AS `Total de partidos`,
        v_goles_tot                     AS `Total de goles`,
        v_prom_gol                      AS `Promedio de goles por partido`;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 2 — TABLA DE GRUPOS
       Filtros activos: p_grupo, p_seleccion
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        g.grupo                         AS `Grupo`,
        g.posicion                      AS `Pos.`,
        s.nombre                        AS `Selección`,
        g.pj                            AS `PJ`,
        g.pg                            AS `PG`,
        g.pe                            AS `PE`,
        g.pp                            AS `PP`,
        g.gf                            AS `GF`,
        g.gc                            AS `GC`,
        g.dif                           AS `Dif`,
        g.pts                           AS `Pts`,
        IF(g.clasificado, 'Sí', 'No') AS `Clasificó`
    FROM    grupos      g
    JOIN    selecciones s ON s.id_seleccion = g.id_seleccion
    WHERE   g.id_mundial = v_id_mundial
        AND (p_grupo     IS NULL OR g.grupo       = UPPER(p_grupo))
        AND (p_seleccion IS NULL OR s.nombre LIKE CONCAT('%', p_seleccion, '%'))
    ORDER BY g.grupo, g.posicion;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 3 — PARTIDOS Y RESULTADOS
       Filtros activos: p_grupo, p_seleccion, p_fecha
       Nota: el filtro de grupo aplica sólo a la fase de grupos (etapa LIKE '%Grupo%')
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        p.numero_partido                AS `Nº`,
        p.fecha                         AS `Fecha`,
        p.etapa                         AS `Etapa / Fase`,
        sl.nombre                       AS `Local`,
        p.goles_local                   AS `GL`,
        p.goles_visitante               AS `GV`,
        sv.nombre                       AS `Visitante`,
        CASE
            WHEN p.goles_local  > p.goles_visitante THEN sl.nombre
            WHEN p.goles_local  < p.goles_visitante THEN sv.nombre
            ELSE 'Empate'
        END                             AS `Resultado`,
        -- Goles anotados en el partido (con minuto y tipo)
        GROUP_CONCAT(
            CASE WHEN pg.id_partido IS NOT NULL
                 THEN CONCAT(
                        COALESCE(jg.nombre, '?'), ' ',
                        pg.minuto, '\' ',
                        CASE pg.tipo_gol
                            WHEN 'penal'   THEN '(P)'
                            WHEN 'autogol' THEN '(AG)'
                            ELSE ''
                        END
                      )
            END
            ORDER BY pg.minuto
            SEPARATOR ' | '
        )                               AS `Goles detalle`
    FROM    partidos        p
    JOIN    selecciones     sl ON sl.id_seleccion = p.id_local
    JOIN    selecciones     sv ON sv.id_seleccion = p.id_visitante
    LEFT JOIN partido_goles pg ON pg.id_partido  = p.id_partido
    LEFT JOIN jugadores     jg ON jg.id_jugador  = pg.id_jugador
    WHERE   p.id_mundial = v_id_mundial
        AND (p_fecha IS NULL OR p.fecha = p_fecha)
        AND (
            p_seleccion IS NULL
            OR sl.nombre LIKE CONCAT('%', p_seleccion, '%')
            OR sv.nombre LIKE CONCAT('%', p_seleccion, '%')
        )
        -- Filtro por grupo: sólo aplica si la etapa contiene la letra del grupo
        AND (
            p_grupo IS NULL
            OR p.etapa LIKE CONCAT('%Grupo ', UPPER(p_grupo), '%')
            OR p.etapa LIKE CONCAT('%Group ', UPPER(p_grupo), '%')
        )
    GROUP BY
        p.id_partido,
        p.numero_partido,
        p.fecha,
        p.etapa,
        sl.nombre,
        p.goles_local,
        p.goles_visitante,
        sv.nombre
    ORDER BY p.fecha, p.numero_partido;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 4 — POSICIONES FINALES
       Filtros activos: p_seleccion
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        pf.posicion                     AS `Posición Final`,
        s.nombre                        AS `Selección`,
        pf.etapa                        AS `Hasta qué fase llegó`,
        pf.pj                           AS `PJ`,
        pf.pg                           AS `PG`,
        pf.pe                           AS `PE`,
        pf.pp                           AS `PP`,
        pf.gf                           AS `GF`,
        pf.gc                           AS `GC`,
        pf.dif                          AS `Dif`,
        pf.pts                          AS `Pts`
    FROM    posiciones_finales  pf
    JOIN    selecciones         s  ON s.id_seleccion = pf.id_seleccion
    WHERE   pf.id_mundial = v_id_mundial
        AND (p_seleccion IS NULL OR s.nombre LIKE CONCAT('%', p_seleccion, '%'))
    ORDER BY pf.posicion;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 5 — TABLA DE GOLEADORES puede ser TOP 10 o filtrado por selección
       Filtros activos: p_seleccion
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        go.posicion                     AS `Pos.`,
        j.nombre                        AS `Jugador`,
        s.nombre                        AS `Selección`,
        go.goles                        AS `Goles`,
        go.partidos                     AS `Partidos jugados`,
        go.promedio_gol                 AS `Promedio por partido`
    FROM    goleadores      go
    JOIN    jugadores       j  ON j.id_jugador   = go.id_jugador
    JOIN    selecciones     s  ON s.id_seleccion = j.id_seleccion_actual
    WHERE   go.id_mundial = v_id_mundial
        AND (p_seleccion IS NULL OR s.nombre LIKE CONCAT('%', p_seleccion, '%'))
    ORDER BY go.posicion
    LIMIT 10;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 6 — PREMIOS INDIVIDUALES Y COLECTIVOS
       sin filtros adicionales, aplica siempre que se consulte el mundial
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        pr.tipo_premio                  AS `Premio`,
        COALESCE(j.nombre,  '—')        AS `Jugador`,
        COALESCE(s.nombre,  '—')        AS `Selección`
    FROM    premios         pr
    LEFT JOIN jugadores     j  ON j.id_jugador   = pr.id_jugador
    LEFT JOIN selecciones   s  ON s.id_seleccion = pr.id_seleccion
    WHERE   pr.id_mundial = v_id_mundial
    ORDER BY pr.tipo_premio;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 7 — DISCIPLINA: TARJETAS TOP 10 o filtrado por selección
       Filtros activos: p_seleccion
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        j.nombre                        AS `Jugador`,
        s.nombre                        AS `Selección`,
        t.partidos                      AS `Partidos`,
        t.amarillas                     AS `Amarillas`,
        t.rojas                         AS `Rojas`,
        t.rojas_directas                AS `Rojas directas`,
        t.rojas_x2amarillas             AS `Rojas (2ª amarilla)`
    FROM    tarjetas        t
    JOIN    jugadores       j  ON j.id_jugador   = t.id_jugador
    JOIN    selecciones     s  ON s.id_seleccion = t.id_seleccion
    WHERE   t.id_mundial = v_id_mundial
        AND (p_seleccion IS NULL OR s.nombre LIKE CONCAT('%', p_seleccion, '%'))
        AND (t.amarillas > 0 OR t.rojas > 0)
    ORDER BY t.rojas DESC, t.amarillas DESC
    LIMIT 10;

    END IF; -- fin validación id_mundial

END$$

DELIMITER ;

-- =============================================================================
-- Ejemplos de llamada
-- =============================================================================
-- CALL sp_info_mundial(2014, NULL,  NULL,         NULL);
-- CALL sp_info_mundial(2018, 'B',   NULL,         NULL);
 CALL sp_info_mundial(2022, NULL,  'Argentina',  NULL);
-- CALL sp_info_mundial(2014, NULL,  NULL,         '2014-07-13');
-- CALL sp_info_mundial(2010, 'A',   'España',     NULL);