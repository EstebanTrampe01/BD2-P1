# Reproducir Dia 1 (Fase 2)

Este documento deja los pasos minimos para reproducir el **Dia 1 de carga simulada** (aplicar cambios, validar y generar respaldo).

## 1) Prerrequisitos

- Docker y Docker Compose instalados.
- Python 3 disponible.
- Dependencias Python:

```bash
pip install pandas mysql-connector-python
```

## 2) Levantar base limpia

Desde la carpeta `fase2/`:

```bash
docker compose up -d
```

Verificar que el contenedor este sano:

```bash
docker ps
```

Debe aparecer `mundiales_db` en estado `healthy`.

## 3) Cargar datos base (CSV -> MySQL)

```bash
python3 cargar_bd.py
```

Esto carga los CSV de `output_db/` sobre la BD `mundiales`.

## 4) Crear tablas LOG

```bash
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/create_logs.sql
```

## 5) Ejecutar cambios del Dia 1

```bash
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/day1_changes.sql
```

Este script actualiza marcadores en partidos del mundial 2026 para los partidos:
`1, 4, 5, 7, 8, 9, 10, 11, 13, 14`.


## 9) Reinicio opcional para repetir la prueba

Si quieres repetir todo desde cero si ya tenias volumenes:

```bash
docker compose down -v
docker compose up -d
python3 cargar_bd.py
```
