# Documento de Diseño Técnico (Design Document) - Sincronización Móvil Food Store
**Materia:** Base de Datos II · Tecnicatura Universitaria en Programación (UTN)  
**Proyecto:** Food Store en la feria · Unidad 8  
**Autor:** Fabrizio Simon  
**Herramienta de especificación:** Kiro Specification Engine  

---

## 1. Arquitectura y Topología de Datos

El módulo móvil resuelve la operación del Food Truck en ferias gastronómicas con conectividad intermitente o nula mediante una arquitectura **Offline-First**:

```
[ Servidor Central: PostgreSQL 18 ] (Fuente de Verdad Única - OLTP)
         │  
         │ (Exportación periódica / Descarga de catálogo)
         ▼
[ CSV Instantánea: v_snapshot_movil ]
         │  
         │ (Importación a la tablet)
         ▼
[ Tablet / Móvil: SQLite 3.50+ (STRICT) ]
  ├── snapshot_servidor   (Copia cruda del CSV del servidor)
  ├── producto_cache      (Catálogo local offline para ventas)
  ├── pedido_borrador     (Encabezado de orden local con UUID)
  ├── item_borrador       (Detalle de líneas con precio congelado)
  └── cola_sync           (Cola de sincronización y estado del semáforo)
```

---

## 2. Decisiones de Diseño en SQLite

1. **Tablas Estrictas (`STRICT`):**  
   Se utiliza la cláusula `STRICT` en las cuatro tablas locales para forzar tipado estático (evitando la permisividad histórica de afinidad de SQLite). Esto garantiza que no ingresen strings en campos numéricos ni datos truncados.
2. **Precios en Centavos (`INTEGER`):**  
   Para eliminar errores de redondeo de punto flotante en dispositivos móviles, todos los importes monetarios se manejan como enteros en centavos (`precio_centavos = ROUND(precio * 100)`).
3. **Identificadores UUID:**  
   Los identificadores locales (`id_local`, `solicitud_uuid`) se generan como cadenas UUID v4 para evitar colisiones entre múltiples tablets concurrentes que no pueden coordinar secuencias autonuméricas centralizadas.
4. **Activación de Claves Foráneas:**  
   Se impone `PRAGMA foreign_keys = ON;` al abrir la conexión local para impedir ítems huérfanos o pedidos que apunten a productos inexistentes.

---

## 3. Modelo del Semáforo de Sincronización

El motor de conciliación evalúa cada solicitud con estado `'PENDIENTE'` cruzándola con la instantánea más reciente del servidor (`snapshot_servidor`):

* **Prioridad 1: ROJO (`RECHAZADO`)**  
  Se dispara si algún ítem incumple integridad estructural:
  - El producto no existe en el snapshot (`s.id IS NULL`).
  - El producto está inactivo (`s.disponible IN ('f', '0')`).
  - El producto fue dado de baja lógica / lápida activa (`s.eliminado IN ('t', '1')`).
  - La cantidad pedida supera el stock físico del servidor (`i.cantidad > s.stock`).
* **Prioridad 2: AMARILLO (`CONFLICTO`)**  
  No hay causales de rechazo, pero el precio visto por el cliente difiere del precio vigente en el servidor (`i.precio_centavos_visto <> s.precio_centavos`). Permite renegociación o aceptación en mostrador sin anular la solicitud.
* **Prioridad 3: VERDE (`SIMULADO_APROBADO`)**  
  Todos los ítems verifican stock, vigencia y paridad exacta de precio.

---

## 4. Garantía de Integridad y Límite de Autoridad
* **Aislamiento del Servidor:** La ejecución del semáforo ocurre estrictamente en el entorno de la tablet. No se ejecutan `UPDATE` ni `INSERT` sobre las tablas transaccionales de PostgreSQL (`pedido`, `pedido_producto`, `producto.stock`).
* **Estado de Simulación:** El valor `'SIMULADO_APROBADO'` representa una pre-validación teórica; no constituye una transacción fiscal ni disminuye inventario hasta que una sincronización formal sea autorizada por el backend transaccional.
