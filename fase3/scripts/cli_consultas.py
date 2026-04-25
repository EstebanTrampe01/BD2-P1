import json
import argparse
from metodos_consultas import metodo_info_mundial, metodo_info_pais


SEP = "=" * 80
SUB = "-" * 80


def imprimir_json(resultado):
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


def imprimir_partido(p, pref=""):
    print(f"{pref}Partido #{p.get('numero', '-')}")
    print(f"{pref}Fecha: {p.get('fecha', '-')}")
    print(f"{pref}Etapa: {p.get('etapa', '-')}")
    print(
        f"{pref}{p.get('local', '-')} {p.get('goles_local', '-')} - "
        f"{p.get('goles_visitante', '-')} {p.get('visitante', '-')}"
    )

    goles = p.get("goles", [])
    if goles:
        print(f"{pref}Goles:")
        for g in goles:
            print(
                f"{pref}  - {g.get('jugador', '-')} "
                f"({g.get('seleccion', '-')}) "
                f"min {g.get('minuto', '-')} "
                f"[{g.get('tipo_gol', '-')}]"
            )


def imprimir_mundial(resultado):
    if not resultado.get("ok"):
        print(resultado.get("mensaje", "Consulta no exitosa"))
        return

    print(SEP)
    print("CONSULTA POR MUNDIAL")
    print(SEP)

    if resultado.get("mensaje"):
        print("Mensaje:", resultado["mensaje"])
        print()

    filtros = resultado.get("filtros", {})
    print("Filtros:")
    print(f"  Año   : {filtros.get('anio')}")
    print(f"  Grupo : {filtros.get('grupo')}")
    print(f"  País  : {filtros.get('pais')}")
    print(f"  Fecha : {filtros.get('fecha')}")
    print()

    info = resultado.get("info_general", {})
    print("Información general:")
    print(f"  Año                : {info.get('anio')}")
    print(f"  Organizador        : {info.get('organizador')}")
    print(f"  Campeón            : {info.get('campeon')}")
    print(f"  Subcampeón         : {info.get('subcampeon')}")
    print(f"  Selecciones total  : {info.get('selecciones_total')}")
    print(f"  Partidos total     : {info.get('partidos_total')}")
    print(f"  Goles total        : {info.get('goles_total')}")
    print(f"  Promedio gol       : {info.get('promedio_gol')}")
    print()

    grupos = resultado.get("grupos", [])
    print(SUB)
    print(f"GRUPOS ({len(grupos)})")
    print(SUB)
    for g in grupos:
        print(
            f"{g.get('grupo', '-')} | {g.get('seleccion', '-')} | "
            f"Pos {g.get('posicion', '-')} | PJ {g.get('pj', '-')} | "
            f"PG {g.get('pg', '-')} | PE {g.get('pe', '-')} | PP {g.get('pp', '-')} | "
            f"GF {g.get('gf', '-')} | GC {g.get('gc', '-')} | DIF {g.get('dif', '-')} | "
            f"PTS {g.get('pts', '-')} | Clasificado {g.get('clasificado', '-')}"
        )
    print()

    partidos = resultado.get("partidos", [])
    print(SUB)
    print(f"PARTIDOS ({len(partidos)})")
    print(SUB)
    for p in partidos:
        imprimir_partido(p)
        print()

    posiciones = resultado.get("posiciones_finales", [])
    print(SUB)
    print(f"POSICIONES FINALES ({len(posiciones)})")
    print(SUB)
    for p in posiciones:
        print(
            f"#{p.get('posicion', '-')} | {p.get('seleccion', '-')} | "
            f"{p.get('etapa', '-')} | PJ {p.get('pj', '-')} | "
            f"PG {p.get('pg', '-')} | PE {p.get('pe', '-')} | "
            f"PP {p.get('pp', '-')} | GF {p.get('gf', '-')} | "
            f"GC {p.get('gc', '-')} | DIF {p.get('dif', '-')}"
        )
    print()

    goleadores = resultado.get("goleadores", [])
    print(SUB)
    print(f"GOLEADORES ({len(goleadores)})")
    print(SUB)
    for g in goleadores:
        print(
            f"#{g.get('posicion', '-')} | {g.get('jugador', '-')} | "
            f"{g.get('seleccion', '-')} | Goles {g.get('goles', '-')} | "
            f"Partidos {g.get('partidos', '-')} | Prom {g.get('promedio_gol', '-')}"
        )
    print()

    premios = resultado.get("premios", [])
    print(SUB)
    print(f"PREMIOS ({len(premios)})")
    print(SUB)
    for p in premios:
        print(f"{p.get('tipo_premio', '-')} -> {p.get('ganador', '-')}")
    print()

    tarjetas = resultado.get("tarjetas", [])
    print(SUB)
    print(f"TARJETAS ({len(tarjetas)})")
    print(SUB)
    for t in tarjetas:
        print(
            f"{t.get('jugador', '-')} | {t.get('seleccion', '-')} | "
            f"A {t.get('amarillas', '-')} | R {t.get('rojas', '-')} | "
            f"RD {t.get('rojas_directas', '-')} | TA2 {t.get('rojas_x2amarillas', '-')}"
        )
    print()

    planteles = resultado.get("planteles", [])
    print(SUB)
    print(f"PLANTELES ({len(planteles)})")
    print(SUB)
    for pl in planteles:
        jugadores = pl.get("jugadores", [])
        print(f"Selección: {pl.get('seleccion', '-')} | Jugadores: {len(jugadores)}")
    print()


def imprimir_pais(resultado):
    if not resultado.get("ok"):
        print(resultado.get("mensaje", "Consulta no exitosa"))
        return

    print(SEP)
    print("CONSULTA POR PAÍS")
    print(SEP)

    if resultado.get("mensaje"):
        print("Mensaje:", resultado["mensaje"])
        print()

    filtros = resultado.get("filtros", {})
    print("Filtros:")
    print(f"  País buscado : {filtros.get('pais_buscado')}")
    print(f"  País resuelto: {filtros.get('pais_resuelto')}")
    print(f"  Año          : {filtros.get('anio')}")
    print(f"  Fase         : {filtros.get('fase')}")
    print()

    info = resultado.get("info_historica", {})
    print("Información histórica:")
    print(f"  Nombre              : {info.get('nombre')}")
    print(f"  Mundiales jugados   : {info.get('mundiales_jugados')}")
    print(f"  Campeón veces       : {info.get('campeon_veces')}")
    print(f"  Años campeón        : {info.get('campeon_anios')}")
    print(f"  Subcampeón veces    : {info.get('subcampeon_veces')}")
    print(f"  Años subcampeón     : {info.get('subcampeon_anios')}")
    print(f"  Posición histórica  : {info.get('posicion_historica')}")
    print(f"  PJ                  : {info.get('partidos_jugados')}")
    print(f"  PG                  : {info.get('partidos_ganados')}")
    print(f"  PE                  : {info.get('partidos_empatados')}")
    print(f"  PP                  : {info.get('partidos_perdidos')}")
    print(f"  GF                  : {info.get('goles_favor')}")
    print(f"  GC                  : {info.get('goles_contra')}")
    print(f"  DIF                 : {info.get('diferencia_gol')}")
    print(f"  Sedes               : {info.get('sedes')}")
    print(f"  Años participación  : {info.get('anios_participacion')}")
    print()

    participaciones = resultado.get("participaciones", [])
    print(SUB)
    print(f"PARTICIPACIONES ({len(participaciones)})")
    print(SUB)

    for part in participaciones:
        print(f"Año: {part.get('anio')}")
        print(f"  Fue sede       : {part.get('fue_sede')}")
        print(f"  Fue campeón    : {part.get('fue_campeon')}")
        print(f"  Fue subcampeón : {part.get('fue_subcampeon')}")
        print(f"  Posición final : {part.get('posicion_final')}")
        print(f"  Etapa final    : {part.get('etapa_final')}")

        grupo = part.get("grupo")
        if grupo:
            print("  Grupo:")
            print(
                f"    {grupo.get('grupo', '-')} | Pos {grupo.get('posicion', '-')} | "
                f"PJ {grupo.get('pj', '-')} | PG {grupo.get('pg', '-')} | "
                f"PE {grupo.get('pe', '-')} | PP {grupo.get('pp', '-')} | "
                f"GF {grupo.get('gf', '-')} | GC {grupo.get('gc', '-')} | "
                f"PTS {grupo.get('pts', '-')}"
            )

        partidos = part.get("partidos", [])
        print(f"  Partidos ({len(partidos)}):")
        for p in partidos:
            imprimir_partido(p, pref="    ")
            print(f"    Resultado para el país: {p.get('resultado_para_el_pais', '-')}")
            print()

        plantel = part.get("plantel", [])
        print(f"  Plantel ({len(plantel)} jugadores)")

        estadisticas = part.get("estadisticas_jugadores", [])
        print(f"  Estadísticas de jugadores ({len(estadisticas)})")
        print(SUB)


def main():
    parser = argparse.ArgumentParser(description="Consultas de Mundiales de Fútbol en MongoDB")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    parser_mundial = subparsers.add_parser("mundial", help="Consultar información de un mundial por año")
    parser_mundial.add_argument("anio", type=int, help="Año del mundial")
    parser_mundial.add_argument("--grupo", type=str, default=None, help="Grupo, por ejemplo A")
    parser_mundial.add_argument("--pais", type=str, default=None, help="País, por ejemplo Argentina")
    parser_mundial.add_argument("--fecha", type=str, default=None, help="Fecha exacta, por ejemplo 18-Dec-2022")
    parser_mundial.add_argument("--json", action="store_true", help="Imprimir resultado en JSON")

    parser_pais = subparsers.add_parser("pais", help="Consultar información histórica de una selección")
    parser_pais.add_argument("pais", type=str, help="Nombre del país")
    parser_pais.add_argument("--anio", type=int, default=None, help="Filtrar por año")
    parser_pais.add_argument("--fase", type=str, default=None, help="Filtrar por fase, por ejemplo Final")
    parser_pais.add_argument("--json", action="store_true", help="Imprimir resultado en JSON")

    args = parser.parse_args()

    if args.comando == "mundial":
        resultado = metodo_info_mundial(
            anio=args.anio,
            grupo=args.grupo,
            pais=args.pais,
            fecha=args.fecha
        )
        if args.json:
            imprimir_json(resultado)
        else:
            imprimir_mundial(resultado)

    elif args.comando == "pais":
        resultado = metodo_info_pais(
            pais=args.pais,
            anio=args.anio,
            fase=args.fase
        )
        if args.json:
            imprimir_json(resultado)
        else:
            imprimir_pais(resultado)


if __name__ == "__main__":
    main()