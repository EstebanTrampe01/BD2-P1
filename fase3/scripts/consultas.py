"""
consultas.py
============
Métodos de consulta requeridos por el proyecto (puntos c y d).

  c) consulta_mundial(anio, grupo=None, pais=None, fecha=None)
  d) consulta_pais(pais, anio=None, solo_partidos=False)

Requisitos:
    pip install pymongo

Uso rápido:
    python consultas.py

O importar desde otro módulo:
    from consultas import consulta_mundial, consulta_pais
"""

import sys
from datetime import datetime

try:
    from pymongo import MongoClient
except ImportError:
    print("[ERROR] pymongo no instalado. Ejecuta: pip install pymongo")
    sys.exit(1)

MONGO_URI = "mongodb://mundiales_user:mundiales1234@127.0.0.1:27017/mundiales?authSource=admin"
DB_NAME   = "mundiales"

_client = None
_db     = None


def _get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _db     = _client[DB_NAME]
    return _db


# ─────────────────────────────────────────────────────────────
#  UTILIDADES DE PRESENTACIÓN
# ─────────────────────────────────────────────────────────────

SEP  = "─" * 60
SEP2 = "═" * 60
COL  = "  "


def _titulo(txt):
    print(f"\n{SEP2}")
    print(f"  {txt}")
    print(SEP2)


def _seccion(txt):
    print(f"\n{COL}{SEP[:56]}")
    print(f"{COL}  {txt}")
    print(f"{COL}{SEP[:56]}")


def _resultado_partido(p, prefix=""):
    local     = p.get("local", "?")
    visitante = p.get("visitante", "?")
    gl        = p.get("goles_local")
    gv        = p.get("goles_visitante")
    score     = f"{gl} - {gv}" if gl is not None and gv is not None else "? - ?"
    etapa     = p.get("etapa", "")
    fecha     = p.get("fecha", "")
    num       = p.get("numero", "")
    print(f"{prefix}  #{num:>3}  [{fecha}]  {etapa}")
    print(f"{prefix}       {local:<25} {score:>7}  {visitante}")


# ─────────────────────────────────────────────────────────────
#  c)  consulta_mundial
# ─────────────────────────────────────────────────────────────

def consulta_mundial(anio, grupo=None, pais=None, fecha=None):
    """
    Muestra toda la información de un Mundial, con filtros opcionales.

    Parámetros
    ----------
    anio  : int | str  — Año del mundial (requerido).
    grupo : str        — Filtrar por letra de grupo, ej. "A", "B".
    pais  : str        — Mostrar solo partidos donde interviene ese país.
    fecha : str        — Filtrar partidos por fecha exacta, ej. "20-Nov-2022".
    """
    db  = _get_db()
    col = db["mundiales"]

    doc = col.find_one({"anio": int(anio)})
    if not doc:
        print(f"\n[!] No se encontró el Mundial {anio}.")
        return

    _titulo(f"MUNDIAL {doc['anio']}  ·  Sede: {doc.get('organizador','?')}  ·  Campeón: {doc.get('campeon','?')}")

    print(f"\n{COL}Subcampeón      : {doc.get('subcampeon','?')}")
    print(f"{COL}Selecciones     : {doc.get('selecciones_total','?')}")
    print(f"{COL}Partidos totales: {doc.get('partidos_total','?')}")
    print(f"{COL}Goles totales   : {doc.get('goles_total','?')}")
    print(f"{COL}Promedio goles  : {doc.get('promedio_gol','?')}")

    # ── GRUPOS ─────────────────────────────────────────────────
    grupos_raw = doc.get("grupos", [])
    if grupos_raw:
        # Agrupar por letra
        letras = {}
        for g in grupos_raw:
            letra = g.get("grupo", "?")
            if grupo and letra.upper() != grupo.upper():
                continue
            letras.setdefault(letra, []).append(g)

        if letras:
            _seccion("FASE DE GRUPOS")
            for letra in sorted(letras.keys()):
                print(f"\n{COL}  Grupo {letra}")
                print(f"{COL}  {'Selección':<25} {'PJ':>3} {'PG':>3} {'PE':>3} {'PP':>3} {'GF':>3} {'GC':>3} {'Dif':>4} {'Pts':>4}")
                print(f"{COL}  {'-'*58}")
                for r in letras[letra]:
                    sel = r.get("seleccion", "?")
                    clasificado = "✓" if r.get("clasificado") else " "
                    print(
                        f"{COL}  {clasificado}{sel:<24} "
                        f"{_n(r,'pj'):>3} {_n(r,'pg'):>3} {_n(r,'pe'):>3} "
                        f"{_n(r,'pp'):>3} {_n(r,'gf'):>3} {_n(r,'gc'):>3} "
                        f"{_n(r,'dif'):>4} {_n(r,'pts'):>4}"
                    )

    # ── PARTIDOS ───────────────────────────────────────────────
    partidos = doc.get("partidos", [])

    # Aplicar filtros
    if grupo:
        etapa_filtro = f"Grupo {grupo.upper()}"
        partidos = [p for p in partidos if etapa_filtro.lower() in (p.get("etapa") or "").lower()]
    if pais:
        p_lower = pais.lower()
        partidos = [
            p for p in partidos
            if p_lower in (p.get("local") or "").lower()
            or p_lower in (p.get("visitante") or "").lower()
        ]
    if fecha:
        partidos = [p for p in partidos if (p.get("fecha") or "") == fecha]

    if partidos:
        filtros_txt = " | ".join(filter(None, [
            f"Grupo {grupo.upper()}" if grupo else None,
            f"País: {pais}" if pais else None,
            f"Fecha: {fecha}" if fecha else None,
        ])) or "Todos"
        _seccion(f"PARTIDOS  [{filtros_txt}]")

        etapas_order = {}
        for p in partidos:
            etapa = p.get("etapa", "Sin etapa")
            etapas_order.setdefault(etapa, []).append(p)

        for etapa, ps in etapas_order.items():
            print(f"\n{COL}  ▸ {etapa}")
            for p in sorted(ps, key=lambda x: x.get("numero") or 0):
                _resultado_partido(p, prefix=COL)

    # ── POSICIONES FINALES ─────────────────────────────────────
    pos = doc.get("posiciones_finales", [])
    if pos and not (grupo or fecha):
        _seccion("POSICIONES FINALES")
        print(f"\n{COL}  {'Pos':>3}  {'Selección':<25}  {'Etapa':<25}  {'PJ':>3} {'PG':>3} {'GF':>3} {'GC':>3}")
        print(f"{COL}  {'-'*72}")
        for r in sorted(pos, key=lambda x: x.get("posicion") or 999):
            if pais and pais.lower() not in (r.get("seleccion") or "").lower():
                continue
            print(
                f"{COL}  {_n(r,'posicion'):>3}  {r.get('seleccion','?'):<25}  "
                f"{r.get('etapa','?'):<25}  {_n(r,'pj'):>3} {_n(r,'pg'):>3} "
                f"{_n(r,'gf'):>3} {_n(r,'gc'):>3}"
            )

    # ── GOLEADORES ─────────────────────────────────────────────
    gol = doc.get("goleadores", [])
    if gol and not (grupo or fecha):
        _seccion("GOLEADORES")
        print(f"\n{COL}  {'#':>3}  {'Jugador':<30}  {'Sel':<20}  {'Goles':>6}  {'PJ':>3}")
        print(f"{COL}  {'-'*65}")
        for r in sorted(gol, key=lambda x: x.get("posicion") or 999):
            if pais and pais.lower() not in (r.get("seleccion") or "").lower():
                continue
            print(
                f"{COL}  {_n(r,'posicion'):>3}  {r.get('jugador','?'):<30}  "
                f"{r.get('seleccion','?'):<20}  {_n(r,'goles'):>6}  {_n(r,'partidos'):>3}"
            )

    # ── PREMIOS ────────────────────────────────────────────────
    prem = doc.get("premios", [])
    if prem and not (grupo or fecha):
        _seccion("PREMIOS")
        for r in prem:
            print(f"{COL}  {r.get('tipo_premio','?'):<30} → {r.get('jugador') or r.get('seleccion','?')}")

    print(f"\n{SEP2}\n")


# ─────────────────────────────────────────────────────────────
#  d)  consulta_pais
# ─────────────────────────────────────────────────────────────

def consulta_pais(pais, anio=None, solo_partidos=False):
    """
    Muestra toda la información histórica de una selección.

    Parámetros
    ----------
    pais          : str        — Nombre del país (requerido).
    anio          : int | str  — Filtrar solo para ese año del mundial.
    solo_partidos : bool       — Si True, muestra solo los partidos (sin plantel).
    """
    db  = _get_db()
    col = db["selecciones"]

    # Búsqueda flexible (case-insensitive)
    doc = col.find_one({"nombre": {"$regex": f"^{pais}$", "$options": "i"}})
    if not doc:
        # Búsqueda parcial
        doc = col.find_one({"nombre": {"$regex": pais, "$options": "i"}})
    if not doc:
        print(f"\n[!] No se encontró la selección '{pais}'.")
        return

    nombre = doc["nombre"]
    _titulo(f"SELECCIÓN: {nombre.upper()}")

    # ── ESTADÍSTICAS GLOBALES ──────────────────────────────────
    print(f"\n{COL}Mundiales jugados  : {doc.get('mundiales_jugados','?')}")
    print(f"{COL}Campeón veces      : {doc.get('campeon_veces',0)}", end="")
    if doc.get("campeon_anios"):
        print(f"  ({', '.join(doc['campeon_anios'])})", end="")
    print()
    print(f"{COL}Subcampeón veces   : {doc.get('subcampeon_veces',0)}", end="")
    if doc.get("subcampeon_anios"):
        print(f"  ({', '.join(doc['subcampeon_anios'])})", end="")
    print()
    print(f"{COL}Posición histórica : {doc.get('posicion_historica','?')}")
    print(f"{COL}PJ / PG / PE / PP  : "
          f"{doc.get('partidos_jugados','?')} / {doc.get('partidos_ganados','?')} / "
          f"{doc.get('partidos_empatados','?')} / {doc.get('partidos_perdidos','?')}")
    print(f"{COL}Goles F / C / Dif  : "
          f"{doc.get('goles_favor','?')} / {doc.get('goles_contra','?')} / "
          f"{doc.get('diferencia_gol','?')}")

    if doc.get("sedes"):
        print(f"{COL}Sede de:           : {', '.join(str(s) for s in doc['sedes'])}")

    # ── PARTICIPACIONES ────────────────────────────────────────
    participaciones = doc.get("participaciones", [])
    if anio:
        participaciones = [p for p in participaciones if str(p.get("anio")) == str(anio)]

    if not participaciones:
        print(f"\n{COL}(Sin participaciones registradas para los filtros indicados)")
        print(f"\n{SEP2}\n")
        return

    _seccion(f"PARTICIPACIONES  ({len(participaciones)} mundiales)")

    for part in participaciones:
        a = part.get("anio", "?")
        fue_sede      = "🏟 SEDE"      if part.get("fue_sede")      else ""
        fue_campeon   = "🏆 CAMPEÓN"   if part.get("fue_campeon")   else ""
        fue_sub       = "🥈 SUBCAMPEÓN" if part.get("fue_subcampeon") else ""
        badges = "  ".join(filter(None, [fue_sede, fue_campeon, fue_sub]))

        print(f"\n{COL}{'─'*54}")
        print(f"{COL}  📅  Mundial {a}  {badges}")

        pos_final  = part.get("posicion_final")
        etapa_fin  = part.get("etapa_final")
        if pos_final:
            print(f"{COL}  Posición final: #{pos_final}  ({etapa_fin})")

        # Grupo
        g = part.get("grupo")
        if g:
            print(
                f"{COL}  Grupo {g.get('grupo','?')}  |  "
                f"Pos: {g.get('posicion','?')}  "
                f"PJ:{_n(g,'pj')} PG:{_n(g,'pg')} PE:{_n(g,'pe')} PP:{_n(g,'pp')}  "
                f"GF:{_n(g,'gf')} GC:{_n(g,'gc')}  Pts:{_n(g,'pts')}"
            )

        # Partidos
        partidos_part = part.get("partidos", [])
        if partidos_part:
            print(f"\n{COL}  Partidos:")
            for p in sorted(partidos_part, key=lambda x: x.get("numero") or 0):
                _resultado_partido(p, prefix=COL + "  ")

        # Plantel (solo si no se pidió solo_partidos)
        plantel = part.get("plantel", [])
        if plantel and not solo_partidos:
            print(f"\n{COL}  Plantel ({len(plantel)} jugadores):")
            print(f"{COL}  {'#':>3}  {'Jugador':<30}  {'Pos':<12}  {'Club'}")
            print(f"{COL}  {'-'*60}")
            for j in sorted(plantel, key=lambda x: x.get("camiseta") or 99):
                print(
                    f"{COL}  {_n(j,'camiseta'):>3}  {j.get('jugador','?'):<30}  "
                    f"{j.get('posicion','?'):<12}  {j.get('club','?')}"
                )

    print(f"\n{SEP2}\n")


# ─────────────────────────────────────────────────────────────
#  Helper numérico para formato de tabla
# ─────────────────────────────────────────────────────────────

def _n(d, key):
    v = d.get(key)
    return str(v) if v is not None else "-"


# ─────────────────────────────────────────────────────────────
#  Demo / prueba rápida
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 60)
    print("  DEMO — Consultas Mundiales de Fútbol (MongoDB)")
    print("═" * 60)

    # ── PUNTO c) ───────────────────────────────────────────────
    print("\n>>> consulta_mundial(2022)")
    consulta_mundial(2022)

    print("\n>>> consulta_mundial(2022, grupo='A')")
    consulta_mundial(2022, grupo="A")

    print("\n>>> consulta_mundial(2018, pais='Francia')")
    consulta_mundial(2018, pais="Francia")

    # ── PUNTO d) ───────────────────────────────────────────────
    print("\n>>> consulta_pais('Argentina')")
    consulta_pais("Argentina")

    print("\n>>> consulta_pais('Brasil', anio=2014)")
    consulta_pais("Brasil", anio=2014)

    print("\n>>> consulta_pais('Alemania', solo_partidos=True)")
    consulta_pais("Alemania", solo_partidos=True)
