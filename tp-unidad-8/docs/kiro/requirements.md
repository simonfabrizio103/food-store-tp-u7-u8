# Especificación de Requisitos de Software (EARS) - Sincronización Móvil Food Store
**Materia:** Base de Datos II · Tecnicatura Universitaria en Programación (UTN)  
**Proyecto:** Food Store en la feria · Unidad 8  
**Autor:** Fabrizio Simon  
**Herramienta de especificación:** Kiro Specification Engine  

---

## 1. Contexto y Regla de Oro
> **Regla de oro:** *El móvil propone, el servidor dispone.*  
> La tablet opera en modo desconectado (offline) en la feria de comidas, consultando únicamente un catálogo local en caché y generando borradores de venta locales. El servidor central (PostgreSQL) es la única fuente de verdad y autoridad final sobre precios, stock, estado de productos y registro definitivo de ventas.

---

## 2. Requisitos Funcionales en Notación EARS

### REQ-01: Detección de Discrepancia de Precios (Conflicto)
* **Requisito:** `WHEN` el precio actual en la instantánea del servidor (`snapshot_servidor.precio_centavos`) difiere del precio registrado en el ítem del borrador (`item_borrador.precio_centavos_visto`) y se cumplen todas las condiciones de stock y disponibilidad, `THE SYSTEM SHALL` marcar el estado de la solicitud en `cola_sync` como `'CONFLICTO'` y detallar el motivo del cambio de tarifa.
* **Caso de prueba asociado:** `C2` (Modificación de precio posterior en servidor).

---

### REQ-02: Control de Stock Insuficiente (Rechazo)
* **Requisito:** `WHEN` la cantidad solicitada de uno o más ítems en el borrador supera el stock físico disponible en el servidor (`item_borrador.cantidad > snapshot_servidor.stock`), `THE SYSTEM SHALL` marcar la solicitud como `'RECHAZADO'` especificando en el motivo el quiebre de stock.
* **Caso de prueba asociado:** `C3` (Borrador por cantidad superior al stock remanente).

---

### REQ-03: Producto Inactivo o Baja Lógica (Rechazo por Descatalogado)
* **Requisito:** `WHEN` uno o más productos contenidos en el borrador no existen en el servidor, figuran como no disponibles (`disponible = 0 / 'f'`) o fueron dados de baja lógica (`eliminado = 1 / 't'`), `THE SYSTEM SHALL` marcar la solicitud como `'RECHAZADO'` informando que el producto se encuentra inactivo o fuera de catálogo.
* **Caso de prueba asociado:** `C4` (Baja lógica mediante lápida/tombstone tras la toma del pedido).

---

### REQ-04: Validación Exitosa de Solicitud (Simulación Aprobada)
* **Requisito:** `WHEN` todos los productos del borrador existen, están disponibles, no están eliminados, sus precios coinciden exactamente y el stock del servidor cubre la cantidad solicitada, `THE SYSTEM SHALL` marcar la solicitud como `'SIMULADO_APROBADO'`.
* **Caso de prueba asociado:** `C5` (Borrador sin discrepancias con el servidor).

---

### REQ-05: Idempotencia y Deduplicación de Transmisión
* **Requisito:** `WHEN` la tablet o el cliente reenvía una solicitud con un identificador unívoco (`solicitud_uuid`) previamente procesado o presente en `cola_sync`, `THE SYSTEM SHALL` rechazar la inserción por restricción de clave primaria (`PRIMARY KEY`) y abstenerse de reevaluar o alterar el estado existente.
* **Caso de prueba asociado:** `C6` (Reenvío idéntico por reintentos de red o fallas de ACK).
