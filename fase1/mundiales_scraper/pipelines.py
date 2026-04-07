# Define your item pipelines here
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import os

from itemadapter import ItemAdapter

from mundiales_scraper.items import (
    MundialItem,
    SeleccionItem,
    JugadorItem,
    JugadorMundialItem,
    GoleadorMundialItem,
    PartidoItem,
    PosicionFinalItem,
    PremioItem,
    GrupoItem,
    TarjetaItem,
    PartidoJugadorItem,
    PartidoGolItem,
    PlantelItem,
)

OUTPUT_DIR = "output"


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


# ---------------------------------------------------------------------------
# Field definitions per item type
# ---------------------------------------------------------------------------

MUNDIALES_FIELDS = [
    "anio", "organizador", "campeon", "selecciones",
    "partidos", "goles", "promedio_gol", "url", "fecha_scraping",
]

SELECCIONES_FIELDS = [
    "seleccion", "mundiales_jugados",
    "campeon_veces", "campeon_anios",
    "subcampeon_veces", "subcampeon_anios",
    "posicion_historica",
    "partidos_jugados", "partidos_ganados", "partidos_empatados", "partidos_perdidos",
    "goles_favor", "goles_contra", "diferencia_gol",
    "url", "fecha_scraping",
]

JUGADORES_FIELDS = [
    "nombre", "nombre_completo", "fecha_nacimiento", "lugar_nacimiento",
    "posicion", "seleccion", "numeros_camiseta", "altura", "apodo",
    "total_mundiales", "total_partidos", "total_goles", "promedio_gol",
    "campeon", "url", "fecha_scraping",
]

JUGADORES_MUNDIAL_FIELDS = [
    "jugador", "seleccion", "mundial", "camiseta", "posicion",
    "jugados", "titular", "capitan", "no_jugo",
    "goles", "promedio_gol",
    "tarjetas_amarillas", "tarjetas_rojas",
    "pg", "pe", "pp", "posicion_final",
    "url_jugador", "fecha_scraping",
]

GOLEADORES_FIELDS = [
    "mundial", "posicion", "jugador", "seleccion", "goles",
    "partidos", "promedio_gol",
    "url_jugador", "url", "fecha_scraping",
]

PARTIDOS_FIELDS = [
    "mundial", "num", "fecha", "etapa",
    "local", "goles_local", "goles_visitante", "visitante",
    "url_partido", "url", "fecha_scraping",
]

POSICIONES_FINALES_FIELDS = [
    "mundial", "posicion", "seleccion", "etapa",
    "pts", "pj", "pg", "pe", "pp", "gf", "gc", "dif",
    "url", "fecha_scraping",
]

PREMIOS_FIELDS = [
    "mundial", "tipo_premio", "jugador_o_seleccion", "url_jugador",
    "url", "fecha_scraping",
]

GRUPOS_FIELDS = [
    "mundial", "grupo", "posicion", "seleccion",
    "pj", "pg", "pe", "pp", "gf", "gc", "dif", "pts",
    "clasificado", "url", "fecha_scraping",
]

TARJETAS_FIELDS = [
    "mundial", "jugador", "seleccion",
    "amarillas", "rojas", "rd", "ta2",
    "partidos", "url_jugador", "url", "fecha_scraping",
]

PARTIDO_JUGADORES_FIELDS = [
    "mundial", "url_partido", "seleccion", "jugador", "url_jugador",
    "camiseta", "posicion", "rol", "capitan",
    "minuto_entrada", "minuto_salida", "goles_count", "goles_minutos",
    "fecha_scraping",
]

PARTIDO_GOLES_FIELDS = [
    "mundial", "url_partido", "seleccion", "jugador",
    "minuto", "tipo_gol", "fecha_scraping",
]

PLANTELES_FIELDS = [
    "mundial", "seleccion", "camiseta", "jugador", "url_jugador",
    "posicion_grupo", "fecha_nacimiento", "altura", "club",
    "url", "fecha_scraping",
]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class CsvPipeline:
    """
    Writes each typed item to its own CSV file with clean named columns.
    - mundiales.csv
    - selecciones.csv
    - jugadores.csv
    - jugadores_por_mundial.csv
    - goleadores.csv
    - partidos.csv
    - posiciones_finales.csv
    - premios.csv
    - grupos.csv
    - tarjetas.csv
    - partido_jugadores.csv
    - partido_goles.csv
    - planteles.csv
    """

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider=None):
        _ensure_dir(OUTPUT_DIR)
        self._files = {}
        self._writers = {}

        specs = [
            ("mundiales",           MUNDIALES_FIELDS),
            ("selecciones",         SELECCIONES_FIELDS),
            ("jugadores",           JUGADORES_FIELDS),
            ("jugadores_por_mundial", JUGADORES_MUNDIAL_FIELDS),
            ("goleadores",          GOLEADORES_FIELDS),
            ("partidos",            PARTIDOS_FIELDS),
            ("posiciones_finales",  POSICIONES_FINALES_FIELDS),
            ("premios",             PREMIOS_FIELDS),
            ("grupos",              GRUPOS_FIELDS),
            ("tarjetas",            TARJETAS_FIELDS),
            ("partido_jugadores",   PARTIDO_JUGADORES_FIELDS),
            ("partido_goles",       PARTIDO_GOLES_FIELDS),
            ("planteles",           PLANTELES_FIELDS),
        ]
        for name, fields in specs:
            path = os.path.join(OUTPUT_DIR, f"{name}.csv")
            is_new = not os.path.exists(path) or os.path.getsize(path) == 0
            f = open(path, "a", buffering=1, newline="", encoding="utf-8")
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            if is_new:
                writer.writeheader()
            self._files[name] = f
            self._writers[name] = writer

    def close_spider(self, spider=None):
        for f in self._files.values():
            f.close()

    def process_item(self, item, spider=None):
        data = dict(ItemAdapter(item))

        if isinstance(item, MundialItem):
            self._writers["mundiales"].writerow(data)
            self._files["mundiales"].flush()

        elif isinstance(item, SeleccionItem):
            self._writers["selecciones"].writerow(data)
            self._files["selecciones"].flush()

        elif isinstance(item, JugadorItem):
            self._writers["jugadores"].writerow(data)
            self._files["jugadores"].flush()

        elif isinstance(item, JugadorMundialItem):
            self._writers["jugadores_por_mundial"].writerow(data)
            self._files["jugadores_por_mundial"].flush()

        elif isinstance(item, GoleadorMundialItem):
            self._writers["goleadores"].writerow(data)
            self._files["goleadores"].flush()

        elif isinstance(item, PartidoItem):
            self._writers["partidos"].writerow(data)
            self._files["partidos"].flush()

        elif isinstance(item, PosicionFinalItem):
            self._writers["posiciones_finales"].writerow(data)
            self._files["posiciones_finales"].flush()

        elif isinstance(item, PremioItem):
            self._writers["premios"].writerow(data)
            self._files["premios"].flush()

        elif isinstance(item, GrupoItem):
            self._writers["grupos"].writerow(data)
            self._files["grupos"].flush()

        elif isinstance(item, TarjetaItem):
            self._writers["tarjetas"].writerow(data)
            self._files["tarjetas"].flush()

        elif isinstance(item, PartidoJugadorItem):
            self._writers["partido_jugadores"].writerow(data)
            self._files["partido_jugadores"].flush()

        elif isinstance(item, PartidoGolItem):
            self._writers["partido_goles"].writerow(data)
            self._files["partido_goles"].flush()

        elif isinstance(item, PlantelItem):
            self._writers["planteles"].writerow(data)
            self._files["planteles"].flush()

        return item
