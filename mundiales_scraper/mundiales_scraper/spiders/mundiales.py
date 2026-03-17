import re
from datetime import datetime
from urllib.parse import urlparse

import scrapy
from bs4 import BeautifulSoup

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


# ---------------------------------------------------------------------------
# URL classification patterns
# ---------------------------------------------------------------------------
TIPO_URL_PATTERNS = {
    "mundial":            re.compile(r"/mundiales/\d{4}_mundial\.php"),
    "resultados":         re.compile(r"/mundiales/\d{4}_resultados\.php"),
    "posiciones_finales": re.compile(r"/mundiales/\d{4}_posiciones_finales\.php"),
    "goleadores_mundial": re.compile(r"/mundiales/\d{4}_goleadores\.php"),
    "premios":            re.compile(r"/mundiales/\d{4}_premios\.php"),
    "grupo":              re.compile(r"/mundiales/\d{4}_grupo_\w+\.php"),
    "tarjetas":           re.compile(r"/mundiales/\d{4}_tarjetas\.php"),
    "partido":            re.compile(r"/partidos/\d{4}_\w+\.php"),
    "plantel":            re.compile(r"/planteles/\d{4}_\w+_jugadores\.php"),
    "seleccion":          re.compile(r"/selecciones/\w+_seleccion\.php"),
    "jugador":            re.compile(r"/jugadores/[^/]+\.php"),
}

IGNORAR_EXTENSIONES = re.compile(
    r"\.(jpg|jpeg|png|gif|svg|ico|css|js|pdf|zip|xml|json|txt)$",
    re.IGNORECASE,
)

IGNORAR_FRAGMENTOS = re.compile(
    r"(facebook\.com|instagram\.com|twitter\.com|x\.com|linkedin\.com|"
    r"whatsapp|reddit|addthis|google|wa\.me|sobrefutbol|thesoccerworldcups)",
    re.IGNORECASE,
)


def clasificar_tipo(url: str) -> str:
    for tipo, patron in TIPO_URL_PATTERNS.items():
        if patron.search(url):
            return tipo
    return "otro"


def limpiar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto or "").strip()


# ---------------------------------------------------------------------------
# Spider
# ---------------------------------------------------------------------------

class MundialesSpider(scrapy.Spider):
    name = "mundiales"
    allowed_domains = ["losmundialesdefutbol.com", "www.losmundialesdefutbol.com"]
    start_urls = [
        "https://www.losmundialesdefutbol.com/",
        # Index pages garantizan cobertura de todos los tipos aunque el DFS
        # no llegue a procesarlos desde la homepage
        "https://www.losmundialesdefutbol.com/mundiales.php",
        "https://www.losmundialesdefutbol.com/selecciones.php",
        "https://www.losmundialesdefutbol.com/jugadores.php",
    ]

    custom_settings = {
        "DEPTH_LIMIT": 5,
    }

    def parse(self, response):
        url = response.url
        tipo = clasificar_tipo(url)
        soup = BeautifulSoup(response.text, "lxml")

        if tipo == "mundial":
            yield from self._parse_mundial(response, soup, url)
        elif tipo == "resultados":
            yield from self._parse_resultados(response, soup, url)
        elif tipo == "posiciones_finales":
            yield from self._parse_posiciones_finales(response, soup, url)
        elif tipo == "goleadores_mundial":
            yield from self._parse_goleadores_completo(response, soup, url)
        elif tipo == "premios":
            yield from self._parse_premios(response, soup, url)
        elif tipo == "grupo":
            yield from self._parse_grupo(response, soup, url)
        elif tipo == "tarjetas":
            yield from self._parse_tarjetas(response, soup, url)
        elif tipo == "partido":
            yield from self._parse_partido(response, soup, url)
        elif tipo == "plantel":
            yield from self._parse_plantel(response, soup, url)
        elif tipo == "seleccion":
            yield from self._parse_seleccion(response, soup, url)
        elif tipo == "jugador":
            yield from self._parse_jugador(response, soup, url)

        yield from self._seguir_enlaces(response)

    # -----------------------------------------------------------------------
    # Parser: mundial  (/mundiales/YYYY_mundial.php)
    # -----------------------------------------------------------------------

    def _parse_mundial(self, response, soup, url):
        now = datetime.utcnow().isoformat()

        # Year from URL
        anio_m = re.search(r"/(\d{4})_mundial\.php", url)
        anio = anio_m.group(1) if anio_m else ""

        # Champion: <td> that starts with "Campeón:"
        campeon = ""
        for td in soup.find_all("td"):
            txt = limpiar(td.get_text())
            if txt.startswith("Campe"):
                # May contain a link (past WC) or plain text like "-" (future WC)
                a = td.find("a")
                if a:
                    campeon = limpiar(a.get_text())
                else:
                    raw = re.sub(r"Campe[oó]n\s*:\s*", "", txt, flags=re.IGNORECASE).strip()
                    campeon = raw if raw != "-" else ""
                break

        # Key stats live inside a <p> with "- Organizador:" pattern
        organizador = selecciones = partidos = goles = promedio = ""
        for p in soup.find_all("p"):
            txt = p.get_text()
            if "Organizador:" in txt:
                for line in txt.splitlines():
                    line = limpiar(line)
                    if line.startswith("- Organizador:"):
                        organizador = limpiar(line.replace("- Organizador:", ""))
                    elif line.startswith("- Selecciones:"):
                        selecciones = limpiar(line.replace("- Selecciones:", ""))
                    elif line.startswith("- Partidos:"):
                        partidos = limpiar(line.replace("- Partidos:", ""))
                    elif line.startswith("- Goles:"):
                        goles = limpiar(line.replace("- Goles:", ""))
                    elif line.startswith("- Promedio de Gol:"):
                        promedio = limpiar(line.replace("- Promedio de Gol:", ""))
                break

        yield MundialItem(
            anio=anio,
            organizador=organizador,
            campeon=campeon,
            selecciones=selecciones,
            partidos=partidos,
            goles=goles,
            promedio_gol=promedio,
            url=url,
            fecha_scraping=now,
        )

    def _parse_goleadores_mundial(self, soup, url, anio, now):
        """Extract the top-scorers mini-table on a mundial page."""
        # The goleadores table has a <h3> "Goleadores" just above it;
        # rows look like: <td>N.</td> <td class="a-left">flag + player link</td> <td>N goals</td>
        goleadores_h3 = soup.find("h3", string=re.compile(r"Goleadores", re.I))
        if not goleadores_h3:
            return
        tabla = goleadores_h3.find_next("table")
        if not tabla:
            return

        pos = 0
        for tr in tabla.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 3:
                continue
            pos_txt = limpiar(tds[0].get_text())
            if not re.match(r"^\d", pos_txt):
                continue
            pos += 1

            # player td: contains flag img + player link
            jugador_td = tds[1]
            player_link = jugador_td.find("a")
            jugador_nombre = limpiar(player_link.get_text()) if player_link else limpiar(jugador_td.get_text())
            url_jugador = player_link["href"] if player_link and player_link.get("href") else ""

            # seleccion from img alt
            seleccion = ""
            img = jugador_td.find("img")
            if img:
                seleccion = limpiar(img.get("alt", ""))

            # goals td
            goles_txt = limpiar(tds[2].get_text())
            goles_num = re.search(r"\d+", goles_txt)
            goles = goles_num.group(0) if goles_num else goles_txt

            yield GoleadorMundialItem(
                mundial=anio,
                posicion=str(pos),
                jugador=jugador_nombre,
                seleccion=seleccion,
                goles=goles,
                url_jugador=url_jugador,
                url=url,
                fecha_scraping=now,
            )

    # -----------------------------------------------------------------------
    # Parser: resultados  (/mundiales/YYYY_resultados.php)
    # -----------------------------------------------------------------------

    def _parse_resultados(self, response, soup, url):
        now = datetime.utcnow().isoformat()
        anio_m = re.search(r"/(\d{4})_resultados\.php", url)
        anio = anio_m.group(1) if anio_m else ""

        # Each date block: div.clearfix with an h3 "Fecha: DD-Mon-YYYY"
        for bloque in soup.find_all("div", class_=re.compile(r"overflow-x-auto")):
            h3 = bloque.find("h3", class_="t-enc-2")
            if not h3:
                continue
            fecha_txt = limpiar(h3.get_text())
            fecha = re.sub(r"Fecha\s*:\s*", "", fecha_txt).strip()

            # Each match row inside this date block
            for match_div in bloque.find_all("div", class_=re.compile(r"margen-y3")):
                # Match number from first strong inside a wpx-30 div
                num = ""
                num_div = match_div.find("div", class_=re.compile(r"wpx-30"))
                if num_div:
                    num = re.search(r"\d+", limpiar(num_div.get_text()))
                    num = num.group(0) if num else ""

                # Stage from the a-left wpx-170 div
                etapa = ""
                etapa_div = match_div.find("div", class_=re.compile(r"wpx-170"))
                if etapa_div:
                    etapa = limpiar(etapa_div.get_text())

                # The .game div holds teams and score
                game_div = match_div.find("div", class_=re.compile(r"game"))
                if not game_div:
                    continue

                imgs = game_div.find_all("img")
                local = limpiar(imgs[0].get("alt", "")) if len(imgs) > 0 else ""
                visitante = limpiar(imgs[1].get("alt", "")) if len(imgs) > 1 else ""

                # Score link: "X - Y" text, href = match detail page
                score_a = game_div.find("a", href=re.compile(r"/partidos/"))
                goles_local = goles_visitante = url_partido = ""
                if score_a:
                    score_txt = limpiar(score_a.get_text())
                    score_m = re.match(r"(\d+)\s*-\s*(\d+)", score_txt)
                    if score_m:
                        goles_local = score_m.group(1)
                        goles_visitante = score_m.group(2)
                    url_partido = score_a.get("href", "")

                if not local and not visitante:
                    continue

                yield PartidoItem(
                    mundial=anio,
                    num=num,
                    fecha=fecha,
                    etapa=etapa,
                    local=local,
                    goles_local=goles_local,
                    goles_visitante=goles_visitante,
                    visitante=visitante,
                    url_partido=url_partido,
                    url=url,
                    fecha_scraping=now,
                )

    # -----------------------------------------------------------------------
    # Parser: posiciones_finales  (/mundiales/YYYY_posiciones_finales.php)
    # -----------------------------------------------------------------------

    def _parse_posiciones_finales(self, response, soup, url):
        now = datetime.utcnow().isoformat()
        anio_m = re.search(r"/(\d{4})_posiciones_finales\.php", url)
        anio = anio_m.group(1) if anio_m else ""

        # Find the rankings table — it has a header row with "Posición"
        for table in soup.find_all("table"):
            header_cells = [limpiar(td.get_text()) for td in table.find_all("tr")[0].find_all(["td", "th"])] if table.find_all("tr") else []
            if not any("Posici" in c for c in header_cells):
                continue

            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 8:
                    continue
                pos_txt = limpiar(tds[0].get_text()).rstrip(".")
                if not re.match(r"^\d+$", pos_txt):
                    continue

                # Selección td: use img alt if present, else text
                sel_td = tds[1]
                img = sel_td.find("img")
                if img:
                    seleccion = limpiar(img.get("alt", ""))
                else:
                    seleccion = limpiar(sel_td.get_text())

                etapa = limpiar(tds[2].get_text()) if len(tds) > 2 else ""
                pts  = limpiar(tds[3].get_text()) if len(tds) > 3 else ""
                pj   = limpiar(tds[4].get_text()) if len(tds) > 4 else ""
                pg   = limpiar(tds[5].get_text()) if len(tds) > 5 else ""
                pe   = limpiar(tds[6].get_text()) if len(tds) > 6 else ""
                pp   = limpiar(tds[7].get_text()) if len(tds) > 7 else ""
                gf   = limpiar(tds[8].get_text()) if len(tds) > 8 else ""
                gc   = limpiar(tds[9].get_text()) if len(tds) > 9 else ""
                dif  = limpiar(tds[10].get_text()) if len(tds) > 10 else ""

                yield PosicionFinalItem(
                    mundial=anio,
                    posicion=pos_txt,
                    seleccion=seleccion,
                    etapa=etapa,
                    pts=pts,
                    pj=pj,
                    pg=pg,
                    pe=pe,
                    pp=pp,
                    gf=gf,
                    gc=gc,
                    dif=dif,
                    url=url,
                    fecha_scraping=now,
                )

    # -----------------------------------------------------------------------
    # Parser: premios  (/mundiales/YYYY_premios.php)
    # -----------------------------------------------------------------------

    def _parse_premios(self, response, soup, url):
        now = datetime.utcnow().isoformat()
        anio_m = re.search(r"/(\d{4})_premios\.php", url)
        anio = anio_m.group(1) if anio_m else ""

        # Each award block: div > div.rd-100-30 > p.negri (award name) + p (player)
        for bloque in soup.find_all("div", style=re.compile(r"border")):
            for inner in bloque.find_all("div", class_=re.compile(r"rd-100-30")):
                tipo_p = inner.find("p", class_="negri")
                if not tipo_p:
                    continue
                tipo_premio = limpiar(tipo_p.get_text())

                # Player paragraph: the one right after the award name
                # May have multiple players (e.g. Equipo Ideal has 11)
                for p in inner.find_all("p"):
                    if "negri" in p.get("class", []):
                        continue
                    a = p.find("a")
                    if a:
                        jugador = limpiar(a.get_text())
                        url_jugador = a.get("href", "")
                    else:
                        txt = limpiar(p.get_text())
                        if not txt:
                            continue
                        jugador = txt
                        url_jugador = ""

                    if jugador:
                        yield PremioItem(
                            mundial=anio,
                            tipo_premio=tipo_premio,
                            jugador_o_seleccion=jugador,
                            url_jugador=url_jugador,
                            url=url,
                            fecha_scraping=now,
                        )

    # -----------------------------------------------------------------------
    # Parser: goleadores_completo  (/mundiales/YYYY_goleadores.php)
    # -----------------------------------------------------------------------

    def _parse_goleadores_completo(self, response, soup, url):
        now = datetime.utcnow().isoformat()
        anio_m = re.search(r"/(\d{4})_goleadores\.php", url)
        anio = anio_m.group(1) if anio_m else ""

        for table in soup.find_all("table"):
            # Identify the scorers table by its header
            header_row = table.find("tr", class_="t-enc-2")
            if not header_row:
                continue
            headers = [limpiar(td.get_text()) for td in header_row.find_all(["td", "th"])]
            if not any("Goles" in h for h in headers):
                continue

            pos = 0
            for tr in table.find_all("tr"):
                if "t-enc-2" in tr.get("class", []):
                    continue
                tds = tr.find_all("td")
                if len(tds) < 3:
                    continue
                pos_txt = limpiar(tds[0].get_text()).rstrip(".")
                if not re.match(r"^\d+$", pos_txt):
                    continue
                pos += 1

                # Player td
                jugador_td = tds[1]
                player_link = jugador_td.find("a")
                jugador_nombre = limpiar(player_link.get_text()) if player_link else limpiar(jugador_td.get_text())
                url_jugador = player_link["href"] if player_link and player_link.get("href") else ""
                img = jugador_td.find("img")
                seleccion_from_img = limpiar(img.get("alt", "")) if img else ""

                goles    = limpiar(tds[2].get_text()) if len(tds) > 2 else ""
                partidos = limpiar(tds[3].get_text()) if len(tds) > 3 else ""
                promedio = limpiar(tds[4].get_text()) if len(tds) > 4 else ""
                seleccion = limpiar(tds[5].get_text()) if len(tds) > 5 else seleccion_from_img

                yield GoleadorMundialItem(
                    mundial=anio,
                    posicion=pos_txt,
                    jugador=jugador_nombre,
                    seleccion=seleccion,
                    goles=goles,
                    partidos=partidos,
                    promedio_gol=promedio,
                    url_jugador=url_jugador,
                    url=url,
                    fecha_scraping=now,
                )
            break  # only first matching table

    # -----------------------------------------------------------------------
    # Parser: grupo  (/mundiales/YYYY_grupo_X.php)
    # -----------------------------------------------------------------------

    def _parse_grupo(self, response, soup, url):
        now = datetime.utcnow().isoformat()
        anio_m = re.search(r"/(\d{4})_grupo_(\w+)\.php", url)
        anio  = anio_m.group(1) if anio_m else ""
        grupo = anio_m.group(2).upper() if anio_m else ""

        for table in soup.find_all("table"):
            # Group tables use t-enc-5 for the header row (NOT t-enc-2)
            header_row = table.find("tr", class_="t-enc-5")
            if not header_row:
                continue
            headers = [limpiar(td.get_text()) for td in header_row.find_all(["td", "th"])]
            # Verify it's the standings table by looking for PTS or PJ
            if not any(h in ("PTS", "PJ") for h in headers):
                continue

            # Column order: Posición | Selección | PTS | PJ | PG | PE | PP | GF | GC | Dif | Clasificado
            for tr in table.find_all("tr"):
                # Skip header and separator rows
                if "t-enc-5" in tr.get("class", []):
                    continue
                if tr.find("div", class_="linea-2"):
                    continue
                tds = tr.find_all("td")
                if len(tds) < 4:
                    continue

                # Position in td[0], strip trailing "."
                pos_txt = limpiar(tds[0].get_text()).rstrip(".").strip()
                if not re.match(r"^\d+$", pos_txt):
                    continue

                # Selección in td[1]: use img alt if present, else text
                sel_td = tds[1]
                img = sel_td.find("img")
                if img:
                    seleccion = limpiar(img.get("alt", ""))
                else:
                    seleccion = limpiar(sel_td.get_text())
                if not seleccion:
                    continue

                # Stats: PTS PJ PG PE PP GF GC Dif [Clasificado]
                pts  = limpiar(tds[2].get_text()) if len(tds) > 2  else ""
                pj   = limpiar(tds[3].get_text()) if len(tds) > 3  else ""
                pg   = limpiar(tds[4].get_text()) if len(tds) > 4  else ""
                pe   = limpiar(tds[5].get_text()) if len(tds) > 5  else ""
                pp   = limpiar(tds[6].get_text()) if len(tds) > 6  else ""
                gf   = limpiar(tds[7].get_text()) if len(tds) > 7  else ""
                gc   = limpiar(tds[8].get_text()) if len(tds) > 8  else ""
                dif  = limpiar(tds[9].get_text()) if len(tds) > 9  else ""
                clasificado = limpiar(tds[10].get_text()) if len(tds) > 10 else ""

                yield GrupoItem(
                    mundial=anio,
                    grupo=grupo,
                    posicion=pos_txt,
                    seleccion=seleccion,
                    pts=pts, pj=pj, pg=pg, pe=pe, pp=pp,
                    gf=gf, gc=gc, dif=dif,
                    clasificado=clasificado,
                    url=url,
                    fecha_scraping=now,
                )
            break  # one standings table per page

    # -----------------------------------------------------------------------
    # Parser: tarjetas  (/mundiales/YYYY_tarjetas.php)
    # -----------------------------------------------------------------------

    def _parse_tarjetas(self, response, soup, url):
        now = datetime.utcnow().isoformat()
        anio_m = re.search(r"/(\d{4})_tarjetas\.php", url)
        anio = anio_m.group(1) if anio_m else ""

        def extract_cards(td):
            text = limpiar(td.get_text())
            if text == "-":
                return "0"
            m = re.search(r"\d+", text)
            return m.group(0) if m else "0"

        for table in soup.find_all("table"):
            header_row = table.find("tr", class_="t-enc-2")
            if not header_row:
                continue

            for tr in table.find_all("tr", class_="a-top"):
                tds = tr.find_all("td")
                if len(tds) < 6:
                    continue

                # tds[0]=empty, tds[1]=player(colspan=2), tds[2]=amarillas,
                # tds[3]=rojas, tds[4]=(RD/2TA), tds[5]=partidos, tds[6]=seleccion
                jugador_td = tds[1]
                player_link = jugador_td.find("a")
                jugador = limpiar(player_link.get_text()) if player_link else limpiar(jugador_td.get_text())
                url_jugador = player_link["href"] if player_link and player_link.get("href") else ""
                img = jugador_td.find("img")
                seleccion_from_img = limpiar(img.get("alt", "")) if img else ""

                amarillas = extract_cards(tds[2]) if len(tds) > 2 else "0"
                rojas     = extract_cards(tds[3]) if len(tds) > 3 else "0"

                rd = ta2 = ""
                if len(tds) > 4:
                    rdta_txt = limpiar(tds[4].get_text())
                    if rdta_txt != "-":
                        m = re.match(r"\(\s*([\d-]+)\s*/\s*([\d-]+)\s*\)", rdta_txt)
                        if m:
                            rd  = m.group(1).strip()
                            ta2 = m.group(2).strip()

                partidos  = limpiar(tds[5].get_text()) if len(tds) > 5 else ""
                seleccion = limpiar(tds[6].get_text()) if len(tds) > 6 else seleccion_from_img

                yield TarjetaItem(
                    mundial=anio,
                    jugador=jugador,
                    seleccion=seleccion,
                    amarillas=amarillas,
                    rojas=rojas,
                    rd=rd,
                    ta2=ta2,
                    partidos=partidos,
                    url_jugador=url_jugador,
                    url=url,
                    fecha_scraping=now,
                )

    # -----------------------------------------------------------------------
    # Parser: partido  (/partidos/YYYY_eq1_eq2.php)
    # -----------------------------------------------------------------------

    def _parse_partido(self, response, soup, url):
        now = datetime.utcnow().isoformat()
        anio_m = re.search(r"/partidos/(\d{4})_", url)
        anio = anio_m.group(1) if anio_m else ""

        from bs4 import Tag

        # === Identify local / visitante teams ===
        # Primary: extract from Jugadores tables (same source used for partido_jugadores,
        # guaranteed to work — first table = local, second table = visitante)
        local = visitante = ""
        for h3 in soup.find_all("h3"):
            if "Jugadores" in limpiar(h3.get_text()):
                container = h3.find_next_sibling("div")
                if container:
                    tables = container.find_all("table")
                    if len(tables) >= 1:
                        first_tr = tables[0].find("tr")
                        img = first_tr.find("img") if first_tr else None
                        local = limpiar(img.get("alt", "")) if img else ""
                    if len(tables) >= 2:
                        first_tr = tables[1].find("tr")
                        img = first_tr.find("img") if first_tr else None
                        visitante = limpiar(img.get("alt", "")) if img else ""
                break
        # Fallback: w40 divs in <main>
        if not local or not visitante:
            main = soup.find("main")
            if main:
                w40 = main.find_all("div", class_=lambda c: c and "w-40" in c)
                if len(w40) >= 2:
                    if not local:
                        li = w40[0].find("img")
                        local = limpiar(li.get("alt", "")) if li else ""
                    if not visitante:
                        vi = w40[-1].find("img")
                        visitante = limpiar(vi.get("alt", "")) if vi else ""

        # === Parse Goles ===
        for div in soup.find_all("div", class_=re.compile(r"bb-2")):
            if re.search(r"Goles", div.get_text()):
                goles_container = div.find_next_sibling("div")
                if goles_container:
                    children = [c for c in goles_container.children if isinstance(c, Tag)]
                    for d in children:
                        cls = " ".join(d.get("class", []))
                        if cls.strip() == "clear":
                            continue
                        ball_img = d.find("img", alt=re.compile(r"Gol min", re.I))
                        if not ball_img:
                            continue
                        equipo = local if "a-right" in cls else visitante
                        min_m = re.search(r"min (\d+)", ball_img.get("alt", ""))
                        minuto = min_m.group(1) if min_m else ""
                        overflow = d.find("div", class_="overflow-x-auto")
                        tipo_txt = jugador = ""
                        if overflow:
                            type_div = overflow.find("div", class_="d-inline-block")
                            tipo_txt = limpiar(type_div.get_text()) if type_div else ""
                            if type_div:
                                type_div.decompose()
                            jugador = limpiar(overflow.get_text())
                        tipo_gol = (
                            "penal" if "penal" in tipo_txt.lower()
                            else "autogol" if any(x in tipo_txt.lower() for x in ["contra", "propia"])
                            else "normal"
                        )
                        yield PartidoGolItem(
                            mundial=anio, url_partido=url, seleccion=equipo,
                            jugador=jugador, minuto=minuto, tipo_gol=tipo_gol,
                            fecha_scraping=now,
                        )
                break

        # === Parse Jugadores ===
        jugadores_h3 = None
        for h3 in soup.find_all("h3"):
            if "Jugadores" in limpiar(h3.get_text()):
                jugadores_h3 = h3
                break
        if jugadores_h3:
            container = jugadores_h3.find_next_sibling("div")
            if container:
                for table in container.find_all("table"):
                    first_tr = table.find("tr")
                    team_img = first_tr.find("img") if first_tr else None
                    equipo = limpiar(team_img.get("alt", "")) if team_img else ""
                    current_rol = "Titular"
                    for tr in table.find_all("tr"):
                        if tr.get("bgcolor"):
                            txt = limpiar(tr.get_text())
                            if "Titular" in txt:
                                current_rol = "Titular"
                            elif "Ingresaron" in txt:
                                current_rol = "Ingreso"
                            elif "Suplente" in txt:
                                current_rol = "Suplente"
                            continue
                        if tr.find("div", class_="linea-2"):
                            continue
                        if "a-top" not in " ".join(tr.get("class", [])):
                            continue
                        tds = tr.find_all("td")
                        if len(tds) < 3:
                            continue
                        posicion = limpiar(tds[0].get_text())
                        if posicion not in ("AR", "DF", "MC", "DL"):
                            continue
                        camiseta = limpiar(tds[1].get_text()).rstrip(".")
                        jugador_td = tds[2]
                        left_div = jugador_td.find(
                            "div", class_=lambda c: c and "left" in c and "right" not in c
                        )
                        player_a = (
                            (left_div.find("a") if left_div else None)
                            or jugador_td.find("a")
                        )
                        jugador_nombre = limpiar(player_a.get_text()) if player_a else ""
                        url_jugador = (
                            player_a["href"]
                            if player_a and player_a.get("href")
                            else ""
                        )
                        capitan = (
                            "Si"
                            if "(C)" in (limpiar(left_div.get_text()) if left_div else "")
                            else "No"
                        )
                        right_div = jugador_td.find("div", class_="right")
                        goles_count = 0
                        goles_minutos = []
                        minuto_entrada = minuto_salida = ""
                        if right_div:
                            for bi in right_div.find_all("img", alt=re.compile(r"Gol min")):
                                mm = re.search(r"min (\d+)", bi.get("alt", ""))
                                if mm:
                                    goles_minutos.append(mm.group(1))
                                    goles_count += 1
                            for mdiv in right_div.find_all("div", class_=re.compile(r"margen-l2")):
                                mhtml = str(mdiv)
                                mm = re.search(r"(\d+)'", limpiar(mdiv.get_text()))
                                if mm:
                                    if "#C33" in mhtml:
                                        minuto_salida = mm.group(1)
                                    elif "#339966" in mhtml:
                                        minuto_entrada = mm.group(1)
                        yield PartidoJugadorItem(
                            mundial=anio, url_partido=url, seleccion=equipo,
                            jugador=jugador_nombre, url_jugador=url_jugador,
                            camiseta=camiseta, posicion=posicion, rol=current_rol,
                            capitan=capitan, minuto_entrada=minuto_entrada,
                            minuto_salida=minuto_salida,
                            goles_count=str(goles_count),
                            goles_minutos=",".join(goles_minutos),
                            fecha_scraping=now,
                        )

    # -----------------------------------------------------------------------
    # Parser: plantel  (/planteles/YYYY_PAIS_jugadores.php)
    # -----------------------------------------------------------------------

    def _parse_plantel(self, response, soup, url):
        now = datetime.utcnow().isoformat()
        m = re.search(r"/planteles/(\d{4})_", url)
        anio = m.group(1) if m else ""
        seleccion_a = soup.find("a", href=re.compile(r"/selecciones/\w+_seleccion\.php"))
        seleccion = limpiar(seleccion_a.get_text()) if seleccion_a else ""

        for table in soup.find_all("table"):
            header_tr = table.find("tr", class_="t-enc-2")
            if not header_tr:
                continue
            h = limpiar(header_tr.get_text())
            if "Arquero" in h:
                pos_grupo = "Arquero"
            elif "Defensor" in h:
                pos_grupo = "Defensor"
            elif "Mediocampista" in h:
                pos_grupo = "Mediocampista"
            elif "Delantero" in h:
                pos_grupo = "Delantero"
            elif "Entrenador" in h:
                pos_grupo = "Entrenador"
            else:
                continue

            for tr in table.find_all("tr", class_="a-top"):
                tds = tr.find_all("td")
                if pos_grupo == "Entrenador":
                    nombre = limpiar(tds[0].get_text()) if tds else ""
                    yield PlantelItem(
                        mundial=anio, seleccion=seleccion, camiseta="",
                        jugador=nombre, url_jugador="", posicion_grupo="Entrenador",
                        fecha_nacimiento="", altura="", club="",
                        url=url, fecha_scraping=now,
                    )
                    continue
                if len(tds) < 3:
                    continue
                camiseta = limpiar(tds[0].get_text())
                player_a = tds[1].find("a")
                jugador = (
                    limpiar(player_a.get_text()) if player_a
                    else limpiar(tds[1].get_text())
                )
                url_jugador = (
                    player_a["href"] if player_a and player_a.get("href") else ""
                )
                info_c = tds[2].find("div", class_=re.compile(r"clearfix"))
                if info_c:
                    sd = info_c.find_all("div", recursive=False)
                    fecha_nac = limpiar(sd[0].get_text()) if len(sd) > 0 else ""
                    altura_raw = limpiar(sd[1].get_text()) if len(sd) > 1 else ""
                    am = re.search(r"[\d.]+\s*m", altura_raw)
                    altura = am.group(0).strip() if am else altura_raw
                    club = limpiar(sd[2].get_text()) if len(sd) > 2 else ""
                else:
                    fecha_nac = altura = club = ""
                yield PlantelItem(
                    mundial=anio, seleccion=seleccion, camiseta=camiseta,
                    jugador=jugador, url_jugador=url_jugador,
                    posicion_grupo=pos_grupo, fecha_nacimiento=fecha_nac,
                    altura=altura, club=club, url=url, fecha_scraping=now,
                )

    # -----------------------------------------------------------------------
    # Parser: seleccion  (/selecciones/PAIS_seleccion.php)
    # -----------------------------------------------------------------------

    def _parse_seleccion(self, response, soup, url):
        now = datetime.utcnow().isoformat()

        # Team name from h1
        h1 = soup.find("h1")
        nombre_raw = limpiar(h1.get_text()) if h1 else ""
        # "Brasil en los Mundiales de Fútbol: Estadísticas Generales" → "Brasil"
        nombre = nombre_raw.split(" en los Mundiales")[0].strip()

        # ----------- Mundiales jugados -----------
        mundiales_jugados = ""
        # find the td that has the country img + name then get the sibling td with the number
        for td in soup.find_all("td"):
            span = td.find("span", class_="size-11")
            if span:
                num = limpiar(span.get_text())
                if re.match(r"^\d+$", num):
                    mundiales_jugados = num
                    break

        # ----------- Campeón / Subcampeón -----------
        campeon_anios = []
        subcampeon_anios = []

        for tr in soup.find_all("tr"):
            tds = tr.find_all("td")
            # The champion row has a <tr class="t-enc-2"> with "Campeón" and "Subcampeón"
            enc_txt = limpiar(tr.get_text())
            if "Campeón" in enc_txt and "Subcampeón" in enc_txt:
                # next sibling tr holds the data
                next_tr = tr.find_next_sibling("tr")
                if next_tr:
                    data_tds = next_tr.find_all("td")
                    if len(data_tds) >= 2:
                        for a in data_tds[0].find_all("a"):
                            yr = re.search(r"\d{4}", a["href"])
                            if yr:
                                campeon_anios.append(yr.group(0))
                        sub_text = limpiar(data_tds[1].get_text())
                        # "2\n1950, 1998" or "2\n1950, 1998"
                        sub_years = re.findall(r"\d{4}", sub_text)
                        subcampeon_anios = sub_years
                break

        # ----------- Posición histórica -----------
        posicion_historica = ""
        for td in soup.find_all("td"):
            prev = td.find_previous(["td", "th"])
            p = td.find("a", href=re.compile(r"tabla_de_posiciones"))
            if p:
                txt = limpiar(td.get_text())
                num = re.match(r"^(\d+)", txt)
                if num:
                    posicion_historica = num.group(1)
                break

        # ----------- Partidos -----------
        pj = pg = pe = pp = ""
        for tr in soup.find_all("tr", class_="t-enc-4"):
            cells = [limpiar(td.get_text()) for td in tr.find_all("td")]
            if "Jugados" in cells:
                next_tr = tr.find_next_sibling("tr")
                if next_tr:
                    vals = [limpiar(td.get_text()) for td in next_tr.find_all("td")]
                    if len(vals) >= 4:
                        pj = re.search(r"\d+", vals[0]).group(0) if re.search(r"\d+", vals[0]) else vals[0]
                        pg = re.search(r"\d+", vals[1]).group(0) if re.search(r"\d+", vals[1]) else vals[1]
                        pe = re.search(r"\d+", vals[2]).group(0) if re.search(r"\d+", vals[2]) else vals[2]
                        pp = re.search(r"\d+", vals[3]).group(0) if re.search(r"\d+", vals[3]) else vals[3]
                break

        # ----------- Goles -----------
        gf = gc = dif = ""
        for tr in soup.find_all("tr", class_="t-enc-4"):
            cells = [limpiar(td.get_text()) for td in tr.find_all("td")]
            if "A Favor" in cells and "En Contra" in cells:
                next_tr = tr.find_next_sibling("tr")
                if next_tr:
                    vals = [limpiar(td.get_text()) for td in next_tr.find_all("td")]
                    if len(vals) >= 3:
                        gf_m = re.search(r"[\d]+", vals[0])
                        gc_m = re.search(r"[\d]+", vals[1])
                        gf = gf_m.group(0) if gf_m else vals[0]
                        gc = gc_m.group(0) if gc_m else vals[1]
                        dif = vals[2]
                break

        yield SeleccionItem(
            seleccion=nombre,
            mundiales_jugados=mundiales_jugados,
            campeon_veces=str(len(campeon_anios)),
            campeon_anios=",".join(campeon_anios),
            subcampeon_veces=str(len(subcampeon_anios)),
            subcampeon_anios=",".join(subcampeon_anios),
            posicion_historica=posicion_historica,
            partidos_jugados=pj,
            partidos_ganados=pg,
            partidos_empatados=pe,
            partidos_perdidos=pp,
            goles_favor=gf,
            goles_contra=gc,
            diferencia_gol=dif,
            url=url,
            fecha_scraping=now,
        )

    # -----------------------------------------------------------------------
    # Parser: jugador  (/jugadores/NOMBRE.php)
    # -----------------------------------------------------------------------

    def _parse_jugador(self, response, soup, url):
        now = datetime.utcnow().isoformat()

        # ----------- Bio from key-value table -----------
        h1 = soup.find("h1")
        nombre = limpiar(h1.get_text()).replace(" en los Mundiales de Fútbol", "").strip() if h1 else ""

        bio = {}
        for tr in soup.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) == 2:
                key = limpiar(tds[0].get_text()).replace(":", "").strip()
                val = limpiar(tds[1].get_text())
                if key:
                    bio[key] = val

        seleccion = ""
        seleccion_a = soup.find("a", href=re.compile(r"selecciones/\w+_seleccion\.php"))
        if seleccion_a:
            seleccion = limpiar(seleccion_a.get_text())

        # ----------- Career totals -----------
        total_mundiales = total_partidos = total_goles = promedio_gol = campeon_anios = ""
        # The stats summary has a t-enc-4 row with "Mundiales", "Total de Partidos", "Campeón"
        for tr in soup.find_all("tr", class_="t-enc-4"):
            cells = [limpiar(td.get_text()) for td in tr.find_all("td")]
            if "Mundiales" in cells and "Total de Partidos" in cells:
                next_tr = tr.find_next_sibling("tr")
                if next_tr:
                    vals = [limpiar(td.get_text()) for td in next_tr.find_all("td")]
                    if len(vals) >= 1:
                        nm = re.search(r"\d+", vals[0])
                        total_mundiales = nm.group(0) if nm else vals[0]
                    if len(vals) >= 2:
                        nm = re.search(r"\d+", vals[1])
                        total_partidos = nm.group(0) if nm else vals[1]
                    if len(vals) >= 3:
                        # Campeón years
                        cmp_years = re.findall(r"\d{4}", vals[2])
                        campeon_anios = ",".join(cmp_years)
                break

        # Goals summary: row with "Goles" header, next row has "N Goles Anotados" and "Promedio"
        for tr in soup.find_all("tr", class_="t-enc-4"):
            cells = [limpiar(td.get_text()) for td in tr.find_all("td")]
            if any("Goles" in c for c in cells) and not any("Total de Partidos" in c for c in cells):
                next_tr = tr.find_next_sibling("tr")
                if next_tr:
                    vals = [limpiar(td.get_text()) for td in next_tr.find_all("td")]
                    if len(vals) >= 2:
                        nm = re.search(r"\d+", vals[0])
                        total_goles = nm.group(0) if nm else vals[0]
                        nm2 = re.search(r"[\d.]+", vals[1])
                        promedio_gol = nm2.group(0) if nm2 else vals[1]
                break

        yield JugadorItem(
            nombre=nombre,
            nombre_completo=bio.get("Nombre completo", ""),
            fecha_nacimiento=bio.get("Fecha de Nacimiento", ""),
            lugar_nacimiento=bio.get("Lugar de nacimiento", ""),
            posicion=bio.get("Posición", ""),
            seleccion=seleccion,
            numeros_camiseta=bio.get("Números de camiseta", ""),
            altura=bio.get("Altura", ""),
            apodo=bio.get("Apodo", ""),
            total_mundiales=total_mundiales,
            total_partidos=total_partidos,
            total_goles=total_goles,
            promedio_gol=promedio_gol,
            campeon=campeon_anios,
            url=url,
            fecha_scraping=now,
        )

        # ----------- Per-mundial detail table -----------
        yield from self._parse_jugador_por_mundial(soup, nombre, seleccion, url, now)

    def _parse_jugador_por_mundial(self, soup, nombre, seleccion, url, now):
        """
        The per-mundial stats table has a t-enc-4 header with columns:
        Mundial | Camiseta | Posición | Jugó | Titular | Capitán | No Jugó |
        Goles | Prom. Gol | Amar. | Roja | PG | PE | PP | Pos. Final
        """
        for tr in soup.find_all("tr", class_="t-enc-4"):
            cells = [limpiar(td.get_text()) for td in tr.find_all("td")]
            if "Mundial" in cells and "Jugó" in cells:
                # Iterate data rows
                current = tr.find_next_sibling("tr")
                while current:
                    cls = current.get("class", [])
                    if "t-enc-4" in cls:
                        break
                    if "t-enc-5" in cls:
                        # sub-header row (e.g. "Amar. / Roja") — skip it
                        current = current.find_next_sibling("tr")
                        continue
                    tds = current.find_all("td")
                    if not tds:
                        current = current.find_next_sibling("tr")
                        continue

                    # Skip separator rows and totals row
                    all_txt = limpiar(current.get_text())
                    if "linea" in str(current) or "Totales" in all_txt:
                        current = current.find_next_sibling("tr")
                        continue

                    if len(tds) < 14:
                        current = current.find_next_sibling("tr")
                        continue

                    vals = [limpiar(td.get_text()) for td in tds]

                    # Mundial year
                    mundial_a = tds[0].find("a")
                    if not mundial_a:
                        current = current.find_next_sibling("tr")
                        continue
                    mundial_yr = limpiar(mundial_a.get_text())
                    if not re.match(r"^\d{4}$", mundial_yr):
                        current = current.find_next_sibling("tr")
                        continue

                    # Camiseta number is in vals[1] after stripping flag img alt
                    camiseta = re.search(r"\d+$", vals[1])
                    camiseta = camiseta.group(0) if camiseta else ""

                    yield JugadorMundialItem(
                        jugador=nombre,
                        seleccion=seleccion,
                        mundial=mundial_yr,
                        camiseta=camiseta,
                        posicion=vals[2] if len(vals) > 2 else "",
                        jugados=vals[3] if len(vals) > 3 else "",
                        titular=vals[4] if len(vals) > 4 else "",
                        capitan=vals[5] if len(vals) > 5 else "",
                        no_jugo=vals[6] if len(vals) > 6 else "",
                        goles=vals[7] if len(vals) > 7 else "",
                        promedio_gol=vals[8] if len(vals) > 8 else "",
                        tarjetas_amarillas=vals[9] if len(vals) > 9 else "",
                        tarjetas_rojas=vals[10] if len(vals) > 10 else "",
                        pg=vals[11] if len(vals) > 11 else "",
                        pe=vals[12] if len(vals) > 12 else "",
                        pp=vals[13] if len(vals) > 13 else "",
                        posicion_final=vals[14] if len(vals) > 14 else "",
                        url_jugador=url,
                        fecha_scraping=now,
                    )

                    current = current.find_next_sibling("tr")
                break

    # -----------------------------------------------------------------------
    # Link follower
    # -----------------------------------------------------------------------

    def _seguir_enlaces(self, response):
        base_domain = "losmundialesdefutbol.com"
        for href in response.css("a::attr(href)").getall():
            if href.startswith("#"):
                continue
            url_abs = response.urljoin(href)
            parsed = urlparse(url_abs)
            if base_domain not in parsed.netloc:
                continue
            if IGNORAR_EXTENSIONES.search(parsed.path):
                continue
            if IGNORAR_FRAGMENTOS.search(url_abs):
                continue
            if parsed.scheme not in ("http", "https"):
                continue
            yield response.follow(url_abs, callback=self.parse)
