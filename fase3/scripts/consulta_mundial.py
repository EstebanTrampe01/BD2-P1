from pprint import pprint
from metodos_consultas import metodo_info_mundial

print("=== CONSULTA POR MUNDIAL ===")
r1 = metodo_info_mundial(2010, grupo="B", pais="España")
pprint(r1)