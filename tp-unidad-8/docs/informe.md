# Informe Técnico Integrador: Arquitectura Móvil, Sincronización y Cierre de la Capa de Datos (TP N.° 8)
**Asignatura:** Base de Datos II · Tecnicatura Universitaria en Programación  
**Institución:** Universidad Tecnológica Nacional (UTN)  
**Autor:** Fabrizio Simon  
**Herramientas:** PostgreSQL 18 · SQLite 3.50+ · MongoDB · Python 3.10+  
**Ciclo Lectivo:** 2026 · Semana 13  

---

## 1. Consigna 1.a · Selección y Justificación de Datos que Viajan al Dispositivo Móvil

Para operar en la feria gastronómica sin acceso confiable a Internet, la tablet requiere una copia local mínima del catálogo para armar borradores de venta de manera autónoma.

### 1.1 Matriz de Transferencia de Columnas de Producto

| Columna | ¿Viaja a la tablet? | Justificación Funcional y de Seguridad |
| :--- | :---: | :--- |
| `id` (identificador producto) | **SÍ** | Permite vincular de forma unívoca las líneas de los borradores con el catálogo descargado. |
| `nombre` | **SÍ** | Indispensable para que el cajero o mozo identifique el producto visualmente en pantalla. |
| `precio_centavos` | **SÍ** | Permite calcular el importe preliminar del pedido sin depender de conexión de red externa. |
| `stock_visto` | **SÍ** | Orienta al vendedor sobre la existencia disponible al momento de la última descarga. |
| `disponible` (activo) | **SÍ** | Bandera booleana (0 o 1) que habilita o inhabilita la selección del ítem en la interfaz. |
| `eliminado` (lápida) | **SÍ** | Permite ocultar productos dados de baja lógica conservando la integridad referencial histórica. |
| `fecha_copia` | **SÍ** | Marca temporal para auditar la vigencia y obsolescencia de la caché local del dispositivo. |
| `datos de usuarios` (email, hash, rol) | **NO** | Información confidencial sensible (PII/seguridad) que no debe residir en dispositivos públicos expuestos. |
| `costos internos / margen de ganancia` | **NO** | Secreto comercial del negocio. Si la tablet es robada físicamente, no se filtran costos ni proveedores. |
| `pedidos históricos de otras sucursales` | **NO** | Saturaría el almacenamiento de la tablet y violaría el principio de mínimo privilegio. |

### 1.2 Regla de Autoridad y Fuente de Verdad
**PostgreSQL es la única e indiscutible Fuente de Verdad (Single Source of Truth).** A la tablet solo viaja una instantánea desensibilizada estrictamente necesaria para armar pedidos provisionales fuera de línea. La tablet no tiene potestad para alterar el inventario ni confirmar transacciones fiscales: el móvil propone, el servidor dispone.

---

## 2. Consigna 2.c · Resolución de Casos de Sincronización mediante el Semáforo

Se ejecutó el semáforo sobre la base `foodstore_movil.db` contra la instantánea del servidor central (`snapshot_servidor`), evaluando las solicitudes pendientes bajo la jerarquía **Rojo (`RECHAZADO`) > Amarillo (`CONFLICTO`) > Verde (`SIMULADO_APROBADO`)**.

### Caso C2: Subida de Precio en Servidor (Conflicto) y Aceptación en Mostrador
* **Comandos ejecutados:**
  1. Mozo crea borrador con Producto 1 (Muzza) a precio visto $100.00 (10000 centavos):  
     `INSERT INTO cola_sync VALUES ('s0000002...1', 'b0000002...2', 'PENDIENTE', ...);`
  2. En el servidor sube el precio a $125.00 (12500 centavos):  
     `UPDATE snapshot_servidor SET precio_centavos = 12500 WHERE id = 1;`
  3. Ejecución del semáforo:  
     `WITH evaluacion ... UPDATE cola_sync SET estado = ev.nuevo_estado ...`
  4. El cliente acepta la diferencia:  
     `UPDATE item_borrador SET precio_centavos_visto = 12500 ...;`  
     `INSERT INTO cola_sync VALUES ('s0000002...2', 'b0000002...2', 'PENDIENTE', ...);`
  5. Reejecución del semáforo.
* **Resultados observados:**  
  - Solicitud 1: **`CONFLICTO`** (`CONFLICTO: el precio del servidor cambió respecto al visto en la tablet`).  
  - Solicitud 2: **`SIMULADO_APROBADO`** (`SIMULADO_APROBADO: validación exitosa (precio, stock y vigencia verificados)`).
* **Explicación:** El semáforo protege la rentabilidad del Food Store al detectar que el precio cambió. Al aceptar el cliente, se actualiza el borrador local y el nuevo intento valida limpiamente.

### Caso C3: Solicitud de Cantidad Superior al Stock Remanente (Rechazo)
* **Comandos ejecutados:**  
  `INSERT INTO pedido_borrador VALUES ('b0000003...3', 'mozo_feria', 'TARJETA', ...);`  
  `INSERT INTO item_borrador VALUES ('b0000003...3', 2, 50, 12000); -- Pide 50 unidades de Napolitana`  
  `INSERT INTO cola_sync VALUES ('s0000003...1', 'b0000003...3', 'PENDIENTE', ...);`  
  `-- Ejecución de semaforo.sql`
* **Resultado observado:**  
  **`RECHAZADO`** (`RECHAZADO: stock insuficiente en el servidor para cubrir la cantidad`).
* **Explicación:** El Producto 2 posee un stock de 10 unidades en el servidor. Al solicitar 50, la condición `ib.cantidad > s.stock` dispara de inmediato la prioridad Roja (Rechazo), evitando quiebres de inventario o sobreventas en la feria.

### Caso C4: Producto Dado de Baja Lógica / Lápida (Rechazo y Ocultamiento)
* **Comandos ejecutados:**  
  1. Borrador tomado con Producto 3 (Producto masivo 3) mientras estaba activo:  
     `INSERT INTO item_borrador VALUES ('b0000004...4', 3, 1, 241800);`
  2. En el servidor se aplica baja lógica:  
     `UPDATE snapshot_servidor SET eliminado = 't' WHERE id = 3;`
  3. Ejecución de `semaforo.sql`.
  4. Sincronización del catálogo en la tablet:  
     `UPDATE producto_cache SET eliminado = 1 WHERE id = 3;`
* **Resultados observados:**  
  - Semáforo: **`RECHAZADO`** (`RECHAZADO: producto dado de baja lógica (lápida activa) en el servidor`).  
  - Consulta de catálogo: `SELECT COUNT(*) FROM producto_cache WHERE id = 3;` -> **1 fila existente**;  
    `SELECT COUNT(*) FROM producto_cache WHERE id = 3 AND disponible = 1 AND eliminado = 0;` -> **0 filas visibles**.
* **Explicación:** El producto dado de baja lógica en el servidor no puede venderse. Al refrescar la caché local, la fila permanece físicamente en la tablet para no romper claves foráneas de borradores previos, pero desaparece de la vista del catálogo de ventas.

### Caso C5: Borrador sin Cambios (Aprobación Limpia)
* **Comandos ejecutados:**  
  `INSERT INTO pedido_borrador VALUES ('b0000005...5', 'mozo_feria', 'EFECTIVO', ...);`  
  `INSERT INTO item_borrador VALUES ('b0000005...5', 4, 2, 413800); -- Producto 4 con stock 130`  
  `INSERT INTO cola_sync VALUES ('s0000005...1', 'b0000005...5', 'PENDIENTE', ...);`  
  `-- Ejecución de semaforo.sql`
* **Resultado observado:**  
  **`SIMULADO_APROBADO`** (`SIMULADO_APROBADO: validación exitosa (precio, stock y vigencia verificados)`).
* **Explicación:** Todas las líneas coinciden en precio, el producto está disponible y existe stock suficiente. La solicitud queda lista para su posterior confirmación transaccional.

### Caso C6: Reenvío de la Misma Solicitud / Idempotencia (Mismo UUID)
* **Comandos ejecutados:**  
  `-- Intento de reenviar la solicitud s0000005...1`  
  `INSERT INTO cola_sync VALUES ('s0000005...1', 'b0000005...5', 'PENDIENTE', ...);`
* **Resultado observado:**  
  Error inmediato capturado por SQLite: `sqlite3.IntegrityError: UNIQUE constraint failed: cola_sync.solicitud_uuid`.  
  Al reejecutar el semáforo, el estado de la solicitud existente permanece intacto en `SIMULADO_APROBADO` sin reevaluarse.
* **Explicación:** La restricción de clave primaria previene registros duplicados en el cliente.
* **Protección Real en Arquitectura de Servidor (Parada 8):** En un sistema de producción, la protección de idempotencia reside en el **Gateway/API del servidor central**. Cada request HTTP incluye un encabezado `Idempotency-Key: <UUID>`. El backend consulta una tabla de tokens procesados; si el UUID ya fue recibido, retorna inmediatamente la respuesta almacenada previamente sin volver a descontar stock ni generar un segundo cobro fiscal.

### 2.3 Auditoría de Invariabilidad en PostgreSQL Central
Tras la ejecución completa de todas las simulaciones y casos C1 a C7, se corrió en PostgreSQL la consulta de verificación de integridad:

```sql
SELECT COUNT(*) AS total_pedidos FROM pedido;
SELECT id_producto, nombre, stock, precio_lista FROM producto WHERE id_producto IN (1, 2, 3, 4) ORDER BY id_producto;
```
* **Resultado obtenido en PostgreSQL:**  
  - `total_pedidos`: **200,001** (exactamente la misma cifra inicial; cero pedidos insertados).  
  - `stock`: Producto 1 = **5**, Producto 2 = **10**, Producto 3 = **115**, Producto 4 = **130** (exactamente los mismos valores iniciales; cero unidades descontadas).  
* **Conclusión:** Se verifica fehacientemente que la base de datos central permaneció intacta. La simulación aprueba borradores en la tablet pero no constituye una venta fiscal en el servidor.

---

## 3. Consigna 3.a · Mapa de la Capa de Datos del Ecosistema Food Store

A lo largo de la cursada integramos tres motores de bases de datos especializados:

| Motor / Tecnología | Rol y Capa Arquitectónica | ¿Qué guarda? | ¿Quién manda sobre cada dato? (Autoridad) |
| :--- | :--- | :--- | :--- |
| **PostgreSQL 18** | **Núcleo Transaccional Central (OLTP)**<br>Single Source of Truth | • Usuarios, contraseñas hash, roles (RBAC).<br>• Catálogo maestro de productos y precios oficiales.<br>• Stock físico maestro e inventario.<br>• Ventas confirmadas fiscales (`pedido`, `pedido_producto`).<br>• Auditoría y logs forenses. | **Autoridad ABSOLUTA** sobre precios, stock, transacciones fiscales, seguridad y usuarios. Ningún otro motor puede contradecirlo. |
| **MongoDB**<br>*(Unidad 7)* | **Read Model / Store Documental (CQRS)**<br>Consultas masivas web | • Colección de pedidos desnormalizados con ítems embebidos (`lineas`).<br>• Instantáneas de clientes embebidas (`cliente`).<br>• Catálogo en formato JSON/BSON para lectura rápida de apps móviles y web. | **Autoridad subordinada (Solo Lectura).** Optimizado para responder consultas rápidas sin JOINs. Si hay desincronización, PostgreSQL manda y MongoDB se reconstruye. |
| **SQLite 3.50+**<br>*(Unidad 8)* | **Base Embebida de Borde (Edge / Offline-First)**<br>Tablet del Food Truck en feria | • Instantánea descargada (`snapshot_servidor`).<br>• Catálogo local (`producto_cache`).<br>• Borradores de pedidos locales (`pedido_borrador`).<br>• Ítems temporales y cola de conciliación (`cola_sync`). | **Autoridad local exclusiva** sobre la interfaz del cajero y los borradores temporales. **CERO autoridad** sobre stock y precios del servidor. |

---

## 4. Consigna 3.b · Plan de Mantenimiento y Contingencia Integral

Como extensión directa de los procedimientos de contingencia y recuperación probados en la Unidad 6:

1. **¿Qué se respalda y cómo se prueba la restauración?**  
   - **PostgreSQL:** Se respaldan diariamente copias lógicas completas comprimidas con `pg_dump` y se archivan de forma continua los segmentos WAL para recuperación punto en el tiempo (PITR). La restauración se prueba periódicamente de forma automatizada mediante el script `restore_test.ps1`, levantando una base efímera `foodstore_restore_test` y validando integridad referencial, RTO (tiempo de recuperación: 4.84 s) y RPO (pérdida máxima de datos: 1.70 min).
   - **MongoDB:** Se realizan backups lógicos semanales con `mongodump`. En caso de pérdida total, se regenera desde el catálogo relacional central.
   - **SQLite (Tablets):** Las bases locales son **descartables (efímeras)**; no requieren backups empresariales. Si una tablet se rompe o extravía, se provisiona otra, se descarga la instantánea fresca del servidor y se continúa operando. Solo se resguardan las solicitudes no sincronizadas de `cola_sync` volcándolas vía USB o red local si la conexión falla.

2. **Si se restaura un respaldo viejo de PostgreSQL, ¿qué hacen las tablets?**  
   - Cada instantánea exportada incluye un número de versión o marca de época (`snapshot_epoch`). Si el servidor central sufre un desastre y se restaura un backup desactualizado (por ejemplo, de 24 horas atrás), la tablet detecta que el epoch del servidor es anterior a su fecha de catálogo local.
   - La tablet **invalida inmediatamente su caché local (`producto_cache`)**, bloquea el alta de nuevos pedidos hasta descargar una instantánea coherente con el servidor restaurado, y pasa todas las solicitudes no consolidadas a estado **`CONFLICTO_RESTAURACION`**. De este modo se evita la venta con precios obsoletos y la reinyección de ventas que pudieran generar inconsistencias contables.

3. **¿Cada cuánto y quién revisa las solicitudes en CONFLICTO o RECHAZADO?**  
   - **En tiempo real durante la feria:** El propio operador/mozo de la tablet. Si el semáforo arroja `CONFLICTO` (cambio de precio), dialoga con el cliente en el mostrador para aceptar la diferencia o cancelar el borrador. Si da `RECHAZADO` (quiebre de stock), se cancela la orden al instante.
   - **Cierre de jornada (cada 24 horas):** El encargado de operaciones de la feria y el administrador de bases de datos (`admin_datos`). Al finalizar el evento, se genera un reporte consolidado de `cola_sync` para detectar patrones de productos agotados, discrepancias de tarifas recurrentes o intentos reiterados de duplicación.

---

## 5. Consigna 3.c · Code Review con IA sobre Scripts de la Cursada

Se sometieron a revisión los scripts desarrollados en las Unidades 5, 6 y 8 utilizando el agente de análisis:

### 5.1 Matriz de Hallazgos y Decisiones Técnicas

| ID | Unidad | Script / Componente | Propuesta de la IA | Decisión Humana | Motivo Técnico |
| :---: | :---: | :--- | :--- | :---: | :--- |
| **H-1** | **U5** | `fn_autenticar` (Seguridad) | Cambiar de `SECURITY INVOKER` a `SECURITY DEFINER` con search_path explícito. | **ACEPTADO Y CORREGIDO** | El rol `app_web` no tiene SELECT sobre `usuario`. Como invoker fallaba por permisos; con definer funciona de forma segura. |
| **H-2** | **U6** | `maintenance.sql` (Mantenimiento) | Ejecutar `VACUUM FULL ANALYZE` diariamente en todas las tablas transaccionales. | **DESCARTADO CON FUNDAMENTO** | `VACUUM FULL` aplica un bloqueo exclusivo de tabla (`ACCESS EXCLUSIVE LOCK`), volteando la disponibilidad web y de las tablets. |
| **H-3** | **U8** | `schema_sqlite.sql` (Móvil) | Utilizar claves primarias `AUTOINCREMENT` en `pedido_borrador` y `cola_sync`. | **DESCARTADO CON FUNDAMENTO** | En un entorno offline distribuido con múltiples tablets, los enteros autoincrementales colisionan inevitablemente. Se impuso **UUID v4**. |

### 5.2 Desarrollo y Comprobación en Base de Datos de los Tres Hallazgos

1. **Hallazgo H-1 (U5 - Aceptado y Corregido): Permisos en `fn_autenticar`**  
   - *Comprobación en base:* Al simular el acceso desde la aplicación con `SET ROLE app_web; SELECT fn_autenticar('admin@foodstore.com', 'pass');`, PostgreSQL arrojó `ERROR: permission denied for table usuario`.  
   - *Solución implementada:* Se ejecutó `ALTER FUNCTION fn_autenticar(text, text) OWNER TO admin_datos; ALTER FUNCTION fn_autenticar(text, text) SECURITY DEFINER; ALTER FUNCTION fn_autenticar(text, text) SET search_path = public, pg_temp;`. Al repetir la prueba como `app_web`, la autenticación validó correctamente sin concederle privilegios directos sobre la tabla de usuarios.
2. **Hallazgo H-2 (U6 - Descartado con Fundamento): Inviabilidad de `VACUUM FULL` en Producción**  
   - *Comprobación en base:* Se analizó el catálogo `pg_locks` durante una prueba de `VACUUM FULL` sobre una tabla de 200,000 registros, verificando la adquisición del bloqueo `AccessExclusiveLock`.  
   - *Fundamento del descarte:* Un bloqueo exclusivo impide cualquier lectura (`SELECT`) o escritura concurrente. En un sistema en producción como Food Store, ejecutarlo en horarios operativos dejaría la tienda caída durante minutos. Se mantuvo `VACUUM (ANALYZE, VERBOSE)` que corre concurrentemente sin interrumpir transacciones.
3. **Hallazgo H-3 (U8 - Descartado con Fundamento): Colisión de Claves Autonuméricas en Arquitectura Offline**  
   - *Comprobación en base:* Si la Tablet A genera los pedidos 1, 2 y 3 mientras la Tablet B genera los pedidos 1, 2 y 3, al conectarse a la red para sincronizar se produce una colisión insalvable en la clave primaria de pedidos.  
   - *Fundamento del descarte:* Se rechazó la propuesta de la IA y se diseñaron `id_local` y `solicitud_uuid` como cadenas de 36 caracteres conteniendo **UUID v4**. Esto garantiza unicidad probabilística global en dispositivos desconectados sin requerir coordinación centralizada.
