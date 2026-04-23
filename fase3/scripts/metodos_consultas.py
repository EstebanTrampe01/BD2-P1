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


def _resultado_desde_partido(partido: dict, pais: str) -> str:
    local = partido.get("local")
    visitante = partido.get("visitante")
    gl = partido.get("goles_local")
    gv = partido.get("goles_visitante")

    if local == pais:
        if gl > gv:
            return "Victoria"
        if gl < gv:
            return "Derrota"
        return "Empate"

    if visitante == pais:
        if gv > gl:
            return "Victoria"
        if gv < gl:
            return "Derrota"
        return "Empate"

    return "No aplica"


def metodo_info_mundial(anio: int, grupo: Optional[str] = None, pais: Optional[str] = None, fecha: Optional[str] = None) -> dict:
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

    # filtro por grupo
    if grupo is not None:
        grupo = grupo.strip().upper()
        grupos = [g for g in grupos if str(g.get("grupo", "")).upper() == grupo]
        partidos = [
            p for p in partidos
            if _match_text(p.get("etapa", ""), f"Grupo {grupo}") or _match_text(p.get("etapa", ""), f"Group {grupo}")
        ]

    # filtro por país
    if pais is not None:
        pais = pais.strip()
        partidos = [
            p for p in partidos
            if _match_text(p.get("local", ""), pais) or _match_text(p.get("visitante", ""), pais)
        ]
        grupos = [g for g in grupos if _match_text(g.get("seleccion", ""), pais)]
        posiciones_finales = [p for p in posiciones_finales if _match_text(p.get("seleccion", ""), pais)]
        goleadores = [g for g in goleadores if _match_text(g.get("seleccion", ""), pais)]
        tarjetas = [t for t in tarjetas if _match_text(t.get("seleccion", ""), pais)]
        planteles = [pl for pl in planteles if _match_text(pl.get("seleccion", ""), pais)]

    # filtro por fecha
    if fecha is not None:
        fecha = fecha.strip()
        partidos = [p for p in partidos if p.get("fecha") == fecha]

    return {
        "ok": True,
        "tipo_consulta": "mundial",
        "filtros": {
            "anio": int(anio),
            "grupo": grupo,
            "pais": pais,
            "fecha": fecha
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


def metodo_info_pais(pais: str, anio: Optional[int] = None, fase: Optional[str] = None) -> dict:
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

    if anio is not None:
        participaciones = [p for p in participaciones if p.get("anio") == int(anio)]

    if fase is not None:
        fase = fase.strip()
        nuevas_participaciones = []
        for part in participaciones:
            partidos_filtrados = [
                pa for pa in part.get("partidos", [])
                if _match_text(pa.get("etapa", ""), fase)
            ]
            copia = dict(part)
            copia["partidos"] = partidos_filtrados
            nuevas_participaciones.append(copia)
        participaciones = nuevas_participaciones

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

    anios_participacion = [p.get("anio") for p in doc.get("participaciones", [])]

    return {
        "ok": True,
        "tipo_consulta": "pais",
        "filtros": {
            "pais_buscado": pais,
            "pais_resuelto": nombre_real,
            "anio": anio,
            "fase": fase
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