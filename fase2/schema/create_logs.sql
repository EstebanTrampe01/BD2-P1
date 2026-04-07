USE mundiales;

CREATE TABLE IF NOT EXISTS log_ejecucion (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    evento VARCHAR(80) NOT NULL,
    detalle VARCHAR(255),
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_fragmentacion (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    tabla VARCHAR(128) NOT NULL,
    engine VARCHAR(32),
    table_rows BIGINT,
    data_length BIGINT,
    index_length BIGINT,
    data_free BIGINT,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_mundiales (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_selecciones (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_jugadores (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_seleccion_titulos (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_jugador_camisetas (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_partidos (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_grupos (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_posiciones_finales (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_goleadores (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_premios (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_tarjetas (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_jugadores_por_mundial (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_planteles (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_partido_jugadores (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS log_partido_goles (
    id_log BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fecha_evento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dia_carga TINYINT UNSIGNED,
    operacion ENUM('INSERT','UPDATE','DELETE','INFO') NOT NULL,
    id_entidad VARCHAR(64),
    detalle_antes JSON,
    detalle_despues JSON,
    PRIMARY KEY (id_log)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO log_ejecucion (dia_carga, evento, detalle)
VALUES (0, 'SETUP', 'Tablas LOG creadas/validadas para Fase 2');
