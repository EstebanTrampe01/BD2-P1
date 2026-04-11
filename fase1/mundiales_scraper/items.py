# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MundialItem(scrapy.Item):
    anio = scrapy.Field()
    organizador = scrapy.Field()
    campeon = scrapy.Field()
    selecciones = scrapy.Field()
    partidos = scrapy.Field()
    goles = scrapy.Field()
    promedio_gol = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class SeleccionItem(scrapy.Item):
    seleccion = scrapy.Field()
    mundiales_jugados = scrapy.Field()
    campeon_veces = scrapy.Field()
    campeon_anios = scrapy.Field()
    subcampeon_veces = scrapy.Field()
    subcampeon_anios = scrapy.Field()
    posicion_historica = scrapy.Field()
    partidos_jugados = scrapy.Field()
    partidos_ganados = scrapy.Field()
    partidos_empatados = scrapy.Field()
    partidos_perdidos = scrapy.Field()
    goles_favor = scrapy.Field()
    goles_contra = scrapy.Field()
    diferencia_gol = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class JugadorItem(scrapy.Item):
    nombre = scrapy.Field()
    nombre_completo = scrapy.Field()
    fecha_nacimiento = scrapy.Field()
    lugar_nacimiento = scrapy.Field()
    posicion = scrapy.Field()
    seleccion = scrapy.Field()
    numeros_camiseta = scrapy.Field()
    altura = scrapy.Field()
    apodo = scrapy.Field()
    total_mundiales = scrapy.Field()
    total_partidos = scrapy.Field()
    total_goles = scrapy.Field()
    promedio_gol = scrapy.Field()
    campeon = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class JugadorMundialItem(scrapy.Item):
    jugador = scrapy.Field()
    seleccion = scrapy.Field()
    mundial = scrapy.Field()
    camiseta = scrapy.Field()
    posicion = scrapy.Field()
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
    posicion_final = scrapy.Field()
    url_jugador = scrapy.Field()
    fecha_scraping = scrapy.Field()


class GoleadorMundialItem(scrapy.Item):
    mundial = scrapy.Field()
    posicion = scrapy.Field()
    jugador = scrapy.Field()
    seleccion = scrapy.Field()
    goles = scrapy.Field()
    partidos = scrapy.Field()
    promedio_gol = scrapy.Field()
    url_jugador = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PartidoItem(scrapy.Item):
    mundial = scrapy.Field()
    num = scrapy.Field()
    fecha = scrapy.Field()
    etapa = scrapy.Field()
    local = scrapy.Field()
    goles_local = scrapy.Field()
    goles_visitante = scrapy.Field()
    visitante = scrapy.Field()
    url_partido = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PosicionFinalItem(scrapy.Item):
    mundial = scrapy.Field()
    posicion = scrapy.Field()
    seleccion = scrapy.Field()
    etapa = scrapy.Field()
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
    mundial = scrapy.Field()
    tipo_premio = scrapy.Field()
    jugador_o_seleccion = scrapy.Field()
    url_jugador = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class GrupoItem(scrapy.Item):
    mundial = scrapy.Field()
    grupo = scrapy.Field()
    posicion = scrapy.Field()
    seleccion = scrapy.Field()
    pj = scrapy.Field()
    pg = scrapy.Field()
    pe = scrapy.Field()
    pp = scrapy.Field()
    gf = scrapy.Field()
    gc = scrapy.Field()
    dif = scrapy.Field()
    pts = scrapy.Field()
    clasificado = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class TarjetaItem(scrapy.Item):
    mundial = scrapy.Field()
    jugador = scrapy.Field()
    seleccion = scrapy.Field()
    amarillas = scrapy.Field()
    rojas = scrapy.Field()
    rd = scrapy.Field()
    ta2 = scrapy.Field()
    partidos = scrapy.Field()
    url_jugador = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PartidoJugadorItem(scrapy.Item):
    mundial = scrapy.Field()
    url_partido = scrapy.Field()
    seleccion = scrapy.Field()
    jugador = scrapy.Field()
    url_jugador = scrapy.Field()
    camiseta = scrapy.Field()
    posicion = scrapy.Field()
    rol = scrapy.Field()
    capitan = scrapy.Field()
    minuto_entrada = scrapy.Field()
    minuto_salida = scrapy.Field()
    goles_count = scrapy.Field()
    goles_minutos = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PartidoGolItem(scrapy.Item):
    mundial = scrapy.Field()
    url_partido = scrapy.Field()
    seleccion = scrapy.Field()
    jugador = scrapy.Field()
    minuto = scrapy.Field()
    tipo_gol = scrapy.Field()
    fecha_scraping = scrapy.Field()


class PlantelItem(scrapy.Item):
    mundial = scrapy.Field()
    seleccion = scrapy.Field()
    camiseta = scrapy.Field()
    jugador = scrapy.Field()
    url_jugador = scrapy.Field()
    posicion_grupo = scrapy.Field()
    fecha_nacimiento = scrapy.Field()
    altura = scrapy.Field()
    club = scrapy.Field()
    url = scrapy.Field()
    fecha_scraping = scrapy.Field()
