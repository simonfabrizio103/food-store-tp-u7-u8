# Informe técnico — TP Unidad 7: NoSQL y nuevas formas de almacenamiento (Food Store)
**Tecnicatura Universitaria en Programación — Base de Datos II (UTN FRM)**  
**Alumno:** Fabrizio Simon | **Fecha:** 10 de noviembre de 2026 | **Motores:** PostgreSQL 18.6 & MongoDB 7+  
**Archivos adjuntos:** `consultas_mongodb.js`, `consultas_postgresql.sql`, `ejecutar_mongodb.js`, `SPEC_U7.md`, `BITACORA.md`  

---

## 1. Modelo documental y estrategia de migración (Parte 1)

### a) Tablas y claves involucradas en PostgreSQL
En la base relacional `foodstore`, los datos de ventas se encuentran normalizados en 5 tablas vinculadas por claves primarias y foráneas:
- `pedido` (`id_pedido` PK, `fecha`, `estado`, `forma_pago`, `id_cliente` FK).
- `cliente` (`id_cliente` PK, `nombre`, `email`, `telefono`).
- `pedido_producto` (`id_pedido` PK/FK, `id_producto` PK/FK, `cantidad`, `precio_unitario`).
- `producto` (`id_producto` PK, `nombre`, `precio_lista`, `stock`, `id_categoria` FK).
- `categoria` (`id_categoria` PK, `nombre`).

### b) Esquema documental propuesto en MongoDB (`foodstore_nosql.pedidos`)
Para representar este dominio en MongoDB diseñé una única colección llamada `pedidos`, agrupando la información bajo el patrón de **diseño orientado a agregados** (*Aggregate-Oriented Design*):

```json
{
  "_id": 2,
  "fecha": "2025-10-30T18:44:05.346Z",
  "forma_pago": "EFECTIVO",
  "estado": "ENTREGADO",
  "cliente": {
    "id_cliente": 1,
    "nombre": "Juan",
    "email": "juan@test.com"
  },
  "lineas": [
    {
      "id_producto": 3,
      "nombre": "Producto masivo 3",
      "categoria": "Pizzas",
      "cantidad": 1,
      "precio_unitario": 500.00,
      "subtotal": 500.00
    },
    {
      "id_producto": 4,
      "nombre": "Producto masivo 4",
      "categoria": "Categoria masiva 1",
      "cantidad": 2,
      "precio_unitario": 600.00,
      "subtotal": 1200.00
    }
  ],
  "total": 1700.00
}
```

### c) Justificación de diseño: Embeber vs. Referenciar (Consigna 3)
1. **Líneas de pedido embebidas:** Las líneas de un pedido no tienen sentido por sí solas en el negocio; siempre que se consulta un pedido se necesita ver qué productos se compraron. Al embeberlas en el arreglo `lineas`, MongoDB recupera el pedido entero en una sola lectura de disco (`findOne`), sin tener que hacer JOINs costosos entre tablas separadas. Además, la escritura es atómica por naturaleza dentro del documento.
2. **Cliente parcialmente embebido (Snapshot):** Guardé un subdocumento `cliente` únicamente con los datos esenciales de facturación (`id_cliente`, `nombre`, `email`). Esto actúa como un snapshot histórico: si el cliente cambia de correo o teléfono el mes que viene, el ticket de la compra vieja queda congelado con los datos válidos al momento de la venta.
3. **Reglas de integridad conservadas:**
   - Para cada línea, `cantidad > 0`, `precio_unitario >= 0`, y `subtotal == cantidad * precio_unitario`.
   - El campo `total` del documento es exactamente igual a la suma de los subtotales de sus líneas.
   - Los precios unitarios son históricos e inmutables, protegiendo la facturación si cambia el precio de lista del producto.

---

## 2. Consultas ejecutadas y evidencia de resultados (Parte 2)

Migré un subconjunto de 6 pedidos reales de Food Store (IDs del 2 al 7) con múltiples líneas y clientes asociados. Las consultas se ejecutaron y verificaron en ambos motores:

### a) Mostrar todos los pedidos con su identificador y estado
- **MongoDB:** `db.pedidos.find({}, { _id: 1, estado: 1 }).sort({ _id: 1 })`
- **PostgreSQL:** `SELECT id_pedido, estado FROM pedido WHERE id_pedido BETWEEN 2 AND 7 ORDER BY id_pedido;`
- **Resultado obtenido (6 pedidos):**
  - ID 2: `ENTREGADO` | ID 3: `PENDIENTE` | ID 4: `ENTREGADO`
  - ID 5: `CANCELADO` | ID 6: `PENDIENTE` | ID 7: `ENTREGADO`

### b) Filtrar pedidos por estado = 'ENTREGADO'
- **MongoDB:** `db.pedidos.find({ estado: "ENTREGADO" }, { _id: 1, fecha: 1, estado: 1, "cliente.nombre": 1, total: 1 })`
- **PostgreSQL:** `SELECT p.id_pedido, p.fecha, p.estado, c.nombre, SUM(pp.cantidad * pp.precio_unitario) AS total FROM pedido p JOIN cliente c ON c.id_cliente = p.id_cliente JOIN pedido_producto pp ON pp.id_pedido = p.id_pedido WHERE p.id_pedido BETWEEN 2 AND 7 AND p.estado = 'ENTREGADO' GROUP BY p.id_pedido, p.fecha, p.estado, c.nombre;`
- **Resultado obtenido (3 pedidos):** IDs 2 ($1700), 4 ($2050), 7 ($500).

### c) Buscar pedidos que contengan el producto con ID 3 en sus líneas
- **MongoDB:** `db.pedidos.find({ "lineas.id_producto": 3 }, { _id: 1, estado: 1, "cliente.nombre": 1, total: 1, "lineas.$": 1 })`
- **PostgreSQL:** `SELECT DISTINCT p.id_pedido, p.estado FROM pedido p JOIN pedido_producto pp ON pp.id_pedido = p.id_pedido WHERE p.id_pedido BETWEEN 2 AND 7 AND pp.id_producto = 3;`
- **Resultado obtenido (3 pedidos):** IDs 2, 4, 6.

### d) Buscar pedidos cuyo total sea superior a un importe elegido ($2000.00)
- **Justificación del umbral:** En Food Store las compras diarias individuales promedian entre $500 y $1700. Un umbral de $2000.00 permite segmentar de forma precisa pedidos grandes o compras mayoristas/familiares.
- **MongoDB:** `db.pedidos.find({ total: { $gt: 2000.00 } }, { _id: 1, "cliente.nombre": 1, estado: 1, total: 1 })`
- **PostgreSQL:** `SELECT p.id_pedido, c.nombre, p.estado, SUM(pp.cantidad * pp.precio_unitario) AS total FROM pedido p JOIN cliente c ON c.id_cliente = p.id_cliente JOIN pedido_producto pp ON pp.id_pedido = p.id_pedido WHERE p.id_pedido BETWEEN 2 AND 7 GROUP BY p.id_pedido, c.nombre, p.estado HAVING SUM(pp.cantidad * pp.precio_unitario) > 2000.00;`
- **Resultado obtenido (2 pedidos):** IDs 4 ($2050) y 6 ($3500).

---

## 3. Tabla de verificación cruzada entre motores (Consigna 5)

| Consulta / Filtro ejecutado | Cantidad en PostgreSQL | Cantidad en MongoDB | ¿Coinciden los IDs exactamente? | Detalle de IDs recuperados |
| :--- | :---: | :---: | :---: | :--- |
| **Estado seleccionado (`'ENTREGADO'`)** | **3** | **3** | **Sí** | IDs: `[2, 4, 7]` |
| **Producto seleccionado (`id_producto = 3`)** | **3** | **3** | **Sí** | IDs: `[2, 4, 6]` |

*Explicación:* No se detectó ninguna discrepancia entre ambos motores. Al conservar los mismos identificadores primarios (`_id = id_pedido`), los mismos precios unitarios históricos y las cantidades, los filtros por estado y por producto dentro del arreglo devolvieron exactamente los mismos conjuntos de datos.

---

## 4. Evaluación de la tecnología y contraste con la IA (Parte 3)

Le pedí a la IA que compare PostgreSQL y MongoDB para el almacenamiento y consulta de pedidos en Food Store, considerando acceso frecuente a pedidos completos, consistencia de precios y transacciones. Contrasté críticamente dos afirmaciones de su respuesta:

### Contraste 1: Soporte de transacciones ACID en MongoDB
- **Lo que afirmó la IA:** *"No conviene usar MongoDB para pedidos porque carece de soporte para transacciones ACID, lo que puede provocar que el pedido quede grabado sin descontar el stock o con totales corruptos."*
- **Contraste con la documentación oficial:** **Falso y desactualizado.** El manual oficial de MongoDB (*MongoDB Manual - Transactions*) documenta que desde la versión 4.0 (2018) y 4.2+ existen transacciones multi-documento distribuidas con semántica ACID completa (`startTransaction()`, `commitTransaction()`, `abortTransaction()`). Pero además, en nuestro modelo con líneas embebidas, cualquier inserción o actualización sobre un pedido es **atómica por naturaleza a nivel de documento individual** sin necesidad de transacciones distribuidas complejas.

### Contraste 2: Rendimiento de los JOINs en PostgreSQL
- **Lo que afirmó la IA:** *"En PostgreSQL cada consulta de un pedido completo colapsa el rendimiento porque requiere 4 JOINs pesados obligatorios entre tablas normalizadas."*
- **Contraste con la evidencia del laboratorio:** **Exagerado.** En el laboratorio comprobé con `EXPLAIN ANALYZE` que hacer un `JOIN` entre `pedido` y `pedido_producto` sobre una clave foránea indexada (`idx_pp_pedido`) demora **0.08 ms** en PostgreSQL, incluso con 200.000 filas. El cuello de botella no es el JOIN en la base de datos, sino la sobrecarga en la aplicación web para transformar filas relacionales planas en objetos estructurados (mapeo ORM). MongoDB ahorra ese costo porque devuelve directamente el JSON estructurado.

---

## 5. Conclusión técnica fundamentada (Consigna 7)

Para Food Store recomiendo adoptar una **arquitectura híbrida políglota** con separación de responsabilidades (patrón CQRS).  

En el **módulo transaccional y de facturación**, **PostgreSQL** debe mantenerse como la fuente única de la verdad (*Single Source of Truth*). Criterio técnico 1: **Garantía estricta de integridad referencial y unicidad**: las claves foráneas y restricciones `CHECK` impiden inconsistencias contables, pedidos huérfanos o ventas de productos inexistentes, algo fundamental para auditoría fiscal.  

En el **módulo de consulta de la tienda web y mobile**, **MongoDB** es la solución superior para almacenar los pedidos cerrados y el catálogo de productos. Criterio técnico 2: **Patrón de acceso orientado a agregados y escalabilidad de lectura**: la aplicación web consulta el pedido como un único bloque atómico (datos del cliente, líneas y total). Al estar embebidos en un solo documento BSON, MongoDB resuelve la lectura en un único acceso a disco (`findOne`), evitando la sobrecarga de ensamblado y permitiendo escalabilidad horizontal (*sharding*) sin degradar la base transaccional principal. *(166 palabras).*
