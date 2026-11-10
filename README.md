# Food Store — Trabajos Prácticos (Unidades 7 y 8)
**Tecnicatura Universitaria en Programación — Base de Datos II (UTN FRM)**  
**Ciclo Lectivo:** 2026 | **Estudiante:** Fabrizio Simon  
**Repositorio Oficial:** `https://github.com/simonfabrizio103/food-store-tp-u7-u8`  

---

## 📌 Contenido del Repositorio

Este repositorio aloja las entregas y desarrollos correspondientes al segundo tramo de la materia (Unidades 7 y 8) para el proyecto integrador **Food Store**:

```text
food-store-tp-u7-u8/
├── tp-unidad-7/         # Unidad 7: NoSQL y nuevas formas de almacenamiento (MongoDB & PostgreSQL)
│   ├── consultas_mongodb.js
│   ├── consultas_postgresql.sql
│   ├── ejecutar_mongodb.js
│   ├── evidencia_mongodb.txt
│   ├── SPEC_U7.md
│   ├── BITACORA.md
│   ├── informe_u7.md
│   ├── informe_u7.pdf   # Informe oficial de entrega (2 páginas)
│   ├── generar_pdf_u7.py
│   ├── package.json
│   └── README.md
│
├── tp-unidad-8/         # Unidad 8: Food Store en la feria: la base de la tablet y el cierre de datos
│   ├── README.md        # Guía de reproducción paso a paso y ensayo oral de defensa
│   ├── movil/
│   │   ├── schema_sqlite.sql        # Esquema DDL SQLite en modo STRICT con centavos enteros
│   │   ├── pruebas_sqlite.sql       # Pruebas de transacciones, rollback, C1 y C7
│   │   ├── semaforo.sql             # Algoritmo de evaluación jerárquico del semáforo
│   │   ├── simulador.py             # Ejecutor integral de simulación y auditoría
│   │   ├── servidor_snapshot.csv    # Instantánea exportada desde PostgreSQL (v_snapshot_movil)
│   │   ├── foodstore_movil.db       # Base SQLite local generada tras las pruebas
│   │   └── evidencia_simulacion.txt # Log completo de salida y verificación en PostgreSQL
│   └── docs/
│       ├── informe.pdf              # Informe técnico consolidado (2 páginas, máximo permitido: 6)
│       ├── informe.md               # Fuente en Markdown del informe
│       ├── kiro/
│       │   ├── requirements.md      # Especificación formal de requisitos EARS
│       │   ├── design.md            # Documento de diseño arquitectónico y Offline-First
│       │   └── tasks.md             # Plan de tareas Kiro
│       ├── bitacora_ia.md           # Registro de prompts y refutación crítica a la IA
│       └── DUIA.md                  # Declaración de Uso de Inteligencia Artificial (UTN)
│
└── README.md            # Este índice general
```

---

## 📂 Detalle de Unidades

### [Unidad 7 — NoSQL y nuevas formas de almacenamiento (`tp-unidad-7/`)](./tp-unidad-7/)
- **Modelado documental en MongoDB:** Representación orientada a agregados de pedidos de Food Store con líneas embebidas y snapshot histórico del cliente.
- **Migración y consultas:** Script `insertMany()` con pedidos reales y 4 consultas en MongoDB con su contraparte relacional en PostgreSQL 18.6.
- **Verificación cruzada:** 100% de coincidencia exacta en cantidades e identificadores entre ambos motores.
- **Evaluación y contraste de IA:** Refutación técnica documentada sobre transacciones ACID en MongoDB y rendimiento de JOINs en PostgreSQL, con justificación de arquitectura híbrida políglota / CQRS.
- **Informe:** Archivo PDF oficial de 2 páginas con canvas numerado: [`tp-unidad-7/informe_u7.pdf`](./tp-unidad-7/informe_u7.pdf).

### [Unidad 8 — Food Store en la feria: la base de la tablet y el cierre de la capa de datos (`tp-unidad-8/`)](./tp-unidad-8/)
- **Operación Offline-First en SQLite 3.50+:** Definición de tablas en modo `STRICT`, precios en centavos enteros para evitar errores de coma flotante, e identificadores universales **UUID v4** para prevenir colisiones en múltiples tablets distribuidas.
- **Semáforo de Sincronización:** Implementación de algoritmo jerárquico de conciliación (Rojo / Amarillo / Verde) resolviendo los casos de prueba C1 a C7:
  - **C1:** Consulta de catálogo disponible sin conexión de red.
  - **C2:** Subida de precios en servidor (`CONFLICTO`) y resolución tras aceptación del cliente (`SIMULADO_APROBADO`).
  - **C3:** Quiebre de stock en servidor (`RECHAZADO`).
  - **C4:** Baja lógica / lápida en servidor (`RECHAZADO` y ocultamiento automático del catálogo local).
  - **C5:** Solicitud limpia sin alteraciones (`SIMULADO_APROBADO`).
  - **C6:** Reenvío de solicitud idéntica e idempotencia (captura de colisión por `PRIMARY KEY`).
  - **C7:** Validación de restricciones locales (fallo ante cantidad = 0 y clave foránea de producto inexistente).
- **Regla de Oro Comprobada:** `"El móvil propone, el servidor dispone"`. Se auditó PostgreSQL demostrando que la cantidad de pedidos (200,001) y el stock físico permanecieron **invariables**. `SIMULADO_APROBADO` no es una venta.
- **Cierre Integral de la Capa de Datos:** Matriz comparativa de los tres motores (PostgreSQL, MongoDB, SQLite), plan de mantenimiento y contingencia ante restore desfasado, y Code Review de IA con descarte técnico fundamentado de `VACUUM FULL`.
- **Informe:** Archivo PDF de 2 páginas compilado con ReportLab: [`tp-unidad-8/docs/informe.pdf`](./tp-unidad-8/docs/informe.pdf).
