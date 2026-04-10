-- =============================================================================
-- Parámetros:
--   p_seleccion   VARCHAR  REQUIRED  Nombre (parcial) del país  ej. 'Brasil', 'Arg'
--   p_anio        SMALLINT OPTIONAL  Filtrar por un mundial específico
--                                    NULL = todos los años
--   p_solo_fase   VARCHAR  OPTIONAL  Filtrar partidos por etapa/fase
--                                    ej. 'Final', 'Grupo', 'Semifinal'
--                                    NULL = todas las fases
-- =============================================================================

USE mundiales;
SET NAMES utf8mb4;

DROP PROCEDURE IF EXISTS sp_info_pais;

DELIMITER $$

CREATE PROCEDURE sp_info_pais (
    IN p_seleccion  VARCHAR(100),
    IN p_anio       SMALLINT,
    IN p_solo_fase  VARCHAR(100)
)
BEGIN

    /* ── Variables auxiliares ─────────────────────────────────────────────── */
    DECLARE v_id_seleccion      INT UNSIGNED DEFAULT NULL;
    DECLARE v_nombre_pais       VARCHAR(100) DEFAULT NULL;
    DECLARE v_mundiales_jug     SMALLINT UNSIGNED DEFAULT 0;
    DECLARE v_campeon_veces     TINYINT UNSIGNED  DEFAULT 0;
    DECLARE v_subcampeon_veces  TINYINT UNSIGNED  DEFAULT 0;
    DECLARE v_pj_hist           SMALLINT UNSIGNED DEFAULT 0;
    DECLARE v_pg_hist           SMALLINT UNSIGNED DEFAULT 0;
    DECLARE v_pe_hist           SMALLINT UNSIGNED DEFAULT 0;
    DECLARE v_pp_hist           SMALLINT UNSIGNED DEFAULT 0;
    DECLARE v_gf_hist           SMALLINT UNSIGNED DEFAULT 0;
    DECLARE v_gc_hist           SMALLINT UNSIGNED DEFAULT 0;
    DECLARE v_dif_hist          SMALLINT          DEFAULT 0;

    /* ── 1. Resolver la selección (búsqueda parcial) ─────────────────────── */
    SELECT  id_seleccion,
            nombre,
            mundiales_jugados,
            campeon_veces,
            subcampeon_veces,
            partidos_jugados,
            partidos_ganados,
            partidos_empatados,
            partidos_perdidos,
            goles_favor,
            goles_contra,
            diferencia_gol
    INTO    v_id_seleccion,
            v_nombre_pais,
            v_mundiales_jug,
            v_campeon_veces,
            v_subcampeon_veces,
            v_pj_hist,
            v_pg_hist,
            v_pe_hist,
            v_pp_hist,
            v_gf_hist,
            v_gc_hist,
            v_dif_hist
    FROM    selecciones
    WHERE   nombre LIKE CONCAT('%', p_seleccion, '%')
    ORDER BY nombre
    LIMIT 1;

    /* ── Validación ───────────────────────────────────────────────────────── */
    IF v_id_seleccion IS NULL THEN
        SELECT CONCAT('No se encontró ningún país que coincida con "',
                      p_seleccion, '". Verifique el nombre ingresado.') AS mensaje;
    ELSE

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 1 — FICHA HISTÓRICA GLOBAL DEL PAÍS
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        v_nombre_pais                           AS `SELECCIÓN`,
        v_mundiales_jug                         AS `Mundiales jugados`,
        CASE
            WHEN v_campeon_veces = 0 THEN 'Nunca'
            ELSE CAST(v_campeon_veces AS CHAR)
        END                                     AS `Veces campeón`,
        CASE
            WHEN v_subcampeon_veces = 0 THEN 'Nunca'
            ELSE CAST(v_subcampeon_veces AS CHAR)
        END                                     AS `Veces subcampeón`,
        v_pj_hist                               AS `Partidos jugados (histórico)`,
        v_pg_hist                               AS `Ganados`,
        v_pe_hist                               AS `Empatados`,
        v_pp_hist                               AS `Perdidos`,
        v_gf_hist                               AS `Goles a favor`,
        v_gc_hist                               AS `Goles en contra`,
        v_dif_hist                              AS `Diferencia de goles`,
        ROUND(v_pg_hist * 100.0 / NULLIF(v_pj_hist, 0), 1)
                                                AS `% Efectividad (victorias)`;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 2 — AÑOS DE PARTICIPACIÓN Y POSICIÓN FINAL ALCANZADA
       Filtro activo: p_anio
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        mu.anio                                 AS `Mundial`,
        pf.posicion                             AS `Posición Final`,
        pf.etapa                                AS `Fase alcanzada`,
        pf.pj                                   AS `PJ`,
        pf.pg                                   AS `PG`,
        pf.pe                                   AS `PE`,
        pf.pp                                   AS `PP`,
        pf.gf                                   AS `GF`,
        pf.gc                                   AS `GC`,
        pf.dif                                  AS `Dif`,
        pf.pts                                  AS `Pts`,
        CASE
            WHEN mu.id_campeon = v_id_seleccion    THEN 'CAMPEÓN'
            WHEN mu.id_organizador = v_id_seleccion THEN 'Sede'
            ELSE '—'
        END                                     AS `Distinción`
    FROM    posiciones_finales  pf
    JOIN    mundiales           mu ON mu.id_mundial    = pf.id_mundial
    WHERE   pf.id_seleccion = v_id_seleccion
        AND (p_anio IS NULL OR mu.anio = p_anio)
    ORDER BY mu.anio;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 3 — MUNDIALES COMO SEDE
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        mu.anio                                 AS `Año`,
        COALESCE(sc.nombre, '—')                AS `Campeón en esa edición`,
        mu.selecciones_participan               AS `Selecciones`,
        mu.partidos                             AS `Partidos`,
        mu.goles                                AS `Goles`,
        mu.promedio_gol                         AS `Promedio goles/partido`
    FROM    mundiales       mu
    LEFT JOIN selecciones   sc ON sc.id_seleccion = mu.id_campeon
    WHERE   mu.id_organizador = v_id_seleccion
        AND (p_anio IS NULL OR mu.anio = p_anio)
    ORDER BY mu.anio;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 4 — DESEMPEÑO EN FASE DE GRUPOS tabla de posición por mundial
       Filtro activo: p_anio
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        mu.anio                                 AS `Mundial`,
        g.grupo                                 AS `Grupo`,
        g.posicion                              AS `Pos. en grupo`,
        g.pj                                    AS `PJ`,
        g.pg                                    AS `PG`,
        g.pe                                    AS `PE`,
        g.pp                                    AS `PP`,
        g.gf                                    AS `GF`,
        g.gc                                    AS `GC`,
        g.dif                                   AS `Dif`,
        g.pts                                   AS `Pts`,
        IF(g.clasificado, 'Clasificó', 'Eliminado')
                                                AS `Resultado del grupo`
    FROM    grupos          g
    JOIN    mundiales       mu ON mu.id_mundial = g.id_mundial
    WHERE   g.id_seleccion = v_id_seleccion
        AND (p_anio IS NULL OR mu.anio = p_anio)
    ORDER BY mu.anio;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 5 — PARTIDOS Y RESULTADOS (todos los mundiales o filtrado)
       Filtros activos: p_anio, p_solo_fase
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        mu.anio                                 AS `Mundial`,
        p.fecha                                 AS `Fecha`,
        p.etapa                                 AS `Etapa / Fase`,
        p.numero_partido                        AS `Nº Partido`,
        sl.nombre                               AS `Local`,
        p.goles_local                           AS `GL`,
        p.goles_visitante                       AS `GV`,
        sv.nombre                               AS `Visitante`,
        CASE
            -- Resultado desde la perspectiva del país consultado
            WHEN sl.id_seleccion = v_id_seleccion THEN
                CASE
                    WHEN p.goles_local > p.goles_visitante  THEN 'Victoria'
                    WHEN p.goles_local = p.goles_visitante  THEN 'Empate'
                    ELSE 'Derrota'
                END
            ELSE
                CASE
                    WHEN p.goles_visitante > p.goles_local  THEN 'Victoria'
                    WHEN p.goles_visitante = p.goles_local  THEN 'Empate'
                    ELSE 'Derrota'
                END
        END                                     AS `Resultado`,
        -- Detalle de goles con minuto y tipo
        GROUP_CONCAT(
            CASE WHEN pg.id_partido IS NOT NULL
                 THEN CONCAT(
                        COALESCE(jg.nombre, '?'), ' ',
                        pg.minuto, '\' ',
                        CASE pg.tipo_gol
                            WHEN 'penal'   THEN '(P)'
                            WHEN 'autogol' THEN '(AG)'
                            ELSE ''
                        END,
                        ' [', COALESCE(seq.nombre, '?'), ']'
                      )
            END
            ORDER BY pg.minuto
            SEPARATOR ' | '
        )                                       AS `Goles (jugador min tipo [selección])`
    FROM    partidos        p
    JOIN    mundiales       mu ON mu.id_mundial    = p.id_mundial
    JOIN    selecciones     sl ON sl.id_seleccion  = p.id_local
    JOIN    selecciones     sv ON sv.id_seleccion  = p.id_visitante
    LEFT JOIN partido_goles pg ON pg.id_partido    = p.id_partido
    LEFT JOIN jugadores     jg ON jg.id_jugador    = pg.id_jugador
    LEFT JOIN selecciones   seq ON seq.id_seleccion = pg.id_seleccion
    WHERE   (p.id_local = v_id_seleccion OR p.id_visitante = v_id_seleccion)
        AND (p_anio      IS NULL OR mu.anio    = p_anio)
        AND (p_solo_fase IS NULL OR p.etapa   LIKE CONCAT('%', p_solo_fase, '%'))
    GROUP BY
        mu.anio, p.fecha, p.etapa, p.numero_partido,
        sl.nombre, p.goles_local, p.goles_visitante, sv.nombre,
        sl.id_seleccion
    ORDER BY mu.anio, p.fecha, p.numero_partido;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 6 — TÍTULOS Y SUBCAMPEONATOS
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        mu.anio                                 AS `Mundial`,
        st.tipo                                 AS `Logro`
    FROM    seleccion_titulos    st
    JOIN    mundiales            mu ON mu.id_mundial = st.id_mundial
    WHERE   st.id_seleccion = v_id_seleccion
        AND (p_anio IS NULL OR mu.anio = p_anio)
    ORDER BY mu.anio;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 7 — GOLEADORES DEL PAÍS por mundial
       Filtro activo: p_anio
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        mu.anio                                 AS `Mundial`,
        j.nombre                                AS `Jugador`,
        go.posicion                             AS `Pos. ranking goleadores`,
        go.goles                                AS `Goles`,
        go.partidos                             AS `Partidos`,
        go.promedio_gol                         AS `Promedio`
    FROM    goleadores      go
    JOIN    mundiales       mu ON mu.id_mundial  = go.id_mundial
    JOIN    jugadores       j  ON j.id_jugador   = go.id_jugador
    JOIN    jugadores_por_mundial jpm
                               ON jpm.id_jugador  = go.id_jugador
                              AND jpm.id_mundial  = go.id_mundial
    WHERE   jpm.id_seleccion = v_id_seleccion
        AND (p_anio IS NULL OR mu.anio = p_anio)
    ORDER BY mu.anio, go.goles DESC;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 8 — PREMIOS OBTENIDOS POR EL PAÍS O SUS JUGADORES
       Filtro activo: p_anio
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        mu.anio                                 AS `Mundial`,
        pr.tipo_premio                          AS `Premio`,
        COALESCE(j.nombre, '—')                 AS `Jugador`,
        COALESCE(seq.nombre, '—')               AS `Selección (premio colectivo)`
    FROM    premios         pr
    JOIN    mundiales       mu  ON mu.id_mundial    = pr.id_mundial
    LEFT JOIN jugadores     j   ON j.id_jugador     = pr.id_jugador
    LEFT JOIN selecciones   seq ON seq.id_seleccion = pr.id_seleccion
    WHERE   (pr.id_seleccion = v_id_seleccion
             OR j.id_seleccion_actual = v_id_seleccion)
        AND (p_anio IS NULL OR mu.anio = p_anio)
    ORDER BY mu.anio, pr.tipo_premio;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 9 — DISCIPLINA: JUGADORES CON TARJETAS
       Filtro activo: p_anio
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        mu.anio                                 AS `Mundial`,
        j.nombre                                AS `Jugador`,
        t.partidos                              AS `Partidos`,
        t.amarillas                             AS `Amarillas`,
        t.rojas                                 AS `Rojas`,
        t.rojas_directas                        AS `Rojas directas`,
        t.rojas_x2amarillas                     AS `Rojas (2ª amarilla)`
    FROM    tarjetas        t
    JOIN    mundiales       mu ON mu.id_mundial  = t.id_mundial
    JOIN    jugadores       j  ON j.id_jugador   = t.id_jugador
    WHERE   t.id_seleccion = v_id_seleccion
        AND (t.amarillas > 0 OR t.rojas > 0)
        AND (p_anio IS NULL OR mu.anio = p_anio)
    ORDER BY mu.anio, t.rojas DESC, t.amarillas DESC;

    /* ═══════════════════════════════════════════════════════════════════════
       SECCIÓN 10 — RESUMEN ESTADÍSTICO POR MUNDIAL     
       Filtro activo: p_anio
    ═══════════════════════════════════════════════════════════════════════ */
    SELECT
        mu.anio                                             AS `Mundial`,
        COUNT(p.id_partido)                                 AS `Partidos jugados`,
        SUM(CASE
            WHEN p.id_local = v_id_seleccion
                 AND p.goles_local > p.goles_visitante      THEN 1
            WHEN p.id_visitante = v_id_seleccion
                 AND p.goles_visitante > p.goles_local      THEN 1
            ELSE 0 END)                                     AS `Victorias`,
        SUM(CASE
            WHEN p.goles_local = p.goles_visitante          THEN 1
            ELSE 0 END)                                     AS `Empates`,
        SUM(CASE
            WHEN p.id_local = v_id_seleccion
                 AND p.goles_local < p.goles_visitante      THEN 1
            WHEN p.id_visitante = v_id_seleccion
                 AND p.goles_visitante < p.goles_local      THEN 1
            ELSE 0 END)                                     AS `Derrotas`,
        SUM(CASE
            WHEN p.id_local     = v_id_seleccion            THEN p.goles_local
            ELSE p.goles_visitante END)                     AS `Goles a favor`,
        SUM(CASE
            WHEN p.id_local     = v_id_seleccion            THEN p.goles_visitante
            ELSE p.goles_local END)                         AS `Goles en contra`
    FROM    partidos    p
    JOIN    mundiales   mu ON mu.id_mundial = p.id_mundial
    WHERE   (p.id_local = v_id_seleccion OR p.id_visitante = v_id_seleccion)
        AND (p_anio IS NULL OR mu.anio = p_anio)
    GROUP BY mu.anio
    ORDER BY mu.anio;

    END IF; -- fin validación

END$$

DELIMITER ;

-- =============================================================================
-- Ejemplos de llamada
-- =============================================================================
-- CALL sp_info_pais('Brasil',    NULL, NULL);          -- historial completo
-- CALL sp_info_pais('Argentina', 2022, NULL);          -- solo Mundial 2022
-- CALL sp_info_pais('Alemania',  NULL, 'Final');       -- solo partidos de finales
-- CALL sp_info_pais('Uruguay',   NULL, 'Grupo');       -- solo fase de grupos
-- CALL sp_info_pais('Méx',       NULL, NULL);          -- búsqueda parcial "México"
-- CALL sp_info_pais('Francia',   1998, NULL);          -- Francia 1998 completo
