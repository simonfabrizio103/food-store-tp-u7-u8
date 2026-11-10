# Declaración de Uso de Inteligencia Artificial (DUIA)
**Cátedra:** Base de Datos II · Tecnicatura Universitaria en Programación  
**Institución:** Universidad Tecnológica Nacional (UTN)  
**Trabajo Práctico:** N.° 8 - Food Store en la feria: la base de la tablet y el cierre de la capa de datos  
**Estudiante:** Fabrizio Simon  
**Fecha:** 10 de Noviembre de 2026  

---

## 1. Declaración de Compromiso y Autoría
En cumplimiento con las normativas académicas y las directivas de la cátedra de Base de Datos II, declaro formalmente:

1. **Uso como Asistente de Desarrollo:** He utilizado herramientas de Inteligencia Artificial (OpenCode, Kiro y asistentes LLM) como copiloto y soporte técnico para acelerar el formateo de consultas SQL, la generación de borradores de prueba y la redacción estructural de documentación.
2. **Revisión y Validación Humana Excluyente:** Ninguna línea de código, script SQL (`schema_sqlite.sql`, `pruebas_sqlite.sql`, `semaforo.sql`) ni script de simulación (`simulador.py`) fue incorporada al proyecto de forma ciega. Cada sentencia fue leída, testeada en un motor de base de datos real (PostgreSQL 18 y SQLite 3.50+), y contrastada contra las reglas del negocio.
3. **Refutación de Alucinaciones y Descarte Técnico:** He identificado, refutado y descartado activamente propuestas técnicamente inviables de la IA (tales como la ejecución de `VACUUM FULL` en caliente, la generación de identificadores autonuméricos colisionables en SQLite y triggers sincrónicos entre tablet y servidor), documentando las razones en la bitácora técnica.
4. **Defensa Individual:** Me declaro en total capacidad y preparación para explicar, justificar y defender en vivo cada una de las decisiones de diseño, restricciones (`STRICT`, `CHECK`, `FOREIGN KEY`), transacciones (`COMMIT`, `ROLLBACK`), vistas y consultas desarrolladas en este trabajo práctico.

---

## 2. Detalle de Herramientas y Alcance

| Herramienta / Modelo | Alcance y Propósito | Grado de Modificación Humana |
| :--- | :--- | :--- |
| **Kiro (Spec Engine)** | Generación de plantillas de requisitos EARS y plan de tareas. | Alto (definición de casos C2 a C6 y jerarquía del semáforo). |
| **OpenCode / LLM** | Prototipado del CTE de conciliación y scripts de prueba. | Total (reescritura con `UPDATE ... FROM`, tipado `STRICT` y centavos enteros). |
| **Python / ReportLab** | Compilación programática del informe técnico en PDF. | Medio (diseño tipográfico, diagramación y ajuste a límite de páginas). |

---

**Firma del Estudiante:**  
*Fabrizio Simon*  
Estudiante de Tecnicatura Universitaria en Programación - UTN
