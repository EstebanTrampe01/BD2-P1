"""
verificar_integridad.py
=======================
Consultas de verificación de datos en MongoDB.
Desde simples (conteos, campos nulos) hasta complejas (rankings, cruces).

Uso:
    python verificar_integridad.py
"""

import sys
from collections import defaultdict

try:
    from pymongo import MongoClient
except ImportError:
    print("[ERROR] pymongo no instalado. Ejecuta: pip install pymongo")
    sys.exit(1)

MONGO_URI = "mongodb://mundiales_user:mundiales1234@127.0.0.1:27017/mundiales?authSource=admin"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db     = client["mundiales"]

SEP  = "─" * 62
SEP2 = "═" * 62

def titulo(txt):
    print(f"\n{SEP2}")
    print(f"  {txt}")
    print(SEP2)

def seccion(num, txt):
    print(f"\n{SEP}")
    print(f"  [{num}] {txt}")
    print(SEP)

def ok(msg):  print(f"  ✅  {msg}")
def warn(msg):print(f"  ⚠️   {msg}")
def info(msg):print(f"  ℹ️   {msg}")


# ═══════════════════════════════════════════════════════════════
#  BLOQUE 1 — CONSULTAS SIMPLES
#  Conteos básicos, presencia de datos, campos clave
# ═══════════════════════════════════════════════════════════════

titulo("BLOQUE 1 — CONSULTAS SIMPLES")

# ── 1.1 Conteo de documentos en cada colección ─────────────────
seccion("1.1", "Conteo total de documentos por colección")

n_mundiales   = db.mundiales.count_documents({})
n_selecciones = db.selecciones.count_documents({})
print(f"  mundiales   : {n_mundiales:>5} documentos")
print(f"  selecciones : {n_selecciones:>5} documentos")

if n_mundiales > 0:  ok("Colección mundiales tiene datos.")
else:                warn("Colección mundiales VACÍA.")
if n_selecciones > 0: ok("Colección selecciones tiene datos.")
else:                 warn("Colección selecciones VACÍA.")


# ── 1.2 Listar todos los años de Mundiales cargados ────────────
seccion("1.2", "Años de Mundiales cargados")

anios = sorted([d["anio"] for d in db.mundiales.find({}, {"anio": 1, "_id": 0})])
print(f"  {anios}")
info(f"Total: {len(anios)} mundiales cargados.")


# ── 1.3 Buscar un Mundial específico (datos de cabecera) ────────
seccion("1.3", "Datos de cabecera — Mundial 2022")

doc = db.mundiales.find_one(
    {"anio": 2022},
    {"anio":1, "organizador":1, "campeon":1, "subcampeon":1,
     "selecciones_total":1, "partidos_total":1, "goles_total":1,
     "promedio_gol":1, "_id":0}
)
if doc:
    for k, v in doc.items():
        print(f"  {k:<25}: {v}")
    ok("Mundial 2022 encontrado correctamente.")
else:
    warn("No se encontró el Mundial 2022.")


# ── 1.4 Buscar una selección por nombre ────────────────────────
seccion("1.4", "Estadísticas globales — Argentina")

sel = db.selecciones.find_one(
    {"nombre": {"$regex": "^Argentina$", "$options": "i"}},
    {"nombre":1, "mundiales_jugados":1, "campeon_veces":1,
     "campeon_anios":1, "posicion_historica":1,
     "partidos_jugados":1, "goles_favor":1, "goles_contra":1, "_id":0}
)
if sel:
    for k, v in sel.items():
        print(f"  {k:<25}: {v}")
    ok("Argentina encontrada.")
else:
    warn("Argentina no encontrada — revisar nombre en CSV.")


# ── 1.5 Campeones de todos los mundiales ───────────────────────
seccion("1.5", "Campeón de cada Mundial")

docs = db.mundiales.find(
    {},
    {"anio":1, "campeon":1, "organizador":1, "_id":0}
).sort("anio", 1)

print(f"  {'Año':<6}  {'Sede':<25}  {'Campeón'}")
print(f"  {'-'*55}")
for d in docs:
    print(f"  {d['anio']:<6}  {d.get('organizador','?'):<25}  {d.get('campeon','?')}")


# ── 1.6 Mundiales donde fue sede un país ───────────────────────
seccion("1.6", "Años en que Brasil fue sede")

brasil = db.selecciones.find_one(
    {"nombre": {"$regex": "Brasil", "$options": "i"}},
    {"sedes": 1, "_id": 0}
)
if brasil:
    sedes = brasil.get("sedes", [])
    if sedes:
        print(f"  Brasil fue sede en: {sedes}")
        ok(f"{len(sedes)} vez/veces encontradas.")
    else:
        warn("Brasil no tiene sedes registradas.")
else:
    warn("Brasil no encontrado.")


# ═══════════════════════════════════════════════════════════════
#  BLOQUE 2 — CONSULTAS MEDIAS
#  Subconsultas en arrays, aggregations simples
# ═══════════════════════════════════════════════════════════════

titulo("BLOQUE 2 — CONSULTAS MEDIAS")


# ── 2.1 Partidos totales por Mundial ───────────────────────────
seccion("2.1", "Total de partidos embebidos por Mundial (vs campo partidos_total)")

pipeline = [
    {"$project": {
        "anio": 1,
        "partidos_total": 1,
        "partidos_array_size": {"$size": {"$ifNull": ["$partidos", []]}},
        "_id": 0
    }},
    {"$sort": {"anio": 1}}
]
print(f"  {'Año':<6}  {'Campo partidos_total':>22}  {'Partidos en array':>18}  {'¿Coincide?'}")
print(f"  {'-'*60}")
errores = 0
for d in db.mundiales.aggregate(pipeline):
    total  = d.get("partidos_total") or 0
    array  = d["partidos_array_size"]
    match  = "✅" if total == array else "⚠️ "
    if total != array: errores += 1
    print(f"  {d['anio']:<6}  {total:>22}  {array:>18}  {match}")
if errores == 0: ok("Todos los totales de partidos coinciden.")
else:            warn(f"{errores} mundiales con discrepancia en conteo de partidos.")


# ── 2.2 Selecciones con más participaciones ────────────────────
seccion("2.2", "Top 10 selecciones con más Mundiales jugados")

pipeline = [
    {"$project": {
        "nombre": 1,
        "mundiales_jugados": 1,
        "participaciones_registradas": {"$size": {"$ifNull": ["$participaciones", []]}},
        "_id": 0
    }},
    {"$sort": {"mundiales_jugados": -1}},
    {"$limit": 10}
]
print(f"  {'Selección':<28}  {'Jugados (campo)':>16}  {'Participaciones (array)':>24}")
print(f"  {'-'*70}")
for d in db.selecciones.aggregate(pipeline):
    print(f"  {d['nombre']:<28}  {str(d.get('mundiales_jugados','?')):>16}  {d['participaciones_registradas']:>24}")


# ── 2.3 Mundiales con más goles ────────────────────────────────
seccion("2.3", "Top 5 Mundiales con más goles")

pipeline = [
    {"$match":   {"goles_total": {"$ne": None}}},
    {"$sort":    {"goles_total": -1}},
    {"$limit":   5},
    {"$project": {"anio":1, "goles_total":1, "promedio_gol":1,
                  "partidos_total":1, "_id":0}}
]
print(f"  {'Año':<6}  {'Goles':>7}  {'Partidos':>9}  {'Promedio':>9}")
print(f"  {'-'*35}")
for d in db.mundiales.aggregate(pipeline):
    print(f"  {d['anio']:<6}  {d.get('goles_total','?'):>7}  "
          f"{d.get('partidos_total','?'):>9}  {d.get('promedio_gol','?'):>9}")


# ── 2.4 Verificar que los partidos tienen local y visitante ─────
seccion("2.4", "Partidos con local o visitante nulo (integridad)")

pipeline = [
    {"$unwind": "$partidos"},
    {"$match": {
        "$or": [
            {"partidos.local":     {"$in": [None, ""]}},
            {"partidos.visitante": {"$in": [None, ""]}}
        ]
    }},
    {"$group": {"_id": "$anio", "count": {"$sum": 1}}},
    {"$sort":  {"_id": 1}}
]
resultados = list(db.mundiales.aggregate(pipeline))
if not resultados:
    ok("Ningún partido tiene local o visitante nulo.")
else:
    warn(f"{sum(r['count'] for r in resultados)} partidos con campos nulos:")
    for r in resultados:
        print(f"    Mundial {r['_id']}: {r['count']} partido(s) con problema")


# ── 2.5 Selecciones campeonas — verificar cruce ────────────────
seccion("2.5", "Verificar cruce: campeón en mundiales vs campeon_anios en selecciones")

campeones_mund = {
    str(d["anio"]): d.get("campeon")
    for d in db.mundiales.find({}, {"anio":1, "campeon":1, "_id":0})
    if d.get("campeon")
}

discrepancias = 0
for anio, campeon in sorted(campeones_mund.items()):
    sel = db.selecciones.find_one(
        {"nombre": campeon},
        {"campeon_anios": 1, "_id": 0}
    )
    if not sel:
        warn(f"  {anio}: campeón '{campeon}' no encontrado en colección selecciones.")
        discrepancias += 1
    elif anio not in (sel.get("campeon_anios") or []):
        warn(f"  {anio}: '{campeon}' es campeón en mundiales pero no aparece en campeon_anios.")
        discrepancias += 1

if discrepancias == 0:
    ok(f"Todos los campeones ({len(campeones_mund)}) están correctamente cruzados.")
else:
    warn(f"{discrepancias} discrepancias encontradas.")


# ═══════════════════════════════════════════════════════════════
#  BLOQUE 3 — CONSULTAS COMPLEJAS
#  Pipelines de aggregation, cruces entre colecciones, rankings
# ═══════════════════════════════════════════════════════════════

titulo("BLOQUE 3 — CONSULTAS COMPLEJAS")


# ── 3.1 Selecciones que más veces llegaron a la Final ──────────
seccion("3.1", "Selecciones con más finales jugadas (campeón + subcampeón)")

pipeline = [
    {"$project": {
        "nombre": 1,
        "finales": {
            "$add": [
                {"$ifNull": ["$campeon_veces", 0]},
                {"$ifNull": ["$subcampeon_veces", 0]}
            ]
        },
        "campeon_veces":    1,
        "subcampeon_veces": 1,
        "_id": 0
    }},
    {"$match": {"finales": {"$gt": 0}}},
    {"$sort":  {"finales": -1, "campeon_veces": -1}},
    {"$limit": 10}
]
print(f"  {'Selección':<28}  {'Finales':>8}  {'Campeón':>8}  {'Subcampeón':>11}")
print(f"  {'-'*60}")
for d in db.selecciones.aggregate(pipeline):
    print(f"  {d['nombre']:<28}  {d['finales']:>8}  "
          f"{d.get('campeon_veces',0):>8}  {d.get('subcampeon_veces',0):>11}")


# ── 3.2 Mundial con mayor cantidad de selecciones distintas ────
seccion("3.2", "Selecciones distintas en el plantel de cada Mundial")

pipeline = [
    {"$unwind": "$planteles"},
    {"$group": {
        "_id":   "$anio",
        "selecciones_con_plantel": {"$sum": 1}
    }},
    {"$sort": {"_id": 1}}
]
print(f"  {'Año':<6}  {'Selecciones con plantel cargado':>32}")
print(f"  {'-'*40}")
for d in db.mundiales.aggregate(pipeline):
    print(f"  {d['_id']:<6}  {d['selecciones_con_plantel']:>32}")


# ── 3.3 Promedio de goles por etapa en el Mundial 2022 ─────────
seccion("3.3", "Promedio de goles por fase — Mundial 2022")

pipeline = [
    {"$match": {"anio": 2022}},
    {"$unwind": "$partidos"},
    {"$match": {
        "partidos.goles_local":     {"$ne": None},
        "partidos.goles_visitante": {"$ne": None}
    }},
    {"$group": {
        "_id": "$partidos.etapa",
        "partidos_jugados": {"$sum": 1},
        "goles_totales": {
            "$sum": {
                "$add": ["$partidos.goles_local", "$partidos.goles_visitante"]
            }
        }
    }},
    {"$addFields": {
        "promedio_goles": {
            "$round": [{"$divide": ["$goles_totales", "$partidos_jugados"]}, 2]
        }
    }},
    {"$sort": {"goles_totales": -1}}
]
print(f"  {'Fase':<35}  {'Partidos':>9}  {'Goles':>7}  {'Promedio':>9}")
print(f"  {'-'*65}")
for d in db.mundiales.aggregate(pipeline):
    print(f"  {d['_id']:<35}  {d['partidos_jugados']:>9}  "
          f"{d['goles_totales']:>7}  {d['promedio_goles']:>9}")


# ── 3.4 Selecciones con partidos pero sin plantel registrado ───
seccion("3.4", "Selecciones que participaron pero no tienen plantel (integridad)")

pipeline = [
    {"$unwind": "$participaciones"},
    {"$match": {
        "participaciones.partidos.0": {"$exists": True},   # jugó al menos 1 partido
        "participaciones.plantel":    {"$in": [None, []]}  # pero sin plantel
    }},
    {"$group": {
        "_id": "$nombre",
        "mundiales_sin_plantel": {"$push": "$participaciones.anio"}
    }},
    {"$sort": {"_id": 1}},
    {"$limit": 15}
]
resultados = list(db.selecciones.aggregate(pipeline))
if not resultados:
    ok("Todas las selecciones con partidos tienen plantel registrado.")
else:
    warn(f"{len(resultados)} selecciones con partidos pero sin plantel:")
    for r in resultados:
        print(f"  {r['_id']:<28} → Mundiales sin plantel: {r['mundiales_sin_plantel']}")


# ── 3.5 Top goleadores históricos (suma por selección) ─────────
seccion("3.5", "Selecciones con más goles en toda su historia (desde estadísticas globales)")

pipeline = [
    {"$match": {"goles_favor": {"$ne": None}}},
    {"$sort":  {"goles_favor": -1}},
    {"$limit": 10},
    {"$project": {
        "nombre": 1, "goles_favor": 1, "goles_contra": 1,
        "diferencia_gol": 1, "partidos_jugados": 1, "_id": 0
    }}
]
print(f"  {'Selección':<28}  {'GF':>6}  {'GC':>6}  {'Dif':>6}  {'PJ':>5}")
print(f"  {'-'*58}")
for d in db.selecciones.aggregate(pipeline):
    print(f"  {d['nombre']:<28}  {str(d.get('goles_favor','?')):>6}  "
          f"{str(d.get('goles_contra','?')):>6}  "
          f"{str(d.get('diferencia_gol','?')):>6}  "
          f"{str(d.get('partidos_jugados','?')):>5}")


# ── 3.6 Partidos más goleadores de la historia ─────────────────
seccion("3.6", "Top 10 partidos con más goles en la historia")

pipeline = [
    {"$unwind": "$partidos"},
    {"$match": {
        "partidos.goles_local":     {"$ne": None},
        "partidos.goles_visitante": {"$ne": None}
    }},
    {"$addFields": {
        "total_goles_partido": {
            "$add": ["$partidos.goles_local", "$partidos.goles_visitante"]
        }
    }},
    {"$sort": {"total_goles_partido": -1}},
    {"$limit": 10},
    {"$project": {
        "anio": 1,
        "total_goles_partido": 1,
        "local":     "$partidos.local",
        "visitante": "$partidos.visitante",
        "goles_l":   "$partidos.goles_local",
        "goles_v":   "$partidos.goles_visitante",
        "etapa":     "$partidos.etapa",
        "fecha":     "$partidos.fecha",
        "_id": 0
    }}
]
print(f"  {'Año':<6}  {'Local':<22}  {'Res':>5}  {'Visitante':<22}  {'Goles':>6}  {'Fase'}")
print(f"  {'-'*85}")
for d in db.mundiales.aggregate(pipeline):
    score = f"{d['goles_l']}-{d['goles_v']}"
    print(f"  {d['anio']:<6}  {d['local']:<22}  {score:>5}  "
          f"{d['visitante']:<22}  {d['total_goles_partido']:>6}  {d.get('etapa','?')}")


# ── 3.7 Evolución del promedio de goles por mundial ────────────
seccion("3.7", "Evolución del promedio de goles por partido a lo largo de los años")

pipeline = [
    {"$match": {"promedio_gol": {"$ne": None}}},
    {"$sort":  {"anio": 1}},
    {"$project": {"anio":1, "promedio_gol":1, "goles_total":1, "partidos_total":1, "_id":0}}
]
print(f"  {'Año':<6}  {'Promedio goles':>15}  {'Barra visual'}")
print(f"  {'-'*50}")
for d in db.mundiales.aggregate(pipeline):
    prom  = d.get("promedio_gol") or 0
    barra = "█" * int(prom * 4)
    print(f"  {d['anio']:<6}  {prom:>15.2f}  {barra}")


# ── 3.8 Selecciones que participaron en TODOS los mundiales ────
seccion("3.8", "Selecciones que participaron en todos los Mundiales cargados")

total_mundiales = db.mundiales.count_documents({})

pipeline = [
    {"$project": {
        "nombre": 1,
        "total_participaciones": {"$size": {"$ifNull": ["$participaciones", []]}},
        "_id": 0
    }},
    {"$match": {"total_participaciones": total_mundiales}},
    {"$sort":  {"nombre": 1}}
]
resultados = list(db.selecciones.aggregate(pipeline))
if resultados:
    ok(f"{len(resultados)} selección(es) participaron en los {total_mundiales} mundiales:")
    for r in resultados:
        print(f"  {r['nombre']}")
else:
    info(f"Ninguna selección tiene participaciones en los {total_mundiales} mundiales cargados.")
    # Mostrar las más cercanas
    pipeline2 = [
        {"$project": {
            "nombre": 1,
            "total_participaciones": {"$size": {"$ifNull": ["$participaciones", []]}},
            "_id": 0
        }},
        {"$sort": {"total_participaciones": -1}},
        {"$limit": 5}
    ]
    print(f"  Las más cercanas:")
    for r in db.selecciones.aggregate(pipeline2):
        print(f"    {r['nombre']:<28} → {r['total_participaciones']} participaciones")


# ═══════════════════════════════════════════════════════════════
#  RESUMEN FINAL
# ═══════════════════════════════════════════════════════════════

titulo("RESUMEN DE INTEGRIDAD")

total_partidos = list(db.mundiales.aggregate([
    {"$unwind": "$partidos"},
    {"$count": "total"}
]))
total_planteles = list(db.mundiales.aggregate([
    {"$unwind": "$planteles"},
    {"$unwind": "$planteles.jugadores"},
    {"$count": "total"}
]))
total_grupos = list(db.mundiales.aggregate([
    {"$unwind": "$grupos"},
    {"$count": "total"}
]))

tp = total_partidos[0]["total"]  if total_partidos  else 0
tpl= total_planteles[0]["total"] if total_planteles else 0
tg = total_grupos[0]["total"]    if total_grupos    else 0

print(f"\n  {'Mundiales cargados':<35}: {n_mundiales}")
print(f"  {'Selecciones cargadas':<35}: {n_selecciones}")
print(f"  {'Partidos totales (todos los mundiales)':<35}: {tp}")
print(f"  {'Registros de grupo (filas)':<35}: {tg}")
print(f"  {'Jugadores en planteles':<35}: {tpl}")

print(f"\n{SEP2}")
print("  Verificación completada.")
print(SEP2 + "\n")

client.close()
