#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
COMPILADOR DE INFORME TÉCNICO EN PDF - TPI SEGUNDA ENTREGA (UNIDADES 4 A 8)
============================================================================
Estudiante: Fabrizio Simon
Asignatura: Base de Datos II · Tecnicatura Universitaria en Programación
Institución: UTN - Facultad Regional Mendoza
Salida: INFORME_SEGUNDA_ENTREGA_TPI.pdf
============================================================================
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Encabezado institucional sutil
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#334155"))
        self.drawString(36, 762, "UTN FRM · TECNICATURA UNIVERSITARIA EN PROGRAMACIÓN | BASE DE DATOS II")
        self.setFont("Helvetica", 7.5)
        self.drawRightString(612 - 36, 762, "TPI: Food Store · Segunda Entrega (Unidades 4 a 8)")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(36, 756, 612 - 36, 756)

        # Pie de página
        self.line(36, 32, 612 - 36, 32)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawString(36, 22, "Estudiante: Fabrizio Simon · Cierre Integral de la Capa de Datos (Ciclo 2026)")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(612 - 36, 22, page_str)
        self.restoreState()

def generar_pdf():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, "INFORME_SEGUNDA_ENTREGA_TPI.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#0F2942")     # Azul institucional profundo
    secondary_color = colors.HexColor("#1E3A8A")   # Azul marino medio
    dark_text = colors.HexColor("#0F172A")         # Carbón slate
    border_color = colors.HexColor("#CBD5E1")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13.5,
        leading=16.5,
        textColor=primary_color,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=10.5,
        textColor=colors.HexColor("#475569"),
        spaceAfter=4
    )

    h1_style = ParagraphStyle(
        'SectionHeading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=primary_color,
        spaceBefore=5,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.6,
        leading=9.8,
        textColor=dark_text,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.4,
        leading=9.5,
        textColor=colors.HexColor("#1E3A8A")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.5,
        textColor=dark_text
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.8,
        leading=8.5,
        textColor=primary_color
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.6,
        leading=8,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # =========================================================================
    # PÁGINA 1: TÍTULO, REPOSITORIOS, INTRODUCCIÓN, SECCIÓN 1 Y SECCIÓN 2
    # =========================================================================
    story.append(Paragraph("Trabajo Práctico Integrador — Segunda Entrega (Unidades 4 a 8)", title_style))
    story.append(Paragraph(
        "<b>Food Store:</b> Cierre Integral de la Capa de Datos (PostgreSQL 18 · MongoDB · SQLite 3.50+)<br/>"
        "<b>Estudiante:</b> Fabrizio Simon · <b>Cátedra:</b> Base de Datos II (UTN FRM) · <b>Ciclo Lectivo:</b> 2026",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=4))

    # Repositorios
    repo_box = [[
        Paragraph(
            "<b>Repositorios Oficiales en GitHub:</b><br/>"
            "• <b>Parte 1 (Unidades 1 a 6):</b> <code>https://github.com/simonfabrizio103/food-store-tp</code> "
            "(Carpetas <code>facultad/food-store-tp-unidad4/</code>, <code>u5/</code>, <code>u6/</code> en rama <code>master</code>, commit <code>202aecb</code>).<br/>"
            "• <b>Parte 2 (Unidades 7 y 8):</b> <code>https://github.com/simonfabrizio103/food-store-tp-u7-u8</code> "
            "(Carpetas <code>tp-unidad-7/</code> y <code>tp-unidad-8/</code> en rama <code>main</code>, etiqueta oficial <b><code>tp8</code></b>).",
            callout_style
        )
    ]]
    t_repo = Table(repo_box, colWidths=[540])
    t_repo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_repo)
    story.append(Spacer(1, 3))

    # Introducción
    story.append(Paragraph(
        "<b>Introducción y Enfoque Personal:</b> Para esta segunda entrega del TPI integré las unidades 4 a 8 cubriendo desde la refactorización avanzada "
        "en PostgreSQL hasta la arquitectura políglota con MongoDB y la base embebida Offline-First en SQLite para las tablets del Food Truck. "
        "En cada etapa trabajé sobre copias de prueba (<code>food_store_copia</code>, <code>foodstore_restore_test</code>), medí tiempos reales con EXPLAIN "
        "y cronómetros de PowerShell, y mantuve una auditoría técnica estricta sobre las sugerencias de la IA, descartando propuestas inviables para producción.",
        body_style
    ))
    story.append(Spacer(1, 2))

    # Sección 1
    story.append(Paragraph("1. Qué elementos implementé en cada unidad (4 a 8)", h1_style))
    data_u_impl = [
        [Paragraph("Unidad / Eje Temático", table_header_style), Paragraph("Componentes y Scripts Implementados", table_header_style), Paragraph("Descripción Funcional y Arquitectónica", table_header_style)],
        [
            Paragraph("<b>Unidad 4</b><br/>Normalización avanzada y redundancia", table_cell_bold),
            Paragraph("• <code>tp_fnbc_control_lote.sql</code><br/>• <code>tp_desnormalizacion_top_categorias.sql</code><br/>• Vista de compatibilidad y triggers", code_style),
            Paragraph("Descompuse <code>control_lote_almacen</code> a FNBC eliminando la dependencia <code>ResponsableControlID &rarr; DepositoID</code> sin pérdida de datos. Creé la tabla agregada <code>categoria_venta_dia</code> (top 5 categorías diarias) con triggers de sincronización y auditoría periódica.", table_cell_style)
        ],
        [
            Paragraph("<b>Unidad 5</b><br/>Administración y seguridad", table_cell_bold),
            Paragraph("• <code>sql/roles.sql</code> (RBAC)<br/>• <code>sql/auditoria_test.sql</code><br/>• <code>sql/simulacro_incidente.sql</code><br/>• <code>sql/usuario_anon.sql</code>", code_style),
            Paragraph("Diseñé el esquema RBAC de mínimo privilegio con roles de grupo y login, permisos a nivel de columna sobre <code>usuario.email</code> y default privileges. Activé auditoría nativa (<code>log_connections</code>, <code>log_disconnections</code>, <code>log_statement = all</code>), ejecuté simulacro forense y apliqué pseudonimización determinista con sal.", table_cell_style)
        ],
        [
            Paragraph("<b>Unidad 6</b><br/>Mantenimiento de bases de datos", table_cell_bold),
            Paragraph("• <code>maintenance.sql</code><br/>• <code>backup_foodstore.ps1</code><br/>• <code>restore_test.ps1</code><br/>• <code>validate_restore.sql</code>", code_style),
            Paragraph("Formulé el plan de mantenimiento preventivo (<code>VACUUM ANALYZE</code>, <code>REINDEX CONCURRENTLY</code>, estadísticas). Automaticé backups diarios lógicos comprimidos con rotación de 7 días. Ejecuté simulacro de recuperación contra reloj en base efímera y validé integridad.", table_cell_style)
        ],
        [
            Paragraph("<b>Unidad 7</b><br/>NoSQL (MongoDB) y políglota", table_cell_bold),
            Paragraph("• <code>consultas_mongodb.js</code><br/>• <code>consultas_postgresql.sql</code><br/>• <code>ejecutar_mongodb.js</code><br/>• <code>SPEC_U7.md</code> / <code>BITACORA.md</code>", code_style),
            Paragraph("Modelé la colección <code>pedidos</code> embebiendo líneas con precio unitario congelado e instantánea del cliente. Desarrollé 4 consultas analíticas en MongoDB y en PostgreSQL con 100% de coincidencia exacta, fundamentando la arquitectura híbrida CQRS.", table_cell_style)
        ],
        [
            Paragraph("<b>Unidad 8</b><br/>Bases de datos móviles e integración", table_cell_bold),
            Paragraph("• <code>schema_sqlite.sql</code> (STRICT)<br/>• <code>semaforo.sql</code> / <code>simulador.py</code><br/>• <code>pruebas_sqlite.sql</code><br/>• <code>servidor_snapshot.csv</code>", code_style),
            Paragraph("Implementé la base SQLite para la tablet del Food Truck en modo Offline-First con tablas <code>STRICT</code>, precios en centavos enteros y UUIDs v4. Creé el algoritmo de semáforo de conciliación (Rojo/Amarillo/Verde), simulé casos C1 a C7 y comprobé la regla de oro en PostgreSQL.", table_cell_style)
        ]
    ]

    t_u_impl = Table(data_u_impl, colWidths=[105, 145, 290])
    t_u_impl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
    ]))
    story.append(t_u_impl)
    story.append(Spacer(1, 3))

    # Sección 2
    story.append(Paragraph("2. Cómo probé el funcionamiento", h1_style))
    data_pruebas = [
        [Paragraph("Técnica de Prueba", table_header_style), Paragraph("Unidad / Escenario Real Probado", table_header_style), Paragraph("Metodología y Comprobación en el Motor", table_header_style)],
        [
            Paragraph("<b>Transacciones reversibles</b><br/>(BEGIN / ROLLBACK)", table_cell_bold),
            Paragraph("Unidad 4 (Migración FNBC)<br/>Unidad 8 (Borradores móviles)", table_cell_style),
            Paragraph("En U4 ejecuté la desestructuración de lotes dentro de bloques de transacción para validar que no hubiera tuplas huérfanas antes de confirmar. En U8 probé la anulación limpia de un pedido en mostrador con <code>ROLLBACK</code>, comprobando mediante <code>COUNT(*) = 0</code> que no quedó basura.", table_cell_style)
        ],
        [
            Paragraph("<b>Copias y bases réplica de prueba</b>", table_cell_bold),
            Paragraph("Unidades 4, 5 y 6<br/><code>food_store_copia</code> y <code>restore_test</code>", table_cell_style),
            Paragraph("Toda modificación de esquema y simulacro destructivo se realizó sobre bases aisladas con datos sintéticos volumétricos (200,001 pedidos y 50,000 productos), resguardando los ambientes de desarrollo limpios y la base productiva.", table_cell_style)
        ],
        [
            Paragraph("<b>Simulacro de acceso indebido</b>", table_cell_bold),
            Paragraph("Unidad 5 (Seguridad)<br/>Rol atacante: <code>app_web</code>", table_cell_style),
            Paragraph("Ejecuté <code>simulacro_incidente.sql</code> forzando ataques desde <code>app_web</code>: lectura masiva, intento de cambio a <code>admin_datos</code>, creación de usuarios espurios y llamadas a <code>fn_autenticar</code>. Verifiqué los bloqueos en el log y el informe forense.", table_cell_style)
        ],
        [
            Paragraph("<b>Simulacro de desastre contra reloj</b>", table_cell_bold),
            Paragraph("Unidad 6 (Continuidad)<br/>Script: <code>restore_test.ps1</code>", table_cell_style),
            Paragraph("Automaticé la restauración cronometrada desde el último backup comprimido hacia <code>foodstore_restore_test</code>. Validé la integridad estructural con <code>validate_restore.sql</code> chequeando claves foráneas, índices y cantidad de registros.", table_cell_style)
        ],
        [
            Paragraph("<b>Casos de conflicto de sincronización</b>", table_cell_bold),
            Paragraph("Unidad 8 (Móvil)<br/>Semáforo de conciliación (C1 a C7)", table_cell_style),
            Paragraph("Probé metódicamente los casos de la feria: consulta offline (C1), subida de precio y aceptación (C2 &rarr; Conflicto &rarr; Aprobado), quiebre de stock (C3 &rarr; Rechazo), baja lógica/lápida (C4 &rarr; Rechazo y ocultamiento de catálogo), idempotencia (C6) y restricciones estrictas (C7).", table_cell_style)
        ]
    ]

    t_pruebas = Table(data_pruebas, colWidths=[115, 125, 300])
    t_pruebas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
    ]))
    story.append(t_pruebas)

    # SALTO A PÁGINA 2
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: SECCIÓN 3 (RESULTADOS) Y SECCIÓN 4 (DECISIONES DE DISEÑO)
    # =========================================================================
    story.append(Paragraph("3. Qué resultados obtuve", h1_style))
    story.append(Paragraph(
        "A continuación se detallan las mediciones reales, métricas de recuperación y resultados empíricos obtenidos en las pruebas de base de datos:",
        body_style
    ))

    data_resultados = [
        [Paragraph("Métrica / Escenario Evaluado", table_header_style), Paragraph("Resultado Numérico y Comportamiento Observado", table_header_style), Paragraph("Evidencia e Impacto en el Proyecto", table_header_style)],
        [
            Paragraph("<b>Rendimiento Desnormalización (U4)</b>", table_cell_bold),
            Paragraph("Consulta original: <b>0.123 ms</b> (Seq Scan)<br/>Con tabla desnormalizada: <b>0.077 ms</b> (Bitmap Heap Scan)", table_cell_style),
            Paragraph("<b>37.4% de reducción en tiempo de respuesta</b> en el cálculo del Top 5 de categorías. Auditoría periódica reportó <b>0 tuplas desincronizadas</b>.", table_cell_style)
        ],
        [
            Paragraph("<b>Hallazgo Crítico Forense H-1 (U5)</b>", table_cell_bold),
            Paragraph("Fallo de autenticación por <code>SECURITY INVOKER</code>.<br/>Remediación: cambio a <code>SECURITY DEFINER</code>.", table_cell_style),
            Paragraph("<code>app_web</code> no podía validar login al carecer de SELECT sobre <code>usuario</code>. Se securizó la función bajo el owner <code>admin_datos</code> con <code>search_path</code> fijo.", table_cell_style)
        ],
        [
            Paragraph("<b>Simulacro de Desastre: RTO (U6)</b>", table_cell_bold),
            Paragraph("<b>RTO medido: 4.84 segundos</b><br/>(Restauración completa de base de 96 MB y 200,001 órdenes)", table_cell_style),
            Paragraph("Superó con holgura el objetivo fijado de RTO &le; 15 min. La base réplica quedó disponible y validada con 0 inconsistencias de foreign keys.", table_cell_style)
        ],
        [
            Paragraph("<b>Simulacro de Desastre: RPO (U6)</b>", table_cell_bold),
            Paragraph("<b>RPO medido: 1.70 minutos</b><br/>(Tiempo entre último respaldo/WAL y el incidente)", table_cell_style),
            Paragraph("Muy por debajo del límite máximo tolerable de 1 hora fijado para el negocio de Food Store en el informe post-incidente.", table_cell_style)
        ],
        [
            Paragraph("<b>Paridad Relacional vs Documental (U7)</b>", table_cell_bold),
            Paragraph("Consulta 4.a (Entregados): 3 pedidos (IDs 2, 4, 7)<br/>Consulta 4.b (Prod. 3): 3 pedidos<br/>Consulta 4.c (Total &gt; $2000): 2 pedidos (IDs 4 y 6)", table_cell_style),
            Paragraph("<b>100% de coincidencia exacta</b> en identificadores, cantidades y montos entre MongoDB y PostgreSQL, validando la integridad del modelo documental.", table_cell_style)
        ],
        [
            Paragraph("<b>Invariabilidad del Servidor Central (U8)</b>", table_cell_bold),
            Paragraph("Conteo en PostgreSQL tras semáforo: <b>200,001 pedidos</b>.<br/>Stock de productos 1, 2, 3 y 4: <b>5, 10, 115 y 130</b>.", table_cell_style),
            Paragraph("<b>Cero pedidos agregados y cero stock descontado en PostgreSQL.</b> Se validó empíricamente que <code>SIMULADO_APROBADO</code> no es una venta.", table_cell_style)
        ]
    ]

    t_resultados = Table(data_resultados, colWidths=[130, 185, 225])
    t_resultados.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_resultados)
    story.append(Spacer(1, 5))

    # Sección 4
    story.append(Paragraph("4. Qué decisiones de diseño tomé", h1_style))
    story.append(Paragraph(
        "A lo largo del proyecto prioricé soluciones de ingeniería que balancean consistencia, seguridad, rendimiento y desacoplamiento:",
        body_style
    ))

    data_decisiones = [
        [Paragraph("Área de Diseño", table_header_style), Paragraph("Decisión de Arquitectura Adoptada", table_header_style), Paragraph("Justificación Técnica y Salvaguardas Implementadas", table_header_style)],
        [
            Paragraph("<b>Refactorización FNBC vs Compatibilidad (U4)</b>", table_cell_bold),
            Paragraph("Separación en dos tablas normalizadas con <b>vista de compatibilidad</b>.", table_cell_style),
            Paragraph("Al extraer <code>responsable_control</code> se eliminaron anomalías de actualización. Para no romper aplicaciones preexistentes, creé una vista con el nombre y columnas de la tabla original, haciendo la transición 100% transparente.", table_cell_style)
        ],
        [
            Paragraph("<b>Criterio de Desnormalización (U4)</b>", table_cell_bold),
            Paragraph("Desnormalización selectiva de <code>categoria_venta_dia</code> con triggers.", table_cell_style),
            Paragraph("Solo desnormalicé la consulta crítica del dashboard para aliviar la CPU en horas pico. Como salvaguarda, implementé triggers para actualización automática y un script de auditoría que alerta cualquier discrepancia.", table_cell_style)
        ],
        [
            Paragraph("<b>Mínimo Privilegio y Seguridad Funcional (U5)</b>", table_cell_bold),
            Paragraph("Cierre de permisos directos y uso de <code>SECURITY DEFINER</code> seguro.", table_cell_style),
            Paragraph("El rol <code>app_web</code> no tiene SELECT sobre la tabla <code>usuario</code> ni acceso a contraseñas. La validación de credenciales se encapsuló en <code>fn_autenticar</code> con owner <code>admin_datos</code> y <code>search_path = public, pg_temp</code>.", table_cell_style)
        ],
        [
            Paragraph("<b>Patrón Híbrido Políglota / CQRS (U7)</b>", table_cell_bold),
            Paragraph("PostgreSQL como núcleo OLTP y MongoDB como Read Model desnormalizado.", table_cell_style),
            Paragraph("No forcé una migración excluyente. PostgreSQL es la única fuente de verdad (ACID, inventario, auditoría y facturación); MongoDB recibe eventos de ventas confirmadas para servir lecturas web masivas a muy baja latencia.", table_cell_style)
        ],
        [
            Paragraph("<b>Diseño Móvil Offline-First (U8)</b>", table_cell_bold),
            Paragraph("SQLite en modo <code>STRICT</code>, precios en centavos enteros y UUIDs v4.", table_cell_style),
            Paragraph("Eliminé errores de redondeo monetario con centavos enteros. Usé UUIDs v4 para que múltiples tablets en la feria no colisionen IDs de pedidos. Rige la regla de oro: <i>el móvil propone borradores, pero solo PostgreSQL confirma ventas</i>.", table_cell_style)
        ]
    ]

    t_decisiones = Table(data_decisiones, colWidths=[120, 160, 260])
    t_decisiones.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_decisiones)

    # SALTO A PÁGINA 3
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: SECCIÓN 5 (HERRAMIENTAS DE IA Y DESCARTES), DUIA Y CONCLUSIÓN
    # =========================================================================
    story.append(Paragraph("5. Herramientas de IA utilizadas, bitácora y descartes fundamentales", h1_style))
    story.append(Paragraph(
        "Utilicé Kiro para el diseño formal de requisitos EARS y especificaciones técnicas, y asistentes de código (OpenCode y LLMs) para prototipado rápido. "
        "Sin embargo, mantuve un criterio estricto de validación humana: <b>toda propuesta fue auditada, probada en el motor y refutada cuando violaba buenas prácticas</b>:",
        body_style
    ))

    data_ia = [
        [Paragraph("ID / Unidad", table_header_style), Paragraph("Componente", table_header_style), Paragraph("Propuesta de la IA", table_header_style), Paragraph("Decisión Humana", table_header_style), Paragraph("Fundamentación Técnica y Motivo de Rechazo", table_header_style)],
        [
            Paragraph("<b>CR-1</b><br/>Unidad 6", table_cell_bold),
            Paragraph("<code>maintenance.sql</code>", table_cell_style),
            Paragraph("Ejecutar <code>VACUUM FULL ANALYZE</code> diariamente para compactar espacio.", table_cell_style),
            Paragraph("<b>DESCARTADO DE PLANO</b>", table_cell_style),
            Paragraph("<code>VACUUM FULL</code> solicita bloqueo exclusivo (<code>ACCESS EXCLUSIVE LOCK</code>), impidiendo lecturas y escrituras durante minutos. En una base con 200,000 pedidos, tiraría la tienda abajo. Mantuve <code>VACUUM (ANALYZE, VERBOSE)</code> concurrente.", table_cell_style)
        ],
        [
            Paragraph("<b>CR-2</b><br/>Unidad 8", table_cell_bold),
            Paragraph("<code>schema_sqlite.sql</code>", table_cell_style),
            Paragraph("Usar claves primarias autonuméricas <code>INTEGER AUTOINCREMENT</code> en pedidos locales.", table_cell_style),
            Paragraph("<b>DESCARTADO DE PLANO</b>", table_cell_style),
            Paragraph("En un entorno distribuido offline con múltiples tablets, los enteros autoincrementales colisionan inevitablemente al sincronizar en el servidor central. Se impuso **UUID v4**.", table_cell_style)
        ],
        [
            Paragraph("<b>CR-3</b><br/>Unidad 8", table_cell_bold),
            Paragraph("Triggers en SQLite", table_cell_style),
            Paragraph("Crear triggers locales que intenten actualizar stock remoto en PostgreSQL por socket.", table_cell_style),
            Paragraph("<b>DESCARTADO DE PLANO</b>", table_cell_style),
            Paragraph("Viola la regla de oro y la premisa Offline-First: si la tablet no tiene señal en la feria, la interfaz se colgaría esperando el timeout de red. La conciliación debe ser asíncrona mediante el semáforo.", table_cell_style)
        ],
        [
            Paragraph("<b>CR-4</b><br/>Unidad 7", table_cell_bold),
            Paragraph("Modelado NoSQL", table_cell_style),
            Paragraph("Afirmar que 'MongoDB carece de soporte para transacciones ACID'.", table_cell_style),
            Paragraph("<b>REFUTADO TÉCNICAMENTE</b>", table_cell_style),
            Paragraph("MongoDB soporta transacciones ACID multi-documento desde la versión 4.0 (2018), y además en agregados con líneas embebidas la atomicidad es nativa a nivel de documento sin overhead de coordinación.", table_cell_style)
        ],
        [
            Paragraph("<b>CR-5</b><br/>Unidad 5", table_cell_bold),
            Paragraph("<code>fn_autenticar</code>", table_cell_style),
            Paragraph("Conceder permisos directos de <code>SELECT</code> a <code>app_web</code> sobre <code>usuario</code>.", table_cell_style),
            Paragraph("<b>DESCARTADO</b>", table_cell_style),
            Paragraph("Viola el mínimo privilegio y expone columnas confidenciales (hashes de contraseñas). La solución profesional fue convertir la función a <code>SECURITY DEFINER</code>.", table_cell_style)
        ]
    ]

    t_ia = Table(data_ia, colWidths=[55, 75, 125, 95, 190])
    t_ia.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_ia)
    story.append(Spacer(1, 4))

    # Párrafo DUIA
    story.append(Paragraph(
        "<b>Declaración de Uso de IA (DUIA):</b> Todas las interacciones, especificaciones en Kiro, prompts empleados y fundamentaciones de descarte "
        "fueron debidamente asentadas en las bitácoras (<code>BITACORA.md</code>) y declaraciones juradas (<code>DUIA.md</code>) de ambos repositorios, "
        "acreditando el dominio conceptual y técnico del estudiante para defender cada línea de código en la instancia oral.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Conclusión final
    story.append(Paragraph("Conclusión Final", h1_style))
    story.append(Paragraph(
        "Esta segunda entrega me demostró la importancia de concebir la base de datos como una arquitectura integral y especializada. "
        "Aprendí que optimizar no es agregar índices sin medir sino estudiar el plan del optimizador; que la seguridad radica en el mínimo privilegio real "
        "y funciones securizadas; que un plan de contingencia requiere pruebas cronometradas de restauración (RTO de 4.84 s y RPO de 1.70 min); y que "
        "en arquitecturas modernas la complementariedad entre PostgreSQL (núcleo transaccional), MongoDB (read-models desnormalizados) y SQLite (borde desconectado) "
        "permite construir soluciones empresariales de alta disponibilidad, seguras y escalables.",
        body_style
    ))

    # Construcción final del PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Informe compilado exitosamente: {pdf_path}")

if __name__ == "__main__":
    generar_pdf()
