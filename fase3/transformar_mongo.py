

import os
import re
import csv
import json
import unicodedata
import pandas as pd
from collections import defaultdict

DIR_ENTRADA = "./output"
DIR_SALIDA  = "./output_mongo"
os.makedirs(DIR_SALIDA, exist_ok=True)



#   unificar mas nombres historicos(se pueden agregar mas , solo es colocando el nombre )

ALIASES = {
    "Alemania Occidental": "Alemania",
    
}

def canonical(nombre):
    s = str(nombre).strip()
    return ALIASES.get(s, s)



#  I/O helpers


def detectar_sep(ruta):
    with open(ruta, "r", encoding="utf-8-sig") as f:
        muestra = f.read(4096)
    try:
        return csv.Sniffer().sniff(muestra, delimiters=",;").delimiter
    except csv.Error:
        return ","


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


def vacio(v):
    return str(v).strip() in ("", "nan", "None", "NULL", "-", "–", "—")


def entero(v):
    s = str(v).strip()
    if vacio(s):
        return None
    m = re.search(r"-?\d+", s)
    return int(m.group()) if m else None


def decimal(v):
    s = str(v).strip().replace(",", ".")
    if vacio(s):
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def texto(v):
    s = str(v).strip()
    return s if s and not vacio(s) else None


def altura_cm(v):
    s = str(v).strip().lower().replace(",", ".")
    if vacio(s):
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*m", s)
    if m:
        try:
            return int(float(m.group(1)) * 100)
        except ValueError:
            return None
    try:
        f = float(s)
        return int(f * 100) if f < 3.0 else int(f)
    except ValueError:
        return None


def slug_url(url):
    """Extrae el nombre de archivo de cualquier URL (relativa o absoluta)."""
    s = str(url).strip()
    return s.split("/")[-1] if s else ""


def col_canonical(df, col):
    """Aplica canonical() sobre una columna, in-place."""
    if df is not None and col in df.columns:
        df[col] = df[col].apply(canonical)



#  Derivar subcampeon desde posiciones_finales (posicion == 2)

def build_subcampeon_anios_por_seleccion(df_pos):
    mapa = defaultdict(list)
    if df_pos is None:
        return mapa

    for _, r in df_pos.iterrows():
        if str(r.get("posicion", "")).strip() == "2":
            anio = texto(r.get("mundial", ""))
            sel = canonical(texto(r.get("seleccion", "")) or "")
            if anio and sel:
                mapa[sel].append(anio)

    for sel in mapa:
        mapa[sel] = sorted(set(mapa[sel]), key=int)

    return mapa

def build_subcampeon_map(df_pos):
    mapa = {}
    if df_pos is None:
        return mapa
    for _, r in df_pos.iterrows():
        if str(r.get("posicion", "")).strip() == "2":
            anio = texto(r.get("mundial", ""))
            sel  = canonical(texto(r.get("seleccion", "")) or "")
            if anio and sel:
                mapa[anio] = sel
    return mapa



#  indices en memoria


def build_index_mundiales(df, subcampeon_map):
    idx = {}
    for _, r in df.iterrows():
        anio = texto(r.get("anio", ""))
        if not anio:
            continue
        # "104 (0 ya jugados)" → extraer primer número
        partidos_raw = texto(r.get("partidos", "")) or ""
        m = re.search(r"\d+", partidos_raw)
        partidos_total = int(m.group()) if m else None

        idx[anio] = {
            "anio":           int(anio),
            "organizador":    canonical(texto(r.get("organizador", "")) or "") or None,
            "campeon":        canonical(texto(r.get("campeon", ""))     or "") or None,
            "subcampeon":     subcampeon_map.get(anio),
            "selecciones":    entero(r.get("selecciones", "")),
            "partidos_total": partidos_total,
            "goles_total":    entero(r.get("goles", "")),
            "promedio_gol":   decimal(r.get("promedio_gol", "")),
        }
    return idx


def build_index_selecciones(df, subcampeon_anios_map):
    idx = {}

    for _, r in df.iterrows():
        nom = canonical(texto(r.get("seleccion", "")) or "")
        if not nom:
            continue

        campeon_anios = [
            a.strip() for a in str(r.get("campeon_anios", "")).split(",")
            if re.match(r"^\d{4}$", a.strip())
        ]

        subcampeon_anios_csv = [
            a.strip() for a in str(r.get("subcampeon_anios", "")).split(",")
            if re.match(r"^\d{4}$", a.strip())
        ]

        # prioridad a lo derivado desde posiciones_finales
        subcampeon_anios = sorted(
            set(subcampeon_anios_csv + subcampeon_anios_map.get(nom, [])),
            key=int
        )

        if nom in idx:
            # fusionar filas duplicadas por alias
            idx[nom]["campeon_anios"] = sorted(
                set(idx[nom]["campeon_anios"] + campeon_anios),
                key=int
            )

            idx[nom]["subcampeon_anios"] = sorted(
                set(idx[nom]["subcampeon_anios"] + subcampeon_anios),
                key=int
            )

            # asegurar coherencia del conteo
            idx[nom]["subcampeon_veces"] = len(idx[nom]["subcampeon_anios"])
            idx[nom]["campeon_veces"] = len(idx[nom]["campeon_anios"]) if idx[nom]["campeon_anios"] else idx[nom].get("campeon_veces")

            for campo in (
                "mundiales_jugados",
                "posicion_historica",
                "partidos_jugados",
                "partidos_ganados",
                "partidos_empatados",
                "partidos_perdidos",
                "goles_favor",
                "goles_contra",
                "diferencia_gol",
            ):
                v_nuevo = entero(r.get(campo, ""))
                v_viejo = idx[nom].get(campo)
                if v_nuevo is not None and (v_viejo is None or v_nuevo > v_viejo):
                    idx[nom][campo] = v_nuevo

            continue

        idx[nom] = {
            "nombre": nom,
            "mundiales_jugados": entero(r.get("mundiales_jugados", "")),
            "campeon_veces": len(campeon_anios) if campeon_anios else entero(r.get("campeon_veces", "")),
            "campeon_anios": sorted(set(campeon_anios), key=int) if campeon_anios else [],
            "subcampeon_veces": len(subcampeon_anios) if subcampeon_anios else entero(r.get("subcampeon_veces", "")),
            "subcampeon_anios": subcampeon_anios,
            "posicion_historica": entero(r.get("posicion_historica", "")),
            "partidos_jugados": entero(r.get("partidos_jugados", "")),
            "partidos_ganados": entero(r.get("partidos_ganados", "")),
            "partidos_empatados": entero(r.get("partidos_empatados", "")),
            "partidos_perdidos": entero(r.get("partidos_perdidos", "")),
            "goles_favor": entero(r.get("goles_favor", "")),
            "goles_contra": entero(r.get("goles_contra", "")),
            "diferencia_gol": entero(r.get("diferencia_gol", "")),
        }

    return idx



#  indices de goles y alineaciones por partido 


def build_goles_por_partido(df):
    agg = defaultdict(list)
    if df is None:
        return agg
    for _, r in df.iterrows():
        slug = slug_url(r.get("url_partido", ""))
        if not slug:
            continue
        agg[slug].append({
            "jugador":   texto(r.get("jugador", "")),
            "seleccion": canonical(texto(r.get("seleccion", "")) or ""),
            "minuto":    texto(r.get("minuto", "")),
            "tipo_gol":  texto(r.get("tipo_gol", "")),
        })
    return agg


def build_alineaciones_por_partido(df):
    """slug → {nombre_seleccion: [jugadores]}"""
    agg = defaultdict(lambda: defaultdict(list))
    if df is None:
        return agg
    for _, r in df.iterrows():
        slug = slug_url(r.get("url_partido", ""))
        sel  = canonical(texto(r.get("seleccion", "")) or "")
        if not slug or not sel:
            continue
        agg[slug][sel].append({
            "jugador":        texto(r.get("jugador", "")),
            "camiseta":       entero(r.get("camiseta", "")),
            "posicion":       texto(r.get("posicion", "")),
            "rol":            texto(r.get("rol", "")),
            "capitan":        str(r.get("capitan","")).strip().lower() in ("si","sí","1","true"),
            "minuto_entrada": texto(r.get("minuto_entrada", "")),
            "minuto_salida":  texto(r.get("minuto_salida", "")),
        })
    return agg



#  Agrupadores


def agrupar_partidos(df, goles_x_slug, alin_x_slug):
    agg = defaultdict(list)
    if df is None:
        return agg
    for _, r in df.iterrows():
        anio      = texto(r.get("mundial", ""))
        local     = canonical(texto(r.get("local", ""))     or "") or None
        visitante = canonical(texto(r.get("visitante", "")) or "") or None
        slug      = slug_url(r.get("url_partido", ""))
        if not anio:
            continue

        alin = alin_x_slug.get(slug, {})
        agg[anio].append({
            "numero":               entero(r.get("num", "")),
            "fecha":                texto(r.get("fecha", "")),
            "etapa":                texto(r.get("etapa", "")),
            "local":                local,
            "goles_local":          entero(r.get("goles_local", "")),
            "goles_visitante":      entero(r.get("goles_visitante", "")),
            "visitante":            visitante,
            "url_partido":          slug or None,
            "goles":                goles_x_slug.get(slug, []),
            "alineacion_local":     alin.get(local, [])     if local     else [],
            "alineacion_visitante": alin.get(visitante, []) if visitante else [],
        })
    return agg


def agrupar_grupos(df):
    agg = defaultdict(list)
    if df is None:
        return agg
    for _, r in df.iterrows():
        anio = texto(r.get("mundial", ""))
        if not anio:
            continue
        agg[anio].append({
            "grupo":       texto(r.get("grupo", "")),
            "seleccion":   canonical(texto(r.get("seleccion", "")) or ""),
            "posicion":    entero(r.get("posicion", "")),
            "pj":  entero(r.get("pj", "")),
            "pg":  entero(r.get("pg", "")),
            "pe":  entero(r.get("pe", "")),
            "pp":  entero(r.get("pp", "")),
            "gf":  entero(r.get("gf", "")),
            "gc":  entero(r.get("gc", "")),
            "dif": entero(r.get("dif", "")),
            "pts": entero(r.get("pts", "")),
            "clasificado": str(r.get("clasificado","")).strip().lower() in ("si","sí","1","true"),
        })
    return agg


def agrupar_posiciones_finales(df):
    agg = defaultdict(list)
    if df is None:
        return agg
    for _, r in df.iterrows():
        anio = texto(r.get("mundial", ""))
        if not anio:
            continue
        agg[anio].append({
            "posicion":  entero(r.get("posicion", "")),
            "seleccion": canonical(texto(r.get("seleccion", "")) or ""),
            "etapa":     texto(r.get("etapa", "")),
            "pts": entero(r.get("pts", "")),
            "pj":  entero(r.get("pj", "")),
            "pg":  entero(r.get("pg", "")),
            "pe":  entero(r.get("pe", "")),
            "pp":  entero(r.get("pp", "")),
            "gf":  entero(r.get("gf", "")),
            "gc":  entero(r.get("gc", "")),
            "dif": entero(r.get("dif", "")),
        })
    return agg


def agrupar_goleadores(df):
    agg = defaultdict(list)
    if df is None:
        return agg
    for _, r in df.iterrows():
        anio = texto(r.get("mundial", ""))
        if not anio:
            continue
        agg[anio].append({
            "posicion":    entero(r.get("posicion", "")),
            "jugador":     texto(r.get("jugador", "")),
            "seleccion":   canonical(texto(r.get("seleccion", "")) or ""),
            "goles":       entero(r.get("goles", "")),
            "partidos":    entero(r.get("partidos", "")),
            "promedio_gol":decimal(r.get("promedio_gol", "")),
        })
    return agg


def agrupar_premios(df):
    agg = defaultdict(list)
    if df is None:
        return agg
    for _, r in df.iterrows():
        anio    = texto(r.get("mundial", ""))
        ganador = texto(r.get("jugador_o_seleccion", ""))
        if not anio or not ganador:
            continue
        agg[anio].append({
            "tipo_premio": texto(r.get("tipo_premio", "")),
            "ganador":     canonical(ganador),
        })
    return agg


def agrupar_tarjetas(df):
    agg = defaultdict(list)
    if df is None:
        return agg
    for _, r in df.iterrows():
        anio = texto(r.get("mundial", ""))
        if not anio:
            continue
        agg[anio].append({
            "jugador":           texto(r.get("jugador", "")),
            "seleccion":         canonical(texto(r.get("seleccion", "")) or ""),
            "amarillas":         entero(r.get("amarillas", "")),
            "rojas":             entero(r.get("rojas", "")),
            "rojas_directas":    entero(r.get("rd", "")),
            "rojas_x2amarillas": entero(r.get("ta2", "")),
            "partidos":          entero(r.get("partidos", "")),
        })
    return agg


def agrupar_planteles(df):
    agg = defaultdict(list)
    if df is None:
        return agg
    for _, r in df.iterrows():
        anio = texto(r.get("mundial", ""))
        sel  = canonical(texto(r.get("seleccion", "")) or "")
        if not anio or not sel:
            continue
        agg[(anio, sel)].append({
            "camiseta":        entero(r.get("camiseta", "")),
            "jugador":         texto(r.get("jugador", "")),
            "posicion":        texto(r.get("posicion_grupo", "")),
            "fecha_nacimiento":texto(r.get("fecha_nacimiento", "")),
            "altura_cm":       altura_cm(r.get("altura", "")),
            "club":            texto(r.get("club", "")),
        })
    return agg


def agrupar_jugadores_por_mundial(df):
    agg = defaultdict(list)
    if df is None:
        return agg
    for _, r in df.iterrows():
        anio = texto(r.get("mundial", ""))
        sel  = canonical(texto(r.get("seleccion", "")) or "")
        if not anio or not sel:
            continue
        agg[(anio, sel)].append({
            "jugador":            texto(r.get("jugador", "")),
            "camiseta":           entero(r.get("camiseta", "")),
            "posicion":           texto(r.get("posicion", "")),
            "partidos_jugados":   entero(r.get("jugados", "")),
            "titular":            entero(r.get("titular", "")),
            "capitan":            str(r.get("capitan","")).strip() in ("1","Si","Sí","si","sí"),
            "goles":              entero(r.get("goles", "")),
            "tarjetas_amarillas": entero(r.get("tarjetas_amarillas", "")),
            "tarjetas_rojas":     entero(r.get("tarjetas_rojas", "")),
            "pg":  entero(r.get("pg", "")),
            "pe":  entero(r.get("pe", "")),
            "pp":  entero(r.get("pp", "")),
        })
    return agg



#  Construccion de documentos MongoDB


def construir_mundiales(
    idx_mund, partidos_x_anio, grupos_x_anio,
    posiciones_x_anio, goleadores_x_anio, premios_x_anio,
    tarjetas_x_anio, planteles_x_anio_sel
):
    docs = []
    for anio, info in sorted(idx_mund.items(), key=lambda x: int(x[0])):
        planteles_lista = [
            {"seleccion": sel, "jugadores": jugs}
            for (a, sel), jugs in sorted(planteles_x_anio_sel.items())
            if a == anio
        ]
        docs.append({
            "anio":              info["anio"],
            "organizador":       info["organizador"],
            "campeon":           info["campeon"],
            "subcampeon":        info["subcampeon"],
            "selecciones_total": info["selecciones"],
            "partidos_total":    info["partidos_total"],
            "goles_total":       info["goles_total"],
            "promedio_gol":      info["promedio_gol"],
            "partidos":          sorted(partidos_x_anio.get(anio, []),
                                        key=lambda x: x.get("numero") or 0),
            "grupos":            grupos_x_anio.get(anio, []),
            "posiciones_finales":sorted(posiciones_x_anio.get(anio, []),
                                        key=lambda x: x.get("posicion") or 99),
            "goleadores":        goleadores_x_anio.get(anio, []),
            "premios":           premios_x_anio.get(anio, []),
            "tarjetas":          tarjetas_x_anio.get(anio, []),
            "planteles":         planteles_lista,
        })
    return docs


def construir_selecciones(
    idx_sel, idx_mund, partidos_x_anio,
    grupos_x_anio, posiciones_x_anio,
    planteles_x_anio_sel, jugadores_x_anio_sel
):
    docs = []
    for nombre, stats in sorted(idx_sel.items()):
        anios_part = set()
        for anio, gl in grupos_x_anio.items():
            if any(g.get("seleccion") == nombre for g in gl):
                anios_part.add(anio)
        for anio, pl in posiciones_x_anio.items():
            if any(p.get("seleccion") == nombre for p in pl):
                anios_part.add(anio)

        participaciones = []
        for anio in sorted(anios_part, key=int):
            info_m    = idx_mund.get(anio, {})
            grupo_info = next((g for g in grupos_x_anio.get(anio, [])
                               if g.get("seleccion") == nombre), None)
            pos_entry  = next((p for p in posiciones_x_anio.get(anio, [])
                               if p.get("seleccion") == nombre), None)
            partidos_sel = [
                p for p in partidos_x_anio.get(anio, [])
                if p.get("local") == nombre or p.get("visitante") == nombre
            ]
            participaciones.append({
                "anio":           int(anio),
                "fue_sede":       info_m.get("organizador") == nombre,
                "fue_campeon":    info_m.get("campeon")     == nombre,
                "fue_subcampeon": info_m.get("subcampeon")  == nombre,
                "grupo":          grupo_info,
                "posicion_final": pos_entry.get("posicion") if pos_entry else None,
                "etapa_final":    pos_entry.get("etapa")    if pos_entry else None,
                "partidos":       sorted(partidos_sel, key=lambda x: x.get("numero") or 0),
                "plantel":        sorted(planteles_x_anio_sel.get((anio, nombre), []),
                                         key=lambda x: x.get("camiseta") or 99),
                "estadisticas_jugadores": jugadores_x_anio_sel.get((anio, nombre), []),
            })

        sedes = sorted(
            [int(a) for a, i in idx_mund.items() if i.get("organizador") == nombre]
        )
        docs.append({**stats, "sedes": sedes, "participaciones": participaciones})
    return docs



#  Main


def main():
    
    print("  Transformador CSV → MongoDB")
    print("=" * 62)

    print("\n──  CSVs leidos")
    df_mund   = leer("mundiales")
    df_sel    = leer("selecciones")
    df_part   = leer("partidos")
    df_grupos = leer("grupos")
    df_pos    = leer("posiciones_finales")
    df_gol    = leer("goleadores")
    df_prem   = leer("premios")
    df_tarj   = leer("tarjetas")
    df_plant  = leer("planteles")
    df_jpmund = leer("jugadores_por_mundial")
    df_pgoles = leer("partido_goles")
    df_pjug   = leer("partido_jugadores")

    if df_mund is None or df_sel is None or df_part is None:
        print("\n[ERROR] Faltan CSVs base: mundiales, selecciones, partidos.")
        return

    #  Aplicar aliases en todos los CSVs
    print(f"\n── Aplicando aliases: {ALIASES}")
    col_canonical(df_mund,   "campeon")
    col_canonical(df_mund,   "organizador")
    for df, cols in [
        (df_part,   ["local", "visitante"]),
        (df_grupos, ["seleccion"]),
        (df_pos,    ["seleccion"]),
        (df_gol,    ["seleccion"]),
        (df_tarj,   ["seleccion"]),
        (df_plant,  ["seleccion"]),
        (df_jpmund, ["seleccion"]),
        (df_pgoles, ["seleccion"]),
        (df_pjug,   ["seleccion"]),
    ]:
        if df is not None:
            for col in cols:
                col_canonical(df, col)

    # Agregar selecciones historicas faltantes
    nombres_sel = set(canonical(n) for n in df_sel["seleccion"].astype(str).str.strip())
    nuevos = set()
    for df_check, cols in [
        (df_part,   ["local", "visitante"]),
        (df_grupos, ["seleccion"]),
        (df_pos,    ["seleccion"]),
    ]:
        if df_check is None:
            continue
        for col in cols:
            for n in df_check[col].dropna().unique():
                n = canonical(n.strip())
                if n and n not in nombres_sel:
                    nuevos.add(n)
                    nombres_sel.add(n)

    if nuevos:
        print(f"  Agregando {len(nuevos)} selecciones historicas: {sorted(nuevos)}")
        df_sel = pd.concat(
            [df_sel, pd.DataFrame([{"seleccion": n} for n in sorted(nuevos)])],
            ignore_index=True
        )

    print("\n── Construccion indices")
    subcampeon_map = build_subcampeon_map(df_pos)
    subcampeon_anios_map = build_subcampeon_anios_por_seleccion(df_pos)

    idx_mund = build_index_mundiales(df_mund, subcampeon_map)
    idx_sel = build_index_selecciones(df_sel, subcampeon_anios_map)
    print(f"  Mundiales: {len(idx_mund)}  |  Selecciones: {len(idx_sel)}")

    print("\n── Indexando goles y alineaciones por partido")
    goles_x_slug = build_goles_por_partido(df_pgoles)
    alin_x_slug  = build_alineaciones_por_partido(df_pjug)
    print(f"  Slugs con goles: {len(goles_x_slug)}  |  con alineaciones: {len(alin_x_slug)}")

    print("\n── Agrupando datos")
    partidos_x_anio      = agrupar_partidos(df_part, goles_x_slug, alin_x_slug)
    grupos_x_anio        = agrupar_grupos(df_grupos)
    posiciones_x_anio    = agrupar_posiciones_finales(df_pos)
    goleadores_x_anio    = agrupar_goleadores(df_gol)
    premios_x_anio       = agrupar_premios(df_prem)
    tarjetas_x_anio      = agrupar_tarjetas(df_tarj)
    planteles_x_anio_sel = agrupar_planteles(df_plant)
    jugadores_x_anio_sel = agrupar_jugadores_por_mundial(df_jpmund)

    total_goles_emb = sum(
        len(p.get("goles", []))
        for v in partidos_x_anio.values() for p in v
    )
    print(f"  Partidos: {sum(len(v) for v in partidos_x_anio.values())}")
    print(f"  Goles incrustados en partidos: {total_goles_emb}")

    print("\n── Construccion de los documentos")
    docs_mundiales = construir_mundiales(
        idx_mund, partidos_x_anio, grupos_x_anio,
        posiciones_x_anio, goleadores_x_anio, premios_x_anio,
        tarjetas_x_anio, planteles_x_anio_sel
    )
    docs_selecciones = construir_selecciones(
        idx_sel, idx_mund, partidos_x_anio,
        grupos_x_anio, posiciones_x_anio,
        planteles_x_anio_sel, jugadores_x_anio_sel
    )
    print(f"  Docs mundiales   : {len(docs_mundiales)}")
    print(f"  Docs selecciones : {len(docs_selecciones)}")

    print("\n── Guardando JSON")
    for nombre, docs in [("mundiales", docs_mundiales), ("selecciones", docs_selecciones)]:
        ruta = os.path.join(DIR_SALIDA, f"{nombre}.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
        print(f"  → {ruta}")

    print("\n" + "=" * 62)
    print("  Transformacion completada")
    


if __name__ == "__main__":
    main()
