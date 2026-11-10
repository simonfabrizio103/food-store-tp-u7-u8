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
│   ├── informe_u7.pdf   # Informe oficial de entrega (2 páginas, compilado con ReportLab)
│   ├── generar_pdf_u7.py
│   ├── package.json
│   └── README.md
│
├── tp-unidad-8/         # Unidad 8: (Próxima entrega)
│
└── README.md            # Este índice general
```

---

## 📂 Detalle de Unidades

### [Unidad 7 — NoSQL y nuevas formas de almacenamiento (`tp-unidad-7/`)](./tp-unidad-7/)
- **Modelado documental en MongoDB:** Representación orientada a agregados del subconjunto de pedidos y detalle de pedidos de Food Store con líneas embebidas y snapshot histórico del cliente.
- **Migración y consultas:** Script `insertMany()` con 6 pedidos reales y 4 consultas analíticas en MongoDB con su contraparte relacional en PostgreSQL 18.6.
- **Verificación cruzada:** 100% de coincidencia exacta en cantidades e identificadores entre ambos motores.
- **Evaluación y contraste de IA:** Refutación técnica documentada sobre transacciones ACID en MongoDB y rendimiento de JOINs en PostgreSQL, con conclusión fundamentada de arquitectura híbrida políglota / CQRS.
- **Informe:** Archivo PDF oficial de 2 páginas con canvas numerado: [`tp-unidad-7/informe_u7.pdf`](./tp-unidad-7/informe_u7.pdf).
