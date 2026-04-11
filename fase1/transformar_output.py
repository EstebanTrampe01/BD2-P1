"""Transforma CSV crudos de output/ a output_db/ para la BD normalizada."""

import os
import re
import csv
import unicodedata
import pandas as pd

DIR_ENTRADA = "./output"
DIR_SALIDA  = "./output_db"
 
os.makedirs(DIR_SALIDA, exist_ok=True)
 
 
def detectar_sep(ruta):
    with open(ruta, "r", encoding="utf-8-sig") as f:
        muestra = f.read(4096)
    return csv.Sniffer().sniff(muestra, delimiters=",;").delimiter
 
 
def leer(nombre):
    ruta = os.path.join(DIR_ENTRADA, f"{nombre}.csv")
    if not os.path.exists(ruta):
        print(f"  [AVISO] No encontrado: {nombre}.csv — se omite.")
        return None
    sep = detectar_sep(ruta)
    df = pd.read_csv(ruta, sep=sep, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    df.columns = df.columns.str.strip().str.lower()
    print(f"  Leído {nombre}.csv  ({len(df)} filas)")
    return df
 
 
def guardar(df, nombre):
    # Evitar IDs con formato float en CSV final (ej. "18.0")
    for col in [c for c in df.columns if c.startswith("id_")]:
        df[col] = df[col].apply(_limpiar_id)

    ruta = os.path.join(DIR_SALIDA, f"{nombre}.csv")
    df.to_csv(ruta, index=False, encoding="utf-8")
    print(f"  Guardado {nombre}.csv  ({len(df)} filas)")
 
 
def vacío(v):
    return str(v).strip() in ("", "nan", "None", "NULL")


def _limpiar_id(v):
    s = str(v).strip()
    if s in ("", "nan", "None", "NULL"):
        return ""
    m = re.match(r"^(\d+)\.0+$", s)
    if m:
        return m.group(1)
    return s


def _extraer_entero(v, permitir_negativo=False):
    s = str(v).strip()
    if s in ("", "nan", "None", "NULL", "-", "–", "—"):
        return ""
    patron = r"-?\d+" if permitir_negativo else r"\d+"
    m = re.search(patron, s)
    if not m:
        return ""
    return m.group(0)


def _extraer_decimal(v):
    s = str(v).strip().replace(",", ".")
    if s in ("", "nan", "None", "NULL", "-", "–", "—"):
        return ""
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return ""
    return m.group(0)


def _altura_a_cm(v):
    s = str(v).strip().lower().replace(",", ".")
    if s in ("", "nan", "none", "null", "-", "–", "—"):
        return ""

    m = re.search(r"(\d+(?:\.\d+)?)\s*m", s)
    if m:
        try:
            return str(int(float(m.group(1)) * 100))
        except ValueError:
            return ""

    try:
        f = float(s)
        return str(int(f * 100)) if f < 3.0 else str(int(f))
    except ValueError:
        return ""
 
 
def construir_mapa_selecciones(df):
    nombres = df["seleccion"].dropna().unique()
    return {nombre.strip(): idx + 1 for idx, nombre in enumerate(sorted(nombres))}
 
 
def _normalizar_clave_url_jugador(u):
    s = str(u).strip()
    if not s:
        return ""
    return s.split("/")[-1]


def _normalizar_clave_url_partido(u):
    s = str(u).strip()
    if not s:
        return ""
    return s.split("/")[-1]


def _slug_nombre_a_php(nombre):
    s = str(nombre).strip().lower()
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    if not s:
        return ""
    return f"{s}.php"


def construir_mapa_jugadores(df):
    urls = df["url"].dropna().unique()
    return {_normalizar_clave_url_jugador(url): idx + 1 for idx, url in enumerate(urls)}


def construir_mapa_jugadores_por_nombre(df, mapa_jug):
    nombres = df.get("nombre", pd.Series([""] * len(df))).astype(str)
    urls    = df.get("url", pd.Series([""] * len(df))).astype(str)
    mapa = {}
    for nom, url in zip(nombres, urls):
        nom = nom.strip()
        url = _normalizar_clave_url_jugador(url)
        if not nom or not url:
            continue
        id_jug = mapa_jug.get(url)
        if id_jug is not None and nom not in mapa:
            mapa[nom] = id_jug
    return mapa
 
 
def construir_mapa_mundiales(df):
    anios = sorted(df["anio"].dropna().unique(), key=lambda x: int(x))
    return {str(a).strip(): idx + 1 for idx, a in enumerate(anios)}
 
 
def construir_mapa_partidos(df):
    urls = df["url_partido"].dropna().unique()
    return {
        _normalizar_clave_url_partido(url): idx + 1
        for idx, url in enumerate(urls)
        if _normalizar_clave_url_partido(url)
    }
 
 
def transformar_selecciones(df, mapa_sel):
    out = pd.DataFrame()
    out["id_seleccion"]       = df["seleccion"].apply(lambda x: mapa_sel.get(x.strip()))
    out["nombre"]             = df["seleccion"].str.strip()
    out["mundiales_jugados"]  = df.get("mundiales_jugados", "")
    out["campeon_veces"]      = df.get("campeon_veces", "")
    out["subcampeon_veces"]   = df.get("subcampeon_veces", "")
    out["posicion_historica"] = df.get("posicion_historica", "")
    out["partidos_jugados"]   = df.get("partidos_jugados", "")
    out["partidos_ganados"]   = df.get("partidos_ganados", "")
    out["partidos_empatados"] = df.get("partidos_empatados", "")
    out["partidos_perdidos"]  = df.get("partidos_perdidos", "")
    out["goles_favor"]        = df.get("goles_favor", "")
    out["goles_contra"]       = df.get("goles_contra", "")
    out["diferencia_gol"]     = df["diferencia_gol"].apply(
        lambda x: str(x).replace("+", "").strip() if not vacío(x) else ""
    )
    return out
 
 
def transformar_mundiales(df, mapa_sel, mapa_mund):
    out = pd.DataFrame()
    out["id_mundial"]             = df["anio"].apply(lambda x: mapa_mund.get(str(x).strip()))
    out["anio"]                   = df["anio"].str.strip()
    out["id_organizador"]         = df.get("organizador", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["id_campeon"]             = df.get("campeon", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["selecciones_participan"] = df.get("selecciones", pd.Series([""] * len(df))).apply(_extraer_entero)
    out["partidos"]               = df.get("partidos", pd.Series([""] * len(df))).apply(_extraer_entero)
    out["goles"]                  = df.get("goles", pd.Series([""] * len(df))).apply(_extraer_entero)
    out["promedio_gol"]           = df.get("promedio_gol", pd.Series([""] * len(df))).apply(_extraer_decimal)
    return out
 
 
def transformar_seleccion_titulos(df, mapa_sel, mapa_mund):
    filas = []
    id_titulo = 1
    for _, r in df.iterrows():
        sel = r.get("seleccion", "").strip()
        id_sel = mapa_sel.get(sel)
        if not id_sel:
            continue
        for anio in str(r.get("campeon_anios", "")).split(","):
            anio = anio.strip()
            if re.match(r"^\d{4}$", anio):
                id_mund = mapa_mund.get(anio)
                if id_mund:
                    filas.append({
                        "id_titulo":   id_titulo,
                        "id_seleccion": id_sel,
                        "id_mundial":  id_mund,
                        "tipo":        "campeon"
                    })
                    id_titulo += 1
        for anio in str(r.get("subcampeon_anios", "")).split(","):
            anio = anio.strip()
            if re.match(r"^\d{4}$", anio):
                id_mund = mapa_mund.get(anio)
                if id_mund:
                    filas.append({
                        "id_titulo":   id_titulo,
                        "id_seleccion": id_sel,
                        "id_mundial":  id_mund,
                        "tipo":        "subcampeon"
                    })
                    id_titulo += 1
    return pd.DataFrame(filas)
 
 
def transformar_jugadores(df, mapa_sel, mapa_jug):
    out = pd.DataFrame()
    out["id_jugador"]           = df["url"].apply(lambda x: mapa_jug.get(_normalizar_clave_url_jugador(x)))
    out["source_url"]           = df["url"].str.strip()
    out["nombre"]               = df.get("nombre", "")
    out["nombre_completo"]      = df.get("nombre_completo", "")
    out["fecha_nacimiento"]     = df.get("fecha_nacimiento", "")
    out["lugar_nacimiento"]     = df.get("lugar_nacimiento", "")
    out["posicion"]             = df.get("posicion", "")
    out["id_seleccion_actual"]  = df.get("seleccion", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["altura_cm"]            = df.get("altura", pd.Series([""] * len(df))).apply(_altura_a_cm)
    out["apodo"]                = df.get("apodo", "")
    out["total_mundiales"]      = df.get("total_mundiales", "")
    out["total_partidos"]       = df.get("total_partidos", "")
    out["total_goles"]          = df.get("total_goles", "")
    out["promedio_gol"]         = df.get("promedio_gol", "")
    return out
 
 
def transformar_jugador_camisetas(df, mapa_jug, mapa_mund):
    filas = []
    id_c = 1
    for _, r in df.iterrows():
        url    = _normalizar_clave_url_jugador(r.get("url", ""))
        id_jug = mapa_jug.get(url)
        if not id_jug:
            continue
        numeros = str(r.get("numeros_camiseta", "")).strip()
        if vacío(numeros):
            continue
        for num in numeros.split(","):
            num = num.strip()
            if num.isdigit():
                filas.append({
                    "id_jugador_camiseta": id_c,
                    "id_jugador":          id_jug,
                    "id_mundial":          "",   # no disponible en jugadores.csv
                    "numero":              int(num)
                })
                id_c += 1
    return pd.DataFrame(filas)
 
 
def transformar_partidos(df, mapa_sel, mapa_mund, mapa_part):
    out = pd.DataFrame()
    out["id_partido"]       = df["url_partido"].apply(
        lambda x: mapa_part.get(_normalizar_clave_url_partido(x))
    )
    out["source_url"]       = df["url_partido"].str.strip()
    out["id_mundial"]       = df.get("mundial", pd.Series([""] * len(df))).apply(
        lambda x: mapa_mund.get(str(x).strip()) if not vacío(x) else ""
    )
    out["numero_partido"]   = df.get("num", "")
    out["fecha"]            = df.get("fecha", "")
    out["etapa"]            = df.get("etapa", "")
    out["id_local"]         = df.get("local", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["goles_local"]      = df.get("goles_local", "")
    out["goles_visitante"]  = df.get("goles_visitante", "")
    out["id_visitante"]     = df.get("visitante", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )

    # Algunas filas no traen url_partido (ej. partidos futuros).
    # Se generan IDs para mantener PK no nula.
    out["id_partido"] = pd.to_numeric(out["id_partido"], errors="coerce")
    faltantes = out["id_partido"].isna()
    if faltantes.any():
        ids_existentes = out.loc[~faltantes, "id_partido"]
        siguiente = int(ids_existentes.max()) + 1 if not ids_existentes.empty else 1
        for idx in out.index[faltantes]:
            out.at[idx, "id_partido"] = siguiente
            siguiente += 1

    out["id_partido"] = out["id_partido"].astype("Int64").astype(str)
    return out
 
 
def transformar_grupos(df, mapa_sel, mapa_mund):
    out = pd.DataFrame()
    out["id_mundial"]   = df.get("mundial", pd.Series([""] * len(df))).apply(
        lambda x: mapa_mund.get(str(x).strip()) if not vacío(x) else ""
    )
    out["grupo"]        = df.get("grupo", "")
    out["id_seleccion"] = df.get("seleccion", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["posicion"]     = df.get("posicion", "")
    out["pj"]           = df.get("pj", "")
    out["pg"]           = df.get("pg", "")
    out["pe"]           = df.get("pe", "")
    out["pp"]           = df.get("pp", "")
    out["gf"]           = df.get("gf", "")
    out["gc"]           = df.get("gc", "")
    out["dif"]          = df.get("dif", pd.Series([""] * len(df))).apply(
        lambda x: str(x).replace("+", "").strip() if not vacío(x) else ""
    )
    out["pts"]          = df.get("pts", "")
    out["clasificado"]  = df.get("clasificado", pd.Series([""] * len(df))).apply(
        lambda x: 1 if str(x).strip().lower() in ("si", "sí", "s", "1", "true", "yes") else 0
    )
    return out
 
 
def transformar_posiciones_finales(df, mapa_sel, mapa_mund):
    out = pd.DataFrame()
    out["id_mundial"]   = df.get("mundial", pd.Series([""] * len(df))).apply(
        lambda x: mapa_mund.get(str(x).strip()) if not vacío(x) else ""
    )
    out["id_seleccion"] = df.get("seleccion", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["posicion"]     = df.get("posicion", "")
    out["etapa"]        = df.get("etapa", "")
    out["pts"]          = df.get("pts", "")
    out["pj"]           = df.get("pj", "")
    out["pg"]           = df.get("pg", "")
    out["pe"]           = df.get("pe", "")
    out["pp"]           = df.get("pp", "")
    out["gf"]           = df.get("gf", "")
    out["gc"]           = df.get("gc", "")
    out["dif"]          = df.get("dif", pd.Series([""] * len(df))).apply(
        lambda x: str(x).replace("+", "").strip() if not vacío(x) else ""
    )
    return out
 
 
def transformar_goleadores(df, mapa_mund, mapa_jug):
    out = pd.DataFrame()
    out["id_mundial"]   = df.get("mundial", pd.Series([""] * len(df))).apply(
        lambda x: mapa_mund.get(str(x).strip()) if not vacío(x) else ""
    )
    out["id_jugador"]   = df.get("url_jugador", pd.Series([""] * len(df))).apply(
        lambda x: mapa_jug.get(_normalizar_clave_url_jugador(x)) if not vacío(x) else ""
    )
    out["posicion"]     = df.get("posicion", "")
    out["goles"]        = df.get("goles", "")
    out["partidos"]     = df.get("partidos", "")
    out["promedio_gol"] = df.get("promedio_gol", "")
    return out
 
 
def transformar_premios(df, mapa_mund, mapa_jug, mapa_sel):
    out = pd.DataFrame()
    out["id_mundial"]   = df.get("mundial", pd.Series([""] * len(df))).apply(
        lambda x: mapa_mund.get(str(x).strip()) if not vacío(x) else ""
    )
    out["tipo_premio"]  = df.get("tipo_premio", "")
    out["id_jugador"]   = df.get("url_jugador", pd.Series([""] * len(df))).apply(
        lambda x: mapa_jug.get(_normalizar_clave_url_jugador(x)) if not vacío(x) else ""
    )
    out["id_seleccion"] = df.get("jugador_o_seleccion", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    return out
 
 
def transformar_tarjetas(df, mapa_mund, mapa_jug, mapa_sel):
    out = pd.DataFrame()
    out["id_mundial"]          = df.get("mundial", pd.Series([""] * len(df))).apply(
        lambda x: mapa_mund.get(str(x).strip()) if not vacío(x) else ""
    )
    out["id_jugador"]          = df.get("url_jugador", pd.Series([""] * len(df))).apply(
        lambda x: mapa_jug.get(_normalizar_clave_url_jugador(x)) if not vacío(x) else ""
    )
    out["id_seleccion"]        = df.get("seleccion", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["amarillas"]           = df.get("amarillas", "")
    out["rojas"]               = df.get("rojas", "")
    out["rojas_directas"]      = df.get("rd", "")
    out["rojas_x2amarillas"]   = df.get("ta2", "")
    out["partidos"]            = df.get("partidos", "")
    return out
 
 
def transformar_jugadores_por_mundial(df, mapa_mund, mapa_jug, mapa_sel):
    out = pd.DataFrame()
    out["id_jugador"]   = df.get("url_jugador", pd.Series([""] * len(df))).apply(
        lambda x: mapa_jug.get(_normalizar_clave_url_jugador(x)) if not vacío(x) else ""
    )
    out["id_mundial"]   = df.get("mundial", pd.Series([""] * len(df))).apply(
        lambda x: mapa_mund.get(str(x).strip()) if not vacío(x) else ""
    )
    out["id_seleccion"] = df.get("seleccion", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["camiseta"]             = df.get("camiseta", "")
    out["posicion"]             = df.get("posicion", "")
    out["jugados"]              = df.get("jugados", "")
    out["titular"]              = df.get("titular", "")
    out["capitan"]              = df.get("capitan", pd.Series([""] * len(df))).apply(
        lambda x: 1 if str(x).strip().lower() in ("si", "sí", "1", "true") else 0
    )
    out["no_jugo"]              = df.get("no_jugo", "")
    out["goles"]                = df.get("goles", "")
    out["promedio_gol"]         = df.get("promedio_gol", "")
    out["tarjetas_amarillas"]   = df.get("tarjetas_amarillas", "")
    out["tarjetas_rojas"]       = df.get("tarjetas_rojas", "")
    out["pg"]                   = df.get("pg", "")
    out["pe"]                   = df.get("pe", "")
    out["pp"]                   = df.get("pp", "")
    out["posicion_final"]       = df.get("posicion_final", "")
    return out
 
 
def transformar_planteles(df, mapa_mund, mapa_sel, mapa_jug):
    out = pd.DataFrame()
    out["id_mundial"]        = df.get("mundial", pd.Series([""] * len(df))).apply(
        lambda x: mapa_mund.get(str(x).strip()) if not vacío(x) else ""
    )
    out["id_seleccion"]      = df.get("seleccion", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["id_jugador"]        = df.get("url_jugador", pd.Series([""] * len(df))).apply(
        lambda x: mapa_jug.get(_normalizar_clave_url_jugador(x)) if not vacío(x) else ""
    )
    out["camiseta"]          = df.get("camiseta", "")
    out["posicion_grupo"]    = df.get("posicion_grupo", "")
    out["fecha_nacimiento"]  = df.get("fecha_nacimiento", "")
    out["altura_cm"]         = df.get("altura", pd.Series([""] * len(df))).apply(_altura_a_cm)
    out["club"]              = df.get("club", "")

    # La tabla planteles requiere id_jugador NOT NULL.
    # Se filtran filas sin id_jugador.
    out = out[(out["id_jugador"] != "") & out["id_jugador"].notna()].reset_index(drop=True)
    return out
 
 
def transformar_partido_jugadores(df, mapa_mund, mapa_part, mapa_jug, mapa_sel):
    out = pd.DataFrame()
    out["id_mundial"]    = df.get("mundial", pd.Series([""] * len(df))).apply(
        lambda x: mapa_mund.get(str(x).strip()) if not vacío(x) else ""
    )
    out["id_partido"]    = df.get("url_partido", pd.Series([""] * len(df))).apply(
        lambda x: mapa_part.get(_normalizar_clave_url_partido(x)) if not vacío(x) else ""
    )
    out["id_jugador"]    = df.get("url_jugador", pd.Series([""] * len(df))).apply(
        lambda x: mapa_jug.get(_normalizar_clave_url_jugador(x)) if not vacío(x) else ""
    )
    out["id_seleccion"]  = df.get("seleccion", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["camiseta"]       = df.get("camiseta", "")
    out["posicion"]       = df.get("posicion", "")
    out["rol"]            = df.get("rol", "")
    out["capitan"]        = df.get("capitan", pd.Series([""] * len(df))).apply(
        lambda x: 1 if str(x).strip().lower() in ("si", "sí", "1", "true") else 0
    )
    out["minuto_entrada"] = df.get("minuto_entrada", "")
    out["minuto_salida"]  = df.get("minuto_salida", "")
    out["goles_count"]    = df.get("goles_count", "")
    return out
 
 
def transformar_partido_goles(df, mapa_mund, mapa_part, mapa_jug, mapa_sel, mapa_jug_por_nombre):
    out = pd.DataFrame()
    out["id_mundial"]   = df.get("mundial", pd.Series([""] * len(df))).apply(
        lambda x: mapa_mund.get(str(x).strip()) if not vacío(x) else ""
    )
    out["id_partido"]   = df.get("url_partido", pd.Series([""] * len(df))).apply(
        lambda x: mapa_part.get(_normalizar_clave_url_partido(x)) if not vacío(x) else ""
    )
    def mapear_jugador_por_nombre(nombre):
        nom = str(nombre).strip()
        if vacío(nom):
            return ""
        id_j = mapa_jug_por_nombre.get(nom)
        if id_j:
            return id_j
        # Respaldo por nombre.
        return mapa_jug.get(_slug_nombre_a_php(nom), "")

    if "url_jugador" in df.columns:
        out["id_jugador"] = df.get("url_jugador", pd.Series([""] * len(df))).apply(
            lambda x: mapa_jug.get(_normalizar_clave_url_jugador(x)) if not vacío(x) else ""
        )
    else:
        out["id_jugador"] = df.get("jugador", pd.Series([""] * len(df))).apply(
            mapear_jugador_por_nombre
        )
    out["id_seleccion"] = df.get("seleccion", pd.Series([""] * len(df))).apply(
        lambda x: mapa_sel.get(x.strip()) if not vacío(x) else ""
    )
    out["minuto"]       = df.get("minuto", "")
    out["tipo_gol"]     = df.get("tipo_gol", "")
    return out
 
 
def main():
    print("=" * 60)
    print("  Transformador de CSVs — Mundiales de Fútbol")
    print("=" * 60)
 
    print("\n── Leyendo CSVs base para construir mapas de IDs...")
    df_sel  = leer("selecciones")
    df_jug  = leer("jugadores")
    df_mund = leer("mundiales")
    df_part = leer("partidos")

    if df_sel is None or df_jug is None or df_mund is None or df_part is None:
        print("\n[ERROR] Faltan CSVs base. Se necesitan: selecciones, jugadores, mundiales, partidos.")
        return

    nombres_sel = set(df_sel["seleccion"].astype(str).str.strip())
    faltantes_globales = set()

    fuentes_con_seleccion = [
        ("grupos", "seleccion"),
        ("posiciones_finales", "seleccion"),
        ("tarjetas", "seleccion"),
        ("jugadores_por_mundial", "seleccion"),
        ("planteles", "seleccion"),
        ("partido_jugadores", "seleccion"),
        ("partido_goles", "seleccion"),
    ]

    for nombre_csv, col in fuentes_con_seleccion:
        df_tmp = leer(nombre_csv)
        if df_tmp is None or col not in df_tmp.columns:
            continue
        usados = set(df_tmp[col].astype(str).str.strip())
        nuevos = {s for s in (usados - nombres_sel) if s}
        if nuevos:
            faltantes_globales |= nuevos
            nombres_sel |= nuevos

    if faltantes_globales:
        print("\n  [INFO] Agregando selecciones históricas faltantes al catálogo:")
        for nombre in sorted(faltantes_globales):
            print(f"    - {nombre}")
        df_sel = pd.concat([
            df_sel,
            pd.DataFrame([{ "seleccion": n } for n in sorted(faltantes_globales)])
        ], ignore_index=True)

    mapa_sel        = construir_mapa_selecciones(df_sel)
    mapa_jug        = construir_mapa_jugadores(df_jug)
    mapa_mund       = construir_mapa_mundiales(df_mund)
    mapa_part       = construir_mapa_partidos(df_part)
    mapa_jug_nombre = construir_mapa_jugadores_por_nombre(df_jug, mapa_jug)
 
    print(f"\n  Mapas construidos:")
    print(f"    selecciones : {len(mapa_sel):,} entradas")
    print(f"    jugadores   : {len(mapa_jug):,} entradas")
    print(f"    mundiales   : {len(mapa_mund):,} entradas")
    print(f"    partidos    : {len(mapa_part):,} entradas")
 
    print("\n── Transformando tablas...")

    guardar(transformar_mundiales(df_mund, mapa_sel, mapa_mund), "mundiales")

    guardar(transformar_selecciones(df_sel, mapa_sel), "selecciones")
    df_st = transformar_seleccion_titulos(df_sel, mapa_sel, mapa_mund)
    if not df_st.empty:
        guardar(df_st, "seleccion_titulos")
    else:
        print("  [AVISO] seleccion_titulos vacío — revisar campeon_anios/subcampeon_anios en selecciones.csv")
 
    guardar(transformar_jugadores(df_jug, mapa_sel, mapa_jug), "jugadores")
    df_jc = transformar_jugador_camisetas(df_jug, mapa_jug, mapa_mund)
    if not df_jc.empty:
        guardar(df_jc, "jugador_camisetas")
    else:
        print("  [AVISO] jugador_camisetas vacío — revisar numeros_camiseta en jugadores.csv")
 
    guardar(transformar_partidos(df_part, mapa_sel, mapa_mund, mapa_part), "partidos")

    tablas = [
        ("grupos",               lambda df: transformar_grupos(df, mapa_sel, mapa_mund)),
        ("posiciones_finales",   lambda df: transformar_posiciones_finales(df, mapa_sel, mapa_mund)),
        ("goleadores",           lambda df: transformar_goleadores(df, mapa_mund, mapa_jug)),
        ("premios",              lambda df: transformar_premios(df, mapa_mund, mapa_jug, mapa_sel)),
        ("tarjetas",             lambda df: transformar_tarjetas(df, mapa_mund, mapa_jug, mapa_sel)),
        ("jugadores_por_mundial",lambda df: transformar_jugadores_por_mundial(df, mapa_mund, mapa_jug, mapa_sel)),
        ("planteles",            lambda df: transformar_planteles(df, mapa_mund, mapa_sel, mapa_jug)),
        ("partido_jugadores",    lambda df: transformar_partido_jugadores(df, mapa_mund, mapa_part, mapa_jug, mapa_sel)),
        ("partido_goles",        lambda df: transformar_partido_goles(df, mapa_mund, mapa_part, mapa_jug, mapa_sel, mapa_jug_nombre)),
    ]
 
    for nombre, fn in tablas:
        df = leer(nombre)
        if df is not None:
            guardar(fn(df), nombre)
 
    print("\n── Guardando mapas de referencia...")
    pd.DataFrame(list(mapa_jug.items()),  columns=["url_original", "id_jugador"]).to_csv(
        os.path.join(DIR_SALIDA, "_mapa_jugadores.csv"), index=False)
    pd.DataFrame(list(mapa_part.items()), columns=["url_original", "id_partido"]).to_csv(
        os.path.join(DIR_SALIDA, "_mapa_partidos.csv"), index=False)
    pd.DataFrame(list(mapa_sel.items()),  columns=["nombre_original", "id_seleccion"]).to_csv(
        os.path.join(DIR_SALIDA, "_mapa_selecciones.csv"), index=False)
    pd.DataFrame(list(mapa_mund.items()), columns=["anio_original", "id_mundial"]).to_csv(
        os.path.join(DIR_SALIDA, "_mapa_mundiales.csv"), index=False)
    print("  Guardados en output_db/_mapa_*.csv")
 
    print("\n" + "=" * 60)
    print("  Transformación completada.")
    print(f"  CSVs limpios en: {DIR_SALIDA}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
