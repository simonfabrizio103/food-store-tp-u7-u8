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
  *Carpetas del proyecto:* `facultad/food-store-tp-unidad4/`, `facultad/food-store-tp-u5/`, `facultad/food-store-tp-u6/` (Rama `master`, commit final: `202aecb`).
* **Repositorio Parte 2 (Unidades 7 y 8):**  
  [`https://github.com/simonfabrizio103/food-store-tp-u7-u8`](https://github.com/simonfabrizio103/food-store-tp-u7-u8)  
  *Carpetas del proyecto:* `tp-unidad-7/`, `tp-unidad-8/` (Rama `main`, etiquetas oficiales: `tp8` y `tpi-entrega2`).

---

## Introducción y Enfoque Personal

Cuando me senté a encarar esta segunda entrega del Trabajo Práctico Integrador de Food Store, me quedó clarísimo que no se trataba de un trabajo práctico más donde tirás cuatro consultas para que devuelvan filas y pasás de largo. Acá el desafío era agarrar todo lo visto en la materia y hacer convivir un esquema que arrancó en un motor relacional tradicional como PostgreSQL, llevarlo al límite con optimización física, blindarlo con políticas de seguridad reales, someterlo a pruebas de desastre contra reloj, extenderlo hacia una base documental con MongoDB y, como frutilla del postre, resolver la operatoria de un food truck vendiendo en una feria sin un gramo de señal de Internet usando SQLite en una tablet.

A lo largo de estas semanas me di cuenta de que una base de datos en el mundo real no es una entidad estática ni un simple depósito de tablas: es un sistema vivo, sometido a bloqueos, cuellos de botella de CPU, caídas de tensión, ataques de inyección y fallas de conectividad. Si uno diseña pensando que "la red nunca se cae", que "el disco es infinito" o que "todos los usuarios son de confianza", el sistema explota en el primer día de producción.

En este camino me apoyé en herramientas de Inteligencia Artificial (Kiro para las especificaciones formales en notación EARS, OpenCode y modelos LLM para prototipar estructuras rápido), pero siempre con una regla de oro que me fijé desde el día uno: **la IA te tira código, pero el que pone la cara y el que firma la arquitectura soy yo**. Cada sentencia SQL, cada script de PowerShell y cada modelo documental que entró en mis repositorios lo leí de punta a punta, lo ejecuté en mi máquina, medí su impacto en el motor y, cuando la IA me tiró sugerencias disparatadas (como meter un `VACUUM FULL` en caliente a diario o poner autonuméricos en dispositivos móviles desconectados), las frené en seco, las descarté y las corregí con fundamentos técnicos de ingeniería.

A continuación presento el desarrollo detallado, unidad por unidad, respondiendo exhaustivamente a los 5 ejes requeridos por la cátedra.

---

## 1. Unidad 4 · Normalización avanzada y redundancia controlada

### 1.1 El problema en el esquema heredado y la violación de FNBC
En la primera parte de esta entrega me encontré con un esquema heredado para la gestión de almacenes y auditoría de lotes de alimentos en Food Store. Al analizar la tabla `control_lote_almacen`, noté de inmediato que presentaba serios problemas de redundancia y anomalías de actualización.

Haciendo el relevamiento de las dependencias funcionales del negocio identifiqué lo siguiente:
* La clave primaria compuesta de la tabla era `(LoteID, ResponsableControlID)`.
* Sin embargo, existía una dependencia funcional oculta y no trivial:  
  $$\text{ResponsableControlID} \longrightarrow \text{DepositoID}$$
  Esto significaba que cada responsable de control pertenecía de manera fija a un depósito determinado de la empresa.

**¿Por qué violaba la Forma Normal de Boyce-Codd (FNBC)?**  
La regla de FNBC es estricta: para toda dependencia funcional no trivial $X \rightarrow Y$, el determinante $X$ **debe ser una superclave** de la relación. En este caso, `ResponsableControlID` por sí solo no era superclave (ya que se necesitaban ambos atributos para identificar el registro). 

Esto provocaba las tres anomalías clásicas de los esquemas mal normalizados:
1. **Redundancia innecesaria:** Si el responsable García controlaba 500 lotes en el Depósito Central, el `DepositoID = 1` se repetía 500 veces en la tabla.
2. **Anomalía de modificación:** Si García era trasladado al Depósito Norte, había que hacer un `UPDATE` masivo sobre cientos de filas. Si una sola fila fallaba, la base quedaba en un estado inconsistente donde García parecía estar en dos depósitos a la vez.
3. **Anomalía de inserción:** No se podía dar de alta a un nuevo empleado auditor y asignarle su depósito hasta que no auditara físicamente su primer lote.

### 1.2 La solución: Descomposición sin pérdida y Vista de Compatibilidad
Para solucionar esto de raíz sin perder información, apliqué el teorema de descomposición en dos relaciones normalizadas:
1. `responsable_control (ResponsableControlID PK, DepositoID, NombreResponsable)`: aquí el determinante es clave primaria pura. Cumple FNBC.
2. `control_lote_almacen_nuevo (LoteID, ResponsableControlID, FechaControl, Estado, CantidadAuditada)`: donde `ResponsableControlID` actúa como foreign key apuntando a la tabla anterior.

Pero acá me topé con un dilema real de la industria: **¿qué pasa con todos los reportes, sistemas viejos y consultas que ya estaban programadas contra la tabla original `control_lote_almacen`?** Si yo simplemente borraba la tabla vieja, rompía todo el sistema. 

Mi decisión fue implementar el patrón de **Vista de Compatibilidad**:
```sql
CREATE OR REPLACE VIEW control_lote_almacen AS
SELECT 
    cla.LoteID,
    cla.ResponsableControlID,
    rc.DepositoID,
    cla.FechaControl,
    cla.Estado,
    cla.CantidadAuditada
FROM control_lote_almacen_nuevo cla
JOIN responsable_control rc ON cla.ResponsableControlID = rc.ResponsableControlID;
```
Con este enfoque logré lo mejor de los dos mundos: normalicé la base eliminando la redundancia en el almacenamiento físico, y al mismo tiempo dejé una interfaz idéntica hacia el exterior para que ningún sistema cliente se enterara del cambio ni tuviera que reescribir sus queries.

### 1.3 Desnormalización controlada para el Dashboard (`categoria_venta_dia`)
En la segunda parte de la Unidad 4 se nos planteó el problema de la consulta gerencial: el dashboard de Food Store necesita mostrar en tiempo real las **Top 5 categorías más vendidas por día**.

Hice la prueba de correr la consulta de agregación clásica sobre las tablas relacionales puras:
```sql
SELECT c.nombre, DATE(p.fecha), SUM(pp.cantidad * pp.precio_unitario) AS total
FROM pedido p
JOIN pedido_producto pp ON p.id_pedido = pp.id_pedido
JOIN producto pr ON pp.id_producto = pr.id_producto
JOIN categoria c ON pr.id_categoria = c.id_categoria
GROUP BY c.nombre, DATE(p.fecha)
ORDER BY total DESC LIMIT 5;
```
Al analizar el plan de ejecución con `EXPLAIN ANALYZE`, el motor tenía que hacer un `Seq Scan` recorriendo cientos de miles de registros de `pedido_producto`, hacer múltiples hash joins y ordenar en memoria, consumiendo **0.123 milisegundos por ejecución**. En una empresa donde entran miles de peticiones simultáneas de directivos y supervisores, esa consulta repetitiva ahogaba la CPU del servidor.

**Mi decisión de diseño:** Desnormalizar de forma controlada creando una tabla dedicada llamada `categoria_venta_dia (fecha DATE, id_categoria INT, nombre_categoria VARCHAR, total_vendido NUMERIC, cantidad_pedidos INT, PRIMARY KEY(fecha, id_categoria))`.

**Las dos salvaguardas que apliqué:**
Desnormalizar sin control es una invitación al desastre. Para asegurar la coherencia de los datos implementé dos mecanismos:
1. **Trigger de sincronización automática:** Creé un trigger `AFTER INSERT OR UPDATE ON pedido_producto` que recalcula y actualiza automáticamente los acumulados de la fila correspondiente en `categoria_venta_dia`.
2. **Script de auditoría periódica:** Diseñé una consulta de control que compara diariamente los datos de la tabla desnormalizada contra la agregación relacional pura. Si la resta da distinto de cero, el sistema dispara una alerta de desincronización. En mis pruebas de validación, la auditoría reportó **0 tuplas desfasadas**.

**El resultado medido:**  
La consulta sobre la tabla desnormalizada con índice compuesto `(fecha, total_vendido DESC)` pasó a ejecutarse mediante un `Bitmap Heap Scan` en tan solo **0.077 milisegundos**, lo que representó una **mejora del 37.4% en tiempo de respuesta de CPU**.

---

## 2. Unidad 5 · Administración, seguridad y laboratorio forense

### 2.1 Modelo RBAC y Principio de Mínimo Privilegio
En la Unidad 5 me tocó encarar la seguridad. Lo primero que hice fue descartar la mala costumbre de conectar los sistemas con el usuario `postgres` o con superusuarios. Diseñé en Kiro una arquitectura RBAC (Role-Based Access Control) bien segmentada en dos niveles:

1. **Roles de grupo (sin login, puramente para herencia de permisos):**
   * `rol_admin_datos`: Control total de DDL y DML sobre el esquema `public`.
   * `rol_app_web`: El rol que usa la tienda online; solo puede consultar catálogo, insertar pedidos y autenticar.
   * `rol_cajero`: Permisos para facturación en local físico.
   * `rol_auditor`: Rol de solo lectura sobre vistas del sistema y catálogos de auditoría.
2. **Usuarios de conexión (con login y contraseñas robustas):**
   * `admin_datos`: Asignado al grupo `rol_admin_datos`.
   * `app_web`: Asignado al grupo `rol_app_web`.

Para blindar la privacidad apliqué **seguridad a nivel de columna (Column-Level Security)**:
```sql
-- La aplicación web solo puede ver los datos mínimos del usuario, jamás su password ni datos confidenciales
GRANT SELECT (id_usuario, nombre, activo) ON usuario TO rol_app_web;
```
Además, para evitar sorpresas a futuro, configuré `ALTER DEFAULT PRIVILEGES IN SCHEMA public ...` de modo que cualquier tabla nueva creada por el administrador nazca bloqueada para los roles públicos por defecto.

### 2.2 Auditoría nativa y el Simulacro de Incidente
Para poder auditar qué pasa en la base, configuré en `postgresql.auto.conf`:
```text
log_connections = on
log_disconnections = on
log_statement = 'all'
```
Luego ejecuté un simulacro de ataque (`sql/simulacro_incidente.sql`) simulando que un atacante lograba vulnerar la aplicación web y ejecutaba comandos desde la sesión `app_web`:
* Intentó cambiar su rol a administrador: `SET ROLE admin_datos;` &rarr; **Rechazado (`permission denied`)**.
* Intentó crear un usuario con privilegios: `CREATE ROLE hacker WITH LOGIN;` &rarr; **Rechazado (`permission denied`)**.
* Intentó hacer un dump de correos electrónicos: `SELECT email FROM usuario;` &rarr; **Rechazado (`permission denied for table usuario`)**.

### 2.3 El Hallazgo Crítico H-1 y la Solución con `SECURITY DEFINER`
Durante este simulacro me topé con un problema gravísimo que casi nadie ve a simple vista: **la aplicación web no podía autenticar a nadie**. 

Al ejecutar el login:
```sql
SELECT fn_autenticar('cliente@foodstore.com', 'clave123');
```
PostgreSQL tiraba el error: `ERROR: permission denied for table usuario`.  
**¿Por qué pasaba esto?** Porque la función `fn_autenticar` había sido creada como `SECURITY INVOKER`. Esto significa que la función corre con los permisos del usuario que la llama. Como yo le había quitado a `app_web` el permiso de `SELECT` sobre la tabla `usuario` (para proteger los hashes de contraseñas), cuando la función intentaba verificar la clave, el motor la bloqueaba.

**La tentación:** La solución rápida y descuidada hubiera sido darle `GRANT SELECT ON usuario TO rol_app_web;`. Pero eso tiraba a la basura todo el mínimo privilegio.  
**Mi solución de ingeniería:** Modifiqué la función para que opere como `SECURITY DEFINER`, asignándole la propiedad a `admin_datos` y blindándole el `search_path`:
```sql
ALTER FUNCTION fn_autenticar(text, text) OWNER TO admin_datos;
ALTER FUNCTION fn_autenticar(text, text) SECURITY DEFINER;
ALTER FUNCTION fn_autenticar(text, text) SET search_path = public, pg_temp;
```
Con esto logré que la función se ejecute con los permisos de su dueño (`admin_datos`), verifique la clave internamente y le devuelva a la aplicación web únicamente un booleano (`true` o `false`). La aplicación puede autenticar a los clientes pero sigue estando totalmente ciega ante los datos sensibles de la tabla.

### 2.4 Anonimización de datos (PII) y Hallazgo H-2
Al revisar el archivo de log crudo con `log_statement = 'all'`, descubrí el **Hallazgo H-2**: el motor registraba en texto plano los parámetros de la función de autenticación, es decir, las contraseñas reales tipeadas por los usuarios. 

Para remediar esto antes de cualquier análisis externo o uso con IA:
1. Programé en Python `sql/anonimizar_log.py`, que procesa las líneas del log y sustituye con expresiones regulares direcciones IP, puertos, correos y contraseñas por tokens hash.
2. Diseñé la tabla `usuario_anon` (`sql/usuario_anon.sql`) para compartir datos de testing sin filtrar datos personales (PII): enmascaré los emails con un hash determinista con sal (`md5(id || 'sal_secreta') || '@anon.example'`), eliminé los hashes de contraseñas y conservé los identificadores numéricos `id_usuario`. En `verificacion_equivalencia.md` comprobé que la tabla anonimizada mantuvo una **equivalencia estadística del 100%** con la original en cantidad de usuarios (6), roles y volumen de pedidos acumulados.

---

## 3. Unidad 6 · Mantenimiento, backup y simulación de desastre

### 3.1 Mantenimiento preventivo en PostgreSQL (`maintenance.sql`)
En la Unidad 6 me enfoqué en la salud del motor. Una base de datos que procesa 200,000 pedidos genera miles de tuplas muertas por día debido a la arquitectura MVCC de PostgreSQL. 

Diseñé un script de mantenimiento con tres pilares:
1. **`VACUUM (ANALYZE, VERBOSE)`:** Limpia las tuplas muertas de las tablas transaccionales (`pedido`, `pedido_producto`) y actualiza el mapa de espacio libre (`FSM`), permitiendo que el motor reutilice los bloques de disco sin inflar el tamaño físico del archivo.
2. **`REINDEX TABLE CONCURRENTLY`:** A medida que se insertan y borran registros, los árboles B-Tree de los índices se desbalancean y fragmentan (el famoso "bloat"). Al reindexar de forma concurrente, el motor crea un índice nuevo en paralelo y reemplaza al viejo sin bloquear las consultas de los usuarios.
3. **Actualización de estadísticas (`ANALYZE`):** Obliga al optimizador a refrescar las muestras de frecuencia y distribución de valores en `pg_statistic`, evitando que el planificador tome malas decisiones como elegir un sequential scan en vez de un index scan.

### 3.2 Automatización de respaldos en PowerShell (`backup_foodstore.ps1`)
Desarrollé un script en PowerShell para automatizar los backups diarios con criterios profesionales:
* Verifica mediante `Get-Service postgresql*` que el servicio esté activo.
* Chequea con `Get-PSDrive` que el disco tenga al menos 500 MB libres para no saturar la máquina.
* Lanza `pg_dump.exe -U postgres -F c -b -v -f <archivo.dump>`, utilizando el formato custom comprimido con zlib (`-Fc`), que es mucho más rápido y permite restauración paralela y selectiva.
* Verifica que el archivo generado exista y tenga peso mayor a 0 bytes.
* Aplica una política de rotación eliminando automáticamente respaldos con más de 7 días de antigüedad.

### 3.3 Simulacro de desastre contra reloj: Medición de RTO y RPO
Para probar si nuestro plan de contingencia servía en la vida real, programé `restore_test.ps1` para simular una caída catastrófica del servidor:
1. El script tomó el último respaldo generado (`foodstore_20261110_155502.dump`, de 11.2 MB comprimido, correspondiente a una base de 96 MB sin comprimir).
2. Levantó una base efímera llamada `foodstore_restore_test`.
3. Inició un cronómetro de alta resolución con `[System.Diagnostics.Stopwatch]::StartNew()`.
4. Ejecutó `pg_restore.exe --no-owner --role=postgres -d foodstore_restore_test`.
5. Detuvo el cronómetro y lanzó `validate_restore.sql` para chequear integridad.

```
[ RESULTADOS DEL SIMULACRO DE DESASTRE ]
• Tamaño de la base de datos en disco: 96 MB
• Cantidad de pedidos recuperados: 200,001
• Cantidad de productos recuperados: 50,002
• Tiempo de Recuperación (RTO Medido): 4.84 segundos
• Objetivo de Negocio fijado (SLA RTO): Menor a 15 minutos (CUMPLIDO CON CRECES)
• Punto de Recuperación (RPO Calculado): 1.70 minutos
• Límite Máximo Tolerable (SLA RPO): Menor a 1 hora (CUMPLIDO CON CRECES)
• Integridad referencial: 0 claves foráneas rotas o tuplas huérfanas
```

Este resultado me demostró que el procedimiento es totalmente repetible y confiable ante un corte de luz o fallo del servidor.

---

## 4. Unidad 7 · NoSQL y nuevas formas de almacenamiento (MongoDB)

### 4.1 Rompiendo el molde relacional: Diseño documental de `pedidos`
En la Unidad 7 nos tocó incorporar MongoDB. Lo primero que entendí fue que **migrar a NoSQL no es agarrar las tablas de PostgreSQL y convertirlas una a una en colecciones de MongoDB con referencias**. Si hacía eso, iba a terminar necesitando hacer `$lookup` (el equivalente al JOIN de SQL) para todo, perdiendo la principal ventaja que tiene una base documental.

Modelé la colección `pedidos` pensando en el concepto de **Agregado (DDD)**:
```javascript
{
  "_id": 2,
  "fecha": ISODate("2026-11-10T12:00:00Z"),
  "estado": "ENTREGADO",
  "cliente": {
    "id_cliente": 201,
    "nombre": "Ana Gómez",
    "email": "ana@example.com"
  },
  "lineas": [
    { "producto_id": 1, "nombre": "Muzza", "cantidad": 2, "precio_unitario": 100.00 },
    { "producto_id": 2, "nombre": "Napolitana", "cantidad": 1, "precio_unitario": 120.00 }
  ],
  "total": 320.00
}
```

**¿Por qué este diseño?**
1. **Precio histórico congelado:** Al embeber las líneas con su `precio_unitario` al momento de la compra, me aseguro de que si mañana la Muzza sube a $150 en el catálogo maestro, el pedido histórico de Ana sigue valiendo $320.00.
2. **Lectura atómica sin JOINs:** Para mostrar el detalle del pedido en la pantalla del celular del cliente, la aplicación web hace una sola lectura sobre un único documento (`db.pedidos.findOne({ _id: 2 })`) y tiene toda la información junta (fecha, estado, cliente, productos, precios y total) en un solo viaje al disco.

### 4.2 Las 4 consultas analíticas y la validación cruzada con PostgreSQL
Desarrollé en `consultas_mongodb.js` cuatro consultas analíticas y luego escribí sus equivalentes exactas en SQL en `consultas_postgresql.sql`:
* **Consulta 4.a (Pedidos por estado):** Buscar órdenes con `estado = 'ENTREGADO'`.
  - MongoDB: `db.pedidos.find({ estado: "ENTREGADO" })` &rarr; Retornó 3 pedidos (IDs 2, 4 y 7).
  - PostgreSQL: `SELECT id_pedido FROM pedido WHERE estado = 'ENTREGADO'` &rarr; Retornó los mismos 3 pedidos (IDs 2, 4 y 7).
* **Consulta 4.b (Filtro en subdocumentos):** Pedidos que contienen el Producto ID = 3 en sus líneas.
  - MongoDB: `db.pedidos.find({ "lineas.producto_id": 3 })` &rarr; Retornó 3 pedidos (IDs 2, 4 y 6).
  - PostgreSQL: `SELECT DISTINCT id_pedido FROM pedido_producto WHERE id_producto = 3` &rarr; Retornó los mismos 3 pedidos (IDs 2, 4 y 6).
* **Consulta 4.c (Filtro por agregación de total):** Pedidos con total mayor a $2000.00.
  - Ambos motores retornaron exactamente 2 pedidos: el ID 4 (por $2050.00) y el ID 6 (por $3500.00).
* **Consulta 4.d (Agrupación con `$unwind` y `$group`):** Cálculo de ventas acumuladas por producto.

La coincidencia fue del **100% exacto**, demostrando que ambos modelos son semánticamente equivalentes.

### 4.3 La Decisión Arquitectónica: Enfoque Híbrido CQRS
Al momento de comparar los motores, no caí en la postura simplista de decir "uno es mejor que el otro". La decisión madura de diseño fue adoptar una **arquitectura híbrida CQRS (Command Query Responsibility Segregation)**:
* **PostgreSQL es el Core Transaccional (OLTP):** Es la Única Fuente de Verdad. Manda sobre el catálogo oficial, precios maestros, control rígido de stock, usuarios, contraseñas y facturación fiscal.
* **MongoDB es el Read Model:** Recibe una copia de los pedidos confirmados para que la aplicación móvil y la tienda web atiendan miles de consultas concurrentes a máxima velocidad sin sobrecargar a PostgreSQL con JOINs pesados. Si MongoDB se cae o se corrompe, se reconstruye desde PostgreSQL sin perder un solo peso.

---

## 5. Unidad 8 · Bases de datos móviles e integración (SQLite)

### 5.1 El escenario del Food Truck en la feria: Venta Offline-First
La Unidad 8 nos puso en el escenario más realista de todos: un food truck de Food Store que va a vender hamburguesas y pizzas a una feria gastronómica en un predio al aire libre donde no hay señal de celular ni WiFi. El cajero tiene una tablet y tiene que poder cobrar y emitir pedidos sin conexión.

Para resolver esto diseñé en SQLite (`schema_sqlite.sql`) un esquema móvil pensado para no fallar:
1. **`PRAGMA foreign_keys = ON;`:** SQLite por defecto tiene las claves foráneas apagadas por compatibilidad histórica; activarlas al inicio fue mandatorio.
2. **Modo `STRICT` en las 4 tablas:** Forcé tipado estricto (`CREATE TABLE ... STRICT;`). Esto impide que alguien meta accidentalmente un string en un campo de stock o un número decimal en una clave.
3. **Precios en centavos enteros (`INT`):** Para evitar los desastres de redondeo de punto flotante de los tipos `REAL` en dispositivos embebidos, todos los importes se manejan como centavos enteros (`$120.50` = `12050 centavos`).
4. **Identificadores UUID v4 (`TEXT PRIMARY KEY`):** Como varias tablets operan en simultáneo fuera de línea, usar secuencias autonuméricas (`1, 2, 3...`) provocaría colisiones seguras al sincronizar. Con UUID v4 cada borrador nace con un identificador único a nivel global.

### 5.2 El Semáforo de Sincronización y la Regla de Oro
El núcleo de la unidad fue el algoritmo del semáforo (`semaforo.sql`). Cuando la tablet recupera conectividad o descarga una instantánea del servidor (`snapshot_servidor`), corre una consulta de conciliación con CTE y `UPDATE ... FROM`:
* **Rojo (`RECHAZADO`):** Si un producto no existe en el servidor, si fue dado de baja lógica (`eliminado = 't'`), si está inactivo (`disponible = 'f'`) o si la cantidad pedida en la feria supera el stock físico real que queda en el servidor.
* **Amarillo (`CONFLICTO`):** Si hay stock y disponibilidad pero el precio cambió en el servidor respecto al precio que la tablet tenía guardado en su catálogo offline. Le permite al mozo negociar con el cliente en el momento: "el producto subió $25; ¿lo acepta?".
* **Verde (`SIMULADO_APROBADO`):** Si precio, stock y vigencia coinciden al 100%.

**La Regla de Oro:** *"El móvil propone, el servidor dispone"*.  
La tablet jamás descuenta stock ni confirma ventas fiscales. El estado `SIMULADO_APROBADO` es una pre-validación teórica.

### 5.3 Simulación de Casos C1 a C7 y Verificación en PostgreSQL
Mediante mi script `simulador.py` probé los 7 casos requeridos:
* **C1:** Consulta offline de catálogo activo (`WHERE disponible = 1 AND eliminado = 0 AND stock_visto > 0`).
* **C7:** Intento de insertar ítem con cantidad = 0 y producto inexistente (ambos rechazados por restricciones `CHECK` y `FOREIGN KEY`).
* **C2:** Subida de precio en servidor &rarr; `CONFLICTO`; cliente acepta, se actualiza el borrador local y reintenta &rarr; `SIMULADO_APROBADO`.
* **C3:** Se piden 50 Napolitanas cuando en el servidor quedan 10 &rarr; `RECHAZADO` (stock insuficiente).
* **C4:** Baja lógica de producto en servidor &rarr; `RECHAZADO`. Al actualizar el catálogo de la tablet, la fila permanece en la base por integridad histórica pero desaparece de la pantalla de ventas.
* **C5:** Pedido limpio coincidente &rarr; `SIMULADO_APROBADO`.
* **C6:** Reenvío de solicitud con el mismo UUID &rarr; SQLite rechaza la duplicación por `PRIMARY KEY` y el semáforo ignora la reevaluación por no estar en estado `PENDIENTE`.

Al finalizar toda la simulación, corrí la auditoría sobre la base central de PostgreSQL:
* `SELECT COUNT(*) FROM pedido;` &rarr; **200,001 pedidos** (exactamente los mismos iniciales; cero ventas insertadas por la tablet).
* `SELECT stock FROM producto WHERE id_producto IN (1, 2, 3, 4);` &rarr; **5, 10, 115 y 130 unidades** (cero unidades descontadas).
La regla de oro quedó demostrada empíricamente.

---

## 6. Revisión Crítica de Inteligencia Artificial y los 5 Descartes Técnicos

A lo largo de todo el trabajo utilicé herramientas de IA (Kiro para la especificación formal de requisitos EARS y OpenCode/LLMs para generación de borradores de código). Sin embargo, mantuve un rol activo de **auditoría y control de calidad**. A continuación expongo los cinco descartes técnicos fundamentales donde la intervención humana corrigió propuestas erróneas o peligrosas de la IA:

```
+-------------------------------------------------------------------------------------------------------+
|                                  MATRIZ DE DESCARTE TÉCNICO A LA IA                                   |
+----+--------+--------------------+-----------------------------------+--------------------------------+
| ID | Unidad | Componente         | Propuesta de la IA                | Decisión y Motivo de Rechazo   |
+----+--------+--------------------+-----------------------------------+--------------------------------+
| 1  | U6     | Mantenimiento SQL  | VACUUM FULL diario en caliente    | RECHAZADO: Lock exclusivo tumba|
|    |        |                    |                                   | producción y paraliza ventas   |
| 2  | U8     | SQLite Móvil       | INTEGER PRIMARY KEY AUTOINCREMENT | RECHAZADO: Colisión masiva de  |
|    |        |                    |                                   | IDs entre tablets sin señal    |
| 3  | U8     | Sincronización     | Triggers remotos por socket       | RECHAZADO: Congela la tablet si|
|    |        |                    |                                   | no hay 4G; rompe Offline-First |
| 4  | U7     | Análisis NoSQL     | Afirmar que MongoDB no tiene ACID | REFUTADO: Soporta ACID multi-  |
|    |        |                    |                                   | doc desde v4.0 y nativo en doc |
| 5  | U5     | Seguridad Login    | GRANT SELECT ON usuario a app_web | RECHAZADO: Expone contraseñas; |
|    |        |                    |                                   | se resolvió con SECURITY DEF.  |
+----+--------+--------------------+-----------------------------------+--------------------------------+
```

### Detalle de los 5 Descartes:
1. **Descarte de `VACUUM FULL` diario (Unidad 6):**  
   La IA recomendó meter `VACUUM FULL` en el script diario para "desfragmentar el disco". Lo rechacé porque `VACUUM FULL` reescribe la tabla adquiriendo un **`ACCESS EXCLUSIVE LOCK`**, bloqueando todas las lecturas y escrituras. En una base con 200,000 pedidos, dejaría a toda la empresa sin sistema durante minutos. Mantuve `VACUUM (ANALYZE, VERBOSE)` concurrente.
2. **Descarte de claves autonuméricas en la tablet (Unidad 8):**  
   La IA propuso `AUTOINCREMENT` en SQLite. Lo descarté porque si tres tablets venden sin conexión, las tres van a generar el pedido con `id = 1`, provocando una colisión fatal al volver a la base central. Impuse **UUID v4**.
3. **Descarte de triggers móviles remotos (Unidad 8):**  
   La IA sugirió que un trigger en SQLite intente pegarle a la API central para descontar stock en el momento. Lo rechacé porque si el food truck está en un pozo sin señal en la feria, la tablet se congelaría esperando el timeout de red, impidiendo cobrar. La sincronización debe ser asíncrona mediante el semáforo.
4. **Refutación de la falacia sobre transacciones ACID en NoSQL (Unidad 7):**  
   La IA repitió el mito de que MongoDB no soporta ACID. Lo refuté demostrando que desde MongoDB 4.0 existen transacciones ACID multi-documento distribuidas, y que además, al embeber las líneas dentro del pedido, la atomicidad es nativa a nivel de documento sin ningún costo de coordinación.
5. **Rechazo a otorgar permisos masivos sobre `usuario` (Unidad 5):**  
   Ante el fallo de `fn_autenticar`, la IA propuso darle `SELECT` a la app sobre toda la tabla `usuario`. Lo rechacé de plano porque exponía los hashes de contraseñas de todos los clientes. Lo solucioné como corresponde en ingeniería: cambiando la función a `SECURITY DEFINER` con search-path seguro.

---

## 7. Conclusión Final y Aprendizajes de Carrera

Haber completado este proyecto integrador a lo largo de las 8 unidades cambió totalmente mi perspectiva sobre lo que significa trabajar con bases de datos. 

Cuando uno recién arranca a programar, piensa que una base de datos es simplemente tirar un `CREATE TABLE`, meter un par de `INSERT` y hacer andar una aplicación. Hoy me doy cuenta de que la base de datos es el corazón de cualquier negocio: si la base se bloquea, la empresa no factura; si la base pierde datos por un desastre y no tiene backups probados, la empresa quiebra; y si la base expone datos por una mala política de permisos, la empresa enfrenta problemas legales gravísimos.

Me llevo aprendizajes concretos que voy a aplicar durante toda mi carrera profesional:
* **Entender los planes del motor:** No basta con que una consulta devuelva lo que pedís; hay que mirar el `EXPLAIN ANALYZE`, ver qué tipo de scan está haciendo y evaluar si conviene un índice parcial, una desnormalización controlada con triggers o una vista materializada.
* **Seguridad por diseño:** El principio de mínimo privilegio no es opcional. Las aplicaciones no deben tener superpoderes en la base de datos; las operaciones sensibles deben aislarse en funciones `SECURITY DEFINER` blindadas contra inyecciones de path.
* **Cultura de contingencia:** Un backup que nunca se restauró es una ilusión. Haber medido un RTO de 4.84 segundos cronometrado con PowerShell me dio la certeza de que el sistema puede levantarse de las cenizas ante un desastre.
* **El valor de la arquitectura políglota:** No hay que casarse con una sola tecnología. PostgreSQL para la consistencia transaccional y la auditoría fiscal, MongoDB para lecturas desnormalizadas masivas a milisegundos, y SQLite para el borde móvil desconectado forman un ecosistema indestructible si se respetan los límites de autoridad de cada motor.
* **Criterio propio ante la Inteligencia Artificial:** La IA es un copiloto espectacular para ahorrar tiempo y tipear menos, pero el piloto soy yo. El verdadero valor de un técnico superior en programación radica en tener el conocimiento teórico y práctico para auditar cada sugerencia, entender los bloqueos en el hardware y defender con orgullo y fundamento cada decisión tomada en la defensa oral.
