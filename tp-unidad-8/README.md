# Food Store en la Feria: La Base de la Tablet y el Cierre de la Capa de Datos (TP N.° 8)

**Asignatura:** Base de Datos II · Tecnicatura Universitaria en Programación  
**Institución:** Universidad Tecnológica Nacional (UTN)  
**Autor:** Fabrizio Simon  
**Herramientas:** PostgreSQL 18 · SQLite 3.50+ (STRICT) · Python 3.10+ · Kiro & OpenCode  
**Fecha de Entrega:** Semana 13 - Ciclo Lectivo 2026  

---

## 1. Estructura del Proyecto

```
tp-unidad-8/
├── README.md                      # Guía de reproducción y ensayo de defensa oral
├── movil/
│   ├── schema_sqlite.sql          # DDL SQLite (STRICT, claves foráneas, centavos)
│   ├── pruebas_sqlite.sql         # Pruebas de transacciones, rollback, C1 y C7
│   ├── semaforo.sql               # Algoritmo de evaluación jerárquico (Rojo/Amarillo/Verde)
│   ├── simulador.py               # Runner automatizado de simulación y auditoría
│   ├── servidor_snapshot.csv      # Instantánea exportada desde PostgreSQL (v_snapshot_movil)
│   ├── foodstore_movil.db         # Base SQLite local generada con la simulación
│   └── evidencia_simulacion.txt   # Registro de salida de pruebas y verificación en PostgreSQL
└── docs/
    ├── informe.pdf                # Informe técnico formal (Consignas 1.a, 2.c, 3.a, 3.b, 3.c)
    ├── informe.md                 # Documento fuente en Markdown del informe
    ├── kiro/
    │   ├── requirements.md        # Especificación EARS de 5 requisitos ligados a casos
    │   ├── design.md              # Documento de arquitectura, tipado estricto y semáforo
    │   └── tasks.md               # Plan de tareas de implementación Kiro
    ├── bitacora_ia.md             # Registro de prompts, decisiones y refutaciones a la IA
    └── DUIA.md                    # Declaración de Uso de Inteligencia Artificial (UTN)
```

---

## 2. Guía de Reproducción Paso a Paso (Desde Cero)

### Requisitos Previos
* **PostgreSQL 16+** en ejecución local (`localhost:5432`) con la base de datos `foodstore`.
* **Python 3.10+** (incluye módulo estándar `sqlite3` compilado con SQLite 3.37+ para soporte de `STRICT`).

### Paso 1: Crear la vista en PostgreSQL y exportar la instantánea
Abrir una terminal de PostgreSQL (`psql`) conectada a la base de pruebas:
```sql
-- Agregar columna de baja lógica si no existe
ALTER TABLE producto ADD COLUMN IF NOT EXISTS eliminado BOOLEAN NOT NULL DEFAULT FALSE;

-- Crear vista para la app móvil (centavos enteros y banderas booleanas)
CREATE OR REPLACE VIEW v_snapshot_movil AS
SELECT 
    id_producto AS id,
    nombre,
    ROUND(precio_lista * 100)::INTEGER AS precio_centavos,
    stock,
    activo AS disponible,
    eliminado
FROM producto;

-- Exportar CSV
\copy (SELECT * FROM v_snapshot_movil) TO 'movil/servidor_snapshot.csv' CSV HEADER
```

### Paso 2: Ejecutar la simulación completa
Desde la carpeta `tp-unidad-8/movil`:
```bash
python simulador.py
```
Este script:
1. Crea `foodstore_movil.db` desde cero aplicando `schema_sqlite.sql`.
2. Importa `servidor_snapshot.csv` en `snapshot_servidor` y carga `producto_cache`.
3. Prueba C1 (catálogo offline) y C7 (violación de constraints).
4. Ejecuta sucesivamente los casos C2 (conflicto y resolución), C3 (quiebre de stock), C4 (baja lógica / lápida), C5 (aprobación limpia) y C6 (idempotencia ante reenvío de UUID).
5. Ejecuta una auditoría final sobre PostgreSQL demostrando que el stock y la cantidad de pedidos permanecieron **invariables**.

---

## 3. Ensayo de Defensa Oral (10 Minutos)

### Minuto 0 a 3: El Mapa de la Capa de Datos y la Regla de Oro
* *"Buenas tardes profesor/a. En este trabajo cerramos la arquitectura integral de datos de Food Store conectando tres motores con propósitos bien diferenciados:"*
  - **PostgreSQL:** Es nuestro núcleo transaccional OLTP y la única fuente de verdad (Single Source of Truth). Solo él confirma ventas fiscales, gobierna la auditoría y tiene autoridad sobre el inventario y los precios oficiales.
  - **MongoDB (Unidad 7):** Actúa como un *Read Model* desnormalizado bajo arquitectura CQRS. Embebe las líneas y los datos de clientes en documentos JSON para alimentar la tienda web con baja latencia sin saturar a PostgreSQL con JOINs complejos.
  - **SQLite (Unidad 8):** Resuelve la operatoria desconectada (Offline-First) del Food Truck en una feria gastronómica sin señal de telefonía. La tablet almacena una caché local liviana y genera borradores.
* *"La regla de oro que rige toda la solución es: **El móvil propone, el servidor dispone**. La tablet jamás puede descontar stock ni actualizar precios directamente; el estado `SIMULADO_APROBADO` es una pre-validación teórica, no una venta real."*

### Minuto 3 a 7: Demostración de un Caso en Vivo (Caso C2 o C4)
* *"Les muestro el funcionamiento del semáforo con el **Caso C2**: subida de precio en el servidor."*
  1. *El mozo toma un pedido fuera de línea para una pizza Muzza a $100.00 (10000 centavos).*
  2. *En el servidor central, la inflación obliga a subir el precio a $125.00 (12500 centavos).*
  3. *Al correr la sincronización contra el nuevo snapshot, el semáforo detecta que hay stock pero el precio no coincide: clasifica la solicitud en **`CONFLICTO` (amarillo)**, evitando vender por debajo del costo.*
  4. *En mostrador, el cliente acepta la diferencia de $25. El cajero actualiza el precio en el borrador local y emite un nuevo reintento de sincronización.*
  5. *El semáforo vuelve a evaluar y esta vez la solicitud pasa a **`SIMULADO_APROBADO` (verde)**.*
* *"Y acá podemos ver la comprobación en PostgreSQL: corremos `SELECT COUNT(*) FROM pedido` y `SELECT stock FROM producto`, y comprobamos que en la base central no se insertó ninguna fila ni se tocó el stock. La transacción fiscal solo ocurrirá cuando el backend central la procese formalmente."*

### Minuto 7 a 10: Un Hallazgo y Refutación a la Inteligencia Artificial
* *"Para cerrar, en la parada de Code Review le pedimos a la IA que examine los scripts de mantenimiento y performance de la Unidad 6."*
  - *La IA propuso incluir `VACUUM FULL` diariamente para desfragmentar las tablas con alto volumen.*
  - ***Lo descartamos categóricamente con fundamento técnico:** `VACUUM FULL` solicita un bloqueo exclusivo absoluto (`ACCESS EXCLUSIVE LOCK`), impidiendo tanto lecturas como escrituras. En una base como Food Store con 200,000 pedidos, ejecutar `VACUUM FULL` tumbaría la tienda web y paralizaría las tablets.*
  - *En su lugar, mantuvimos `VACUUM (ANALYZE, VERBOSE)` concurrente.*
  - *Asimismo, en SQLite la IA propuso identificadores autonuméricos simples; los descartamos por colisión en dispositivos distribuidos y los reemplazamos por **UUIDs**, aplicando además tablas **`STRICT`** e importes expresados estrictamente en **centavos enteros** para evitar errores de punto flotante.*
