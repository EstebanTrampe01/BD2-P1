# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MundialItem(scrapy.Item):
    """Una fila por cada edicion del Mundial."""
    anio = scrapy.Field()           # p. ej. "2022"
    organizador = scrapy.Field()    # p. ej. "Catar"
    campeon = scrapy.Field()        # p. ej. "Argentina"
    selecciones = scrapy.Field()    # p. ej. "32"
    partidos = scrapy.Field()       # p. ej. "64"
    goles = scrapy.Field()          # p. ej. "172"
    promedio_gol = scrapy.Field()   # p. ej. "2.69"
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class SeleccionItem(scrapy.Item):
    """Una fila por cada seleccion nacional."""
    seleccion = scrapy.Field()          # p. ej. "Brasil"
    mundiales_jugados = scrapy.Field()  # p. ej. "23"
    campeon_veces = scrapy.Field()      # p. ej. "5"
    campeon_anios = scrapy.Field()      # p. ej. "1958,1962,1970,1994,2002"
    subcampeon_veces = scrapy.Field()   # p. ej. "2"
    subcampeon_anios = scrapy.Field()   # p. ej. "1950,1998"
    posicion_historica = scrapy.Field() # p. ej. "1"
    partidos_jugados = scrapy.Field()   # p. ej. "114"
    partidos_ganados = scrapy.Field()   # p. ej. "76"
    partidos_empatados = scrapy.Field() # p. ej. "19"
    partidos_perdidos = scrapy.Field()  # p. ej. "19"
    goles_favor = scrapy.Field()        # p. ej. "237"
    goles_contra = scrapy.Field()       # p. ej. "108"
    diferencia_gol = scrapy.Field()     # p. ej. "+129"
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class JugadorItem(scrapy.Item):
    """Una fila por jugador: bio + totales de carrera."""
    nombre = scrapy.Field()             # p. ej. "Lionel Messi"
    nombre_completo = scrapy.Field()
    fecha_nacimiento = scrapy.Field()
    lugar_nacimiento = scrapy.Field()
    posicion = scrapy.Field()
    seleccion = scrapy.Field()          # p. ej. "Argentina"
    numeros_camiseta = scrapy.Field()
    altura = scrapy.Field()
    apodo = scrapy.Field()
    # totales de carrera
    total_mundiales = scrapy.Field()    # p. ej. "5"
    total_partidos = scrapy.Field()     # p. ej. "26"
    total_goles = scrapy.Field()        # p. ej. "13"
    promedio_gol = scrapy.Field()       # p. ej. "0.50"
    campeon = scrapy.Field()            # p. ej. "2022" (o anios separados por coma)
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class JugadorMundialItem(scrapy.Item):
    """Una fila por jugador por Mundial."""
    jugador = scrapy.Field()            # p. ej. "Lionel Messi"
    seleccion = scrapy.Field()          # p. ej. "Argentina"
    mundial = scrapy.Field()            # p. ej. "2022"
    camiseta = scrapy.Field()           # p. ej. "10"
    posicion = scrapy.Field()           # p. ej. "Delantero"
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
    posicion_final = scrapy.Field()     # posicion final del equipo en ese Mundial
    url_jugador = scrapy.Field()
    fecha_scraping = scrapy.Field()


class GoleadorMundialItem(scrapy.Item):
    """Una fila por registro de goleador en _goleadores.php."""
    mundial = scrapy.Field()            # p. ej. "2022"
    posicion = scrapy.Field()           # p. ej. "1"
    jugador = scrapy.Field()            # p. ej. "Kylian Mbappe"
    seleccion = scrapy.Field()          # p. ej. "Francia"
    goles = scrapy.Field()              # p. ej. "8"
    partidos = scrapy.Field()           # p. ej. "7"
    promedio_gol = scrapy.Field()       # p. ej. "1.14"
    url_jugador = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PartidoItem(scrapy.Item):
    """Una fila por partido del calendario de un Mundial (_resultados.php)."""
    mundial = scrapy.Field()            # p. ej. "2022"
    num = scrapy.Field()                # p. ej. "1"
    fecha = scrapy.Field()              # p. ej. "20-Nov-2022"
    etapa = scrapy.Field()              # p. ej. "1ra Ronda, Grupo A"
    local = scrapy.Field()              # p. ej. "Catar"
    goles_local = scrapy.Field()        # p. ej. "0"
    goles_visitante = scrapy.Field()    # p. ej. "2"
    visitante = scrapy.Field()          # p. ej. "Ecuador"
    url_partido = scrapy.Field()        # enlace relativo al detalle del partido
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PosicionFinalItem(scrapy.Item):
    """Una fila por seleccion en la tabla final (_posiciones_finales.php)."""
    mundial = scrapy.Field()            # p. ej. "2022"
    posicion = scrapy.Field()           # p. ej. "1"
    seleccion = scrapy.Field()          # p. ej. "Argentina"
    etapa = scrapy.Field()              # p. ej. "Final"
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
    """Una fila por premio individual en _premios.php."""
    mundial = scrapy.Field()            # p. ej. "2022"
    tipo_premio = scrapy.Field()        # p. ej. "Balon de Oro"
    jugador_o_seleccion = scrapy.Field()  # p. ej. "Lionel Messi"
    url_jugador = scrapy.Field()        # enlace relativo (puede venir vacio en premios de equipo)
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class GrupoItem(scrapy.Item):
    """Una fila por seleccion en una tabla de grupo (_grupo_X.php)."""
    mundial = scrapy.Field()            # p. ej. "2022"
    grupo = scrapy.Field()              # p. ej. "A"
    posicion = scrapy.Field()           # p. ej. "1"
    seleccion = scrapy.Field()          # p. ej. "Ecuador"
    pj = scrapy.Field()
    pg = scrapy.Field()
    pe = scrapy.Field()
    pp = scrapy.Field()
    gf = scrapy.Field()
    gc = scrapy.Field()
    dif = scrapy.Field()
    pts = scrapy.Field()
    clasificado = scrapy.Field()        # p. ej. "Si" o "No"
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class TarjetaItem(scrapy.Item):
    """Una fila por registro de tarjetas de jugador en _tarjetas.php."""
    mundial = scrapy.Field()
    jugador = scrapy.Field()
    seleccion = scrapy.Field()
    amarillas = scrapy.Field()          # conteo como texto, p. ej. "3"
    rojas = scrapy.Field()              # conteo como texto, p. ej. "1"
    rd = scrapy.Field()                 # roja directa, p. ej. "1" o "-"
    ta2 = scrapy.Field()                # roja por 2a amarilla, p. ej. "1" o "-"
    partidos = scrapy.Field()
    url_jugador = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PartidoJugadorItem(scrapy.Item):
    """Una fila por jugador por partido (desde /partidos/)."""
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
    goles_count = scrapy.Field()    # p. ej. "2"
    goles_minutos = scrapy.Field()  # p. ej. "16,31"
    fecha_scraping = scrapy.Field()


class PartidoGolItem(scrapy.Item):
    """Una fila por gol en un partido (desde /partidos/)."""
    mundial = scrapy.Field()
    url_partido = scrapy.Field()
    seleccion = scrapy.Field()
    jugador = scrapy.Field()
    minuto = scrapy.Field()
    tipo_gol = scrapy.Field()       # normal / penal / autogol
    fecha_scraping = scrapy.Field()


class PlantelItem(scrapy.Item):
    """Una fila por jugador en un plantel mundialista."""
    mundial = scrapy.Field()
    seleccion = scrapy.Field()
    camiseta = scrapy.Field()
    jugador = scrapy.Field()
    url_jugador = scrapy.Field()
    posicion_grupo = scrapy.Field() # Arquero/Defensor/Mediocampista/Delantero/Entrenador
    fecha_nacimiento = scrapy.Field()
    altura = scrapy.Field()         # p. ej. "1.89 m"
    club = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()
