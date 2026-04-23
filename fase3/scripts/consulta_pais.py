from pprint import pprint
from metodos_consultas import metodo_info_pais


print("\n=== CONSULTA POR PAÍS ===")
r2 = metodo_info_pais("Brasil", anio=2014)
pprint(r2)