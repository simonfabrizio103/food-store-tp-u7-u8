# Especificación de Modelo NoSQL — Unidad 7: Food Store
**Tecnicatura Universitaria en Programación — Base de Datos II (UTN FRM)**  
**Proyecto:** Food Store | **Motor Relacional:** PostgreSQL 18 | **Motor Documental:** MongoDB 7+  

---

## 1. Identificación del Subconjunto Relacional en PostgreSQL

Para la representación documental en MongoDB se seleccionó el subconjunto transaccional central de Food Store: **«pedidos y detalle de pedidos»**, integrando las entidades de soporte directo (cliente y producto).

### Tablas y claves involucradas en PostgreSQL:
- **`pedido`**: `id_pedido` (PK), `fecha` (TIMESTAMPTZ), `forma_pago` (ENUM), `estado` (VARCHAR), `id_cliente` (FK -> `cliente.id_cliente`).
- **`cliente`**: `id_cliente` (PK), `nombre` (VARCHAR), `email` (VARCHAR UNIQUE), `telefono` (VARCHAR).
- **`pedido_producto`** (detalle): `id_pedido` (PK, FK -> `pedido`), `id_producto` (PK, FK -> `producto`), `cantidad` (INT CHECK > 0), `precio_unitario` (NUMERIC CHECK >= 0).
- **`producto`**: `id_producto` (PK), `nombre` (VARCHAR), `precio_lista` (NUMERIC), `stock` (INT), `id_categoria` (FK -> `categoria`).
- **`categoria`**: `id_categoria` (PK), `nombre` (VARCHAR).

---

## 2. Esquema de la Colección Documental Propuesta (`pedidos`)

Se diseñó una colección única denominada `pedidos` en la base de datos `foodstore_nosql`. Se aplica el patrón de diseño orientado a agregados (*Aggregate-Oriented Design*).

### Estructura formal del documento JSON/BSON:
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

### Desglose de componentes del modelo:
1. **Identificador conservado (`_id`):** Se conserva el valor numérico de `id_pedido` proveniente de PostgreSQL como clave primaria inmutable `_id`. Esto asegura la trazabilidad 1 a 1 entre ambos motores.
2. **Campos principales del pedido:** `fecha` (ISO Date), `forma_pago` (método registrado), `estado` (ciclo de vida del pedido) y `total` (campo precalculado del monto global).
3. **Objeto embebido `cliente`:** Contiene un subdocumento con los datos esenciales de facturación y contacto del cliente (`id_cliente`, `nombre`, `email`).
4. **Arreglo de subdocumentos `lineas`:** Lista de productos adquiridos en el pedido. Cada elemento almacena el `id_producto`, `nombre`, `categoria`, `cantidad`, `precio_unitario` histórico y el `subtotal` de la línea.

---

## 3. Justificación de Diseño: Embeber vs. Referenciar (Consigna 3)

### ¿Por qué se embeben las líneas de pedido?
- **Ciclo de vida y acceso conjunto:** Las líneas de un pedido no tienen existencia independiente fuera del pedido que las contiene. El 99% de las consultas de negocio (ver ticket, consultar factura, despachar mercadería) requieren leer el pedido junto con todo su detalle.
- **Rendimiento de lectura sin JOINs:** Embeber las líneas permite recuperar el pedido completo en una sola operación de lectura sobre un bloque contiguo de memoria/disco (`findOne({ _id: id })`), eliminando la necesidad de realizar costosos JOINs entre tablas.
- **Atomicidad de escritura nativa:** En MongoDB, cualquier modificación dentro de un único documento es atómica por definición. La creación o cancelación de un pedido con todas sus líneas se confirma o se descarta de forma integral sin requerir transacciones multi-documento complejas.

### ¿Por qué se embebe parcialmente el cliente?
- Se adopta el patrón de **desnormalización controlada (Snapshot)**: se copian únicamente los datos de contacto vigentes al momento de la venta (`nombre`, `email`). Si el cliente modifica su teléfono o apellido en el futuro, el comprobante histórico de compra no debe verse alterado retroactivamente.

---

## 4. Reglas de Integridad que Deben Conservarse en la Migración

1. **Consistencia de Cálculo e Invarianza de Importes:** Para cada línea dentro del arreglo `lineas`, se debe verificar que `cantidad > 0` y `precio_unitario >= 0`, garantizando que `subtotal == cantidad * precio_unitario`. A su vez, el campo `total` del documento raíz debe coincidir exactamente con la sumatoria de los subtotales:
   $$\text{total} = \sum_{i=1}^{n} (\text{lineas}[i].\text{cantidad} \times \text{lineas}[i].\text{precio\_unitario})$$
2. **Inmutabilidad del Snapshot Histórico de Precios:** El valor almacenado en `precio_unitario` debe ser el precio histórico real pactado en la transacción original de PostgreSQL, disociado del precio de lista actual en la tabla `producto`. Esto previene alteraciones involuntarias en la facturación ante actualizaciones del catálogo.
