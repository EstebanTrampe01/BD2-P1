-- =============================================================================
-- Base de Datos: Los Mundiales de Futbol
-- =============================================================================

CREATE DATABASE IF NOT EXISTS mundiales
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mundiales;

CREATE TABLE selecciones (
    id_seleccion        INT UNSIGNED            NOT NULL AUTO_INCREMENT,
    nombre              VARCHAR(100)            NOT NULL,
    mundiales_jugados   SMALLINT UNSIGNED,
    campeon_veces       TINYINT UNSIGNED,
    subcampeon_veces    TINYINT UNSIGNED,
    posicion_historica  SMALLINT UNSIGNED,
    partidos_jugados    SMALLINT UNSIGNED,
    partidos_ganados    SMALLINT UNSIGNED,
    partidos_empatados  SMALLINT UNSIGNED,
    partidos_perdidos   SMALLINT UNSIGNED,
    goles_favor         SMALLINT UNSIGNED,
    goles_contra        SMALLINT UNSIGNED,
    diferencia_gol      SMALLINT,
    PRIMARY KEY (id_seleccion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*
anio,organizador,campeon,selecciones,partidos,goles,promedio_gol

 ,url,fecha_scraping
*/
CREATE TABLE mundiales (
    id_mundial              INT UNSIGNED        NOT NULL AUTO_INCREMENT,
    anio                    SMALLINT UNSIGNED   NOT NULL,
    id_organizador          INT UNSIGNED,
    id_campeon              INT UNSIGNED,
    selecciones_participan  SMALLINT UNSIGNED,
    partidos                SMALLINT UNSIGNED,
    goles                   SMALLINT UNSIGNED,
    promedio_gol            DECIMAL(4,2),
    PRIMARY KEY (id_mundial)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE seleccion_titulos (
    id_titulo            BIGINT UNSIGNED        NOT NULL AUTO_INCREMENT,
    id_seleccion         INT UNSIGNED           NOT NULL,
    id_mundial           INT UNSIGNED           NOT NULL,
    tipo                 ENUM('campeon','subcampeon') NOT NULL,
    PRIMARY KEY (id_titulo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE jugadores (
    id_jugador              BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    source_url              VARCHAR(255),
    nombre                  VARCHAR(150),
    nombre_completo         VARCHAR(200),
    fecha_nacimiento        DATE,
    lugar_nacimiento        VARCHAR(150),
    posicion                VARCHAR(50),
    id_seleccion_actual     INT UNSIGNED,
    altura_cm               SMALLINT UNSIGNED,
    apodo                   VARCHAR(150),
    total_mundiales         TINYINT UNSIGNED,
    total_partidos          SMALLINT UNSIGNED,
    total_goles             SMALLINT UNSIGNED,
    promedio_gol            DECIMAL(5,2),
    PRIMARY KEY (id_jugador)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE jugador_camisetas (
    id_jugador_camiseta     BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_jugador              BIGINT UNSIGNED      NOT NULL,
    id_mundial              INT UNSIGNED,
    numero                  TINYINT UNSIGNED     NOT NULL,
    PRIMARY KEY (id_jugador_camiseta)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE partidos (
    id_partido              BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    source_url              VARCHAR(255),
    id_mundial              INT UNSIGNED,
    numero_partido          SMALLINT UNSIGNED,
    fecha                   DATE,
    etapa                   VARCHAR(100),
    id_local                INT UNSIGNED,
    goles_local             TINYINT UNSIGNED,
    goles_visitante         TINYINT UNSIGNED,
    id_visitante            INT UNSIGNED,
    PRIMARY KEY (id_partido)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE grupos (
    id_grupo_fase           BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_mundial              INT UNSIGNED         NOT NULL,
    grupo                   VARCHAR(5)           NOT NULL,
    id_seleccion            INT UNSIGNED         NOT NULL,
    posicion                TINYINT UNSIGNED,
    pj                      TINYINT UNSIGNED,
    pg                      TINYINT UNSIGNED,
    pe                      TINYINT UNSIGNED,
    pp                      TINYINT UNSIGNED,
    gf                      TINYINT UNSIGNED,
    gc                      TINYINT UNSIGNED,
    dif                     SMALLINT,
    pts                     TINYINT UNSIGNED,
    clasificado             BOOLEAN,
    PRIMARY KEY (id_grupo_fase)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE posiciones_finales (
    id_posicion_final       BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_mundial              INT UNSIGNED         NOT NULL,
    id_seleccion            INT UNSIGNED         NOT NULL,
    posicion                TINYINT UNSIGNED,
    etapa                   VARCHAR(100),
    pts                     TINYINT UNSIGNED,
    pj                      TINYINT UNSIGNED,
    pg                      TINYINT UNSIGNED,
    pe                      TINYINT UNSIGNED,
    pp                      TINYINT UNSIGNED,
    gf                      TINYINT UNSIGNED,
    gc                      TINYINT UNSIGNED,
    dif                     SMALLINT,
    PRIMARY KEY (id_posicion_final)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE goleadores (
    id_goleador             BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_mundial              INT UNSIGNED         NOT NULL,
    id_jugador              BIGINT UNSIGNED      NOT NULL,
    posicion                TINYINT UNSIGNED,
    goles                   TINYINT UNSIGNED,
    partidos                TINYINT UNSIGNED,
    promedio_gol            DECIMAL(5,2),
    PRIMARY KEY (id_goleador)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE premios (
    id_premio               BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_mundial              INT UNSIGNED,
    tipo_premio             VARCHAR(150)         NOT NULL,
    id_jugador              BIGINT UNSIGNED,
    id_seleccion            INT UNSIGNED,
    PRIMARY KEY (id_premio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tarjetas (
    id_tarjeta              BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_mundial              INT UNSIGNED         NOT NULL,
    id_jugador              BIGINT UNSIGNED      NOT NULL,
    id_seleccion            INT UNSIGNED,
    amarillas               TINYINT UNSIGNED,
    rojas                   TINYINT UNSIGNED,
    rojas_directas          TINYINT UNSIGNED,
    rojas_x2amarillas       TINYINT UNSIGNED,
    partidos                TINYINT UNSIGNED,
    PRIMARY KEY (id_tarjeta)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE jugadores_por_mundial (
    id_jugador_mundial      BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_jugador              BIGINT UNSIGNED      NOT NULL,
    id_mundial              INT UNSIGNED         NOT NULL,
    id_seleccion            INT UNSIGNED,
    camiseta                TINYINT UNSIGNED,
    posicion                VARCHAR(50),
    jugados                 TINYINT UNSIGNED,
    titular                 TINYINT UNSIGNED,
    capitan                 BOOLEAN,
    no_jugo                 TINYINT UNSIGNED,
    goles                   TINYINT UNSIGNED,
    promedio_gol            DECIMAL(5,2),
    tarjetas_amarillas      TINYINT UNSIGNED,
    tarjetas_rojas          TINYINT UNSIGNED,
    pg                      TINYINT UNSIGNED,
    pe                      TINYINT UNSIGNED,
    pp                      TINYINT UNSIGNED,
    posicion_final          VARCHAR(100),
    PRIMARY KEY (id_jugador_mundial)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE planteles (
    id_plantel              BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_mundial              INT UNSIGNED         NOT NULL,
    id_seleccion            INT UNSIGNED         NOT NULL,
    id_jugador              BIGINT UNSIGNED      NOT NULL,
    camiseta                TINYINT UNSIGNED,
    posicion_grupo          VARCHAR(30),
    fecha_nacimiento        DATE,
    altura_cm               SMALLINT UNSIGNED,
    club                    VARCHAR(150),
    PRIMARY KEY (id_plantel)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE partido_jugadores (
    id_partido_jugador      BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_mundial              INT UNSIGNED,
    id_partido              BIGINT UNSIGNED,
    id_jugador              BIGINT UNSIGNED,
    id_seleccion            INT UNSIGNED,
    camiseta                TINYINT UNSIGNED,
    posicion                VARCHAR(5),
    rol                     VARCHAR(20),
    capitan                 BOOLEAN,
    minuto_entrada          TINYINT UNSIGNED,
    minuto_salida           TINYINT UNSIGNED,
    goles_count             TINYINT UNSIGNED,
    PRIMARY KEY (id_partido_jugador)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE partido_goles (
    id_partido_gol          BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_mundial              INT UNSIGNED,
    id_partido              BIGINT UNSIGNED,
    id_jugador              BIGINT UNSIGNED,
    id_seleccion            INT UNSIGNED,
    minuto                  TINYINT UNSIGNED,
    tipo_gol                ENUM('normal','penal','autogol') NOT NULL,
    PRIMARY KEY (id_partido_gol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE scraping_runs (
    id_scraping_run         BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    fuente                  VARCHAR(120),
    fecha_scraping          DATETIME             NOT NULL,
    notas                   VARCHAR(255),
    PRIMARY KEY (id_scraping_run)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE scraping_metadata (
    id_scraping_metadata    BIGINT UNSIGNED      NOT NULL AUTO_INCREMENT,
    id_scraping_run         BIGINT UNSIGNED      NOT NULL,
    tabla                   VARCHAR(50)          NOT NULL,
    entidad_id              BIGINT UNSIGNED      NOT NULL,
    url_fuente              VARCHAR(255),
    PRIMARY KEY (id_scraping_metadata)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- FOREIGN KEYS
-- =============================================================================

ALTER TABLE mundiales
    ADD CONSTRAINT fk_mundiales_organizador
        FOREIGN KEY (id_organizador) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_mundiales_campeon
        FOREIGN KEY (id_campeon) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE seleccion_titulos
    ADD CONSTRAINT fk_st_seleccion
        FOREIGN KEY (id_seleccion) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_st_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE jugadores
    ADD CONSTRAINT fk_jugadores_seleccion
        FOREIGN KEY (id_seleccion_actual) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE jugador_camisetas
    ADD CONSTRAINT fk_jc_jugador
        FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_jc_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE partidos
    ADD CONSTRAINT fk_partidos_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_partidos_local
        FOREIGN KEY (id_local) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_partidos_visitante
        FOREIGN KEY (id_visitante) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE grupos
    ADD CONSTRAINT fk_grupos_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_grupos_seleccion
        FOREIGN KEY (id_seleccion) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE posiciones_finales
    ADD CONSTRAINT fk_pf_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_pf_seleccion
        FOREIGN KEY (id_seleccion) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE goleadores
    ADD CONSTRAINT fk_goleadores_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_goleadores_jugador
        FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
        ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE premios
    ADD CONSTRAINT fk_premios_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_premios_jugador
        FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_premios_seleccion
        FOREIGN KEY (id_seleccion) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE tarjetas
    ADD CONSTRAINT fk_tarjetas_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_tarjetas_jugador
        FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_tarjetas_seleccion
        FOREIGN KEY (id_seleccion) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE jugadores_por_mundial
    ADD CONSTRAINT fk_jpm_jugador
        FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_jpm_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_jpm_seleccion
        FOREIGN KEY (id_seleccion) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE planteles
    ADD CONSTRAINT fk_planteles_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_planteles_seleccion
        FOREIGN KEY (id_seleccion) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_planteles_jugador
        FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
        ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE partido_jugadores
    ADD CONSTRAINT fk_pj_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_pj_partido
        FOREIGN KEY (id_partido) REFERENCES partidos(id_partido)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_pj_jugador
        FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_pj_seleccion
        FOREIGN KEY (id_seleccion) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE partido_goles
    ADD CONSTRAINT fk_pg_mundial
        FOREIGN KEY (id_mundial) REFERENCES mundiales(id_mundial)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_pg_partido
        FOREIGN KEY (id_partido) REFERENCES partidos(id_partido)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_pg_jugador
        FOREIGN KEY (id_jugador) REFERENCES jugadores(id_jugador)
        ON UPDATE CASCADE ON DELETE SET NULL,
    ADD CONSTRAINT fk_pg_seleccion
        FOREIGN KEY (id_seleccion) REFERENCES selecciones(id_seleccion)
        ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE scraping_metadata
    ADD CONSTRAINT fk_sm_run
        FOREIGN KEY (id_scraping_run) REFERENCES scraping_runs(id_scraping_run)
        ON UPDATE CASCADE ON DELETE CASCADE;
