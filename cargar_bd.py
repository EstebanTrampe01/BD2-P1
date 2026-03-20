"""Carga CSV normalizado (output_db/) a MySQL en Docker."""

import cargar_datos


if __name__ == "__main__":
    cargar_datos.cargar_bd()
