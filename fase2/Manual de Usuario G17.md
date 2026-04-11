# Universidad de San Carlos de Guatemala

## Facultad de Ingenieria

### Escuela de Ciencias y Sistemas

---

## Sistemas de Bases de Datos 2

### Proyecto Fase 1 - Manual de Usuario

**Seccion:** B  
**Grupo:** 17  

**Integrantes:**

- Engel Emilio Coc Raxjal - 202200314
- Harold Alejandro Sanchez Hernandez - 202200100
- Juan Esteban Chacon Trampe - 202300431

---

## 1. Objetivos

- realizar backups `FULL` e `INCREMENTAL`,
- restaurar la base de datos desde respaldos,
- interpretar los registros de respaldo,
- ejecutar validaciones post-restauracion.

## 2. Alcance

Este procedimiento aplica al proyecto usando MySQL en Docker y Percona XtraBackup.

## 3. Herramientas y requisitos

### 3.1 Software requerido

- Linux (recomendado Ubuntu).
- Docker.
- Docker Compose.
- Imagen `percona/percona-xtrabackup:8.0`.
- Contenedor MySQL `mundiales_db`.

### 3.2 Estructura esperada del proyecto

Deben existir estas rutas:

- `comandos/generarBackups/`
- `comandos/restaurarBackups/`
- `backups/`
- `backups_evidencia/`
- `logs_tiempo/`
- `evidencias/`

### 3.3 Credenciales utilizadas por scripts

- Usuario MySQL: `root`
- Password MySQL: `root1234`
- Base de datos: `mundiales`

## 4. Verificaciones iniciales

Desde la raiz ejecutar:

```bash
docker --version
docker compose version
docker ps
```

Si el contenedor no esta levantado:

```bash
docker compose up -d
```

## 5. Flujo operativo recomendado

1. Preparar entorno base (Dia 0).
2. Aplicar cambios del dia.
3. Ejecutar backup FULL.
4. Ejecutar backup INCREMENTAL.
5. Guardar evidencias de respaldo.
6. Restaurar FULL y validar.
7. Restaurar INCREMENTAL y validar.

## 6. Instalacion de XtraBackup

Script:

- `comandos/generarBackups/install-xtrabackup`

Ejecucion:

```bash
bash comandos/generarBackups/install-xtrabackup
```

Salida esperada:

- `logs_tiempo/install_xtrabackup.sec`
- `evidencias/install_xtrabackup_resumen.txt`

## 7. Como realizar backups FULL

Scripts por dia:

- `comandos/generarBackups/day1-backup-full`
- `comandos/generarBackups/day2-backup-full`
- `comandos/generarBackups/day3-backup-full`

Ejemplo (Dia 1):

```bash
bash comandos/generarBackups/day1-backup-full
```

Resultados esperados:

- Backup en `backups/full/day1`
- Tar en `backups_evidencia/full_day1.tar.gz`
- Tiempo en `logs_tiempo/full_day1.sec`
- Resumen en `evidencias/full_day1_resumen.txt`

## 8. Como realizar backups INCREMENTAL

Scripts por dia:

- `comandos/generarBackups/day1-backup-inc`
- `comandos/generarBackups/day2-backup-inc`
- `comandos/generarBackups/day3-backup-inc`

Ejemplo (Dia 2):

```bash
bash comandos/generarBackups/day2-backup-inc
```

Resultados esperados:

- Backup en `backups/inc/day2`
- Tar en `backups_evidencia/inc_day2.tar.gz`
- Tiempo en `logs_tiempo/inc_day2.sec`
- Resumen en `evidencias/inc_day2_resumen.txt`

## 9. Como restaurar backups FULL

Scripts por dia:

- `comandos/restaurarBackups/day1-restore-full`
- `comandos/restaurarBackups/day2-restore-full`
- `comandos/restaurarBackups/day3-restore-full`

Ejemplo (Dia 3):

```bash
bash comandos/restaurarBackups/day3-restore-full
```

El flujo del script incluye:

1. Detener BD.
2. Limpiar/recrear volumen MySQL.
3. `xtrabackup --prepare`.
4. `xtrabackup --copy-back`.
5. Corregir permisos.
6. Levantar BD.
7. Guardar tiempos y resumen.

Salida esperada:

- `evidencias/restore_day3_full_resumen.txt`
- `logs_tiempo/restore_day3_full_prepare.sec`
- `logs_tiempo/restore_day3_full_copyback.sec`

## 10. Como restaurar backups INCREMENTAL

Scripts por dia:

- `comandos/restaurarBackups/day1-restore-inc`
- `comandos/restaurarBackups/day2-restore-inc`
- `comandos/restaurarBackups/day3-restore-inc`

Ejemplo (Dia 3):

```bash
bash comandos/restaurarBackups/day3-restore-inc
```

El flujo del script incluye:

1. Detener BD y limpiar volumen.
2. Prepare base con `--apply-log-only`.
3. Aplicar incrementales en secuencia.
4. Prepare final.
5. `copy-back`.
6. Corregir permisos y levantar BD.
7. Guardar resumen de tiempos.

Salida esperada:

- `evidencias/restore_day3_inc_resumen.txt`
- `logs_tiempo/restore_day3_inc_prepare_*.sec`
- `logs_tiempo/restore_day3_inc_copyback.sec`

## 11. Interpretacion de registros de respaldo

### 11.1 Archivos de tiempo crudo

Ubicacion:

- `logs_tiempo/*.sec`

Interpretacion:

- Cada archivo contiene segundos de ejecucion de una etapa.
- Ejemplo: `full_day1.sec = 7.63`.

### 11.2 Archivos resumen

Ubicacion:

- `evidencias/*_resumen.txt`

Campos principales:

- `inicio`
- `fin`
- `duracion_seg`

Campos adicionales para restore:

- `duracion_prepare_seg`
- `duracion_copyback_seg`
- `duracion_restore_nucleo_seg`
- `duracion_restore_total_operativa_seg`

Uso recomendado:

- Para informes y tablas finales, usar `*_resumen.txt`.
- Para depuracion tecnica, usar `logs_tiempo/*.sec`.

## 12. Validacion post-restauracion

Despues de cada restore, ejecutar:

```bash
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/validaciones_dia/2026.sql
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/validaciones_dia/muestras.sql
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/validaciones_dia/conteos.sql
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/validaciones_dia/logs.sql
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/validaciones_restauraciones/inteRes.sql
```

Checklist de validacion:

- Conteos correctos por tabla.
- Datos de muestra del dia esperado.
- Eventos en logs de ejecucion.
- Integridad referencial sin huerfanos.
- Registros de fragmentacion presentes (`log_fragmentacion`).

## 13. Errores comunes y solucion

- Error: imagen de XtraBackup no disponible.
  - Solucion: ejecutar `bash comandos/generarBackups/install-xtrabackup`.

- Error: permisos al restaurar.
  - Solucion: aplicar `chown -R mysql:mysql /var/lib/mysql` dentro del contenedor auxiliar.

- Error: backup no encontrado.
  - Solucion: verificar `backups/full/dayX`, `backups/inc/dayX` o `backups_evidencia/*.tar.gz`.

- Error: MySQL no levanta tras restore.
  - Solucion: revisar `docker compose logs db` y confirmar volumen limpio/restaurado.

## 14. Recomendaciones operativas

- Ejecutar backups y restores sin cargas pesadas paralelas en el host.
- Mantener evidencia por dia (capturas + TXT + resumenes).
- Probar restauracion periodicamente, no solo tomar respaldos.
- Registrar siempre fecha/hora de ejecucion en evidencias.

## 15. Evidencia y trazabilidad

Rutas principales:

- Capturas: `evidencias/day0`, `evidencias/day1`, `evidencias/day2`, `evidencias/day3`
- Resumenes de tiempos: `evidencias/*_resumen.txt`
- Selects/exportes: `evidencias/day*/D*_SELECT.txt`
- Scripts: `comandos/generarBackups/`, `comandos/restaurarBackups/`

## 16. Exportar este manual a PDF

1. Abrir `Manual de Usuario.md` en VS Code.
2. Abrir vista previa Markdown.
3. Exportar o imprimir a PDF.
4. Guardar como `Manual_de_Usuario_G17.pdf`.
