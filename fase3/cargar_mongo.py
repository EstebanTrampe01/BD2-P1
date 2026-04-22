

import json
import os
import sys

try:
    from pymongo import MongoClient, ASCENDING, TEXT
    from pymongo.errors import BulkWriteError, ConnectionFailure
except ImportError:
    print("[ERROR] pymongo no está instalado. Ejecuta: pip install pymongo")
    sys.exit(1)

DIR_JSON = "./output_mongo"

MONGO_URI = "mongodb://mundiales_user:mundiales1234@127.0.0.1:27017/mundiales?authSource=admin"
DB_NAME   = "mundiales"


def obtener_cliente():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client
    except ConnectionFailure as e:
        print(f"\n[ERROR] No se pudo conectar a MongoDB: {e}")
        print("  Asegurate de que Docker esté corriendo:")
        print("    docker-compose up -d")
        sys.exit(1)


def cargar_coleccion(db, nombre_coleccion, nombre_json):
    ruta = os.path.join(DIR_JSON, f"{nombre_json}.json")
    if not os.path.exists(ruta):
        print(f"  [AVISO] No encontrado: {ruta}")
        return

    with open(ruta, "r", encoding="utf-8") as f:
        documentos = json.load(f)

    if not documentos:
        print(f"  [AVISO] {nombre_json}.json está vacío.")
        return

    col = db[nombre_coleccion]

    # Limpiar colección antes de insertar (idempotente)
    col.drop()
    print(f"  Colección '{nombre_coleccion}' limpiada.")

    try:
        resultado = col.insert_many(documentos, ordered=False)
        print(f"    {len(resultado.inserted_ids)} documentos insertados en '{nombre_coleccion}'.")
    except BulkWriteError as e:
        print(f"  [ERROR] BulkWriteError en '{nombre_coleccion}': {e.details}")


def crear_indices(db):
    print("\n── creando indices")

    # ── mundiales ──────────────────────────────────────────────
    col_m = db["mundiales"]
    col_m.create_index([("anio", ASCENDING)], unique=True, name="idx_mundiales_anio")
    col_m.create_index([("partidos.local",    ASCENDING)], name="idx_part_local")
    col_m.create_index([("partidos.visitante",ASCENDING)], name="idx_part_visitante")
    col_m.create_index([("partidos.etapa",    ASCENDING)], name="idx_part_etapa")
    col_m.create_index([("partidos.fecha",    ASCENDING)], name="idx_part_fecha")
    col_m.create_index([("grupos.grupo",      ASCENDING)], name="idx_grupo")
    col_m.create_index([("grupos.seleccion",  ASCENDING)], name="idx_grupo_sel")
    print("   indices creados en 'mundiales'.")

    # ── selecciones ────────────────────────────────────────────
    col_s = db["selecciones"]
    col_s.create_index([("nombre", ASCENDING)], unique=True, name="idx_sel_nombre")
    col_s.create_index([("nombre", TEXT)],      name="idx_sel_text", default_language="spanish")
    col_s.create_index([("participaciones.anio",            ASCENDING)], name="idx_sel_part_anio")
    col_s.create_index([("participaciones.partidos.local",  ASCENDING)], name="idx_sel_part_local")
    col_s.create_index([("participaciones.partidos.visitante", ASCENDING)], name="idx_sel_part_visitante")
    print("   indices creados en 'selecciones'.")


def cargar_bd():
    print("\n" + "=" * 60)
    print("  Cargando documentos JSON en MongoDB (mundiales)")
    print("=" * 60)

    client = obtener_cliente()
    db = client[DB_NAME]

    print("\n── Insertando colecciones...")
    cargar_coleccion(db, "mundiales",   "mundiales")
    cargar_coleccion(db, "selecciones", "selecciones")

    crear_indices(db)

    client.close()

    print("\n" + "=" * 60)
    print("  Carga completada en MongoDB.")
    print("  Compass URI: mongodb://mundiales_user:mundiales1234@127.0.0.1:27017/mundiales?authSource=admin")
    print("=" * 60)


if __name__ == "__main__":
    cargar_bd()
