# Fase 2 - Plan operativo y scripts

Este directorio contiene los scripts y la guia de ejecucion para cumplir toda la Fase 2:

- cambios diarios de datos,
- bitacoras/logs,
- validaciones,
- y proceso para respaldos/restauraciones.

## Base operativa en esta carpeta

Para trabajar directamente desde `fase2/`, los archivos base ya estan aqui:

- `docker-compose.yml`
- `init/schema.sql`
- `cargar_bd.py`
- `output_db/*.csv`

Con esto se puede levantar y cargar la BD sin depender de la carpeta `fase1/`.

## Cronograma de 10 dias

### Dia 1 - Preparacion tecnica
- Definir estrategia de respaldo: `FULL + INCREMENTAL` o `FULL + DIFERENCIAL`.
- Confirmar BD base cargada y funcional.
- Crear tablas LOG y estructura de evidencias.
- Definir formato de bitacora de tiempos.

### Dia 2 - Carga simulada (Dia 1 del enunciado)
- Ejecutar cambios de datos de partidos/resultados.
- Registrar logs y fragmentacion.
- Capturas de `SELECT *` y `SELECT COUNT(*)`.
- Ejecutar backup FULL dia 1.
- Ejecutar backup INCREMENTAL/DIFERENCIAL dia 1.

### Dia 3 - Carga simulada (Dia 2 del enunciado)
- Ejecutar segundo bloque de cambios de partidos/resultados.
- Registrar logs y fragmentacion.
- Capturas de `SELECT *` y `SELECT COUNT(*)`.
- Ejecutar backup FULL dia 2.
- Ejecutar backup INCREMENTAL/DIFERENCIAL dia 2.

### Dia 4 - Carga simulada (Dia 3 del enunciado)
- Ejecutar actualizacion de nombres de paises a MAYUSCULAS.
- Registrar logs y fragmentacion.
- Capturas de `SELECT *` y `SELECT COUNT(*)`.
- Ejecutar backup FULL dia 3.
- Ejecutar backup INCREMENTAL/DIFERENCIAL dia 3.

### Dia 5 - Preparacion restauracion FULL
- Eliminar BD completa o recrear entorno limpio.
- Restaurar en un segundo esquema (nombre distinto).
- Probar restauracion inicial de estrategia FULL.

### Dia 6 - Restauracion secuencial FULL
- Restaurar FULL dia 1, dia 2 y dia 3 en orden.
- Medir tiempos de cada restauracion.
- Validar con `SELECT *` y `SELECT COUNT(*)`.

### Dia 7 - Cierre validacion FULL
- Verificar integridad referencial (FK y huerfanos).
- Consolidar tiempos de estrategia FULL.
- Guardar evidencias y comandos ejecutados.

### Dia 8 - Restauracion secuencial INCREMENTAL/DIFERENCIAL
- Limpiar entorno nuevamente.
- Restaurar cadena incremental/diferencial en orden.
- Medir tiempos por restauracion.
- Validar con `SELECT *` y `SELECT COUNT(*)`.

### Dia 9 - Analisis comparativo
- Comparar tiempos de restauracion FULL vs INCREMENTAL/DIFERENCIAL.
- Analizar complejidad, riesgo y recuperabilidad.
- Redactar recomendacion final de estrategia.

### Dia 10 - Entrega final
- Consolidar documentacion tecnica PDF.
- Completar manual de usuario.
- Organizar scripts y evidencias.
- Ensayar la parte practica para calificacion.

## Checklist obligatorio de cumplimiento

- 3 backups FULL.
- 3 backups INCREMENTAL o DIFERENCIAL.
- Capturas con fecha/hora visible despues de cada carga y restauracion.
- Restauracion en esquema con nombre distinto.
- Registro de tiempos de restauracion por estrategia.
- Validacion de integridad post-restauracion.
- Analisis comparativo y conclusion recomendada.

## Version por responsable

### Responsable 1 (Tu) - Cambios de datos y validacion
- Ejecutar scripts de cambios dia 1, 2 y 3.
- Ejecutar validaciones despues de cada cambio.
- Documentar `SELECT *` y `SELECT COUNT(*)` con evidencia.
- Verificar que lo restaurado refleje exactamente los cambios aplicados.

### Responsable 2 (Harold) - Backups estrategia A
- Ejecutar backups FULL diarios.
- Ejecutar backups INCREMENTAL/DIFERENCIAL diarios (estrategia A).
- Registrar comandos, rutas de archivo y tiempos.
- Ejecutar restauraciones correspondientes y medir tiempos.

### Responsable 3 (Engel) - Backups estrategia B / restauraciones
- Ejecutar segunda variante de respaldo/restauracion (si aplica).
- Restaurar secuencialmente por dia y por estrategia.
- Validar integridad post-restore.
- Consolidar comparativa de tiempos final.

### Trabajo conjunto
- Revisar consistencia de evidencias.
- Redactar analisis comparativo final.
- Definir conclusion tecnica y recomendacion.
- Preparar demo practica de calificacion.

## Orden de ejecucion de scripts en esta carpeta

1. `schema/create_logs.sql`
2. `schema/day1_changes.sql`
3. `schema/validacion_post_cambios.sql`
4. backup FULL + INCREMENTAL/DIFERENCIAL (dia 1)
5. `schema/day2_changes.sql`
6. `schema/validacion_post_cambios.sql`
7. backup FULL + INCREMENTAL/DIFERENCIAL (dia 2)
8. `schema/day3_changes.sql`
9. `schema/validacion_post_cambios.sql`
10. backup FULL + INCREMENTAL/DIFERENCIAL (dia 3)
11. `schema/validacion_integridad_restore.sql` (despues de restauraciones)

## Notas

- Estos scripts no usan herramientas visuales.
- Los cambios de los dias 1 y 2 simulan resultados en partidos de 2026.
- El dia 3 convierte los nombres de paises a mayusculas.
- Se registran cambios en tablas `log_*` y en `log_fragmentacion`.
