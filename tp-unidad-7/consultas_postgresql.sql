-- ============================================================================
-- TRABAJO PRÁCTICO · UNIDAD 7: NoSQL y nuevas formas de almacenamiento
-- Proyecto: Food Store | Motor Relacional: PostgreSQL 16+
-- Archivo: consultas_postgresql.sql
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. PREPARACIÓN Y AJUSTE DE COLUMNA ESTADO EN POSTGRESQL (si no existe)
-- ----------------------------------------------------------------------------
ALTER TABLE pedido ADD COLUMN IF NOT EXISTS estado VARCHAR(20) DEFAULT 'ENTREGADO';

UPDATE pedido SET estado = 'PENDIENTE' WHERE id_pedido IN (3, 6);
UPDATE pedido SET estado = 'CANCELADO' WHERE id_pedido = 5;
UPDATE pedido SET estado = 'ENTREGADO' WHERE id_pedido IN (2, 4, 7);

-- Asegurar líneas de prueba coincidentes con la migración
INSERT INTO pedido_producto (id_pedido, id_producto, cantidad, precio_unitario) VALUES
    (2, 4, 2, 600.00),
    (4, 3, 1, 550.00),
    (6, 3, 2, 500.00)
ON CONFLICT (id_pedido, id_producto) DO UPDATE 
SET cantidad = EXCLUDED.cantidad, precio_unitario = EXCLUDED.precio_unitario;

-- ============================================================================
-- 2. CONSULTAS EQUIVALENTES A MONGODB (Consignas 4 y 5)
-- ============================================================================

\echo '====================================================================='
\echo 'CONSULTA 4.a EQUIVALENTE: Todos los pedidos con identificador y estado'
\echo '====================================================================='
SELECT 
    p.id_pedido,
    p.estado
FROM pedido p
WHERE p.id_pedido BETWEEN 2 AND 7
ORDER BY p.id_pedido;

\echo '====================================================================='
\echo 'CONSULTA 4.b EQUIVALENTE: Filtrar pedidos por estado = ENTREGADO'
\echo '====================================================================='
SELECT 
    p.id_pedido,
    p.fecha,
    p.estado,
    c.nombre AS cliente_nombre,
    SUM(pp.cantidad * pp.precio_unitario) AS total
FROM pedido p
JOIN cliente c ON c.id_cliente = p.id_cliente
JOIN pedido_producto pp ON pp.id_pedido = p.id_pedido
WHERE p.id_pedido BETWEEN 2 AND 7 
  AND p.estado = 'ENTREGADO'
GROUP BY p.id_pedido, p.fecha, p.estado, c.nombre
ORDER BY p.id_pedido;

\echo '====================================================================='
\echo 'CONSULTA 4.c EQUIVALENTE: Pedidos que contienen el producto con ID 3'
\echo '====================================================================='
SELECT 
    p.id_pedido,
    p.estado,
    c.nombre AS cliente_nombre,
    pr.nombre AS producto_buscado,
    pp.cantidad,
    pp.precio_unitario,
    (pp.cantidad * pp.precio_unitario) AS subtotal_linea
FROM pedido p
JOIN cliente c ON c.id_cliente = p.id_cliente
JOIN pedido_producto pp ON pp.id_pedido = p.id_pedido
JOIN producto pr ON pr.id_producto = pp.id_producto
WHERE p.id_pedido BETWEEN 2 AND 7
  AND pp.id_producto = 3
ORDER BY p.id_pedido;

\echo '====================================================================='
\echo 'CONSULTA 4.d EQUIVALENTE: Pedidos con total superior a $2000.00'
\echo '====================================================================='
SELECT 
    p.id_pedido,
    c.nombre AS cliente_nombre,
    p.estado,
    SUM(pp.cantidad * pp.precio_unitario) AS total
FROM pedido p
JOIN cliente c ON c.id_cliente = p.id_cliente
JOIN pedido_producto pp ON pp.id_pedido = p.id_pedido
WHERE p.id_pedido BETWEEN 2 AND 7
GROUP BY p.id_pedido, c.nombre, p.estado
HAVING SUM(pp.cantidad * pp.precio_unitario) > 2000.00
ORDER BY p.id_pedido;

\echo '====================================================================='
\echo 'CONSIGNA 5: RESUMEN DE VERIFICACIÓN CRUZADA (POSTGRESQL VS MONGODB)'
\echo '====================================================================='
SELECT 
    'Estado ENTREGADO' AS filtro,
    COUNT(DISTINCT p.id_pedido) AS cantidad_pedidos,
    STRING_AGG(p.id_pedido::text, ', ' ORDER BY p.id_pedido) AS ids_recuperados
FROM pedido p
WHERE p.id_pedido BETWEEN 2 AND 7 AND p.estado = 'ENTREGADO'
UNION ALL
SELECT 
    'Contiene Producto ID 3' AS filtro,
    COUNT(DISTINCT p.id_pedido) AS cantidad_pedidos,
    STRING_AGG(p.id_pedido::text, ', ' ORDER BY p.id_pedido) AS ids_recuperados
FROM pedido p
JOIN pedido_producto pp ON pp.id_pedido = p.id_pedido
WHERE p.id_pedido BETWEEN 2 AND 7 AND pp.id_producto = 3;
