"""Carga CSV normalizados (output_db/) a MySQL en Docker."""

import os
import re
import math
import datetime
import pandas as pd

try:
    import mysql.connector
except ImportError:
    mysql = None
else:
    mysql = mysql.connector


DIR_SALIDA = "./output_db"

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "mundiales_user",
    "password": "mundiales1234",
    "database": "mundiales",
}


def obtener_conexion():
    if mysql is None:
        raise RuntimeError(
            "El módulo mysql-connector-python no está instalado. "
            "Instala con: pip install mysql-connector-python"
        )
    return mysql.connect(**DB_CONFIG)


def cargar_csv_a_tabla(cursor, nombre_csv, tabla, columnas):
    ruta = os.path.join(DIR_SALIDA, f"{nombre_csv}.csv")
    if not os.path.exists(ruta):
        print(f"  [AVISO] No encontrado para carga: {ruta}")
        return

    df = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    if df.empty:
        print(f"  [AVISO] {nombre_csv}.csv está vacío, no se carga.")
        return

    cols_archivo = list(df.columns)
    extra = [c for c in cols_archivo if c not in columnas]
    faltan = [c for c in columnas if c not in cols_archivo]
    if extra:
        print(f"    [INFO] Columnas extra en {nombre_csv}.csv (se ignorarán): {extra}")
    if faltan:
        print(f"    [INFO] Columnas esperadas que no están en {nombre_csv}.csv (se enviarán como NULL): {faltan}")

    # Proteger PK de partidos si llega algún id_partido repetido.
    if tabla == "partidos" and "id_partido" in df.columns:
        try:
            usados = [int(x) for x in df["id_partido"] if x not in (None, "")]
            max_id = max(usados) if usados else 0
        except ValueError:
            max_id = 0

        siguiente_id = max_id + 1
        vistos = {}
        for idx, valor in df["id_partido"].items():
            if valor in (None, ""):
                continue
            if valor not in vistos:
                vistos[valor] = 1
            else:
                df.at[idx, "id_partido"] = str(siguiente_id)
                siguiente_id += 1

    df = df.where(df != "", None)

    def normalizar_valor(col, v, tabla_actual):
        if v is None:
            return None
        if isinstance(v, float) and math.isnan(v):
            return None

        if isinstance(v, str):
            txt = v.strip()
            if txt.lower() in ("nan", "none", "null"):
                return None
            if txt in ("-", "–", "—"):
                return None

            if tabla_actual == "mundiales" and col in ("selecciones_participan", "partidos", "goles"):
                m = re.match(r"^-?\d+", txt)
                if m:
                    return m.group(0)
                return None

            if tabla_actual in ("jugadores", "planteles") and col == "fecha_nacimiento":
                meses = {
                    "enero": 1,
                    "febrero": 2,
                    "marzo": 3,
                    "abril": 4,
                    "mayo": 5,
                    "junio": 6,
                    "julio": 7,
                    "agosto": 8,
                    "septiembre": 9,
                    "setiembre": 9,
                    "octubre": 10,
                    "noviembre": 11,
                    "diciembre": 12,
                }
                t = txt.lower()
                m = re.match(r"^(\d{1,2})\s+de\s+([a-záéíóúñ]+)\s+de\s+(\d{4})$", t)
                if m:
                    dia = int(m.group(1))
                    mes_nombre = m.group(2)
                    anio = int(m.group(3))
                    mes = meses.get(mes_nombre)
                    if mes:
                        try:
                            return datetime.date(anio, mes, dia).isoformat()
                        except ValueError:
                            return None
                return None

            if tabla_actual == "partidos" and col == "fecha":
                try:
                    return datetime.datetime.strptime(txt, "%d-%b-%Y").date().isoformat()
                except ValueError:
                    return None

            return txt

        return v

    cols = ", ".join(columnas)
    placeholders = ", ".join(["%s"] * len(columnas))
    sql = f"INSERT INTO {tabla} ({cols}) VALUES ({placeholders})"

    data = []
    for _, row in df.iterrows():
        fila = []
        for col in columnas:
            if col not in df.columns:
                fila.append(None)
                continue
            fila.append(normalizar_valor(col, row[col], tabla))
        data.append(tuple(fila))

    cursor.executemany(sql, data)
    print(f"  Cargadas {cursor.rowcount} filas en {tabla}")


def cargar_bd():
    print("\n" + "=" * 60)
    print("  Cargando CSVs en la base de datos mundiales")
    print("=" * 60)

    conn = obtener_conexion()
    try:
        cur = conn.cursor()

        tablas_reset = [
            "partido_goles",
            "partido_jugadores",
            "planteles",
            "jugadores_por_mundial",
            "tarjetas",
            "premios",
            "goleadores",
            "posiciones_finales",
            "grupos",
            "partidos",
            "jugador_camisetas",
            "seleccion_titulos",
            "jugadores",
            "mundiales",
            "selecciones",
        ]

        print("\n── Limpiando tablas de destino (TRUNCATE)...")
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        for t in tablas_reset:
            try:
                cur.execute(f"TRUNCATE TABLE {t}")
            except Exception as e:
                print(f"  [AVISO] No se pudo truncar {t}: {e}")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

        pasos = [
            (
                "selecciones",
                "selecciones",
                [
                    "id_seleccion",
                    "nombre",
                    "mundiales_jugados",
                    "campeon_veces",
                    "subcampeon_veces",
                    "posicion_historica",
                    "partidos_jugados",
                    "partidos_ganados",
                    "partidos_empatados",
                    "partidos_perdidos",
                    "goles_favor",
                    "goles_contra",
                    "diferencia_gol",
                ],
            ),
            (
                "mundiales",
                "mundiales",
                [
                    "id_mundial",
                    "anio",
                    "id_organizador",
                    "id_campeon",
                    "selecciones_participan",
                    "partidos",
                    "goles",
                    "promedio_gol",
                ],
            ),
            (
                "jugadores",
                "jugadores",
                [
                    "id_jugador",
                    "source_url",
                    "nombre",
                    "nombre_completo",
                    "fecha_nacimiento",
                    "lugar_nacimiento",
                    "posicion",
                    "id_seleccion_actual",
                    "altura_cm",
                    "apodo",
                    "total_mundiales",
                    "total_partidos",
                    "total_goles",
                    "promedio_gol",
                ],
            ),
            ("seleccion_titulos", "seleccion_titulos", ["id_titulo", "id_seleccion", "id_mundial", "tipo"]),
            ("jugador_camisetas", "jugador_camisetas", ["id_jugador_camiseta", "id_jugador", "id_mundial", "numero"]),
            (
                "partidos",
                "partidos",
                [
                    "id_partido",
                    "source_url",
                    "id_mundial",
                    "numero_partido",
                    "fecha",
                    "etapa",
                    "id_local",
                    "goles_local",
                    "goles_visitante",
                    "id_visitante",
                ],
            ),
            (
                "grupos",
                "grupos",
                [
                    "id_mundial",
                    "grupo",
                    "id_seleccion",
                    "posicion",
                    "pj",
                    "pg",
                    "pe",
                    "pp",
                    "gf",
                    "gc",
                    "dif",
                    "pts",
                    "clasificado",
                ],
            ),
            (
                "posiciones_finales",
                "posiciones_finales",
                ["id_mundial", "id_seleccion", "posicion", "etapa", "pts", "pj", "pg", "pe", "pp", "gf", "gc", "dif"],
            ),
            ("goleadores", "goleadores", ["id_mundial", "id_jugador", "posicion", "goles", "partidos", "promedio_gol"]),
            ("premios", "premios", ["id_mundial", "tipo_premio", "id_jugador", "id_seleccion"]),
            (
                "tarjetas",
                "tarjetas",
                ["id_mundial", "id_jugador", "id_seleccion", "amarillas", "rojas", "rojas_directas", "rojas_x2amarillas", "partidos"],
            ),
            (
                "jugadores_por_mundial",
                "jugadores_por_mundial",
                [
                    "id_jugador",
                    "id_mundial",
                    "id_seleccion",
                    "camiseta",
                    "posicion",
                    "jugados",
                    "titular",
                    "capitan",
                    "no_jugo",
                    "goles",
                    "promedio_gol",
                    "tarjetas_amarillas",
                    "tarjetas_rojas",
                    "pg",
                    "pe",
                    "pp",
                    "posicion_final",
                ],
            ),
            (
                "planteles",
                "planteles",
                ["id_mundial", "id_seleccion", "id_jugador", "camiseta", "posicion_grupo", "fecha_nacimiento", "altura_cm", "club"],
            ),
            (
                "partido_jugadores",
                "partido_jugadores",
                [
                    "id_mundial",
                    "id_partido",
                    "id_jugador",
                    "id_seleccion",
                    "camiseta",
                    "posicion",
                    "rol",
                    "capitan",
                    "minuto_entrada",
                    "minuto_salida",
                    "goles_count",
                ],
            ),
            ("partido_goles", "partido_goles", ["id_mundial", "id_partido", "id_jugador", "id_seleccion", "minuto", "tipo_gol"]),
        ]

        for nombre_csv, tabla, columnas in pasos:
            print(f"\n→ Cargando {nombre_csv}.csv en tabla {tabla}...")
            cargar_csv_a_tabla(cur, nombre_csv, tabla, columnas)
            conn.commit()

        print("\n" + "=" * 60)
        print("  Carga completada en la base de datos.")
        print("=" * 60)

    finally:
        conn.close()


if __name__ == "__main__":
    cargar_bd()
