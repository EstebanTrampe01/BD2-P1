# Documentacion Tecnica G17

## 1. Objetivo del documento

- descripcion de la metodologia por fases,
- modelo entidad-relacion utilizado,
- plan de respaldo,
- especificaciones tecnicas del servidor,
- analisis comparativo de resultados,
- justificacion de conclusiones,
- evidencia completa (capturas y archivos TXT generados).

## 2. Metodologia por fases

### Fase 1: Preparacion y Diseno (Dia 1)

Se analizaron las estrategias para copia de seguridad y restauracion. Se definio el uso obligatorio de backup completo (`FULL`) y se adopto estrategia `INCREMENTAL` con XtraBackup. Tambien se preparo el entorno de trabajo y rutas de almacenamiento para evidencias:

- `backups/full/`
- `backups/inc/`
- `backups_evidencia/`
- `logs_tiempo/`
- `evidencias/`

### Fase 2: Carga de Datos (Dias 2-4)

Durante 3 dias consecutivos se ejecutaron cambios de datos sobre la BD.

- Dia 1: Simulacion de partidos y resultados.
- Dia 2: Simulacion de partidos y resultados.
- Dia 3: Cambio de nombres de paises a MAYUSCULAS.

Al final de cada dia se realizo:

- backup FULL,
- backup incremental,
- validaciones con capturas,
- registro en tablas de log (incluyendo fragmentacion, disponible en `log_fragmentacion` dentro de los TXT de seleccion).

### Fase 3: Restauracion de Full Backup (Dias 5-7)

Se elimino la BD/volumen y se restauraron los 3 respaldos FULL (Dia 1, Dia 2, Dia 3), registrando:

- tiempo de preparacion,
- tiempo de copy-back,
- tiempo total de operacion,
- validaciones de integridad.

### Fase 4: Restauracion de Incremental Backup (Dias 8-10)

Se elimino nuevamente la BD/volumen y se restauraron las cadenas incrementales correspondientes a Dia 1, Dia 2 y Dia 3, con los mismos controles:

- tiempo por etapa,
- validaciones,
- evidencia visual y textual.

### Fase 5: Analisis y conclusiones

Se compararon tiempos y comportamiento de ambas estrategias, se elaboraron tablas comparativas y se generaron conclusiones con base en resultados reales y evidencia reproducible.

Nota de la practica: las capturas incluidas corresponden a la evidencia disponible por el grupo; para entrega final se debe asegurar que todas muestren fecha y hora del sistema operativo.

## 3. Modelo entidad-relacion utilizado

### 3.1 Entidades principales

- `selecciones`
- `mundiales`
- `jugadores`
- `partidos`
- `grupos`
- `posiciones_finales`
- `goleadores`
- `premios`
- `tarjetas`
- `jugadores_por_mundial`
- `planteles`
- `partido_jugadores`
- `partido_goles`
- `scraping_runs`
- `scraping_metadata`
- `log_ejecucion`
- `log_fragmentacion`

### 3.2 Relaciones clave (FK)

- `mundiales.id_organizador -> selecciones.id_seleccion`
- `mundiales.id_campeon -> selecciones.id_seleccion`
- `partidos.id_mundial -> mundiales.id_mundial`
- `partidos.id_local -> selecciones.id_seleccion`
- `partidos.id_visitante -> selecciones.id_seleccion`
- `planteles.id_jugador -> jugadores.id_jugador`
- `planteles.id_mundial -> mundiales.id_mundial`
- `partido_goles.id_partido -> partidos.id_partido`
- `partido_goles.id_jugador -> jugadores.id_jugador`

## 4. Plan de respaldo implementado

### 4.1 Respaldo FULL

- Frecuencia: diario (Dia 1, 2 y 3).
- Herramienta: `percona/percona-xtrabackup:8.0`.
- Destino: `backups/full/dayX`.
- Entrega comprimida: `backups_evidencia/full_dayX.tar.gz`.

### 4.2 Respaldo INCREMENTAL

- Frecuencia: diario (Dia 1, 2 y 3).
- Cadena usada:
  - `inc/day1` basado en `full/day1`
  - `inc/day2` basado en `inc/day1`
  - `inc/day3` basado en `inc/day2`
- Entrega comprimida: `backups_evidencia/inc_dayX.tar.gz`.

### 4.3 Politica de restauracion

- FULL: restaurar directamente backup del dia objetivo.
- INCREMENTAL: aplicar base + incrementales secuenciales + prepare final + copy-back.

## 5. Especificaciones tecnicas del servidor/entorno

- SO: `Linux 6.17.0-20-generic (Ubuntu)`
- CPU: `Intel Celeron N4020`, `2 vCPU`
- RAM total: `7.6 GiB`
- Swap: `4.0 GiB`
- Disco raiz: `73G` (aprox. `11G` libres al momento de medicion)
- Docker: `29.2.0`
- Docker Compose: `v2.40.3`
- Motor de BD: `MySQL 8.0` en contenedor `mundiales_db`

## 6. Tabla consolidada de tiempos (migrada de CSV)

La siguiente tabla reemplaza la bitacora CSV y concentra toda la informacion de tiempos.

| dia | estrategia | accion | hora_inicio | hora_fin | duracion_seg | responsable | archivo_backup | resultado | observaciones |
|---|---|---|---|---|---:|---|---|---|---|
| 1 | FULL | BACKUP | 2026-04-07 17:50:11 | 2026-04-07 17:50:19 | 7.63 | Grupo | fase2/backups_evidencia/full_day1.tar.gz | OK | Fuente: evidencias/full_day1_resumen.txt |
| 1 | INCREMENTAL | BACKUP | 2026-04-07 17:56:16 | 2026-04-07 17:56:22 | 6.16 | Grupo | fase2/backups_evidencia/inc_day1.tar.gz | OK | Fuente: evidencias/inc_day1_resumen.txt |
| 2 | FULL | BACKUP | 2026-04-08 22:40:49 | 2026-04-08 22:41:09 | 20.06 | Grupo | fase2/backups_evidencia/full_day2.tar.gz | OK | Fuente: evidencias/full_day2_resumen.txt |
| 2 | INCREMENTAL | BACKUP | 2026-04-08 23:10:02 | 2026-04-08 23:10:23 | 20.29 | Grupo | fase2/backups_evidencia/inc_day2.tar.gz | OK | Fuente: evidencias/inc_day2_resumen.txt |
| 3 | FULL | BACKUP | 2026-04-09 16:25:43 | 2026-04-09 16:25:57 | 14.12 | Grupo | fase2/backups_evidencia/full_day3.tar.gz | OK | Fuente: evidencias/full_day3_resumen.txt |
| 3 | INCREMENTAL | BACKUP | 2026-04-09 17:21:32 | 2026-04-09 17:21:43 | 10.87 | Grupo | fase2/backups_evidencia/inc_day3.tar.gz | OK | Fuente: evidencias/inc_day3_resumen.txt |
| 1 | FULL | RESTORE | 2026-04-07 18:11:27 | 2026-04-07 18:11:48 | 21.00 | Grupo | fase2/backups/full/day1 | OK | Prepare 7.36 + CopyBack 9.45 (nucleo 16.81) |
| 2 | FULL | RESTORE | 2026-04-09 16:54:08 | 2026-04-09 16:54:42 | 34.00 | Grupo | fase2/backups/full/day2 | OK | Prepare 8.77 + CopyBack 19.37 (nucleo 28.14) |
| 3 | FULL | RESTORE | 2026-04-09 18:44:09 | 2026-04-09 18:44:19 | 10.00 | Grupo | fase2/backups/full/day3 | OK | Prepare 3.32 + CopyBack 3.55 (nucleo 6.87) |
| 1 | INCREMENTAL | RESTORE | 2026-04-07 18:31:25 | 2026-04-07 18:31:54 | 29.00 | Grupo | fase2/backups/full/day1 + fase2/backups/inc/day1 | OK | Prepare 19.17 + CopyBack 7.17 (nucleo 26.34) |
| 2 | INCREMENTAL | RESTORE | 2026-04-09 16:59:40 | 2026-04-09 17:01:26 | 106.00 | Grupo | fase2/backups/full/day1 + fase2/backups/inc/day1/day2 | OK | Prepare 72.66 + CopyBack 25.27 (nucleo 97.93) |
| 3 | INCREMENTAL | RESTORE | 2026-04-09 21:57:07 | 2026-04-09 21:57:37 | 30.00 | Grupo | fase2/backups/full/day1 + fase2/backups/inc/day1/day2/day3 | OK | Prepare 24.64 + CopyBack 3.20 (nucleo 27.84) |

## 7. Analisis detallado de resultados comparativos

### 7.1 Promedios globales

| metrica | valor |
|---|---:|
| Promedio backup FULL | 13.94 s |
| Promedio backup incremental | 12.44 s |
| Promedio restore FULL | 21.67 s |
| Promedio restore incremental | 55.00 s |
| Relacion restore incremental / FULL | 2.54x |

### 7.2 Interpretacion tecnica

- En backups, incremental presenta ventaja ligera sobre FULL en promedio.
- En restauraciones, FULL es considerablemente mas rapido y estable.
- El peor caso se dio en restauracion incremental Dia 2 por acumulacion de etapas `apply-log`.

### 7.3 Causas de discrepancias de tiempos entre dias

Ademas de la estrategia de backup/restore, los tiempos varian por:

- equipo/PC diferente por dia,
- capacidad de CPU y RAM,
- estado del disco y espacio libre,
- carga del sistema operativo en segundo plano,
- variaciones de red y del motor Docker.

Como el trabajo fue distribuido por integrante (Juan/Harold/Engel), una parte de la variacion entre dias se explica por diferencias de hardware y condiciones de ejecucion.

## 8. Justificacion de conclusiones

Conclusiones respaldadas por los datos:

1. `FULL` es la mejor opcion para minimizar tiempo de restauracion (RTO).
2. `INCREMENTAL` ayuda en la ventana de respaldo, pero complica y alarga restauraciones.
3. Para entornos con equipos heterogeneos, se debe reportar el hardware para comparar tiempos de forma justa.

Recomendacion operativa final:

- Si prioridad = recuperacion rapida: usar FULL con mayor frecuencia.
- Si prioridad = menor ventana de backup: usar incremental, pero con pruebas periodicas de restauracion completa.

## 9. Evidencia completa por fases (fotos y TXT)

### 9.1 Fase 1 - Preparacion e inicializacion (Dia 0)

Capturas:

![D0-1_INIT_dockerUp](evidencias/day0/D0-1_INIT_dockerUp.png)
![D0-2_INIT_cargarDatos](evidencias/day0/D0-2_INIT_cargarDatos.png)
![D0-3_INIT_crearLogs](evidencias/day0/D0-3_INIT_crearLogs.png)
![D0-V1_SELECT_partidos2026](evidencias/day0/D0-V1_SELECT_partidos2026.png)
![D0-V2_SELECT_selecciones](evidencias/day0/D0-V2_SELECT_selecciones.png)
![D0-V3_SELECT_logs](evidencias/day0/D0-V3_SELECT_logs.png)
![D0-V4_SELECTCOUNT_all](evidencias/day0/D0-V4_SELECTCOUNT_all.png)

TXT:

- `evidencias/day0/D0_SELECT.txt`

### 9.2 Fase 2 - Carga de datos (Dias 1-3)

#### Dia 1

Capturas:

![D1-1_CAMBIOS_cargarCambios](evidencias/day1/D1-1_CAMBIOS_cargarCambios.png)
![D1-V1_SELECT_partidos2026](evidencias/day1/D1-V1_SELECT_partidos2026.png)
![D1-V2_SELECT_selecciones](evidencias/day1/D1-V2_SELECT_selecciones.png)
![D1-V3_SELECT_logs](evidencias/day1/D1-V3_SELECT_logs.png)
![D1-V4_SELECTCOUNT_all](evidencias/day1/D1-V4_SELECTCOUNT_all.png)
![D1B-1_INSTALL_Xtrabackup](evidencias/day1/D1B-1_INSTALL_Xtrabackup.png)
![D1B-2_FULL_exitoso](evidencias/day1/D1B-2_FULL_exitoso.png)
![D1B-3_INC_exitosos](evidencias/day1/D1B-3_INC_exitosos.png)

TXT:

- `evidencias/day1/D1_SELECT.txt`

#### Dia 2

Capturas:

![D2-1_CAMBIOS_cargarCambios](evidencias/day2/D2-1_CAMBIOS_cargarCambios.png)
![D2-V2_SELECT_selecciones](evidencias/day2/D2-V2_SELECT_selecciones.png)
![D2-V4_SELECTCOUNT_all](evidencias/day2/D2-V4_SELECTCOUNT_all.png)
![D2B-1_INSTALL_Xtrabackup](evidencias/day2/D2B-1_INSTALL_Xtrabackup.png)
![D2B-2_FULL_exitoso](evidencias/day2/D2B-2_FULL_exitoso.png)
![D2B-3_INC_exitosos](evidencias/day2/D2B-3_INC_exitosos.png)
![D1-V1_SELECT_partidos2026_day2](evidencias/day2/D1-V1_SELECT_partidos2026.png)
![D1-V2_SELECT_logs_day2](evidencias/day2/D1-V2_SELECT_logs.png)

TXT:

- `evidencias/day2/D2_SELECT.txt`

#### Dia 3

Capturas:

![D3-1_CAMBIOS_cargarCambios](evidencias/day3/D3-1_CAMBIOS_cargarCambios.png)
![D3-V1_SELECT_partidos2026](evidencias/day3/D3-V1_SELECT_partidos2026.png)
![D3-V2_SELECT_logs](evidencias/day3/D3-V2_SELECT_logs.png)
![D3-V2_SELECT_selecciones](evidencias/day3/D3-V2_SELECT_selecciones.png)
![D3-V4_SELECTCOUNT_all](evidencias/day3/D3-V4_SELECTCOUNT_all.png)
![D3B-1_INSTALL_Xtrabackup](evidencias/day3/D3B-1_INSTALL_Xtrabackup.png)
![D3B-2_FULL_exitoso](evidencias/day3/D3B-2_FULL_exitoso.png)
![D3B-3_INC_exitosos](evidencias/day3/D3B-3_INC_exitosos.png)

TXT:

- `evidencias/day3/D3_SELECT.txt`

### 9.3 Fase 3 - Restauracion de full backup (Dias 5-7)

#### Restore FULL Dia 1

Capturas:

![D1RF-1_PrepararEntorno](evidencias/day1/D1RF-1_PrepararEntorno.png)
![D1RF-2_exitoso](evidencias/day1/D1RF-2_exitoso.png)
![D1RF-V1_SELECTpartidos2029](evidencias/day1/D1RF-V1_SELECTpartidos2029.png)
![D1RF-V2_SELECT_selecciones](evidencias/day1/D1RF-V2_SELECT_selecciones.png)
![D1RF-V3_SELECT_logs](evidencias/day1/D1RF-V3_SELECT_logs.png)
![D1RF-V4_SELECTCOUNT_all](evidencias/day1/D1RF-V4_SELECTCOUNT_all.png)
![D1RF-V5_IF](evidencias/day1/D1RF-V5_IF.png)

TXT:

- `evidencias/day1/D1RF_SELECT.txt`

#### Restore FULL Dia 2

Capturas:

![D2RF-1_PreapararEntorno](evidencias/day2/D2RF-1_PreapararEntorno.png)
![D2RF-2_exitoso](evidencias/day2/D2RF-2_exitoso.png)
![D2RF-V1_SELECTpartidos2026](evidencias/day2/D2RF-V1_SELECTpartidos2026.png)
![D2RF-V2_SELECT_selecciones](evidencias/day2/D2RF-V2_SELECT_selecciones.png)
![D2RF-V3_SELECT_logs](evidencias/day2/D2RF-V3_SELECT_logs.png)
![D2RF-V4_SELECTCOUNT_all](evidencias/day2/D2RF-V4_SELECTCOUNT_all.png)
![D2RF-V5_IF](evidencias/day2/D2RF-V5_IF.png)

#### Restore FULL Dia 3

Capturas:

![D3RF-2_exito](evidencias/day3/D3RF-2_exito.png)
![D3RF-V1_SELECTpartidos2029](evidencias/day3/D3RF-V1_SELECTpartidos2029.png)
![D3RF-V2_SELECT_selecciones](evidencias/day3/D3RF-V2_SELECT_selecciones.png)
![D3RF-V3_SELECT_logs](evidencias/day3/D3RF-V3_SELECT_logs.png)
![D3RF-V4_SELECTCOUNT_all](evidencias/day3/D3RF-V4_SELECTCOUNT_all.png)
![D3RF-V5_IF](evidencias/day3/D3RF-V5_IF.png)

TXT:

- `evidencias/day3/D3RF_SELECT.txt`

### 9.4 Fase 4 - Restauracion incremental (Dias 8-10)

#### Restore INCREMENTAL Dia 1

Capturas:

![D1RI-1_PrepararEntorno](evidencias/day1/D1RI-1_PrepararEntorno.png)
![D1RI-2_exito](evidencias/day1/D1RI-2_exito.png)
![D1RI-V1_SELECT_partidos2026](evidencias/day1/D1RI-V1_SELECT_partidos2026.png)
![D1RI-V2_SELECT_selecciones](evidencias/day1/D1RI-V2_SELECT_selecciones.png)
![D1RI-V3_SELECT_logs](evidencias/day1/D1RI-V3_SELECT_logs.png)
![D1RI-V4_SELECTCOUINT_all](evidencias/day1/D1RI-V4_SELECTCOUINT_all.png)
![D1RI-V5_IF](evidencias/day1/D1RI-V5_IF.png)

TXT:

- `evidencias/day1/D1RI_SELECT.txt`

#### Restore INCREMENTAL Dia 2

Capturas:

![D2RF-1_PreapararEntorno_reuse](evidencias/day2/D2RF-1_PreapararEntorno.png)
![D2RF-2_exitoso_reuse](evidencias/day2/D2RF-2_exitoso.png)
![D2RF-V1_SELECTpartidos2026_reuse](evidencias/day2/D2RF-V1_SELECTpartidos2026.png)
![D2RF-V2_SELECT_selecciones_reuse](evidencias/day2/D2RF-V2_SELECT_selecciones.png)
![D2RF-V3_SELECT_logs_reuse](evidencias/day2/D2RF-V3_SELECT_logs.png)
![D2RF-V4_SELECTCOUNT_all_reuse](evidencias/day2/D2RF-V4_SELECTCOUNT_all.png)
![D2RF-V5_IF_reuse](evidencias/day2/D2RF-V5_IF.png)

#### Restore INCREMENTAL Dia 3

Capturas:

![D3RI-1_PrepararEntorno](evidencias/day3/D3RI-1_PrepararEntorno.png)
![D3RI-2_exito](evidencias/day3/D3RI-2_exito.png)
![D3RI-V1_SELECT_partidos2026](evidencias/day3/D3RI-V1_SELECT_partidos2026.png)
![D3RI-V2_SELECT_selecciones](evidencias/day3/D3RI-V2_SELECT_selecciones.png)
![D3RI-V3_SELECT_logs](evidencias/day3/D3RI-V3_SELECT_logs.png)
![D3RI-V4_SELECTCOUINT_all](evidencias/day3/D3RI-V4_SELECTCOUINT_all.png)
![D3RI-V5_IF](evidencias/day3/D3RI-V5_IF.png)

TXT:

- `evidencias/day3/D3RI_SELECT.txt`

### 9.5 Resumenes de tiempos y trazabilidad (TXT)

- `evidencias/install_xtrabackup_resumen.txt`
- `evidencias/install_xtrabackup_resumen_Dant.txt`
- `evidencias/full_day1_resumen.txt`
- `evidencias/full_day2_resumen.txt`
- `evidencias/full_day3_resumen.txt`
- `evidencias/inc_day1_resumen.txt`
- `evidencias/inc_day2_resumen.txt`
- `evidencias/inc_day3_resumen.txt`
- `evidencias/restore_day1_full_resumen.txt`
- `evidencias/restore_day1_inc_resumen.txt`
- `evidencias/restore_day2_full_resumen.txt`
- `evidencias/restore_day2_inc_resumen.txt`
- `evidencias/restore_day3_full_resumen.txt`
- `evidencias/restore_day3_inc_resumen.txt`

## 10. Validacion post-restauracion

Consultas aplicadas para validar estado final:

```bash
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/validaciones_dia/2026.sql
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/validaciones_dia/muestras.sql
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/validaciones_dia/conteos.sql
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/validaciones_dia/logs.sql
docker exec -i mundiales_db mysql -uroot -proot1234 < schema/validaciones_restauraciones/validacion_inteRes.sql
```

Controles minimos:

- conteos esperados por tabla,
- resultados de partidos y datos de muestra,
- eventos de ejecucion en logs,
- integridad referencial sin huerfanos,
- presencia de registros de fragmentacion (`log_fragmentacion`).


## 11. Conclusiones
1. La estrategia de respaldo `FULL` demostró mayor estabilidad en restauración, con tiempos promedio menores y menor variabilidad entre días, por lo que es la opción más confiable cuando la prioridad es reducir el tiempo de recuperación (RTO).

2. La estrategia `INCREMENTALF` mostró ventajas en algunos tiempos de respaldo, pero incrementó significativamente la complejidad y duración de restauración, especialmente cuando fue necesario aplicar múltiples incrementales en cadena.

3. Las diferencias de resultados entre Día 1, Día 2 y Día 3 no se explican únicamente por el tipo de backup; también influyeron factores de infraestructura como capacidad del equipo, carga del sistema, estado del disco, y recursos disponibles de CPU/RAM al momento de ejecución.

4. La validación post-restauración (conteos, muestras de datos, logs e integridad referencial) confirmó consistencia funcional de la base de datos en los escenarios probados, respaldando la reproducibilidad de la metodología aplicada.

5. Con base en la evidencia técnica y comparativa, se recomienda una política híbrida: mantener respaldos `FULL` periódicos como punto base confiable y usar `INCREMENTAL` solo cuando exista disciplina operativa para pruebas de restauración frecuentes y control estricto de la cadena de respaldos.