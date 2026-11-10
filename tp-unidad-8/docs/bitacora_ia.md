# Bitácora de Interacción con Inteligencia Artificial - Food Store Unidad 8
**Estudiante:** Fabrizio Simon  
**Asignatura:** Base de Datos II · Tecnicatura Universitaria en Programación (UTN)  
**Proyecto:** Food Store Móvil (SQLite & Sincronización con PostgreSQL)  
**Ciclo Lectivo:** 2026  

---

## 1. Registro Cronológico de Prompts y Decisiones

### Entrada 1: Modelado de Tablas Estrictas en SQLite (Consigna 1.b)
* **Lo que le pedí a la IA:**  
  "Diseñá el script DDL `schema_sqlite.sql` para SQLite con las cuatro tablas requeridas (`producto_cache`, `pedido_borrador`, `item_borrador`, `cola_sync`), asegurando integridad y claves foráneas."
* **Lo que la IA propuso:**  
  La IA propuso usar tipos estándar flexibles de SQLite (`INTEGER PRIMARY KEY AUTOINCREMENT` para los pedidos locales y campos `NUMERIC` con decimales para los precios).
* **Lo que acepté:**  
  Acepté la definición de las tablas y la activación inicial obligatoria de `PRAGMA foreign_keys = ON;`.
* **Lo que descarté y por qué (Corrección humana):**  
  Descarté el uso de `AUTOINCREMENT` autonumérico y los importes con decimales flotantes:
  1. En una arquitectura distribuida donde varias tablets toman pedidos en simultáneo fuera de línea, usar secuencias autonuméricas (`1, 2, 3...`) provocaría colisiones inevitables al momento de sincronizar. Se reemplazó por identificadores universales **UUID v4** en formato texto (`TEXT PRIMARY KEY`).
  2. Descarté decimales y afinidad laxa: se exigió la cláusula **`STRICT`** en las 4 tablas (incorporada en SQLite 3.37+) y se fijó el precio como **`INT` en centavos** (`precio_centavos`). Esto previene discrepancias de redondeo binario y prohíbe que SQLite almacene cadenas o tipos inválidos en columnas numéricas.

---

### Entrada 2: Algoritmo de Conciliación del Semáforo (Consigna 2.b)
* **Lo que le pedí a la IA:**  
  "Escribí una consulta SQL en SQLite que actualice la tabla `cola_sync` comparando los pedidos pendientes con `snapshot_servidor`, clasificando en RECHAZADO, CONFLICTO y SIMULADO_APROBADO."
* **Lo que la IA propuso:**  
  La IA propuso una serie de sentencias `UPDATE` independientes con subconsultas correlacionadas `WHERE EXISTS (...)`, evaluando primero el precio y luego el stock.
* **Lo que acepté:**  
  Acepté la lógica de comparación entre `precio_centavos_visto` y el precio del snapshot.
* **Lo que descarté y por qué (Corrección humana):**  
  Descarté las subconsultas múltiples con orden arbitrario:
  1. Si un producto cambió de precio pero **además se quedó sin stock**, la propuesta de la IA lo clasificaba erróneamente en `CONFLICTO` (amarillo) en lugar de `RECHAZADO` (rojo). Se impuso una jerarquía estricta de evaluación: **Rojo > Amarillo > Verde**.
  2. Se optimizó la consulta mediante un **Common Table Expression (CTE) con agregación condicional (`SUM(...)`)** y la sintaxis **`UPDATE ... FROM`** soportada en SQLite moderno, reduciendo la complejidad de múltiples pasadas a una única evaluación atómica y determinística.
  3. Se incluyó el soporte para booleanos de PostgreSQL (`'t'`, `'f'`), ya que el CSV exportado por `psql` no usa números binarios sino caracteres de texto.

---

### Entrada 3: Code Review de Mantenimiento de Base de Datos (Consigna 3.c)
* **Lo que le pedí a la IA:**  
  "Revisá los scripts de optimización y mantenimiento de la Unidad 6 y recomendá mejoras de performance para tablas con alto volumen de pedidos."
* **Lo que la IA propuso:**  
  La IA recomendó ejecutar `VACUUM FULL` diariamente dentro del script de mantenimiento para "recuperar espacio en disco y desfragmentar completamente las tablas".
* **Lo que acepté:**  
  Acepté la recomendación de analizar índices y regenerar estadísticas con `ANALYZE`.
* **Lo que descarté y por qué (Corrección humana fundamentada):**  
  **DESCARTÉ CATEGÓRICAMENTE `VACUUM FULL`:**
  - `VACUUM FULL` adquiere un bloqueo exclusivo absoluto (`ACCESS EXCLUSIVE LOCK`) sobre toda la tabla, impidiendo cualquier lectura (`SELECT`) y escritura (`INSERT`/`UPDATE`) por parte de la aplicación web y las tablets durante minutos u horas.
  - En un entorno de producción de Food Store con 200,000 pedidos, bloquear las tablas degrada el servicio y rompe la disponibilidad operativa.
  - Se mantuvo en su lugar el mantenimiento estándar concurrente con `VACUUM (ANALYZE, VERBOSE)`, que limpia tuplas muertas sin bloquear el acceso de los usuarios.

---

## 2. Conclusión sobre el Uso de Herramientas de IA
La inteligencia artificial es sumamente productiva para estructurar esqueletos iniciales de consultas y scripts, pero **carece de criterio de producción si no se la audita**:
- Tiende a obviar la concurrencia distribuida (generando autonuméricos en lugar de UUIDs).
- Ignora el impacto de bloqueos en bases transaccionales (`VACUUM FULL` vs `VACUUM`).
- Puede alterar prioridades en máquinas de estados si no se formalizan previamente los requisitos (como se hizo en la spec con notación EARS).
Toda línea de código generada fue leída, testeada en SQLite/PostgreSQL y validada manualmente.
