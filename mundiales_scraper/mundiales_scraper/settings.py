# Scrapy settings for mundiales_scraper project
#
# https://docs.scrapy.org/en/latest/topics/settings.html

BOT_NAME = "mundiales_scraper"

SPIDER_MODULES = ["mundiales_scraper.spiders"]
NEWSPIDER_MODULE = "mundiales_scraper.spiders"

ADDONS = {}

# Identificación del bot (buenas prácticas)
USER_AGENT = (
    "mundiales_scraper/1.0 "
    "(+https://github.com/tu_usuario/mundiales_scraper; educational use)"
)

# Respetar robots.txt
ROBOTSTXT_OBEY = True

# --- Concurrencia y throttling ---
# Una sola request en paralelo al dominio para no sobrecargar el servidor
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1.5          # espera 1.5s entre requests al mismo dominio
RANDOMIZE_DOWNLOAD_DELAY = True  # varía el delay entre 0.5x y 1.5x

# AutoThrottle: ajusta la velocidad automáticamente según la latencia del servidor
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# --- Profundidad máxima del crawler ---
DEPTH_LIMIT = 5

# --- Filtro de duplicados (evita visitar la misma URL dos veces) ---
DUPEFILTER_CLASS = "scrapy.dupefilters.RFPDupeFilter"

# --- BFS (breadth-first) para garantizar cobertura uniforme por niveles ---
# Sin esto Scrapy usa DFS y se pierde en ramas profundas de jugadores
# antes de procesar las páginas de mundiales (profundidad 1)
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"

# --- Caché HTTP (opcional: descomentar para no repetir requests ya hechas) ---
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 86400   # 1 día
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 408]
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# --- Cookies ---
COOKIES_ENABLED = False

# --- Timeouts ---
DOWNLOAD_TIMEOUT = 30

# --- Reintentos ---
RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# --- Headers por defecto ---
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es,en;q=0.5",
}

# --- Pipelines ---
ITEM_PIPELINES = {
    "mundiales_scraper.pipelines.CsvPipeline": 400,
}

# --- Encoding de exportación ---
FEED_EXPORT_ENCODING = "utf-8"

# --- Log level (cambiar a DEBUG para más detalle) ---
LOG_LEVEL = "INFO"
