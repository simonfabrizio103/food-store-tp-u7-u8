# Plan de Tareas de Implementación (Tasks) - Food Store Móvil
**Materia:** Base de Datos II · Tecnicatura Universitaria en Programación (UTN)  
**Proyecto:** Food Store en la feria · Unidad 8  
**Autor:** Fabrizio Simon  
**Herramienta de especificación:** Kiro Specification Engine  

---

- [ ] **Tarea 1: Esquema de Base Local SQLite (Consigna 1.b)**
  - [ ] 1.1 Configurar `PRAGMA foreign_keys = ON;`.
  - [ ] 1.2 Definir tabla `producto_cache` en modo `STRICT` con checks de precio no negativo y flags binarios (0 o 1).
  - [ ] 1.3 Definir tabla `pedido_borrador` en modo `STRICT` con check de formas de pago válidas (`EFECTIVO`, `TARJETA`, `TRANSFERENCIA`).
  - [ ] 1.4 Definir tabla `item_borrador` en modo `STRICT` con checks de cantidad > 0 y claves foráneas hacia pedido y catálogo.
  - [ ] 1.5 Definir tabla `cola_sync` en modo `STRICT` con check de estados válidos (`PENDIENTE`, `CONFLICTO`, `RECHAZADO`, `SIMULADO_APROBADO`).

- [ ] **Tarea 2: Pruebas Unitarias de Transacciones y Restricciones Locales (Consigna 1.c)**
  - [ ] 2.1 Demostrar atomicidad local mediante `BEGIN ... COMMIT` para alta de borrador completa.
  - [ ] 2.2 Demostrar reversión limpia mediante `BEGIN ... ROLLBACK` ante cancelación de venta.
  - [ ] 2.3 Ejecutar Caso C1: consulta de catálogo offline con filtros de disponibilidad y stock remanente.
  - [ ] 2.4 Ejecutar Caso C7: verificación de fallos ante cantidad = 0 y clave foránea de producto inexistente.

- [ ] **Tarea 3: Instantánea del Servidor Central (Consigna 2.a)**
  - [ ] 3.1 Crear vista `v_snapshot_movil` en PostgreSQL con stock, precio en centavos y marcas de baja lógica.
  - [ ] 3.2 Exportar datos a `servidor_snapshot.csv` mediante `\copy`.
  - [ ] 3.3 Importar snapshot a tabla `snapshot_servidor` en SQLite y sincronizar `producto_cache`.

- [ ] **Tarea 4: Lógica del Semáforo y Casos de Prueba (Consigna 2.b y 2.c)**
  - [ ] 4.1 Implementar consulta de semáforo jerárquico (Rojo > Amarillo > Verde) en `semaforo.sql` y `simulador.py`.
  - [ ] 4.2 Probar Caso C2: discrepancia de precio -> `CONFLICTO` y posterior aceptación -> `SIMULADO_APROBADO`.
  - [ ] 4.3 Probar Caso C3: quiebre de stock -> `RECHAZADO`.
  - [ ] 4.4 Probar Caso C4: baja lógica de producto en servidor -> `RECHAZADO`.
  - [ ] 4.5 Probar Caso C5: solicitud sin alteraciones -> `SIMULADO_APROBADO`.
  - [ ] 4.6 Probar Caso C6: deduplicación e idempotencia por colisión de UUID.
  - [ ] 4.7 Verificar invariabilidad de stock y órdenes en PostgreSQL tras simulaciones.

- [ ] **Tarea 5: Análisis de Arquitectura y Mantenimiento (Consigna 3.a, 3.b, 3.c)**
  - [ ] 5.1 Confeccionar mapa de la capa de datos entre PostgreSQL, MongoDB y SQLite con matrices de autoridad.
  - [ ] 5.2 Formular plan de contingencia ante restore de backups obsoletos y revisión de cola de conflictos.
  - [ ] 5.3 Conducir Code Review con IA sobre scripts de la cursada, documentando 3 hallazgos y fundamentando 1 descarte crítico.

- [ ] **Tarea 6: Artefactos de Entrega y Compilación del Informe (Consigna 4 y Entrega)**
  - [ ] 6.1 Redactar Bitácora de Interacción con IA (`bitacora_ia.md`) y Declaración Jurada (`DUIA.md`).
  - [ ] 6.2 Redactar `README.md` con guía de reproducción paso a paso y ensayo de defensa oral de 10 minutos.
  - [ ] 6.3 Redactar y compilar `informe.pdf` respetando el límite máximo de 6 páginas con diseño profesional.
