-- ============================================================================
-- SCRIPT: pruebas_sqlite.sql
-- DESCRIPCIÓN: Pruebas unitarias de esquema, transacciones y casos C1 y C7
-- PROYECTO: Food Store Móvil - Unidad 8
-- AUTOR: Fabrizio Simon
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- CARGA DE PRODUCTOS DE PRUEBA EN PRODUCTO_CACHE
-- (Simula catálogo precargado en la tablet)
-- ----------------------------------------------------------------------------
INSERT INTO producto_cache (id, nombre, precio_centavos, stock_visto, disponible, eliminado, fecha_copia) VALUES
(1, 'Hamburguesa Clásica', 120000, 25, 1, 0, '2026-11-10 10:00:00'),
(2, 'Papas Rústicas',       45000, 50, 1, 0, '2026-11-10 10:00:00'),
(3, 'Cerveza Artesanal IPA', 60000, 30, 1, 0, '2026-11-10 10:00:00'),
(4, 'Gaseosa Cola 500ml',    35000, 40, 1, 0, '2026-11-10 10:00:00'),
(5, 'Sándwich Vegano',       95000,  0, 1, 0, '2026-11-10 10:00:00'), -- Sin stock
(6, 'Postre Chocotorta',     50000, 10, 0, 0, '2026-11-10 10:00:00'), -- No disponible
(7, 'Combo Promo Antigua',   80000, 15, 1, 1, '2026-11-10 10:00:00'); -- Eliminado (lápida)

-- ----------------------------------------------------------------------------
-- 1.A OPERACIÓN GUARDADA CON ÉXITO (BEGIN ... COMMIT)
-- Alta atómica de un borrador completo: cabecera + 2 ítems + solicitud sync
-- ----------------------------------------------------------------------------
BEGIN TRANSACTION;

INSERT INTO pedido_borrador (id_local, usuario, forma_pago, fecha)
VALUES ('b1000000-0000-0000-0000-000000000001', 'mozo_feria_1', 'EFECTIVO', '2026-11-10 14:15:00');

INSERT INTO item_borrador (id_local, producto_id, cantidad, precio_centavos_visto)
VALUES 
('b1000000-0000-0000-0000-000000000001', 1, 2, 120000), -- 2 Hamburguesas Clásicas
('b1000000-0000-0000-0000-000000000001', 2, 1, 45000);  -- 1 Papas Rústicas

INSERT INTO cola_sync (solicitud_uuid, id_local, estado, motivo)
VALUES ('s1000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001', 'PENDIENTE', 'Alta de pedido en feria');

COMMIT;

-- Verificación de inserción exitosa
SELECT pb.id_local, pb.usuario, pb.forma_pago, COUNT(ib.producto_id) AS total_items, cs.estado
FROM pedido_borrador pb
JOIN item_borrador ib ON pb.id_local = ib.id_local
JOIN cola_sync cs ON pb.id_local = cs.id_local
WHERE pb.id_local = 'b1000000-0000-0000-0000-000000000001'
GROUP BY pb.id_local, pb.usuario, pb.forma_pago, cs.estado;


-- ----------------------------------------------------------------------------
-- 1.B OPERACIÓN CANCELADA Y DESHECHA (BEGIN ... ROLLBACK)
-- El cliente cancela en mostrador antes de enviar a la cola de sincronización
-- ----------------------------------------------------------------------------
BEGIN TRANSACTION;

INSERT INTO pedido_borrador (id_local, usuario, forma_pago, fecha)
VALUES ('b2000000-0000-0000-0000-000000000002', 'mozo_feria_2', 'TARJETA', '2026-11-10 14:20:00');

INSERT INTO item_borrador (id_local, producto_id, cantidad, precio_centavos_visto)
VALUES ('b2000000-0000-0000-0000-000000000002', 3, 4, 60000);

-- Se aborta la operación:
ROLLBACK;

-- Verificación de que no quedaron rastros del borrador cancelado
SELECT COUNT(*) AS filas_borrador_cancelado
FROM pedido_borrador
WHERE id_local = 'b2000000-0000-0000-0000-000000000002';


-- ----------------------------------------------------------------------------
-- 2. CASO C1: CONSULTA DEL CATÁLOGO DISPONIBLE SIN CONECTARSE AL SERVIDOR
-- La tablet muestra sólo los productos que están activos, no eliminados y con stock
-- ----------------------------------------------------------------------------
SELECT 
    id, 
    nombre, 
    (precio_centavos / 100.0) AS precio_pesos, 
    stock_visto,
    disponible,
    eliminado
FROM producto_cache
WHERE disponible = 1 
  AND eliminado = 0 
  AND stock_visto > 0
ORDER BY id;


-- ----------------------------------------------------------------------------
-- 3. CASO C7: INTEGRIDAD Y CONTROL DE ERRORES (CANTIDAD 0 Y PRODUCTO INEXISTENTE)
-- Ambos deben fallar y la tabla no debe incorporar registros espurios
-- ----------------------------------------------------------------------------

-- 3.1 Intento de borrador para probar fallos:
INSERT INTO pedido_borrador (id_local, usuario, forma_pago, fecha)
VALUES ('b7000000-0000-0000-0000-000000000007', 'cajero_test', 'TRANSFERENCIA', '2026-11-10 14:30:00');

-- 3.2 Intento de insertar ítem con cantidad = 0 (Debe fallar: CHECK constraint failed: cantidad > 0)
-- INSERT INTO item_borrador (id_local, producto_id, cantidad, precio_centavos_visto)
-- VALUES ('b7000000-0000-0000-0000-000000000007', 1, 0, 120000);

-- 3.3 Intento de insertar ítem con producto inexistente (Debe fallar: FOREIGN KEY constraint failed)
-- INSERT INTO item_borrador (id_local, producto_id, cantidad, precio_centavos_visto)
-- VALUES ('b7000000-0000-0000-0000-000000000007', 99999, 1, 50000);

-- Verificación de que la tabla item_borrador no contiene ningún ítem para b7000000...:
SELECT COUNT(*) AS total_items_invalidos
FROM item_borrador
WHERE id_local = 'b7000000-0000-0000-0000-000000000007';
