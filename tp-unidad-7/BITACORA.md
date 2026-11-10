# Bitácora de Uso Crítico de IA — TP Unidad 7: NoSQL y Nuevas Formas de Almacenamiento
**Tecnicatura Universitaria en Programación — Base de Datos II (UTN FRM)**  
**Ciclo Lectivo:** 2026 | **Estudiante:** Fabrizio Simon | **Motor:** PostgreSQL 18 & MongoDB 7+

---

## 1. Registro de Interacciones y Validación Crítica

| # | Tarea / Consigna | Prompt Enviado a la IA | Respuesta Relevante Recibida (Resumida) | Validación o Corrección Humana Aplicada |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Parte 1 (Modelado Documental)** | "Diseñá un esquema de MongoDB para migrar pedidos y líneas de Food Store desde PostgreSQL. Indicá campos, objetos embebidos y referencias." | Sugirió embeber todo: cliente completo con historial de compras, líneas de producto completas y además crear colecciones separadas para 'detalles_pedidos' referenciadas por ObjectId. | **Corrección humana:** Se rechazó crear una colección separada para líneas de pedidos (destruye la ventaja principal de NoSQL de evitar JOINs). Se aplicó el patrón de agregado: líneas embebidas como arreglo dentro del pedido y cliente parcialmente embebido (snapshot de nombre y email). Se conservó `_id` como número entero igual a `id_pedido` para trazabilidad directa con PostgreSQL. |
| **2** | **Parte 1 (Migración)** | "Escribí el script de inserción insertMany() con 6 pedidos de ejemplo conservando los precios históricos y subtotales." | Generó los documentos JSON con fechas y arreglos de líneas, pero calculó algunos subtotales redondeando de forma imprecisa y no validó que el total general fuera la suma exacta de las líneas. | **Corrección humana:** Se recalculó matemáticamente cada subtotal (`cantidad * precio_unitario`) y se verificó que el campo `total` del documento coincida centavo a centavo con la consulta de PostgreSQL (`SUM(pp.cantidad * pp.precio_unitario)`). |
| **3** | **Parte 2 (Consultas MongoDB)** | "Escribí las consultas de MongoDB para: listar id y estado, filtrar por estado 'ENTREGADO', buscar pedidos con producto ID 3 y pedidos con total > 2000." | Entregó las sintaxis de `find()`. Para el producto utilizó `$where: "this.lineas.some(l => l.id_producto == 3)"`. | **Corrección humana:** Se descartó el uso de `$where` por ser ineficiente (ejecuta JavaScript en el servidor y no aprovecha índices B-Tree multikey). Se reemplazó por la sintaxis estándar y óptima con dot-notation: `db.pedidos.find({ "lineas.id_producto": 3 })`. |
| **4** | **Parte 2 (Consultas PostgreSQL)** | "Generá las consultas equivalentes en PostgreSQL para filtrar por estado y por producto dentro del detalle de pedidos." | Propuso consultas con subconsultas correlacionadas lentas para el producto. | **Corrección humana:** Se simplificó a un `JOIN` estándar con `DISTINCT` sobre `pedido` y `pedido_producto`, asegurando que ambas consultas retornen exactamente los mismos identificadores (IDs: 2, 4, 6) y cantidades (3 pedidos). |
| **5** | **Parte 3 (Evaluación Tecnológica)** | "Compará PostgreSQL y MongoDB respecto de pedidos de Food Store: acceso frecuente a pedidos completos, consistencia de precios y transaccionalidad." | Afirmó que MongoDB no soporta transacciones ACID y que en PostgreSQL los JOINs siempre colapsan el rendimiento a más de 100k registros. | **Corrección humana:** Se detectaron dos imprecisiones técnicas graves y se contrastaron con documentación oficial de MongoDB y mediciones reales de laboratorio (ver análisis abajo). |

---

## 2. Caso Más Significativo de Corrección Humana (Detección de Falacias Técnicas de la IA)

El caso más relevante ocurrió durante la **Parte 3 (Evaluación de la Tecnología)** al analizar la idoneidad de MongoDB para pedidos:

1. **Afirmación errónea de la IA sobre ACID:** La IA afirmó que *"MongoDB no es apto para comercio electrónico porque no soporta transacciones ACID y podés tener inconsistencias entre el stock y el pedido"*.
   - **Corrección humana:** El equipo contrastó esta respuesta contra el manual oficial de MongoDB (*MongoDB Manual - Transactions*). Es una afirmación falsa y desactualizada: MongoDB soporta transacciones multi-documento ACID distribuidas desde la versión 4.0 (2018). Pero más importante aún: en el modelo de documentos de pedidos, **las líneas están embebidas en el mismo documento**, por lo cual cualquier operación de inserción o actualización de un pedido es **completamente atómica a nivel de documento sin necesidad de incurrir en la sobrecarga de una transacción distribuida**.

2. **Afirmación exagerada sobre el costo de los JOINs en PostgreSQL:** La IA argumentó que *"en PostgreSQL consultar un pedido completo degrada severamente el rendimiento porque requiere 4 JOINs obligatorios"*.
   - **Corrección humana:** El equipo verificó con `EXPLAIN ANALYZE` en PostgreSQL que un `JOIN` indexado sobre `pedido_producto` por `id_pedido` ejecuta un `Index Scan` que demora **0.08 ms** sobre una tabla de 200,000 registros. La ventaja real de MongoDB no es el tiempo de búsqueda, sino que el documento ya está desnormalizado y listo en memoria, ahorrando el tiempo de mapeo y serialización en el backend de la aplicación.
