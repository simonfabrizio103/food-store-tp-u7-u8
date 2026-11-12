# Trabajo Práctico Integrador — Segunda Entrega (Unidades 4 a 8)
## Food Store: Cierre Integral de la Capa de Datos (Relacional, Documental y Móvil)

**Materia:** Base de Datos II · Tecnicatura Universitaria en Programación  
**Institución:** Universidad Tecnológica Nacional — Facultad Regional Mendoza (UTN FRM)  
**Estudiante:** Fabrizio Simon  
**Ciclo Lectivo:** 2026  

---

### Enlaces a los Repositorios Oficiales del Proyecto
* **Repositorio Parte 1 (Unidades 1 a 6):**  
  [`https://github.com/simonfabrizio103/food-store-tp`](https://github.com/simonfabrizio103/food-store-tp/tree/master/facultad)  
  *Carpetas clave:* `facultad/food-store-tp-unidad4/`, `facultad/food-store-tp-u5/`, `facultad/food-store-tp-u6/` (Rama `master`, commit final: `202aecb`).
* **Repositorio Parte 2 (Unidades 7 y 8):**  
  [`https://github.com/simonfabrizio103/food-store-tp-u7-u8`](https://github.com/simonfabrizio103/food-store-tp-u7-u8)  
  *Carpetas clave:* `tp-unidad-7/`, `tp-unidad-8/` (Rama `main`, etiqueta oficial: `tp8`).

---

## Introducción y Enfoque Personal

Para esta segunda entrega del Trabajo Práctico Integrador de Food Store, el desafío fue consolidar y cerrar toda la capa de datos del proyecto, abarcando desde la normalización avanzada en PostgreSQL hasta la integración con MongoDB y SQLite en las tablets de los Food Trucks. 

A lo largo de las Unidades 4, 5, 6, 7 y 8 no me limité a tirar comandos o aceptar ciegamente lo que me devolvían las herramientas de IA (Kiro, OpenCode o asistentes LLM). En cada etapa me aseguré de entender qué pasaba por detrás en el motor, armar entornos de prueba sobre copias de la base (`food_store_copia`, `foodstore_restore_test`), medir tiempos reales de ejecución con `EXPLAIN ANALYZE` o cronómetros de PowerShell, y discutirle técnicamente a la IA cuando proponía cosas inviables para producción (como clavar un `VACUUM FULL` en caliente o meter autonuméricos en dispositivos móviles sin conexión).

A continuación desarrollo los 5 puntos solicitados en la consigna, explicando qué hice, cómo lo probé y qué decisiones tomé.

---

## 1. Qué elementos implementé en cada unidad (4 a 8)

### Unidad 4 · Normalización avanzada y redundancia controlada
* **Refactorización FNBC:** Analicé el esquema heredado y detecté que la tabla `control_lote_almacen` violaba la Forma Normal de Boyce-Codd por la dependencia funcional `ResponsableControlID -> DepositoID` (el determinante no era superclave). La descompuse sin pérdida de información en dos tablas: `responsable_control` y `control_lote_almacen_nuevo`, creando además una vista de compatibilidad para que el código existente no se rompiera.
* **Migración reversible:** Especifiqué en Kiro el plan de migración y lo ejecuté dentro de transacciones reversibles con bloques `BEGIN ... COMMIT / ROLLBACK`, asegurando que no se perdiera ni un solo registro.
* **Desnormalización controlada:** Creé la tabla agregada `categoria_venta_dia` para consultar el top 5 de categorías vendidas por día sin tener que recalcular `SUM` y `JOIN` sobre cientos de miles de filas en cada carga del dashboard. Le agregué triggers para mantenerla sincronizada y un script de auditoría periódica.

### Unidad 5 · Administración y seguridad
* **RBAC y mínimo privilegio:** Diseñé en Kiro (`requirements.md` y `design.md`) e implementé en `sql/roles.sql` una estructura estricta de roles: roles de grupo (`rol_admin_datos`, `rol_app_web`, `rol_cajero`, `rol_auditor`) y cuentas de login (`admin_datos`, `app_web`). Apliqué permisos a nivel de columna (por ejemplo, `app_web` solo puede ver `id_usuario`, `nombre` y `activo` en la tabla `usuario`, pero no contraseñas ni emails ajenos) y configuré `ALTER DEFAULT PRIVILEGES`.
* **Auditoría nativa y forense:** Activé en `postgresql.auto.conf` los parámetros `log_connections = on`, `log_disconnections = on` y `log_statement = 'all'`. Reconstruí un incidente simulado a partir del log crudo, armé un script en Python (`anonimizar_log.py`) para enmascarar datos sensibles antes de cualquier análisis, y redacté el informe forense.
* **Anonimización con salt (PII):** Implementé la tabla `usuario_anon` utilizando hash determinista `md5(id || sal)` sobre los correos electrónicos, eliminando hashes de contraseñas y conservando los IDs para no romper integridad referencial con los pedidos históricos.

### Unidad 6 · Mantenimiento y continuidad operativa
* **Plan de mantenimiento rutinario:** Diseñé `maintenance.sql` para ejecutar tareas periódicas: `VACUUM ANALYZE` sobre tablas transaccionales, `REINDEX CONCURRENTLY` para evitar hinchazón de índices (`bloat`), y recálculo de estadísticas del optimizador de costos.
* **Backups automatizados:** Creé el script `backup_foodstore.ps1` en PowerShell que realiza respaldos lógicos con `pg_dump` en formato custom comprimido (`-Fc`), verificando espacio libre en disco, integridad del archivo de salida y rotación automática con retención de 7 días.
* **Simulacro de desastre contra reloj:** Automaticé en `restore_test.ps1` la restauración completa de la base en una base efímera (`foodstore_restore_test`) y validé su consistencia mediante `validate_restore.sql`.

### Unidad 7 · NoSQL y nuevas formas de almacenamiento (MongoDB)
* **Modelado documental orientado a agregados:** Diseñé la colección `pedidos` en MongoDB embebiendo las líneas de productos (`lineas: [{ producto_id, nombre, cantidad, precio_unitario }]`) y una instantánea del cliente (`cliente: { id_cliente, nombre, email }`), resolviendo el cuello de botella de los JOINs en lecturas de la tienda online.
* **Consultas analíticas cruzadas:** Escribí las 4 consultas de negocio en MongoDB (`consultas_mongodb.js`) y sus contrapartes en SQL sobre PostgreSQL 18 (`consultas_postgresql.sql`), ejecutándolas sobre datos reales mediante un runner autónomo (`ejecutar_mongodb.js`).

### Unidad 8 · Bases de datos móviles e integración (SQLite)
* **Esquema Offline-First en SQLite 3.50+:** Diseñé `schema_sqlite.sql` para la tablet del Food Truck en la feria. Forcé modo estricto (`STRICT`), precios en **centavos enteros (`INT`)** para eliminar errores de flotante, identificadores **UUID v4** en formato texto para impedir colisiones entre tablets desconectadas, y `PRAGMA foreign_keys = ON;`.
* **Instantánea y semáforo:** Exporté la vista `v_snapshot_movil` de PostgreSQL a `servidor_snapshot.csv`, la importé en la tablet, e implementé el algoritmo jerárquico del semáforo (`semaforo.sql`) que clasifica solicitudes en `RECHAZADO` (rojo), `CONFLICTO` (amarillo) o `SIMULADO_APROBADO` (verde).
* **Simulación integral y comprobación:** Con `simulador.py` ejecuté y validé los casos C1 a C7, auditando al final en PostgreSQL que la regla de oro se cumpliera: la tablet propone, el servidor dispone.

---

## 2. Cómo probé el funcionamiento

Para no romper nada y asegurarme de que el código realmente anduviera, me apoyé en varias técnicas de prueba:

1. **Transacciones reversibles (`BEGIN ... ROLLBACK`):**
   * En la **Unidad 4**, antes de consolidar la migración de lotes a FNBC, corrí los scripts dentro de transacciones para poder hacer rollback si alguna fila quedaba huérfana.
   * En la **Unidad 8**, en `pruebas_sqlite.sql`, probé el alta completa de un borrador local con `COMMIT`, y después simulé la cancelación de una venta en mostrador con `ROLLBACK`, verificando mediante `COUNT(*)` que en la base de la tablet no quedara ninguna fila de ese pedido cancelado.
2. **Bases réplica y copias de prueba:**
   * En la **Unidad 4 y 5**, trabajé sobre la base réplica `food_store_copia` y `foodstore` (con más de 200,000 pedidos y 50,000 productos inventados), garantizando no tocar ambientes de desarrollo limpios.
   * En la **Unidad 6**, el simulacro de recuperación levantó una base totalmente nueva llamada `foodstore_restore_test` para medir el tiempo real sin pisar la base operativa.
3. **Simulacro de acceso indebido (Unidad 5):**
   * Me conecté intencionalmente con el rol de la aplicación web (`SET ROLE app_web;`) y ejecuté `sql/simulacro_incidente.sql`: intenté 4 veces invocar `fn_autenticar`, hice un `SELECT` masivo sobre tablas de auditoría, intenté leer correos ajenos y forcé sentencias de elevación de privilegios (`SET ROLE admin_datos;`, `CREATE ROLE hacker;`, `GRANT ALL;`). 
   * Verifiqué en el log de PostgreSQL cómo el motor rechazó con `permission denied` los ataques y registré la evidencia forense.
4. **Simulacro de desastre contra reloj (Unidad 6):**
   * Corrí `restore_test.ps1`. El script tomó el último backup generado (`foodstore_20261110_155502.dump`, 11.2 MB comprimido), creó la base réplica, ejecutó `pg_restore` cronometrando cada milisegundo, y lanzó `validate_restore.sql` para chequear tablas clave, conteo de filas y claves foráneas.
5. **Casos de conflicto y semáforo (Unidad 8):**
   * Mediante `simulador.py` probé metódicamente los casos de la feria:
     * **C1:** Consulté el menú offline sin conexión.
     * **C2:** Creé un borrador a $100, subí el precio en el servidor a $125 y corrí el semáforo &rarr; dio `CONFLICTO`. El cliente aceptó, actualicé el borrador local y reintenté &rarr; dio `SIMULADO_APROBADO`.
     * **C3:** Pedí 50 unidades de un producto con stock 10 &rarr; dio `RECHAZADO` (stock insuficiente).
     * **C4:** Di de baja lógica un producto en el servidor (`eliminado = 't'`) &rarr; dio `RECHAZADO`. Al refrescar la tablet, la fila quedó guardada físicamente por integridad pero desapareció del menú de ventas.
     * **C5:** Borrador idéntico al servidor &rarr; dio `SIMULADO_APROBADO`.
     * **C6:** Reenvié el mismo UUID &rarr; saltó error de `PRIMARY KEY` en SQLite y el semáforo no lo reevaluó.
     * **C7:** Probé insertar cantidad 0 y un ID inexistente &rarr; saltaron las restricciones `CHECK` y `FOREIGN KEY`.

---

## 3. Qué resultados obtuve

Los números y resultados empíricos que obtuve en las pruebas fueron los siguientes:

| Unidad | Prueba / Escenario | Resultado / Métrica Obtenida | Validación |
| :---: | :--- | :--- | :--- |
| **U4** | Desnormalización Top 5 categorías | Consulta original: **0.123 ms** (Seq Scan)<br/>Con tabla desnormalizada: **0.077 ms** (Bitmap Heap Scan) | **37.4% de reducción de tiempo**; 0 filas desincronizadas en auditoría. |
| **U5** | Mínimo privilegio y permisos | Permisos a nivel de columna verificados en `information_schema`. | `app_web` bloqueado de leer hashes; `fn_autenticar` parcheada a `SECURITY DEFINER`. |
| **U5** | Anonimización `usuario_anon` | 6 comprobaciones estadísticas sobre distribución de roles y pedidos. | 100% de equivalencia en agregados sin filtrar PII real. |
| **U6** | Simulacro de Desastre (RTO y RPO) | **RTO: 4.84 segundos** (restauración de 96 MB y 200,001 órdenes).<br/>**RPO: 1.70 minutos** (pérdida máxima estimada). | Cumplió holgadamente los objetivos fijados (RTO < 15 min, RPO < 1 hora). |
| **U6** | Integridad post-restauración | `validate_restore.sql`: 0 errores de claves foráneas y conteo exacto de 200,001 pedidos. | Base restaurada 100% íntegra y operativa. |
| **U7** | Consultas cruzadas MongoDB vs PG | Consulta 4.a (Entregados): 3 pedidos (IDs 2, 4, 7).<br/>Consulta 4.b (Prod. 3): 3 pedidos (IDs 2, 4, 6).<br/>Consulta 4.c (Total > $2000): 2 pedidos (IDs 4 y 6). | **100% de coincidencia exacta** entre el motor documental y el relacional. |
| **U8** | Semáforo de Sincronización | Casos C1, C2, C3, C4, C5, C6 y C7 evaluados en `foodstore_movil.db`. | Estados esperados exactos: Conflicto, Rechazos, y Simulado Aprobado. |
| **U8** | Auditoría de Invariabilidad en PostgreSQL | `SELECT COUNT(*) FROM pedido;` &rarr; **200,001**.<br/>Stock de productos 1, 2, 3 y 4: **5, 10, 115 y 130**. | **0 ventas insertadas y 0 unidades descontadas en PG.** La regla de oro se cumplió. |

---

## 4. Qué decisiones de diseño tomé

En cada unidad tuve que tomar decisiones técnicas de arquitectura fundamentadas:

1. **Refactorización FNBC vs. Compatibilidad (Unidad 4):**  
   Al normalizar `control_lote_almacen` separando `responsable_control`, no quise romper las consultas que otros sistemas pudieran estar haciendo contra la tabla vieja. Por eso creé una **vista con el mismo nombre y estructura que la tabla original**, redirigiendo las consultas hacia las dos tablas nuevas de forma totalmente transparente.
2. **Cuándo desnormalizar y con qué salvaguardas (Unidad 4):**  
   Desnormalizar no es duplicar datos porque sí. Solo lo apliqué en `categoria_venta_dia` porque el dashboard de ventas se consulta constantemente en horario pico y recalcular agrupaciones sobre cientos de miles de registros pegaba fuerte en la CPU. Para evitar inconsistencias, implementé un trigger que actualiza el total diario ante cada venta y un script de auditoría que salta si hay diferencias.
3. **Mínimo Privilegio y Remediación H-1 (Unidad 5):**  
   En la Unidad 5 me encontré con un problema crítico: al quitarle a `app_web` el permiso de `SELECT` sobre `usuario` (para proteger contraseñas e emails), la función `fn_autenticar` fallaba con `permission denied` porque era `SECURITY INVOKER`.  
   En vez de la salida fácil (que hubiera sido darle permisos de lectura a la aplicación sobre toda la tabla), decidí aplicar la solución correcta de seguridad: **cambié `fn_autenticar` a `SECURITY DEFINER`, se la asigné a `admin_datos` y le clavé un `search_path = public, pg_temp` estricto**. Así, la app puede autenticar usuarios pero sigue completamente ciega ante los datos sensibles.
4. **Arquitectura Híbrida CQRS en vez del falso dilema SQL vs NoSQL (Unidad 7):**  
   No caí en la trampa de querer reemplazar PostgreSQL por MongoDB ni viceversa. Elegí un enfoque políglota / CQRS:
   * **PostgreSQL** es el núcleo transaccional (OLTP) y la **única fuente de verdad**: garantiza ACID, maneja stock, clientes, usuarios y ventas fiscales.
   * **MongoDB** actúa como un **Read Model documental**: recibe los pedidos ya confirmados y los guarda desnormalizados con sus líneas embebidas para que la web o la app móvil puedan consultar historiales y catálogos a milésimas de segundo sin meterle presión al motor relacional con JOINs.
5. **Arquitectura Móvil Offline-First (Unidad 8):**  
   Para la tablet en la feria gastronómica diseñé una base SQLite con reglas muy firmes:
   * **Precios en centavos enteros (`INT`):** Para evitar que los redondeos de números de coma flotante nos coman centavos en las ventas.
   * **UUID v4 en vez de autonuméricos:** Si tres mozos toman pedidos en tres tablets distintas sin señal, usar `id = 1, 2, 3` provocaría colisiones masivas al sincronizar. Con UUID v4 cada pedido nace con un identificador unívoco a nivel mundial.
   * **Modo `STRICT`:** Forcé tipado estático para que SQLite no acepte textos en columnas numéricas ni datos truncados.
   * **"El móvil propone, el servidor dispone":** La tablet nunca descuenta stock ni fija precios. `SIMULADO_APROBADO` solo le indica al mozo que, según la última foto que tiene, el pedido es viable; la venta real y el descuento de inventario se definen cuando PostgreSQL procesa la orden.

---

## 5. Herramientas de IA utilizadas, bitácora y descartes fundamentales

A lo largo de todo el trabajo utilicé herramientas de IA (Kiro para especificación EARS, OpenCode y asistentes LLM para acelerar el armado de estructuras y scripts). Sin embargo, mantuve siempre una postura de **auditoría técnica humana**: jamás ejecuté código sin leerlo línea por línea ni acepté sugerencias que comprometieran la disponibilidad o la integridad de la base.

### Tabla de Descarte y Corrección Humana a la IA

| Unidad | Componente | Lo que propuso la IA | Decisión y Corrección Humana | Fundamento Técnico |
| :---: | :--- | :--- | :---: | :--- |
| **U6** | `maintenance.sql` | Correr `VACUUM FULL ANALYZE` diariamente en todas las tablas. | **DESCARTADO DE PLANO** | `VACUUM FULL` adquiere bloqueo exclusivo (`ACCESS EXCLUSIVE LOCK`), impidiendo que nadie lea (`SELECT`) ni escriba (`INSERT`) durante minutos. En producción con 200,000 pedidos, tiraría la tienda abajo. Mantuve `VACUUM (ANALYZE, VERBOSE)` concurrente. |
| **U8** | `schema_sqlite.sql` | Usar claves primarias `INTEGER AUTOINCREMENT` en pedidos locales. | **DESCARTADO DE PLANO** | En un sistema desconectado con varias tablets, las claves autonuméricas colisionan inevitablemente al sincronizar. Impuse **UUID v4**. |
| **U8** | Triggers móviles | Crear triggers en SQLite para actualizar el stock remoto en PostgreSQL. | **DESCARTADO DE PLANO** | Viola el diseño Offline-First y la regla de oro: si no hay señal en la feria, la tablet se congelaría esperando el socket de red. La conciliación debe ser asíncrona mediante el semáforo. |
| **U7** | Análisis NoSQL | Afirmar que "MongoDB no soporta transacciones ACID". | **REFUTADO TÉCNICAMENTE** | MongoDB soporta transacciones multi-documento desde la versión 4.0 (2018), y además en documentos con líneas embebidas la atomicidad es nativa a nivel de documento sin overhead distribuido. |
| **U5** | `fn_autenticar` | Concederle permiso `SELECT` a `app_web` sobre la tabla `usuario`. | **DESCARTADO** | Viola el mínimo privilegio al exponer contraseñas en hash. Se corrigió convirtiendo la función a `SECURITY DEFINER` con `search_path` seguro. |

Toda esta interacción crítica quedó formalizada en las bitácoras técnicas (`BITACORA.md`) y en las declaraciones juradas (`DUIA.md`) presentes en cada uno de los repositorios.

---

## Conclusión Final

La realización de este proyecto integrador me permitió entender la base de datos no como un simple depósito de tablas, sino como un **sistema vivo, distribuido y altamente crítico**. 

Aprendí que el rendimiento no se logra metiendo índices a ciegas sino entendiendo los planes de ejecución (`EXPLAIN ANALYZE`), que la seguridad no es una capa externa sino una política estricta de permisos y funciones securizadas (`SECURITY DEFINER`), que un backup no vale nada si no se prueba periódicamente su restauración contra reloj (RTO de 4.84 s), y que en sistemas distribuidos modernos la convivencia entre motores especializados (PostgreSQL para transacciones, MongoDB para lecturas desnormalizadas y SQLite para el borde offline) es el camino más robusto para construir software profesional.
