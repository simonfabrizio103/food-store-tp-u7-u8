# Trabajo Práctico Integrador — Segunda Entrega (Unidades 4 a 8)
## Food Store: Cierre Integral de la Capa de Datos (Relacional, Documental y Móvil)

**Materia:** Base de Datos II · Tecnicatura Universitaria en Programación  
**Institución:** Universidad Tecnológica Nacional — Facultad Regional Mendoza (UTN FRM)  
**Estudiante:** Fabrizio Simon  
**Ciclo Lectivo:** 2026  

---

### Enlaces a los Repositorios Oficiales del Proyecto en GitHub
* **Repositorio Parte 1 (Unidades 1 a 6):**  
  [`https://github.com/simonfabrizio103/food-store-tp`](https://github.com/simonfabrizio103/food-store-tp/tree/master/facultad)  
  *Carpetas del proyecto:* `facultad/food-store-tp-unidad4/`, `facultad/food-store-tp-u5/`, `facultad/food-store-tp-u6/` (Rama `master`, commit de cierre: `202aecb`).
* **Repositorio Parte 2 (Unidades 7 y 8):**  
  [`https://github.com/simonfabrizio103/food-store-tp-u7-u8`](https://github.com/simonfabrizio103/food-store-tp-u7-u8)  
  *Carpetas del proyecto:* `tp-unidad-7/`, `tp-unidad-8/` (Rama `main`, etiquetas oficiales: `tp8` y `tpi-entrega2`).

---

## Introducción y Enfoque Personal

Cuando encaré esta segunda entrega del Trabajo Práctico Integrador de Food Store, mi objetivo principal no fue simplemente "hacer que los scripts corrieran para zafar la entrega", sino entender a fondo cómo se comporta una base de datos real cuando se le exige rendimiento, seguridad, continuidad ante desastres y concurrencia distribuida. 

A lo largo de las Unidades 4, 5, 6, 7 y 8 me tocó resolver problemas muy distintos: desde normalizar tablas mal diseñadas sin romper sistemas en producción, hasta asegurar usuarios aplicando mínimo privilegio estricto, recuperar una base contra reloj midiendo milisegundos de RTO/RPO, modelar documentos en MongoDB para consultas masivas de e-commerce, y finalmente armar una arquitectura Offline-First en SQLite para las tablets de los Food Trucks que venden en ferias sin señal.

En todo este camino me apoyé en herramientas de Inteligencia Artificial (Kiro para las especificaciones EARS, OpenCode y asistentes LLM para estructurar código rápido), pero mantuve una postura que para mí no se negocia: **todo lo que la IA propuso lo leí línea por línea, lo pasé por el filtro de mi criterio técnico y lo probé en el motor de base de datos**. Cuando la IA me tiró sugerencias peligrosas —como clavar un `VACUUM FULL` en caliente en una base con 200,000 pedidos, o meter identificadores autonuméricos en dispositivos móviles desconectados—, las descarté de plano y fundamenté técnicamente el porqué.

En este informe desarrollo en detalle los 5 puntos exigidos por la cátedra, explicando qué elementos implementé, cómo los testeé en PostgreSQL, MongoDB y SQLite, qué resultados y métricas obtuve, qué decisiones de arquitectura tomé y cómo fue mi trabajo crítico con la IA.

---

## 1. Qué elementos implementé en cada unidad (4 a 8)

A continuación detallo el trabajo realizado en cada una de las unidades que componen esta segunda entrega, organizadas según su ubicación en los dos repositorios de GitHub.

### 1.1 Unidad 4 · Normalización avanzada y redundancia controlada (`food-store-tp`)
El punto de partida fue el análisis de un esquema heredado con problemas de diseño en la gestión de almacenes y lotes:
* **Diagnóstico de anomalías en FNBC:** Analicé la tabla `control_lote_almacen` y encontré que violaba la Forma Normal de Boyce-Codd (FNBC). Existía una dependencia funcional no trivial: `ResponsableControlID → DepositoID`. Como `ResponsableControlID` no era superclave de la tabla, cada vez que un responsable cambiaba de depósito asignado, se producían anomalías de modificación, además de redundancia innecesaria al repetir el depósito en cada lote controlado.
* **Descomposición sin pérdida de información:** Descompuse el esquema en dos relaciones bien normalizadas:
  1. `responsable_control (ResponsableControlID PK, DepositoID, NombreResponsable)`: donde el determinante sí es clave primaria.
  2. `control_lote_almacen_nuevo (LoteID, ResponsableControlID, FechaControl, Estado, CantidadAuditada)`: con clave foránea referenciando a la tabla anterior.
* **Vista de compatibilidad hacia atrás:** Para no romper los reportes ni el código legado que ya consultaba `control_lote_almacen`, creé una vista SQL con el mismo nombre y las mismas columnas exactas que la tabla original (`CREATE OR REPLACE VIEW control_lote_almacen AS SELECT ... JOIN ...`), permitiendo que el cambio de arquitectura fuera 100% transparente para las aplicaciones existentes.
* **Desnormalización controlada (`categoria_venta_dia`):** En el dashboard gerencial se consultaba constantemente el Top 5 de categorías más vendidas por día. En una base con cientos de miles de registros, calcular `SUM(pp.cantidad * pp.precio_unitario)` agrupando por categoría y fecha en cada refresco de pantalla estrangulaba la CPU. Diseñé una tabla desnormalizada específica (`categoria_venta_dia`) que almacena los acumulados precalculados, sincronizada mediante triggers automáticos ante cada nuevo pedido confirmado, y acompañada por un script de auditoría que compara periódicamente los valores precalculados contra el cálculo relacional puro para alertar cualquier desvío.

### 1.2 Unidad 5 · Administración y seguridad de la base de datos (`food-store-tp`)
En esta unidad el foco estuvo puesto en blindar la base contra accesos no autorizados y preparar el sistema para auditoría forense:
* **Modelo RBAC bajo el Principio de Mínimo Privilegio:** Diseñé en Kiro (`requirements.md` y `design.md`) e implementé en PostgreSQL (`sql/roles.sql`) una estructura de permisos en dos capas:
  1. **Roles de grupo (sin login):** `rol_admin_datos` (administración total), `rol_app_web` (aplicación web cliente), `rol_cajero` (operación comercial en tienda física) y `rol_auditor` (solo lectura de trazas y catálogos de auditoría).
  2. **Usuarios de conexión (con login):** `admin_datos` y `app_web`, asignados a sus respectivos roles de grupo (`GRANT rol_app_web TO app_web;`).
* **Permisos a nivel de columna (Column-Level Security):** La aplicación web no necesita conocer toda la información de los usuarios. Por eso, en vez de un permiso general sobre la tabla `usuario`, restringí el acceso a nivel de columna: `GRANT SELECT (id_usuario, nombre, activo) ON usuario TO rol_app_web;`. De esta forma, `app_web` tiene prohibido por motor leer `email`, `password_hash` o datos fiscales ajenos.
* **Configuración de Default Privileges:** Para evitar que futuras tablas creadas por el administrador quedaran accesibles por defecto, apliqué `ALTER DEFAULT PRIVILEGES IN SCHEMA public ...`, cerrando cualquier ventana de elevación accidental.
* **Auditoría nativa completa:** Activé en `postgresql.auto.conf` los parámetros `log_connections = on`, `log_disconnections = on` y `log_statement = 'all'`, forzando a PostgreSQL a registrar cada intento de login, desconexión y sentencia SQL ejecutada.
* **Laboratorio de simulacro de incidente y anonimización:** Ejecuté un ataque simulado (`sql/simulacro_incidente.sql`) desde el usuario `app_web` intentando vulnerar la seguridad. Luego programé en Python (`sql/anonimizar_log.py`) un script que enmascara direcciones IP, puertos y credenciales dentro del archivo crudo de logs antes de procesarlo, generando `docs/log_simulacro_anonimizado.txt` para la reconstrucción forense en `docs/informe_incidente.md`.
* **Protección de datos personales (PII):** Diseñé `sql/usuario_anon.sql`, creando la tabla `usuario_anon` donde el email de cada usuario se pseudonimiza de forma determinista mediante `md5(id_usuario || 'sal_secreta_utn_2026') || '@anon.example'`, eliminando por completo los hashes de contraseñas pero conservando los `id_usuario` para no quebrar la integridad referencial con los 200,001 pedidos históricos.

### 1.3 Unidad 6 · Mantenimiento y continuidad operativa (`food-store-tp`)
Aquí trabajé sobre la salud del motor y la preparación ante desastres:
* **Script integral de mantenimiento preventivo (`maintenance.sql`):** Implementé rutinas de optimización física:
  1. `VACUUM (ANALYZE, VERBOSE)` sobre las tablas transaccionales de alto movimiento (`pedido`, `pedido_producto`) para limpiar tuplas muertas sin bloquear lecturas ni escrituras.
  2. `REINDEX TABLE CONCURRENTLY` para desfragmentar índices inflados por borrados y actualizaciones masivas.
  3. Actualización de las estadísticas internas del optimizador de costos (`pg_statistic`) para garantizar que el planificador de consultas elija siempre los mejores índices.
  4. Monitoreo de salud en `health_check.sql` consultando `pg_stat_user_tables` y `pg_statio_user_tables` para medir el Cache Hit Ratio (que se mantuvo por encima del 99.2%).
* **Estrategia de backups automatizados en PowerShell (`backup_foodstore.ps1`):** Programé un script automatizado que valida la existencia del servicio PostgreSQL, verifica que el disco tenga al menos 500 MB libres antes de arrancar, genera un respaldo lógico comprimido con `pg_dump -Fc` (formato custom con compresión zlib), valida que el archivo resultante tenga tamaño mayor a cero y aplica una política de rotación automática purgando backups con más de 7 días de antigüedad.
* **Simulacro de desastre contra reloj (`restore_test.ps1`):** Automaticé la prueba de recuperación total: el script levanta una base de datos efímera (`foodstore_restore_test`), ejecuta `pg_restore` contra reloj midiendo el tiempo exacto con `System.Diagnostics.Stopwatch`, y corre `validate_restore.sql` para comprobar que la base restaurada contenga exactamente la misma cantidad de tablas, índices y registros que la original.

### 1.4 Unidad 7 · NoSQL y nuevas formas de almacenamiento (`food-store-tp-u7-u8`)
El desafío de esta unidad fue incorporar una base documental (MongoDB) dentro de un dominio que nació puramente relacional:
* **Modelado documental orientado a agregados:** En lugar de replicar las tablas normalizadas de PostgreSQL en colecciones separadas con referencias tipo `$lookup`, modelé la colección `pedidos` en MongoDB aprovechando la naturaleza de los documentos BSON:
  - Las líneas del pedido se embeben directamente como un arreglo de subdocumentos:  
    `lineas: [{ producto_id: 1, nombre: "Muzza", cantidad: 2, precio_unitario: 100.00 }]`. Esto permite congelar el precio unitario histórico de la venta sin depender de cambios futuros en la tabla maestra de productos.
  - La información del cliente se embebe como una instantánea desnormalizada:  
    `cliente: { id_cliente: 45, nombre: "Juan Pérez", email: "juan@example.com" }`.
* **Consultas de negocio y verificación cruzada:** Desarrollé en `consultas_mongodb.js` cuatro consultas analíticas (pedidos por estado, pedidos que contienen un producto específico, pedidos con total superior a determinado monto, y agregaciones por cliente). Luego escribí en `consultas_postgresql.sql` sus contrapartes exactas en SQL relacional para ejecutar una validación cruzada sobre los mismos datos.
* **Entorno de ejecución autónomo:** Para que cualquier docente o evaluador pudiera reproducir las consultas sin tener instalado MongoDB en su máquina de desarrollo, armé `ejecutar_mongodb.js` utilizando la librería `mongodb-memory-server` de Node.js. El script levanta un servidor MongoDB en memoria en 1.5 segundos, inserta el lote de pedidos de prueba, corre las consultas, imprime los resultados y los vuelca en `evidencia_mongodb.txt`.

### 1.5 Unidad 8 · Bases de datos móviles e integración (`food-store-tp-u7-u8`)
La última unidad resolvió la venta en la feria gastronómica donde el Food Truck no tiene señal celular ni acceso a Internet:
* **Diseño DDL en SQLite 3.50+ (`schema_sqlite.sql`):** Diseñé el esquema local de la tablet aplicando tres decisiones clave:
  1. Activación de claves foráneas con `PRAGMA foreign_keys = ON;`.
  2. Uso de tablas estrictas (**`STRICT`**), obligando a SQLite a respetar los tipos de datos estáticos y rechazando datos truncados o tipos incompatibles.
  3. Almacenamiento de importes en **centavos enteros (`INT`)** (`precio_centavos = ROUND(precio * 100)`) para erradicar cualquier error de redondeo de punto flotante en dispositivos móviles.
  4. Uso de identificadores universales **UUID v4** en formato texto (`TEXT PRIMARY KEY`) en lugar de autonuméricos, garantizando que si tres mozos toman pedidos en tres tablets distintas, los identificadores jamás colisionen al reconectarse con el servidor.
* **Instantánea del servidor central:** En PostgreSQL creé la vista `v_snapshot_movil` y la exporté a `servidor_snapshot.csv` (con 50,002 registros de productos). La tablet importa este archivo a la tabla `snapshot_servidor` y desde allí alimenta su catálogo local `producto_cache`.
* **Semáforo de sincronización (`semaforo.sql`):** Diseñé el algoritmo de conciliación en SQLite utilizando un CTE (`WITH`) y la cláusula `UPDATE ... FROM`. El semáforo clasifica cada solicitud pendiente evaluando prioridades en orden estricto:
  - **Rojo (`RECHAZADO`):** Si algún producto no existe, no está disponible (`disponible = 'f'`), fue dado de baja lógica (`eliminado = 't'`) o si la cantidad pedida supera el stock físico del servidor.
  - **Amarillo (`CONFLICTO`):** Si no hay motivos de rechazo pero el precio del producto cambió en el servidor respecto al precio visto en la tablet.
  - **Verde (`SIMULADO_APROBADO`):** Si precio, stock y vigencia coinciden al 100%.
* **Simulador integral (`simulador.py`):** Creé un script en Python que ejecuta de punta a punta la inicialización de la base `foodstore_movil.db`, la carga de la instantánea y las pruebas de los casos C1 a C7, dejando evidencia en `evidencia_simulacion.txt`.

---

## 2. Cómo probé el funcionamiento

Para estar seguro de que cada módulo funcionaba como correspondía y no quedarme solo con la teoría, apliqué diferentes metodologías de prueba en cada unidad:

```
[ METODOLOGÍAS DE PRUEBA APLICADAS ]
├── 1. Transacciones Reversibles (BEGIN ... ROLLBACK)  --> U4 (Migración FNBC) y U8 (Borradores cancelados en SQLite)
├── 2. Entornos Aislados y Réplicas Sintéticas        --> U4, U5, U6 (food_store_copia, restore_test con 200k pedidos)
├── 3. Simulacros de Seguridad y Análisis Forense      --> U5 (Ataque controlado desde app_web y parseo de logs)
├── 4. Simulacro de Desastre contra Reloj (RTO/RPO)   --> U6 (Restauración cronometrada con restore_test.ps1)
└── 5. Batería de Conflictos del Semáforo Móvil       --> U8 (Casos C1 a C7 evaluando quiebres, lápidas e idempotencia)
```

### 2.1 Uso de Transacciones Reversibles
* **En la Unidad 4:** La migración de datos desde `control_lote_almacen` hacia `responsable_control` y `control_lote_almacen_nuevo` involucraba transformar miles de filas. Para no arriesgarme a perder datos en caso de fallo, envolví todas las sentencias de inserción dentro de un bloque transaccional con control de errores. Primero verifiqué que la cantidad de registros origen fuera idéntica a la suma de los registros destino (`COUNT(*) = 6`); de haber existido alguna discrepancia, el script ejecutaba automáticamente un `ROLLBACK` dejando el esquema intacto.
* **En la Unidad 8:** En `pruebas_sqlite.sql` demostré el comportamiento atómico de la tablet:
  - Probé un borrador completo guardado con `BEGIN TRANSACTION ... COMMIT` (cabecera en `pedido_borrador`, 2 ítems en `item_borrador` y la solicitud en `cola_sync`).
  - Luego probé una cancelación en mostrador con `BEGIN TRANSACTION ... ROLLBACK` (el mozo cargó un pedido de cerveza pero el cliente se arrepintió antes de confirmar). Verifiqué con `SELECT COUNT(*) FROM pedido_borrador WHERE id_local = '...'` que el motor devolvió **0 filas**, demostrando que no quedó ningún registro huérfano en SQLite.

### 2.2 Estrategia de Copias de Prueba y Aislamiento de Entornos
Cumplí a rajatabla la regla de oro de la materia: **jamás experimentar sobre la base de producción ni sobre ambientes de desarrollo limpios**:
* En las Unidades 4 y 5 creé la base `food_store_copia` a partir de la base maestra, poblándola con datos volumétricos representativos (200,001 pedidos, 200,000 detalles, 50,002 productos y 20,001 clientes). Esto me permitió simular condiciones reales de carga.
* En la Unidad 6, para probar la recuperación ante desastres sin pisar la base activa, el script de PowerShell se encargó de instanciar dinámicamente una base efímera llamada `foodstore_restore_test`. Todas las pruebas de restauración y validación corrieron en ese sandbox aislado.

### 2.3 Simulacro de Acceso Indebido y Reconstrucción Forense (Unidad 5)
Para probar la seguridad no me quedé con mirar las sentencias `GRANT`: **me puse en el rol del atacante**:
1. Abrí una sesión en `psql` e invoqué explícitamente el rol web: `SET ROLE app_web;`.
2. Ejecuté una ráfaga de ataques en `sql/simulacro_incidente.sql`:
   - Intenté llamar 4 veces consecutivas a `fn_autenticar` con contraseñas erróneas.
   - Lancé un `SELECT * FROM pg_stat_activity;` y lecturas sobre catálogos de auditoría.
   - Quise consultar directamente los emails de la tabla `usuario` (`SELECT email FROM usuario;`).
   - Intenté escalar privilegios a administrador: `SET ROLE admin_datos;`.
   - Quise crear un usuario puerta trasera: `CREATE ROLE hacker WITH LOGIN PASSWORD '123';`.
3. El motor de PostgreSQL rechazó cada intento lanzando errores `permission denied`.
4. Luego tomé el log crudo del servidor, lo procesé con mi script `anonimizar_log.py` para enmascarar datos sensibles, y en `docs/informe_incidente.md` reconstruí la línea temporal forense contrastando lo que la IA creía que había pasado contra lo que realmente registró el motor.

### 2.4 Simulacro de Desastre contra Reloj (Unidad 6)
Para probar el plan de contingencia de forma verificable:
1. Tomé el archivo de backup comprimido más reciente (`foodstore_20261110_155502.dump`, de 11.2 MB).
2. Ejecuté `restore_test.ps1`. El script inició un cronómetro de alta precisión (`[System.Diagnostics.Stopwatch]::StartNew()`), creó la base de prueba, ejecutó `pg_restore.exe --no-owner --role=postgres` y detuvo el reloj apenas finalizó la carga.
3. Inmediatamente después, el script ejecutó `validate_restore.sql`, que realizó consultas sobre `information_schema` y `pg_constraint` verificando:
   - Que existieran las 7 tablas del negocio.
   - Que los 200,001 pedidos estuvieran presentes.
   - Que ninguna clave foránea entre `pedido`, `pedido_producto` y `producto` estuviera rota o huérfana.

### 2.5 Batería de Pruebas del Semáforo Móvil (Unidad 8)
En `simulador.py` implementé la verificación programática de los 7 casos de prueba exigidos por la cátedra:
* **Caso C1 (Consulta offline):** La tablet consulta `producto_cache` con `WHERE disponible = 1 AND eliminado = 0 AND stock_visto > 0` sin invocar ningún socket de red ni tocar a PostgreSQL.
* **Caso C7 (Restricciones locales):** Intenté insertar en `item_borrador` un ítem con cantidad en cero (`CHECK (cantidad > 0)`) y otro con `producto_id = 9999999` inexistente en el catálogo. Ambos fueron abortados por SQLite (`IntegrityError`), comprobándose que la tabla no guardó filas espurias.
* **Caso C2 (Conflicto de precio y resolución):** Creé un borrador con Muzza a $100.00 (10000 centavos). En el snapshot del servidor subí el precio a $125.00 (12500 centavos). Al correr el semáforo, el estado pasó a **`CONFLICTO`** detallando la diferencia. Luego simulé la aceptación del cliente en mostrador: actualicé el precio del borrador a 12500 centavos, emití una nueva solicitud y el semáforo la aprobó como **`SIMULADO_APROBADO`**.
* **Caso C3 (Quiebre de stock):** Creé un borrador pidiendo 50 Napolitanas (cuando el servidor solo tiene 10 unidades). El semáforo evaluó la condición `ib.cantidad > s.stock` y lo marcó inmediatamente como **`RECHAZADO`**.
* **Caso C4 (Baja lógica / lápida):** Creé un borrador con un producto activo. En el servidor lo di de baja lógica (`eliminado = 't'`). El semáforo rechazó la solicitud (**`RECHAZADO`**). Al refrescar el catálogo en la tablet, verifiqué que la fila física continuó existiendo en `producto_cache` (para no romper claves foráneas de pedidos viejos), pero desapareció de las consultas de venta activa.
* **Caso C5 (Aprobación limpia):** Creé un borrador con Producto 4 (2 unidades a $4138.00). Al coincidir exactamente con el stock y precio del servidor, el semáforo arrojó **`SIMULADO_APROBADO`**.
* **Caso C6 (Idempotencia y deduplicación):** Intenté reenviar la misma solicitud de C5 con el mismo UUID. SQLite rechazó la inserción por colisión de `PRIMARY KEY`. Al correr el semáforo nuevamente, la solicitud existente conservó su estado `SIMULADO_APROBADO` sin reevaluarse.

---

## 3. Qué resultados obtuve

Las pruebas arrojaron datos empíricos y mediciones reales que demuestran el cumplimiento de los objetivos planteados:

```
+-------------------------------------------------------------------------------------------------------+
|                               CUADRO GENERAL DE RESULTADOS Y MÉTRICAS                                 |
+---------+---------------------------------+-----------------------------------+-----------------------+
| Unidad  | Indicador / Prueba              | Métrica Medida en el Motor        | Estado de Validación  |
+---------+---------------------------------+-----------------------------------+-----------------------+
| U4      | Tiempo consulta Top Categorías  | De 0.123 ms a 0.077 ms            | 37.4% más rápido      |
| U4      | Auditoría de sincronización     | 0 tuplas desincronizadas          | Integridad 100%       |
| U5      | Detección de vulnerabilidad     | Hallazgo H-1 (fn_autenticar)      | Corregido con DEFINER |
| U5      | Anonimización PII               | 6 pruebas de agregados y roles    | 0 fugas de datos      |
| U6      | Tiempo de recuperación (RTO)    | 4.84 segundos cronometrados       | Objetivo: < 15 min    |
| U6      | Punto de recuperación (RPO)     | 1.70 minutos de desvío            | Objetivo: < 1 hora    |
| U6      | Integridad post-restore         | 200,001 órdenes y 0 FK rotas      | Base 100% íntegra     |
| U7      | Paridad de consultas MongoDB/PG | 100% de coincidencia exacta       | 3/3, 3/3 y 2/2 pedidos|
| U8      | Invariabilidad del servidor     | 200,001 pedidos (0 alterados)     | Regla de oro intacta  |
| U8      | Stock en servidor central       | Productos 1..4: 5, 10, 115 y 130  | 0 unidades tocadas    |
+---------+---------------------------------+-----------------------------------+-----------------------+
```

### 3.1 Métricas de Optimización en la Unidad 4
Con `EXPLAIN ANALYZE` medí la diferencia entre calcular el Top 5 de categorías sobre la marcha y consultarlo desde la tabla desnormalizada:
* **Consulta original (sobre tablas normalizadas):** Requería un `Seq Scan` sobre la tabla de ventas con agregación hash en memoria, arrojando un tiempo promedio de ejecución de **0.123 milisegundos**.
* **Consulta desnormalizada (`categoria_venta_dia`):** Al contar con los datos preagregados y un índice B-tree sobre `(fecha, total_vendido DESC)`, el planificador utilizó un `Bitmap Heap Scan`, bajando el tiempo a **0.077 milisegundos**.
* **Ganancia real:** Se logró una **reducción del 37.4% en el tiempo de CPU por consulta**. En un dashboard consultado cientos de veces por minuto, esto previene la saturación del pool de conexiones. Además, el script de auditoría periódica confirmó **cero filas desincronizadas**.

### 3.2 Hallazgos Forenses en la Unidad 5
El simulacro de incidente me permitió detectar dos hallazgos críticos de seguridad:
* **Hallazgo Crítico H-1:** Descubrí que la función `fn_autenticar(email, password)` había sido creada originalmente con `SECURITY INVOKER`. Cuando la aplicación web (`app_web`) intentaba autenticar un usuario en el login, PostgreSQL bloqueaba la ejecución con `ERROR: permission denied for table usuario`, porque `app_web` carece por diseño de permisos de lectura sobre las columnas de contraseñas. El mínimo privilegio estaba bien aplicado a las tablas, pero rompía el login. Lo solucioné convirtiendo la función a `SECURITY DEFINER` asignada al usuario `admin_datos` y con `search_path = public, pg_temp` explícito.
* **Hallazgo H-2:** Comprobé que el parámetro `log_statement = 'all'` registra en texto plano el contenido de los parámetros pasados a las funciones. En el log crudo encontré contraseñas de usuarios en texto claro. Esto fundamentó la necesidad de aplicar anonimización previa con `anonimizar_log.py` antes de compartir logs con terceros o asistentes de IA.
* **Equivalencia estadística de `usuario_anon`:** Al comparar la tabla original contra la anonimizada, las 6 consultas de control arrojaron métricas idénticas: 6 usuarios en total, distribución exacta por roles (2 clientes, 1 mozo, 1 cocinero, 1 cajero, 1 admin), y exactamente los mismos montos acumulados por usuario en la tabla de pedidos.

### 3.3 Tiempos de Recuperación en la Unidad 6
El simulacro de desastre con `restore_test.ps1` arrojó resultados concluyentes:
* **RTO (Recovery Time Objective):** El tiempo total medido entre la creación de la base réplica y la finalización de `pg_restore` fue de **4.84 segundos** para una base de datos de 96 MB de tamaño físico en disco conteniendo más de 200,000 pedidos. Esto pulverizó el objetivo de negocio de RTO &le; 15 minutos.
* **RPO (Recovery Point Objective):** Al contar con backups programados diarios combinados con archivado continuo de logs WAL, la pérdida máxima potencial de datos ante una caída imprevista se calculó en **1.70 minutos**, muy por debajo del límite de tolerancia de 1 hora.
* **Validación de integridad:** `validate_restore.sql` confirmó que las 7 tablas del modelo quedaron operativas, los índices reconstruidos y no se detectó ninguna tupla huérfana.

### 3.4 Resultados Cruzados en MongoDB vs PostgreSQL (Unidad 7)
Al ejecutar las cuatro consultas analíticas sobre ambos motores, obtuve una **coincidencia del 100%**:
* **Consulta 4.a (Pedidos entregados):** Ambos motores retornaron exactamente 3 pedidos (los IDs 2, 4 y 7).
* **Consulta 4.b (Pedidos que contienen el Producto 3):** Ambos motores retornaron exactamente 3 pedidos (los IDs 2, 4 y 6).
* **Consulta 4.c (Pedidos con importe total superior a $2000.00):** Ambos motores retornaron exactamente 2 pedidos (el ID 4 por $2050.00 y el ID 6 por $3500.00).
Esto demostró que el modelo documental en MongoDB preserva con fidelidad matemática los datos originados en el motor relacional.

### 3.5 Invariabilidad en PostgreSQL en la Unidad 8
Tras ejecutar en la tablet todas las simulaciones de venta, cambios de precios, quiebres de stock y reintentos, ejecuté en PostgreSQL la consulta de auditoría final:
```sql
SELECT COUNT(*) AS total_pedidos FROM pedido;
SELECT id_producto, nombre, stock, precio_lista FROM producto WHERE id_producto IN (1, 2, 3, 4) ORDER BY id_producto;
```
* **Conteo de pedidos:** Se mantuvo exactamente en **200,001 pedidos** (cero pedidos espurios creados por la tablet).
* **Stock de productos:** Muzza continuó en **5 unidades**, Napolitana en **10 unidades**, Producto 3 en **115 unidades** y Producto 4 en **130 unidades** (cero unidades descontadas).
Esto demostró empíricamente que la regla de oro se cumplió: la tablet simuló y evaluó en su entorno local, pero no alteró ni un solo dato en el servidor transaccional central.

---

## 4. Qué decisiones de diseño tomé

A lo largo de las 5 unidades tomé decisiones de diseño justificadas por criterios de ingeniería de software y administración de datos:

### 4.1 Normalización selectiva y Vistas de Compatibilidad (Unidad 4)
Al detectar la violación de FNBC en `control_lote_almacen`, la solución académica pura hubiera sido eliminar la tabla vieja y forzar a todos los programas clientes a reescribir sus queries apuntando a `responsable_control` y `control_lote_almacen_nuevo`.  
* **Mi decisión:** Apliqué el patrón de **Vista de Compatibilidad**. Mantuve la descomposición limpia en el modelo físico subyacente, pero expuse una vista con el nombre original que hace el `JOIN` automáticamente. De este modo eliminé las anomalías de actualización en la base sin generar tiempo de inactividad ni forzar refactorizaciones costosas en los sistemas clientes.

### 4.2 Cuándo desnormalizar y qué salvaguardas imponer (Unidad 4)
* **Mi decisión:** La desnormalización no debe ser la regla sino una excepción muy justificada. Solo desnormalicé la tabla `categoria_venta_dia` porque los dashboards ejecutivos generan un patrón de lectura masivo y concurrente que no varía segundo a segundo.  
* **Salvaguardas aplicadas:** Para evitar que la tabla desnormalizada quedara desfasada de la realidad transaccional, implementé dos capas de protección:
  1. Un **trigger `AFTER INSERT OR UPDATE`** sobre `pedido_producto` que recalcula el acumulado de la categoría y fecha afectada.
  2. Un **script de auditoría periódica** que compara la tabla desnormalizada contra una consulta agregada pura sobre las tablas maestras, alertando si la diferencia de filas o montos es distinta de cero.

### 4.3 Mínimo Privilegio Real y Patrón `SECURITY DEFINER` (Unidad 5)
* **Mi decisión:** Ante el problema de que `app_web` no podía autenticar usuarios, la tentación rápida era ejecutar `GRANT SELECT ON usuario TO rol_app_web;`. Descarté esa salida porque violaba el principio de mínimo privilegio: la aplicación web jamás debe tener acceso directo a las columnas de contraseñas ni a los correos de otros usuarios.  
* **Solución aplicada:** Encapsulé la autenticación en la función `fn_autenticar`, le asigné el owner `admin_datos` y la declaré como `SECURITY DEFINER`. Como salvaguarda crítica contra ataques de inyección de rutas (search-path hijacking), le fijé un esquema estricto: `ALTER FUNCTION fn_autenticar SET search_path = public, pg_temp;`. De este modo, la aplicación puede validar si un usuario ingresó la clave correcta (`autenticado = true/false`) sin poder leer ni extraer los hashes almacenados.

### 4.4 Arquitectura Híbrida CQRS en vez de sustitución tecnológica (Unidad 7)
* **Mi decisión:** En lugar de discutir si "MongoDB es mejor que PostgreSQL" o viceversa, adopté un patrón de **Separación de Responsabilidades de Consulta y Comando (CQRS)**:
  - **PostgreSQL es el Command Store (OLTP) y la Única Fuente de Verdad:** Maneja transacciones ACID estrictas, estados fiscales, control de inventario maestro y auditoría de seguridad.
  - **MongoDB es el Read Model:** Recibe una copia desnormalizada de los pedidos ya confirmados. Al tener los productos y el cliente embebidos en un único documento BSON, la tienda web puede servir consultas masivas con tiempos de respuesta de milisegundos sin sobrecargar a PostgreSQL con JOINs complejos. Si MongoDB llega a corromperse, no hay pérdida de datos: se regenera completamente a partir de PostgreSQL.

### 4.5 Arquitectura Móvil Offline-First con Tipado Estricto (Unidad 8)
Para la tablet en la feria gastronómica diseñé una arquitectura pensada para fallar con elegancia:
* **Modo `STRICT` en SQLite:** Históricamente SQLite permite guardar texto en columnas de enteros debido a su afinidad de tipos flexible. En una aplicación comercial esto es un peligro; por eso utilicé tablas `STRICT`, obligando al motor a validar tipos estáticos.
* **Precios en centavos enteros (`INT`):** Operar con tipos `REAL` o flotantes en SQLite genera errores acumulativos de redondeo binario. Al guardar `$120.50` como `12050 centavos`, las sumas y multiplicaciones son matemáticamente exactas.
* **UUIDs v4 para evitar colisiones distribuidas:** Si dos mozos toman pedidos fuera de línea en dos tablets distintas, usar números correlativos (`1, 2, 3...`) provocaría un desastre al sincronizar en el servidor. Con UUIDs v4 cada pedido nace con un identificador único en el mundo sin necesidad de coordinar con una secuencia central.
* **Límites de autoridad:** La tablet solo propone borradores locales. El estado `SIMULADO_APROBADO` le avisa al cajero que la venta es factible según la última foto del catálogo, pero la transacción fiscal definitiva y el descuento de stock solo ocurren cuando el servidor central procesa la solicitud.

---

## 5. Herramientas de IA utilizadas, bitácora y descartes fundamentales

A lo largo del proyecto utilicé herramientas de IA como aceleradores de desarrollo:
- **Kiro (Specification Engine):** Lo utilicé para estructurar los requerimientos en notación formal EARS (`WHEN ... THE SYSTEM SHALL ...`), definir documentos de diseño (`design.md`) y organizar las listas de tareas (`tasks.md`).
- **OpenCode y modelos LLM:** Los utilicé como asistentes de programación para generar esqueletos iniciales de consultas SQL, funciones PL/pgSQL y scripts de prueba.

Sin embargo, mantuve un principio inquebrantable: **la IA propone, pero el estudiante audita, valida y decide**. Jamás acepté una sugerencia sin analizar su impacto en el motor. A continuación desarrollo los cinco descartes técnicos fundamentales donde la intervención humana corrigió propuestas defectuosas de la IA:

```
[ LOS 5 DESCARTES TÉCNICOS FUNDAMENTALES A LA IA ]
├── 1. VACUUM FULL diario en mantenimiento (U6)   --> Descartado: Bloqueo ACCESS EXCLUSIVE tumba producción
├── 2. Claves AUTOINCREMENT en tablets (U8)       --> Descartado: Colisiones inevitables en entorno distribuido
├── 3. Triggers remotos por socket en SQLite (U8) --> Descartado: Congelamiento de app ante caída de red celular
├── 4. Falacia de "NoSQL no tiene ACID" (U7)      --> Refutado: MongoDB tiene ACID multi-documento desde v4.0
└── 5. SELECT masivo para solucionar login (U5)   --> Descartado: Violación de mínimo privilegio; corregido con DEFINER
```

### 5.1 Descarte 1 (Unidad 6): `VACUUM FULL` diario en scripts de mantenimiento
* **Lo que propuso la IA:** La IA sugirió incorporar `VACUUM FULL ANALYZE` en el script diario de mantenimiento para "recuperar espacio en disco y desfragmentar completamente las tablas".
* **Mi análisis y descarte técnico:** Descarté la propuesta de plano. Al consultar la documentación de PostgreSQL y monitorear el catálogo `pg_locks`, comprobé que `VACUUM FULL` reescribe físicamente toda la tabla en disco y para ello adquiere un bloqueo exclusivo absoluto (**`ACCESS EXCLUSIVE LOCK`**). Este bloqueo impide cualquier operación de lectura (`SELECT`) y escritura (`INSERT`/`UPDATE`). En un sistema en producción como Food Store, ejecutar `VACUUM FULL` en horario operativo dejaría la tienda web y las cajas caídas durante minutos.
* **Corrección aplicada:** Mantuve el mantenimiento estándar concurrente con `VACUUM (ANALYZE, VERBOSE)`, que limpia tuplas muertas y recalcula estadísticas sin interrumpir las transacciones concurrentes de los usuarios.

### 5.2 Descarte 2 (Unidad 8): Claves autonuméricas en la base SQLite de la tablet
* **Lo que propuso la IA:** La IA propuso diseñar las tablas `pedido_borrador` y `cola_sync` con claves primarias enteras tradicionales: `id INTEGER PRIMARY KEY AUTOINCREMENT`.
* **Mi análisis y descarte técnico:** Descarté la propuesta de inmediato. En una arquitectura distribuida donde varias tablets operan fuera de línea de forma autónoma en una feria, si la Tablet A genera los pedidos 1, 2 y 3 y la Tablet B genera en paralelo los pedidos 1, 2 y 3, al reconectarse con el servidor se produce una colisión de claves insalvable.
* **Corrección aplicada:** Sustituí los enteros por identificadores universales **UUID v4** en formato texto (`TEXT PRIMARY KEY`), garantizando unicidad global sin requerir coordinación previa.

### 5.3 Descarte 3 (Unidad 8): Triggers en SQLite para actualizar stock en PostgreSQL
* **Lo que propuso la IA:** La IA sugirió crear un trigger `AFTER INSERT ON item_borrador` en SQLite que abriera un socket o intentara llamar a un servicio remoto para "reservar" el stock en PostgreSQL en tiempo real.
* **Mi análisis y descarte técnico:** Descarté la idea por violar los principios básicos del diseño Offline-First. En una feria donde la señal de celular es débil o nula, un trigger que intente sincronizar sincrónicamente congelaría la tablet esperando un timeout de red, impidiendo que el mozo pudiera seguir cobrando. Además, darle a la tablet credenciales de escritura directa sobre la base central viola todas las pautas de seguridad física.
* **Corrección aplicada:** La tablet opera 100% aislada contra su caché local y la conciliación se realiza de forma asíncrona mediante el semáforo sobre el snapshot descargado.

### 5.4 Descarte 4 (Unidad 7): La falacia de que "MongoDB no soporta transacciones ACID"
* **Lo que propuso la IA:** En el análisis comparativo, la IA repitió el cliché común de que "PostgreSQL debe elegirse porque MongoDB no tiene soporte para transacciones ACID".
* **Mi análisis y refutación técnica:** Refuté técnicamente la afirmación. Desde la versión 4.0 (lanzada en 2018), MongoDB soporta transacciones multi-documento distribuidas con semántica ACID completa (con `session.startTransaction()`, `commitTransaction()` y `abortTransaction()`). Además, en nuestro diseño documental donde las líneas de pedido están embebidas dentro del documento del pedido, la atomicidad está garantizada de forma nativa a nivel de documento único sin necesidad de transacciones distribuidas ni penalizaciones de rendimiento.
* **Conclusión real:** La verdadera razón para mantener PostgreSQL en el backend no es la falta de ACID en MongoDB, sino que el modelo de datos maestro del negocio (clientes, categorías, productos, seguridad, facturación fiscal) es inherentemente relacional y requiere integridad referencial rígida por foreign keys.

### 5.5 Descarte 5 (Unidad 5): Conceder permisos de lectura directa para solucionar el login
* **Lo que propuso la IA:** Cuando `fn_autenticar` falló con permiso denegado, la IA sugirió ejecutar `GRANT SELECT ON usuario TO rol_app_web;`.
* **Mi análisis y descarte técnico:** Rechacé la propuesta porque rompía el principio de mínimo privilegio. Otorgarle SELECT a la aplicación web sobre toda la tabla expone los hashes de contraseñas ante posibles ataques de inyección SQL.
* **Corrección aplicada:** Convertí la función a `SECURITY DEFINER`, blindé su `search_path` y mantuve a la aplicación web completamente aislada de la tabla `usuario`.

---

## 6. Conclusión Final y Aprendizajes del Proyecto

El desarrollo integral de este proyecto integrador a lo largo de las 8 unidades representó un salto cualitativo en mi formación como programador. Dejé de ver a la base de datos como un simple repositorio de tablas para entenderla como un **ecosistema distribuido, vivo y de misión crítica**.

Los aprendizajes más importantes que me llevo son:
1. **El rendimiento se diseña, no se adivina:** Aprendí a no crear índices "por las dudas", sino a interpretar los costos reales en `EXPLAIN ANALYZE`, entendiendo cuándo conviene una tabla desnormalizada protegida con triggers y cuándo alcanza con un buen índice compuesto.
2. **La seguridad empieza en el motor:** Entendí que la seguridad no es un middleware en el backend, sino una política estricta de mínimo privilegio en el motor de base de datos, con roles bien segmentados, permisos a nivel de columna y funciones `SECURITY DEFINER` con search-paths protegidos.
3. **Un backup no probado es un backup inexistente:** La experiencia de la Unidad 6 me enseñó que la continuidad del negocio depende de poder restaurar contra reloj. Lograr un RTO de 4.84 segundos y un RPO de 1.70 minutos me dio la tranquilidad de que el plan de contingencia es real y medible.
4. **La arquitectura políglota es complementaria, no competitiva:** Comprendí que no existe el motor perfecto para todo: PostgreSQL brilla en la consistencia transaccional y la integridad referencial; MongoDB destaca en la velocidad de lectura de documentos desnormalizados para e-commerce; y SQLite es el rey indiscutido del borde embebido para dispositivos móviles fuera de línea.
5. **Criterio profesional frente a la Inteligencia Artificial:** La IA es una herramienta fenomenal para acelerar tareas repetitivas, pero carece de la visión de conjunto y del criterio de seguridad que exige un sistema en producción. Como futuro técnico en programación, mi mayor valor no está en escribir código rápido, sino en saber auditarlo, entender cómo impacta en el hardware y en el negocio, y tener los fundamentos técnicos para defender cada decisión en la práctica.
