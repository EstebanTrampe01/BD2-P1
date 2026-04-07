# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MundialItem(scrapy.Item):
    """One row per World Cup edition."""
    anio = scrapy.Field()           # e.g. "2022"
    organizador = scrapy.Field()    # e.g. "Catar"
    campeon = scrapy.Field()        # e.g. "Argentina"
    selecciones = scrapy.Field()    # e.g. "32"
    partidos = scrapy.Field()       # e.g. "64"
    goles = scrapy.Field()          # e.g. "172"
    promedio_gol = scrapy.Field()   # e.g. "2.69"
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class SeleccionItem(scrapy.Item):
    """One row per national team."""
    seleccion = scrapy.Field()          # e.g. "Brasil"
    mundiales_jugados = scrapy.Field()  # e.g. "23"
    campeon_veces = scrapy.Field()      # e.g. "5"
    campeon_anios = scrapy.Field()      # e.g. "1958,1962,1970,1994,2002"
    subcampeon_veces = scrapy.Field()   # e.g. "2"
    subcampeon_anios = scrapy.Field()   # e.g. "1950,1998"
    posicion_historica = scrapy.Field() # e.g. "1"
    partidos_jugados = scrapy.Field()   # e.g. "114"
    partidos_ganados = scrapy.Field()   # e.g. "76"
    partidos_empatados = scrapy.Field() # e.g. "19"
    partidos_perdidos = scrapy.Field()  # e.g. "19"
    goles_favor = scrapy.Field()        # e.g. "237"
    goles_contra = scrapy.Field()       # e.g. "108"
    diferencia_gol = scrapy.Field()     # e.g. "+129"
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class JugadorItem(scrapy.Item):
    """One row per player — bio + career totals."""
    nombre = scrapy.Field()             # e.g. "Lionel Messi"
    nombre_completo = scrapy.Field()
    fecha_nacimiento = scrapy.Field()
    lugar_nacimiento = scrapy.Field()
    posicion = scrapy.Field()
    seleccion = scrapy.Field()          # e.g. "Argentina"
    numeros_camiseta = scrapy.Field()
    altura = scrapy.Field()
    apodo = scrapy.Field()
    # career totals
    total_mundiales = scrapy.Field()    # e.g. "5"
    total_partidos = scrapy.Field()     # e.g. "26"
    total_goles = scrapy.Field()        # e.g. "13"
    promedio_gol = scrapy.Field()       # e.g. "0.50"
    campeon = scrapy.Field()            # e.g. "2022" (or comma-separated years)
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class JugadorMundialItem(scrapy.Item):
    """One row per player-per-World Cup."""
    jugador = scrapy.Field()            # e.g. "Lionel Messi"
    seleccion = scrapy.Field()          # e.g. "Argentina"
    mundial = scrapy.Field()            # e.g. "2022"
    camiseta = scrapy.Field()           # e.g. "10"
    posicion = scrapy.Field()           # e.g. "Delantero"
    jugados = scrapy.Field()
    titular = scrapy.Field()
    capitan = scrapy.Field()
    no_jugo = scrapy.Field()
    goles = scrapy.Field()
    promedio_gol = scrapy.Field()
    tarjetas_amarillas = scrapy.Field()
    tarjetas_rojas = scrapy.Field()
    pg = scrapy.Field()
    pe = scrapy.Field()
    pp = scrapy.Field()
    posicion_final = scrapy.Field()     # team's final standing in that WC
    url_jugador = scrapy.Field()
    fecha_scraping = scrapy.Field()


class GoleadorMundialItem(scrapy.Item):
    """One row per scorer entry from the full _goleadores.php page."""
    mundial = scrapy.Field()            # e.g. "2022"
    posicion = scrapy.Field()           # e.g. "1"
    jugador = scrapy.Field()            # e.g. "Kylian Mbappé"
    seleccion = scrapy.Field()          # e.g. "Francia"
    goles = scrapy.Field()              # e.g. "8"
    partidos = scrapy.Field()           # e.g. "7"
    promedio_gol = scrapy.Field()       # e.g. "1.14"
    url_jugador = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PartidoItem(scrapy.Item):
    """One row per match in a World Cup calendar (_resultados.php)."""
    mundial = scrapy.Field()            # e.g. "2022"
    num = scrapy.Field()                # e.g. "1"
    fecha = scrapy.Field()              # e.g. "20-Nov-2022"
    etapa = scrapy.Field()              # e.g. "1ra Ronda, Grupo A"
    local = scrapy.Field()              # e.g. "Catar"
    goles_local = scrapy.Field()        # e.g. "0"
    goles_visitante = scrapy.Field()    # e.g. "2"
    visitante = scrapy.Field()          # e.g. "Ecuador"
    url_partido = scrapy.Field()        # relative link to match detail page
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PosicionFinalItem(scrapy.Item):
    """One row per team in the final standings table (_posiciones_finales.php)."""
    mundial = scrapy.Field()            # e.g. "2022"
    posicion = scrapy.Field()           # e.g. "1"
    seleccion = scrapy.Field()          # e.g. "Argentina"
    etapa = scrapy.Field()              # e.g. "Final"
    pts = scrapy.Field()
    pj = scrapy.Field()
    pg = scrapy.Field()
    pe = scrapy.Field()
    pp = scrapy.Field()
    gf = scrapy.Field()
    gc = scrapy.Field()
    dif = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PremioItem(scrapy.Item):
    """One row per individual award on a _premios.php page."""
    mundial = scrapy.Field()            # e.g. "2022"
    tipo_premio = scrapy.Field()        # e.g. "Balón de Oro"
    jugador_o_seleccion = scrapy.Field()  # e.g. "Lionel Messi"
    url_jugador = scrapy.Field()        # relative link (may be empty for team awards)
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class GrupoItem(scrapy.Item):
    """One row per team in a group-stage standings table (_grupo_X.php)."""
    mundial = scrapy.Field()            # e.g. "2022"
    grupo = scrapy.Field()              # e.g. "A"
    posicion = scrapy.Field()           # e.g. "1"
    seleccion = scrapy.Field()          # e.g. "Ecuador"
    pj = scrapy.Field()
    pg = scrapy.Field()
    pe = scrapy.Field()
    pp = scrapy.Field()
    gf = scrapy.Field()
    gc = scrapy.Field()
    dif = scrapy.Field()
    pts = scrapy.Field()
    clasificado = scrapy.Field()        # e.g. "Si" or "No"
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class TarjetaItem(scrapy.Item):
    """One row per player card entry on a _tarjetas.php page."""
    mundial = scrapy.Field()
    jugador = scrapy.Field()
    seleccion = scrapy.Field()
    amarillas = scrapy.Field()          # count as string e.g. "3"
    rojas = scrapy.Field()              # count as string e.g. "1"
    rd = scrapy.Field()                 # roja directa count e.g. "1" or "-"
    ta2 = scrapy.Field()                # roja por 2a amarilla e.g. "1" or "-"
    partidos = scrapy.Field()
    url_jugador = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PartidoJugadorItem(scrapy.Item):
    """One row per player per match (from /partidos/ detail pages)."""
    mundial = scrapy.Field()
    url_partido = scrapy.Field()
    seleccion = scrapy.Field()
    jugador = scrapy.Field()
    url_jugador = scrapy.Field()
    camiseta = scrapy.Field()
    posicion = scrapy.Field()       # AR/DF/MC/DL
    rol = scrapy.Field()            # Titular / Ingreso / Suplente
    capitan = scrapy.Field()        # Si / No
    minuto_entrada = scrapy.Field()
    minuto_salida = scrapy.Field()
    goles_count = scrapy.Field()    # e.g. "2"
    goles_minutos = scrapy.Field()  # e.g. "16,31"
    fecha_scraping = scrapy.Field()


class PartidoGolItem(scrapy.Item):
    """One row per goal in a match (from /partidos/ detail pages)."""
    mundial = scrapy.Field()
    url_partido = scrapy.Field()
    seleccion = scrapy.Field()
    jugador = scrapy.Field()
    minuto = scrapy.Field()
    tipo_gol = scrapy.Field()       # normal / penal / autogol
    fecha_scraping = scrapy.Field()


class PlantelItem(scrapy.Item):
    """One row per player in a World Cup squad (/planteles/YYYY_PAIS_jugadores.php)."""
    mundial = scrapy.Field()
    seleccion = scrapy.Field()
    camiseta = scrapy.Field()
    jugador = scrapy.Field()
    url_jugador = scrapy.Field()
    posicion_grupo = scrapy.Field() # Arquero/Defensor/Mediocampista/Delantero/Entrenador
    fecha_nacimiento = scrapy.Field()
    altura = scrapy.Field()         # e.g. "1.89 m"
    club = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()
