-- ============================================================================
-- SCRIPT: semaforo.sql
-- DESCRIPCIÓN: Algoritmo de evaluación del semáforo de sincronización offline
--              Compara solicitudes PENDIENTE de la tablet contra snapshot_servidor
-- PROYECTO: Food Store Móvil - Unidad 8
-- AUTOR: Fabrizio Simon
-- ============================================================================

-- El semáforo evalúa de forma jerárquica:
-- 1. ROJO (RECHAZADO): Inexistente, no disponible ('f' o 0), dado de baja ('t' o 1), o cantidad > stock
-- 2. AMARILLO (CONFLICTO): Sin causales de rechazo, pero precio_visto <> precio_centavos del servidor
-- 3. VERDE (SIMULADO_APROBADO): Coincidencia total en precio, disponibilidad y stock suficiente

WITH evaluacion_solicitudes AS (
    SELECT 
        cs.solicitud_uuid,

        -- 1. CÁLCULO DEL ESTADO RESULTANTE (Jerarquía Rojo > Amarillo > Verde)
        CASE 
            -- Prioridad 1: ROJO (RECHAZADO)
            WHEN SUM(
                CASE 
                    WHEN s.id IS NULL THEN 1                                          -- No existe en servidor
                    WHEN s.disponible NOT IN ('t', '1', 'true', 'TRUE') THEN 1        -- No activo/disponible
                    WHEN s.eliminado IN ('t', '1', 'true', 'TRUE') THEN 1             -- Baja lógica / lápida
                    WHEN ib.cantidad > s.stock THEN 1                                 -- Quiebre de stock
                    ELSE 0 
                END
            ) > 0 THEN 'RECHAZADO'

            -- Prioridad 2: AMARILLO (CONFLICTO)
            WHEN SUM(
                CASE 
                    WHEN ib.precio_centavos_visto <> s.precio_centavos THEN 1 
                    ELSE 0 
                END
            ) > 0 THEN 'CONFLICTO'

            -- Prioridad 3: VERDE (SIMULADO_APROBADO)
            ELSE 'SIMULADO_APROBADO'
        END AS nuevo_estado,

        -- 2. CÁLCULO DEL MOTIVO EXPLICATIVO
        CASE 
            WHEN SUM(CASE WHEN s.id IS NULL THEN 1 ELSE 0 END) > 0 
                THEN 'RECHAZADO: uno o más productos no existen en el servidor'
            WHEN SUM(CASE WHEN s.disponible NOT IN ('t', '1', 'true', 'TRUE') THEN 1 ELSE 0 END) > 0 
                THEN 'RECHAZADO: producto marcado como no disponible en el servidor'
            WHEN SUM(CASE WHEN s.eliminado IN ('t', '1', 'true', 'TRUE') THEN 1 ELSE 0 END) > 0 
                THEN 'RECHAZADO: producto dado de baja lógica (lápida activa) en el servidor'
            WHEN SUM(CASE WHEN ib.cantidad > s.stock THEN 1 ELSE 0 END) > 0 
                THEN 'RECHAZADO: stock insuficiente en el servidor para cubrir la cantidad'
            WHEN SUM(CASE WHEN ib.precio_centavos_visto <> s.precio_centavos THEN 1 ELSE 0 END) > 0 
                THEN 'CONFLICTO: el precio del servidor cambió respecto al visto en la tablet'
            ELSE 'SIMULADO_APROBADO: validación exitosa (precio, stock y vigencia verificados)'
        END AS nuevo_motivo

    FROM cola_sync cs
    JOIN item_borrador ib ON cs.id_local = ib.id_local
    LEFT JOIN snapshot_servidor s ON ib.producto_id = s.id
    WHERE cs.estado = 'PENDIENTE'
    GROUP BY cs.solicitud_uuid
)
UPDATE cola_sync
SET 
    estado = ev.nuevo_estado,
    motivo = ev.nuevo_motivo
FROM evaluacion_solicitudes ev
WHERE cola_sync.solicitud_uuid = ev.solicitud_uuid;
