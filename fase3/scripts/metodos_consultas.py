import re
from pymongo import MongoClient
from typing import Optional

MONGO_URI = "mongodb://mundiales_user:mundiales1234@127.0.0.1:27017/mundiales?authSource=admin"
DB_NAME = "mundiales"


def get_db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[DB_NAME]


def _match_text(value: Optional[str], pattern: Optional[str]) -> bool:
    if pattern is None:
        return True
    if value is None:
        return False
    return pattern.lower() in value.lower()


def _resultado_desde_partido(partido, pais):
    local = partido.get("local")
    visitante = partido.get("visitante")
    gl = partido.get("goles_local")
    gv = partido.get("goles_visitante")

    # Si no hay marcador registrado, no se puede calcular resultado
    if gl is None or gv is None:
        return "Sin resultado registrado"

    if local == pais:
        if gl > gv:
            return "Victoria"
        elif gl < gv:
            return "Derrota"
        else:
            return "Empate"

    if visitante == pais:
        if gv > gl:
            return "Victoria"
        elif gv < gl:
            return "Derrota"
        else:
            return "Empate"

    return "No aplica"


def metodo_info_mundial(anio: int, grupo=None, pais=None, fecha=None) -> dict:
    """
    Método del inciso c.
    Recibe el año del mundial y devuelve toda la información relacionada con ese mundial.
    Filtros opcionales:
      - grupo
      - pais
      - fecha
    """
    db = get_db()
    col = db["mundiales"]

    doc = col.find_one({"anio": int(anio)}, {"_id": 0})
    if not doc:
        return {
            "ok": False,
            "mensaje": f"No se encontró información para el Mundial {anio}"
        }

    partidos = doc.get("partidos", [])
    grupos = doc.get("grupos", [])
    posiciones_finales = doc.get("posiciones_finales", [])
    goleadores = doc.get("goleadores", [])
    premios = doc.get("premios", [])
    tarjetas = doc.get("tarjetas", [])
    planteles = doc.get("planteles", [])

    grupo_norm = grupo.strip().upper() if grupo else None
    pais_norm = pais.strip() if pais else None
    fecha_norm = fecha.strip() if fecha else None

    # 1) filtrar partidos
    if grupo_norm is not None:
        partidos = [
            p for p in partidos
            if _match_text(p.get("etapa", ""), f"Grupo {grupo_norm}")
            or _match_text(p.get("etapa", ""), f"Group {grupo_norm}")
            or _match_text(p.get("etapa", ""), f"Grupo {grupo_norm},")
            or _match_text(p.get("etapa", ""), f"Grupo {grupo_norm} ")
        ]

    if pais_norm is not None:
        partidos = [
            p for p in partidos
            if _match_text(p.get("local", ""), pais_norm)
            or _match_text(p.get("visitante", ""), pais_norm)
        ]

    if fecha_norm is not None:
        partidos = [p for p in partidos if p.get("fecha") == fecha_norm]

    # 2) determinar selecciones activas según los partidos filtrados
    filtros_activos = any(x is not None for x in (grupo_norm, pais_norm, fecha_norm))

    selecciones_en_partidos = set()
    for p in partidos:
        local = p.get("local")
        visitante = p.get("visitante")
        if local:
            selecciones_en_partidos.add(local)
        if visitante:
            selecciones_en_partidos.add(visitante)

    # Si solo se filtró por país y no hubo partidos, mantener el país explícitamente
    # para que al menos el método no pierda contexto del filtro.
    if pais_norm is not None and not selecciones_en_partidos:
        selecciones_en_partidos.add(pais_norm)

    # 3) filtrar grupos
    if filtros_activos:
        grupos = [g for g in grupos if g.get("seleccion") in selecciones_en_partidos]

        if grupo_norm is not None:
            grupos = [g for g in grupos if str(g.get("grupo", "")).upper() == grupo_norm]

    # 4) filtrar posiciones finales, goleadores, tarjetas, planteles
    if filtros_activos:
        posiciones_finales = [
            pf for pf in posiciones_finales
            if pf.get("seleccion") in selecciones_en_partidos
        ]

        goleadores = [
            g for g in goleadores
            if g.get("seleccion") in selecciones_en_partidos
        ]

        tarjetas = [
            t for t in tarjetas
            if t.get("seleccion") in selecciones_en_partidos
        ]

        planteles = [
            pl for pl in planteles
            if pl.get("seleccion") in selecciones_en_partidos
        ]

    # 5) premios: con filtros finos de grupo/fecha no tiene mucho sentido devolverlos completos
    if fecha_norm is not None or grupo_norm is not None:
        premios = []
    elif pais_norm is not None:
        premios = [
            pr for pr in premios
            if _match_text(pr.get("ganador", ""), pais_norm)
        ]

    # 6) mensaje si la combinación de filtros no produjo partidos
    mensaje = None
    if filtros_activos and len(partidos) == 0:
        mensaje = "No hay resultados para la combinación de filtros indicada"

        # Si no hubo partidos, todo lo dependiente de esos partidos debe quedar vacío
        grupos = []
        posiciones_finales = []
        goleadores = []
        tarjetas = []
        planteles = []
        premios = []

    return {
        "ok": True,
        "tipo_consulta": "mundial",
        "mensaje": mensaje,
        "filtros": {
            "anio": int(anio),
            "grupo": grupo_norm,
            "pais": pais_norm,
            "fecha": fecha_norm
        },
        "info_general": {
            "anio": doc.get("anio"),
            "organizador": doc.get("organizador"),
            "campeon": doc.get("campeon"),
            "subcampeon": doc.get("subcampeon"),
            "selecciones_total": doc.get("selecciones_total"),
            "partidos_total": doc.get("partidos_total"),
            "goles_total": doc.get("goles_total"),
            "promedio_gol": doc.get("promedio_gol")
        },
        "grupos": grupos,
        "partidos": partidos,
        "posiciones_finales": posiciones_finales,
        "goleadores": goleadores,
        "premios": premios,
        "tarjetas": tarjetas,
        "planteles": planteles
    }


def metodo_info_pais(pais: str, anio=None, fase=None) -> dict:
    """
    Método del inciso d.
    Recibe el país y devuelve toda la información relacionada con él.
    Filtros opcionales:
      - anio
      - fase
    """
    db = get_db()
    col = db["selecciones"]

    doc = col.find_one(
        {"nombre": {"$regex": f"^{re.escape(pais)}$", "$options": "i"}},
        {"_id": 0}
    )

    if not doc:
        doc = col.find_one(
            {"nombre": {"$regex": re.escape(pais), "$options": "i"}},
            {"_id": 0}
        )

    if not doc:
        return {
            "ok": False,
            "mensaje": f"No se encontró ningún país que coincida con '{pais}'"
        }

    nombre_real = doc.get("nombre")
    participaciones = doc.get("participaciones", [])

    anio_norm = int(anio) if anio is not None else None
    fase_norm = fase.strip() if fase else None

    # 1) filtrar participaciones por año
    if anio_norm is not None:
        participaciones = [p for p in participaciones if p.get("anio") == anio_norm]

    nuevas_participaciones = []

    for part in participaciones:
        partidos = part.get("partidos", [])

        # 2) filtrar partidos por fase
        if fase_norm is not None:
            partidos = [
                pa for pa in partidos
                if _match_text(pa.get("etapa", ""), fase_norm)
            ]

        # 3) si hay filtros y ya no quedan partidos, dejar la participación vacía de forma consistente
        if fase_norm is not None and len(partidos) == 0:
            nuevas_participaciones.append({
                "anio": part.get("anio"),
                "fue_sede": part.get("fue_sede"),
                "fue_campeon": part.get("fue_campeon"),
                "fue_subcampeon": part.get("fue_subcampeon"),
                "grupo": None,
                "posicion_final": part.get("posicion_final"),
                "etapa_final": part.get("etapa_final"),
                "partidos": [],
                "plantel": [],
                "estadisticas_jugadores": []
            })
            continue

        # 4) si sí quedaron partidos, determinar si tiene sentido conservar grupo/plantel/estadísticas
        nueva_part = dict(part)
        nueva_part["partidos"] = partidos

        # si el filtro es por fase distinta de grupos, no tiene sentido mostrar grupo
        if fase_norm is not None and not _match_text(fase_norm, "grupo"):
            nueva_part["grupo"] = None

        # si se filtró por fase, mantener plantel y estadísticas solo si hubo partidos
        # (porque siguen siendo de esa participación/año)
        nueva_part["plantel"] = part.get("plantel", []) if len(partidos) > 0 else []
        nueva_part["estadisticas_jugadores"] = part.get("estadisticas_jugadores", []) if len(partidos) > 0 else []

        nuevas_participaciones.append(nueva_part)

    participaciones = nuevas_participaciones

    anios_participacion = [p.get("anio") for p in doc.get("participaciones", [])]

    resumen_participaciones = []
    for part in participaciones:
        partidos = part.get("partidos", [])
        resumen_participaciones.append({
            "anio": part.get("anio"),
            "fue_sede": part.get("fue_sede"),
            "fue_campeon": part.get("fue_campeon"),
            "fue_subcampeon": part.get("fue_subcampeon"),
            "grupo": part.get("grupo"),
            "posicion_final": part.get("posicion_final"),
            "etapa_final": part.get("etapa_final"),
            "partidos": [
                {
                    "numero": p.get("numero"),
                    "fecha": p.get("fecha"),
                    "etapa": p.get("etapa"),
                    "local": p.get("local"),
                    "goles_local": p.get("goles_local"),
                    "goles_visitante": p.get("goles_visitante"),
                    "visitante": p.get("visitante"),
                    "resultado_para_el_pais": _resultado_desde_partido(p, nombre_real),
                    "goles": p.get("goles", [])
                }
                for p in partidos
            ],
            "plantel": part.get("plantel", []),
            "estadisticas_jugadores": part.get("estadisticas_jugadores", [])
        })

    mensaje = None
    if len(resumen_participaciones) == 0:
        mensaje = "No hay participaciones para los filtros indicados"
    elif fase_norm is not None:
        total_partidos = sum(len(p["partidos"]) for p in resumen_participaciones)
        if total_partidos == 0:
            mensaje = "No hay partidos para la combinación de filtros indicada"

    return {
        "ok": True,
        "tipo_consulta": "pais",
        "mensaje": mensaje,
        "filtros": {
            "pais_buscado": pais,
            "pais_resuelto": nombre_real,
            "anio": anio_norm,
            "fase": fase_norm
        },
        "info_historica": {
            "nombre": nombre_real,
            "mundiales_jugados": doc.get("mundiales_jugados"),
            "campeon_veces": doc.get("campeon_veces"),
            "campeon_anios": doc.get("campeon_anios", []),
            "subcampeon_veces": doc.get("subcampeon_veces"),
            "subcampeon_anios": doc.get("subcampeon_anios", []),
            "posicion_historica": doc.get("posicion_historica"),
            "partidos_jugados": doc.get("partidos_jugados"),
            "partidos_ganados": doc.get("partidos_ganados"),
            "partidos_empatados": doc.get("partidos_empatados"),
            "partidos_perdidos": doc.get("partidos_perdidos"),
            "goles_favor": doc.get("goles_favor"),
            "goles_contra": doc.get("goles_contra"),
            "diferencia_gol": doc.get("diferencia_gol"),
            "sedes": doc.get("sedes", []),
            "anios_participacion": anios_participacion
        },
        "participaciones": resumen_participaciones
    }