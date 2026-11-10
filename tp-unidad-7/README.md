# Trabajo Práctico · Unidad 7: NoSQL y Nuevas Formas de Almacenamiento
**Tecnicatura Universitaria en Programación — Base de Datos II (UTN FRM)**  
**Ciclo Lectivo:** 2026 | **Estudiante:** Fabrizio Simon | **Motores:** PostgreSQL 18.6 & MongoDB 7+  
**Proyecto Integrador:** Food Store  

---

## 📌 Descripción del Trabajo

Este trabajo práctico modela y consulta el subconjunto transaccional central de **Food Store («pedidos y detalle de pedidos»)** en **MongoDB**, contrastando su estructura, rendimiento y resultados con la base relacional en **PostgreSQL**:

1. **Parte 1 — Modelo documental y migración:**
   - Identificación de tablas relacionales (`pedido`, `pedido_producto`, `cliente`, `producto`, `categoria`).
   - Diseño orientado a agregados (*Aggregate-Oriented Design*) con líneas de pedido embebidas y cliente como snapshot histórico.
   - Script de migración `insertMany()` con 6 pedidos representativos conservando identificadores (`_id = id_pedido`), fechas, importes y subtotales.
   - Justificación de embeber vs. referenciar y conservación de reglas de integridad.
2. **Parte 2 — Consultas y verificación cruzada:**
   - Implementación de las 4 consultas solicitadas en MongoDB (`consultas_mongodb.js`) y sus equivalentes en PostgreSQL (`consultas_postgresql.sql`).
   - Tabla de verificación cruzada demostrando coincidencia exacta de cantidades e identificadores (100% de consistencia).
3. **Parte 3 — Evaluación tecnológica y contraste crítico de IA:**
   - Análisis comparativo de patrones de acceso, consistencia ACID y costos de JOINs.
   - Contraste de 2 afirmaciones de la IA con documentación oficial de MongoDB y evidencia de laboratorio.
   - Conclusión técnica fundamentada (166 palabras) recomendando arquitectura políglota / CQRS.

---

## 📁 Estructura del Directorio

```text
food-store-tp-u7/
├── consultas_mongodb.js      # Script oficial de MongoDB con insertMany() y las 4 consultas (Parte 1 y 2)
├── consultas_postgresql.sql  # Script oficial de PostgreSQL con las 4 consultas equivalentes y resumen (Parte 2)
├── ejecutar_mongodb.js       # Ejecutor automatizado con MongoMemoryServer para pruebas reproducibles
├── evidencia_mongodb.txt     # Salida real de ejecución de las consultas en MongoDB
├── SPEC_U7.md                # Especificación técnica formal del modelo documental y reglas de integridad
├── BITACORA.md               # Bitácora obligatoria de uso crítico de IA y refutación de falacias
├── informe_u7.md             # Informe técnico completo en Markdown humanizado
├── informe_u7.pdf            # Informe oficial para entrega en PDF (2 páginas, compilado con ReportLab)
├── generar_pdf_u7.py         # Script generador del PDF oficial con canvas numerado
├── package.json              # Configuración de dependencias de Node.js
└── README.md                 # Este documento
```

---

## 🚀 Instrucciones de Reproducción y Ejecución

### 1. Ejecutar consultas en PostgreSQL
Con la base de datos `foodstore` activa:
```powershell
$env:PGPASSWORD = "postgres"
psql -U postgres -d foodstore -f consultas_postgresql.sql
```

### 2. Ejecutar migración y consultas en MongoDB (Automatizado)
El proyecto incluye un entorno reproducible que inicia una instancia local de MongoDB en memoria y corre las consultas:
```powershell
npm install
node ejecutar_mongodb.js
```

### 3. Recompilar Informe PDF Oficial
```powershell
python generar_pdf_u7.py
```
