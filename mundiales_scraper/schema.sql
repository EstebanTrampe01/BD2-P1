-- =============================================================================
-- Base de Datos: Los Mundiales de Fútbol
-- Motor: MySQL / MariaDB
-- Generado desde: https://www.losmundialesdefutbol.com/
-- Orden de carga recomendado:
--   1. mundiales
--   2. selecciones
--   3. jugadores
--   4. partidos
--   5. grupos, posiciones_finales, goleadores, premios, tarjetas
--   6. jugadores_por_mundial
--   7. planteles
--   8. partido_jugadores, partido_goles
-- =============================================================================

CREATE DATABASE IF NOT EXISTS mundiales
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mundiales;

-- -----------------------------------------------------------------------------
-- 1. mundiales
--    Fuente: /mundiales/YYYY_mundial.php
--    Una fila por edición del Mundial
-- -----------------------------------------------------------------------------
CREATE TABLE mundiales (
    anio            SMALLINT UNSIGNED   NOT NULL,
    organizador     VARCHAR(100),
    campeon         VARCHAR(100),
    selecciones     SMALLINT UNSIGNED,
    partidos        SMALLINT UNSIGNED,
    goles           SMALLINT UNSIGNED,
    promedio_gol    DECIMAL(4,2),
    url             VARCHAR(255),
    fecha_scraping  DATETIME,
    PRIMARY KEY (anio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 2. selecciones
--    Fuente: /selecciones/PAIS_seleccion.php
--    Una fila por selección nacional
-- -----------------------------------------------------------------------------
CREATE TABLE selecciones (
    seleccion           VARCHAR(100)        NOT NULL,
    mundiales_jugados   SMALLINT UNSIGNED,
    campeon_veces       TINYINT UNSIGNED,
    campeon_anios       VARCHAR(100),       -- años separados por coma, e.g. "1958,1962,1970"
    subcampeon_veces    TINYINT UNSIGNED,
    subcampeon_anios    VARCHAR(100),
    posicion_historica  SMALLINT UNSIGNED,
    partidos_jugados    SMALLINT UNSIGNED,
    partidos_ganados    SMALLINT UNSIGNED,
    partidos_empatados  SMALLINT UNSIGNED,
    partidos_perdidos   SMALLINT UNSIGNED,
    goles_favor         SMALLINT UNSIGNED,
    goles_contra        SMALLINT UNSIGNED,
    diferencia_gol      VARCHAR(10),        -- puede ser "+129" o "-5"
    url                 VARCHAR(255),
    fecha_scraping      DATETIME,
    PRIMARY KEY (seleccion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 3. jugadores
--    Fuente: /jugadores/NOMBRE.php
--    Una fila por jugador (bio + totales de carrera)
-- -----------------------------------------------------------------------------
CREATE TABLE jugadores (
    url                 VARCHAR(255)        NOT NULL,
    nombre              VARCHAR(150),
    nombre_completo     VARCHAR(200),
    fecha_nacimiento    VARCHAR(50),        -- e.g. "30-Oct-1987"
    lugar_nacimiento    VARCHAR(150),
    posicion            VARCHAR(50),
    seleccion           VARCHAR(100),
    numeros_camiseta    VARCHAR(50),        -- puede ser "10" o "10,19"
    altura              VARCHAR(20),        -- e.g. "1.70 m"
    apodo               VARCHAR(150),
    total_mundiales     TINYINT UNSIGNED,
    total_partidos      SMALLINT UNSIGNED,
    total_goles         SMALLINT UNSIGNED,
    promedio_gol        DECIMAL(5,2),
    campeon             VARCHAR(100),       -- años separados por coma
    fecha_scraping      DATETIME,
    PRIMARY KEY (url),
    KEY idx_nombre (nombre),
    KEY idx_seleccion (seleccion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 4. partidos
--    Fuente: /mundiales/YYYY_resultados.php
--    Una fila por partido (fecha, equipos, marcador, etapa)
-- -----------------------------------------------------------------------------
CREATE TABLE partidos (
    url_partido         VARCHAR(255)        NOT NULL,
    mundial             SMALLINT UNSIGNED,
    num                 SMALLINT UNSIGNED,
    fecha               VARCHAR(30),        -- e.g. "20-Nov-2022"
    etapa               VARCHAR(100),       -- e.g. "1ra Ronda, Grupo A"
    local               VARCHAR(100),
    goles_local         TINYINT UNSIGNED,
    goles_visitante     TINYINT UNSIGNED,
    visitante           VARCHAR(100),
    url                 VARCHAR(255),
    fecha_scraping      DATETIME,
    PRIMARY KEY (url_partido),
    KEY idx_mundial (mundial),
    KEY idx_local (local),
    KEY idx_visitante (visitante)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 5. grupos
--    Fuente: /mundiales/YYYY_grupo_X.php
--    Una fila por equipo por grupo
-- -----------------------------------------------------------------------------
CREATE TABLE grupos (
    mundial             SMALLINT UNSIGNED   NOT NULL,
    grupo               VARCHAR(5)          NOT NULL,
    posicion            TINYINT UNSIGNED,
    seleccion           VARCHAR(100)        NOT NULL,
    pj                  TINYINT UNSIGNED,
    pg                  TINYINT UNSIGNED,
    pe                  TINYINT UNSIGNED,
    pp                  TINYINT UNSIGNED,
    gf                  TINYINT UNSIGNED,
    gc                  TINYINT UNSIGNED,
    dif                 VARCHAR(10),
    pts                 TINYINT UNSIGNED,
    clasificado         VARCHAR(5),         -- "Si" / "No"
    url                 VARCHAR(255),
    fecha_scraping      DATETIME,
    PRIMARY KEY (mundial, grupo, seleccion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 6. posiciones_finales
--    Fuente: /mundiales/YYYY_posiciones_finales.php
--    Una fila por equipo por Mundial (clasificación final)
-- -----------------------------------------------------------------------------
CREATE TABLE posiciones_finales (
    mundial             SMALLINT UNSIGNED   NOT NULL,
    posicion            TINYINT UNSIGNED,
    seleccion           VARCHAR(100)        NOT NULL,
    etapa               VARCHAR(100),       -- e.g. "Final", "Semifinal"
    pts                 TINYINT UNSIGNED,
    pj                  TINYINT UNSIGNED,
    pg                  TINYINT UNSIGNED,
    pe                  TINYINT UNSIGNED,
    pp                  TINYINT UNSIGNED,
    gf                  TINYINT UNSIGNED,
    gc                  TINYINT UNSIGNED,
    dif                 VARCHAR(10),
    url                 VARCHAR(255),
    fecha_scraping      DATETIME,
    PRIMARY KEY (mundial, seleccion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 7. goleadores
--    Fuente: /mundiales/YYYY_goleadores.php
--    Una fila por goleador por Mundial
-- -----------------------------------------------------------------------------
CREATE TABLE goleadores (
    mundial             SMALLINT UNSIGNED   NOT NULL,
    posicion            TINYINT UNSIGNED,
    jugador             VARCHAR(150)        NOT NULL,
    seleccion           VARCHAR(100),
    goles               TINYINT UNSIGNED,
    partidos            TINYINT UNSIGNED,
    promedio_gol        DECIMAL(5,2),
    url_jugador         VARCHAR(255),
    url                 VARCHAR(255),
    fecha_scraping      DATETIME,
    PRIMARY KEY (mundial, jugador)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 8. premios
--    Fuente: /mundiales/YYYY_premios.php
--    Una fila por premio por Mundial
-- -----------------------------------------------------------------------------
CREATE TABLE premios (
    id                  INT UNSIGNED        NOT NULL AUTO_INCREMENT,
    mundial             SMALLINT UNSIGNED,
    tipo_premio         VARCHAR(150),
    jugador_o_seleccion VARCHAR(150),
    url_jugador         VARCHAR(255),
    url                 VARCHAR(255),
    fecha_scraping      DATETIME,
    PRIMARY KEY (id),
    KEY idx_mundial (mundial)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 9. tarjetas
--    Fuente: /mundiales/YYYY_tarjetas.php
--    Una fila por jugador sancionado por Mundial
-- -----------------------------------------------------------------------------
CREATE TABLE tarjetas (
    mundial             SMALLINT UNSIGNED   NOT NULL,
    jugador             VARCHAR(150)        NOT NULL,
    seleccion           VARCHAR(100)        NOT NULL,
    amarillas           TINYINT UNSIGNED,
    rojas               TINYINT UNSIGNED,
    rd                  VARCHAR(5),         -- rojas directas
    ta2                 VARCHAR(5),         -- rojas por segunda amarilla
    partidos            TINYINT UNSIGNED,
    url_jugador         VARCHAR(255),
    url                 VARCHAR(255),
    fecha_scraping      DATETIME,
    PRIMARY KEY (mundial, jugador, seleccion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 10. jugadores_por_mundial
--     Fuente: /jugadores/NOMBRE.php (tabla de detalle por edición)
--     Una fila por jugador por Mundial
-- -----------------------------------------------------------------------------
CREATE TABLE jugadores_por_mundial (
    jugador             VARCHAR(150)        NOT NULL,
    seleccion           VARCHAR(100),
    mundial             SMALLINT UNSIGNED   NOT NULL,
    camiseta            TINYINT UNSIGNED,
    posicion            VARCHAR(50),
    jugados             TINYINT UNSIGNED,
    titular             TINYINT UNSIGNED,
    capitan             TINYINT UNSIGNED,
    no_jugo             TINYINT UNSIGNED,
    goles               TINYINT UNSIGNED,
    promedio_gol        DECIMAL(5,2),
    tarjetas_amarillas  TINYINT UNSIGNED,
    tarjetas_rojas      TINYINT UNSIGNED,
    pg                  TINYINT UNSIGNED,
    pe                  TINYINT UNSIGNED,
    pp                  TINYINT UNSIGNED,
    posicion_final      VARCHAR(100),
    url_jugador         VARCHAR(255),
    fecha_scraping      DATETIME,
    PRIMARY KEY (jugador, mundial),
    KEY idx_mundial (mundial),
    KEY idx_seleccion (seleccion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 11. planteles
--     Fuente: /planteles/YYYY_PAIS_jugadores.php
--     Una fila por jugador por plantel (squad completo)
-- -----------------------------------------------------------------------------
CREATE TABLE planteles (
    mundial             SMALLINT UNSIGNED   NOT NULL,
    seleccion           VARCHAR(100)        NOT NULL,
    camiseta            TINYINT UNSIGNED,
    jugador             VARCHAR(150)        NOT NULL,
    url_jugador         VARCHAR(255),
    posicion_grupo      VARCHAR(30),        -- Arquero/Defensor/Mediocampista/Delantero/Entrenador
    fecha_nacimiento    VARCHAR(30),        -- e.g. "16-Oct-1986"
    altura              VARCHAR(20),        -- e.g. "1.89 m"
    club                VARCHAR(150),       -- e.g. "River Plate (ARG)"
    url                 VARCHAR(255),
    fecha_scraping      DATETIME,
    PRIMARY KEY (mundial, seleccion, jugador)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 12. partido_jugadores
--     Fuente: /partidos/YYYY_eq1_eq2.php (sección Jugadores)
--     Una fila por jugador por partido
-- -----------------------------------------------------------------------------
CREATE TABLE partido_jugadores (
    id                  INT UNSIGNED        NOT NULL AUTO_INCREMENT,
    mundial             SMALLINT UNSIGNED,
    url_partido         VARCHAR(255),
    seleccion           VARCHAR(100),
    jugador             VARCHAR(150),
    url_jugador         VARCHAR(255),
    camiseta            TINYINT UNSIGNED,
    posicion            VARCHAR(5),         -- AR / DF / MC / DL
    rol                 VARCHAR(20),        -- Titular / Ingreso / Suplente
    capitan             VARCHAR(5),         -- Si / No
    minuto_entrada      TINYINT UNSIGNED,
    minuto_salida       TINYINT UNSIGNED,
    goles_count         TINYINT UNSIGNED,
    goles_minutos       VARCHAR(50),        -- e.g. "16,31"
    fecha_scraping      DATETIME,
    PRIMARY KEY (id),
    KEY idx_partido (url_partido),
    KEY idx_mundial (mundial),
    KEY idx_jugador (jugador)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- -----------------------------------------------------------------------------
-- 13. partido_goles
--     Fuente: /partidos/YYYY_eq1_eq2.php (sección Goles)
--     Una fila por gol por partido
-- -----------------------------------------------------------------------------
CREATE TABLE partido_goles (
    id                  INT UNSIGNED        NOT NULL AUTO_INCREMENT,
    mundial             SMALLINT UNSIGNED,
    url_partido         VARCHAR(255),
    seleccion           VARCHAR(100),
    jugador             VARCHAR(150),
    minuto              TINYINT UNSIGNED,
    tipo_gol            VARCHAR(20),        -- normal / penal / autogol
    fecha_scraping      DATETIME,
    PRIMARY KEY (id),
    KEY idx_partido (url_partido),
    KEY idx_mundial (mundial)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- FOREIGN KEYS
-- Aplicar DESPUÉS de cargar todos los datos con LOAD DATA INFILE
-- para evitar errores de orden de carga.
-- =============================================================================

ALTER TABLE jugadores
    ADD CONSTRAINT fk_jugadores_seleccion
        FOREIGN KEY (seleccion) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE partidos
    ADD CONSTRAINT fk_partidos_mundial
        FOREIGN KEY (mundial) REFERENCES mundiales(anio)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_partidos_local
        FOREIGN KEY (local) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_partidos_visitante
        FOREIGN KEY (visitante) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE grupos
    ADD CONSTRAINT fk_grupos_mundial
        FOREIGN KEY (mundial) REFERENCES mundiales(anio)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_grupos_seleccion
        FOREIGN KEY (seleccion) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE posiciones_finales
    ADD CONSTRAINT fk_posfinales_mundial
        FOREIGN KEY (mundial) REFERENCES mundiales(anio)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_posfinales_seleccion
        FOREIGN KEY (seleccion) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE goleadores
    ADD CONSTRAINT fk_goleadores_mundial
        FOREIGN KEY (mundial) REFERENCES mundiales(anio)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_goleadores_seleccion
        FOREIGN KEY (seleccion) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_goleadores_jugador
        FOREIGN KEY (url_jugador) REFERENCES jugadores(url)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE premios
    ADD CONSTRAINT fk_premios_mundial
        FOREIGN KEY (mundial) REFERENCES mundiales(anio)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE tarjetas
    ADD CONSTRAINT fk_tarjetas_mundial
        FOREIGN KEY (mundial) REFERENCES mundiales(anio)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_tarjetas_seleccion
        FOREIGN KEY (seleccion) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE jugadores_por_mundial
    ADD CONSTRAINT fk_jpm_mundial
        FOREIGN KEY (mundial) REFERENCES mundiales(anio)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_jpm_seleccion
        FOREIGN KEY (seleccion) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_jpm_jugador
        FOREIGN KEY (url_jugador) REFERENCES jugadores(url)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE planteles
    ADD CONSTRAINT fk_planteles_mundial
        FOREIGN KEY (mundial) REFERENCES mundiales(anio)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_planteles_seleccion
        FOREIGN KEY (seleccion) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE partido_jugadores
    ADD CONSTRAINT fk_pj_mundial
        FOREIGN KEY (mundial) REFERENCES mundiales(anio)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_pj_partido
        FOREIGN KEY (url_partido) REFERENCES partidos(url_partido)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_pj_seleccion
        FOREIGN KEY (seleccion) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE partido_goles
    ADD CONSTRAINT fk_pg_mundial
        FOREIGN KEY (mundial) REFERENCES mundiales(anio)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_pg_partido
        FOREIGN KEY (url_partido) REFERENCES partidos(url_partido)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_pg_seleccion
        FOREIGN KEY (seleccion) REFERENCES selecciones(seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;
