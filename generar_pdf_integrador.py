#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
COMPILADOR DE INFORME TÉCNICO EN PDF - TPI SEGUNDA ENTREGA (UNIDADES 4 A 8)
============================================================================
Estudiante: Fabrizio Simon
Asignatura: Base de Datos II · Tecnicatura Universitaria en Programación
Institución: UTN - Facultad Regional Mendoza (UTN FRM)
Salida: INFORME_SEGUNDA_ENTREGA_TPI.pdf (Dossier Técnico Integral Exhaustivo)
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

        # Pie de página inferior
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
        topMargin=40,
        bottomMargin=38
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
        fontSize=14,
        leading=17,
        textColor=primary_color,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569"),
        spaceAfter=5
    )

    h1_style = ParagraphStyle(
        'SectionHeading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionHeading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11.5,
        textColor=secondary_color,
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.6,
        textColor=dark_text,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.6,
        leading=10,
        textColor=colors.HexColor("#1E3A8A")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=dark_text
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=primary_color
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.8,
        leading=8.5,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # =========================================================================
    # PÁGINA 1: PORTADA, REPOSITORIOS, INTRODUCCIÓN Y ENFOQUE PERSONAL
    # =========================================================================
    story.append(Paragraph("Trabajo Práctico Integrador — Segunda Entrega (Unidades 4 a 8)", title_style))
    story.append(Paragraph(
        "<b>Food Store:</b> Cierre Integral de la Capa de Datos (PostgreSQL 18 · MongoDB · SQLite 3.50+)<br/>"
        "<b>Estudiante:</b> Fabrizio Simon · <b>Cátedra:</b> Base de Datos II (UTN FRM) · <b>Ciclo Lectivo:</b> 2026",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=6))

    repo_box = [[
        Paragraph(
            "<b>Repositorios Oficiales en GitHub:</b><br/>"
            "• <b>Parte 1 (Unidades 1 a 6):</b> <code>https://github.com/simonfabrizio103/food-store-tp</code> "
            "(Carpetas <code>facultad/food-store-tp-unidad4/</code>, <code>u5/</code>, <code>u6/</code> en rama <code>master</code>, commit <code>202aecb</code>).<br/>"
            "• <b>Parte 2 (Unidades 7 y 8):</b> <code>https://github.com/simonfabrizio103/food-store-tp-u7-u8</code> "
            "(Carpetas <code>tp-unidad-7/</code> y <code>tp-unidad-8/</code> en rama <code>main</code>, etiquetas oficiales <b><code>tp8</code></b> y <b><code>tpi-entrega2</code></b>).",
            callout_style
        )
    ]]
    t_repo = Table(repo_box, colWidths=[540])
    t_repo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#94A3B8")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_repo)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Introducción y Enfoque Personal", h1_style))
    story.append(Paragraph(
        "Cuando me senté a encarar esta segunda entrega del Trabajo Práctico Integrador de Food Store, me quedó clarísimo que no se trataba "
        "de un trabajo práctico más donde tirás cuatro consultas para que devuelvan filas y pasás de largo. Acá el desafío era agarrar todo "
        "lo visto en la materia y hacer convivir un esquema que arrancó en un motor relacional tradicional como PostgreSQL, llevarlo al límite "
        "con optimización física, blindarlo con políticas de seguridad reales, someterlo a pruebas de desastre contra reloj, extenderlo hacia "
        "una base documental con MongoDB y, como frutilla del postre, resolver la operatoria de un food truck vendiendo en una feria sin señal usando SQLite.",
        body_style
    ))
    story.append(Paragraph(
        "A lo largo de estas semanas me di cuenta de que una base de datos en el mundo real no es un depósito estático de tablas: es un sistema vivo, "
        "sometido a bloqueos, cuellos de botella de CPU, caídas de tensión, ataques de inyección y fallas de conectividad. Si uno diseña pensando que "
        "la red nunca se cae o que los usuarios son de confianza, el sistema explota en el primer día de producción.",
        body_style
    ))
    story.append(Paragraph(
        "En este camino me apoyé en herramientas de IA (Kiro para las especificaciones EARS, OpenCode y LLMs para estructurar código rápido), pero "
        "con una regla innegociable: <b>la IA propone, pero el que firma la arquitectura y pone la cara soy yo</b>. Cada sentencia SQL, script de PowerShell "
        "y modelo documental lo leí, lo probé en mi máquina y, cuando la IA sugirió malas prácticas (como un <code>VACUUM FULL</code> en caliente o autonuméricos "
        "en dispositivos móviles desconectados), las descarté y corregí con fundamentos técnicos de ingeniería.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Matriz resumen de alcance
    data_alcance = [
        [Paragraph("Unidad / Eje Temático", table_header_style), Paragraph("Motor", table_header_style), Paragraph("Problema Principal Resuelto", table_header_style), Paragraph("Resultado Clave Validado", table_header_style)],
        [
            Paragraph("<b>Unidad 4</b> · Normalización", table_cell_bold),
            Paragraph("PostgreSQL", table_cell_style),
            Paragraph("Violación de FNBC en lotes y saturación de CPU en dashboard.", table_cell_style),
            Paragraph("Descomposición sin pérdida con vista de compatibilidad; 37.4% más rápido.", table_cell_style)
        ],
        [
            Paragraph("<b>Unidad 5</b> · Seguridad", table_cell_bold),
            Paragraph("PostgreSQL", table_cell_style),
            Paragraph("Mínimo privilegio, auditoría forense y fallo de login H-1.", table_cell_style),
            Paragraph("Column-Level Security, H-1 corregido con DEFINER y anonimización PII.", table_cell_style)
        ],
        [
            Paragraph("<b>Unidad 6</b> · Mantenimiento", table_cell_bold),
            Paragraph("PostgreSQL", table_cell_style),
            Paragraph("Bloat de índices, backups automáticos y simulación de desastre.", table_cell_style),
            Paragraph("RTO medido en 4.84 s y RPO de 1.70 min restaurando 200,001 órdenes.", table_cell_style)
        ],
        [
            Paragraph("<b>Unidad 7</b> · NoSQL", table_cell_bold),
            Paragraph("MongoDB", table_cell_style),
            Paragraph("Cuello de botella en lecturas web de pedidos y catálogo.", table_cell_style),
            Paragraph("Modelado por agregados con líneas embebidas; 100% de paridad con PG.", table_cell_style)
        ],
        [
            Paragraph("<b>Unidad 8</b> · Móvil", table_cell_bold),
            Paragraph("SQLite", table_cell_style),
            Paragraph("Venta offline en feria sin señal y conciliación asíncrona.", table_cell_style),
            Paragraph("Tablas STRICT, UUIDs y semáforo jerárquico; PG central invariable.", table_cell_style)
        ]
    ]

    t_alcance = Table(data_alcance, colWidths=[110, 65, 195, 170])
    t_alcance.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_alcance)

    # SALTO A PÁGINA 2
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: UNIDAD 4 EN PROFUNDIDAD
    # =========================================================================
    story.append(Paragraph("1. Unidad 4 · Normalización avanzada y redundancia controlada", h1_style))
    story.append(Paragraph("1.1 El problema del esquema heredado y la violación de FNBC", h2_style))
    story.append(Paragraph(
        "Al analizar la tabla heredada <code>control_lote_almacen</code>, identifiqué que la clave primaria compuesta era "
        "<code>(LoteID, ResponsableControlID)</code>. Sin embargo, existía la dependencia funcional no trivial:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>ResponsableControlID &rarr; DepositoID</b><br/>"
        "Como <code>ResponsableControlID</code> no era superclave de la tabla, violaba la Forma Normal de Boyce-Codd (FNBC). "
        "Esto provocaba redundancia masiva (el depósito se repetía por cada lote auditado) y anomalías graves: si un responsable cambiaba "
        "de depósito, un <code>UPDATE</code> fallido dejaba al auditor asignado a dos depósitos distintos simultáneamente.",
        body_style
    ))

    story.append(Paragraph("1.2 Descomposición sin pérdida y Vista de Compatibilidad", h2_style))
    story.append(Paragraph(
        "Descompuse la relación en dos tablas normalizadas:<br/>"
        "1. <code>responsable_control (ResponsableControlID PK, DepositoID, NombreResponsable)</code>.<br/>"
        "2. <code>control_lote_almacen_nuevo (LoteID, ResponsableControlID FK, FechaControl, Estado, CantidadAuditada)</code>.<br/>"
        "Para no romper las aplicaciones existentes ni obligar a reescribir reportes, implementé el patrón de <b>Vista de Compatibilidad</b>:",
        body_style
    ))
    story.append(Paragraph(
        "<code>CREATE OR REPLACE VIEW control_lote_almacen AS<br/>"
        "SELECT cla.LoteID, cla.ResponsableControlID, rc.DepositoID, cla.FechaControl, cla.Estado, cla.CantidadAuditada<br/>"
        "FROM control_lote_almacen_nuevo cla JOIN responsable_control rc ON cla.ResponsableControlID = rc.ResponsableControlID;</code>",
        code_style
    ))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "De este modo, normalicé el almacenamiento físico sin que ningún sistema externo se viera afectado.",
        body_style
    ))

    story.append(Paragraph("1.3 Desnormalización controlada para el Dashboard (categoria_venta_dia)", h2_style))
    story.append(Paragraph(
        "En el dashboard ejecutivo se consultaba constantemente el <b>Top 5 de categorías más vendidas por día</b>. "
        "Calcular <code>SUM(cantidad * precio)</code> agrupando sobre cientos de miles de filas en cada refresco de pantalla consumía <b>0.123 ms</b> por consulta con Seq Scan. "
        "Decidí desnormalizar creando la tabla agregada <code>categoria_venta_dia</code> con un índice B-tree compuesto <code>(fecha, total_vendido DESC)</code>.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Salvaguardas de consistencia:</b><br/>"
        "• <b>Trigger automático:</b> Creé un trigger <code>AFTER INSERT OR UPDATE ON pedido_producto</code> que actualiza los totales precalculados en tiempo real.<br/>"
        "• <b>Auditoría periódica:</b> Implementé una consulta de control que compara la tabla desnormalizada contra la agregación pura. En mis pruebas reportó <b>0 filas desincronizadas</b>.<br/>"
        "• <b>Rendimiento medido con EXPLAIN ANALYZE:</b> El tiempo de consulta cayó a <b>0.077 ms</b> (Bitmap Heap Scan), logrando una <b>mejora del 37.4% en CPU</b>.",
        body_style
    ))

    # SALTO A PÁGINA 3
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: UNIDAD 5 EN PROFUNDIDAD
    # =========================================================================
    story.append(Paragraph("2. Unidad 5 · Administración, seguridad y laboratorio forense", h1_style))
    story.append(Paragraph("2.1 Arquitectura RBAC bajo el Principio de Mínimo Privilegio", h2_style))
    story.append(Paragraph(
        "Diseñé un esquema de control de acceso basado en roles (RBAC) en dos capas separando estrictamente responsabilidades:<br/>"
        "• <b>Roles de grupo:</b> <code>rol_admin_datos</code> (administración total), <code>rol_app_web</code> (tienda online), <code>rol_cajero</code> (ventas físicas) y <code>rol_auditor</code> (auditoría).<br/>"
        "• <b>Usuarios de conexión:</b> <code>admin_datos</code> y <code>app_web</code> asignados a sus respectivos grupos.<br/>"
        "• <b>Column-Level Security:</b> La aplicación web tiene restringido el acceso: <code>GRANT SELECT (id_usuario, nombre, activo) ON usuario TO rol_app_web;</code>. Tiene terminantemente prohibido ver contraseñas o emails de clientes.",
        body_style
    ))

    story.append(Paragraph("2.2 Auditoría nativa y Simulacro de Incidente", h2_style))
    story.append(Paragraph(
        "Activé en PostgreSQL <code>log_connections = on</code>, <code>log_disconnections = on</code> y <code>log_statement = 'all'</code>. "
        "Luego ejecuté un ataque simulado conectándome como <code>app_web</code>: intenté 4 veces invocar <code>fn_autenticar</code> con claves falsas, "
        "quise consultar emails ajenos (<code>SELECT email FROM usuario</code>), intenté elevar privilegios a <code>admin_datos</code> y crear usuarios hacker. "
        "PostgreSQL rechazó cada intento con <code>permission denied</code>, registrando la evidencia en los logs.",
        body_style
    ))

    story.append(Paragraph("2.3 El Hallazgo Crítico H-1 y la Solución con SECURITY DEFINER", h2_style))
    story.append(Paragraph(
        "Al probar el login de clientes descubrí un bug crítico: <code>fn_autenticar</code> fue creada originalmente como <code>SECURITY INVOKER</code>. "
        "Como <code>app_web</code> carece de permiso de SELECT sobre la tabla <code>usuario</code>, PostgreSQL bloqueaba el login arrojando "
        "<code>permission denied for table usuario</code>. La aplicación no podía autenticar a nadie.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Remediación aplicada:</b> En vez de cometer el error de darle SELECT a la app sobre toda la tabla, convertí la función a <code>SECURITY DEFINER</code>, "
        "le asigné el owner <code>admin_datos</code> y le blindé el esquema de búsqueda:",
        body_style
    ))
    story.append(Paragraph(
        "<code>ALTER FUNCTION fn_autenticar(text, text) OWNER TO admin_datos;<br/>"
        "ALTER FUNCTION fn_autenticar(text, text) SECURITY DEFINER;<br/>"
        "ALTER FUNCTION fn_autenticar(text, text) SET search_path = public, pg_temp;</code>",
        code_style
    ))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "Con esto, la función corre con los privilegios de su dueño, verifica la contraseña y retorna solo un booleano, manteniendo a la app web aislada de los datos sensibles.",
        body_style
    ))

    story.append(Paragraph("2.4 Hallazgo H-2 y Anonimización de Datos Personales (PII)", h2_style))
    story.append(Paragraph(
        "El log reveló que <code>log_statement = 'all'</code> guardaba contraseñas en texto claro. Para remediarlo creé <code>anonimizar_log.py</code> en Python "
        "para enmascarar credenciales e IPs antes de compartir trazas. Asimismo, creé la tabla <code>usuario_anon</code> con hash determinista y sal "
        "sobre los emails (<code>md5(id || sal) || '@anon.example'</code>), eliminando contraseñas pero conservando <code>id_usuario</code>. "
        "Las pruebas estadísticas de <code>verificacion_equivalencia.md</code> confirmaron <b>100% de paridad en agregados sin filtrar PII real</b>.",
        body_style
    ))

    # SALTO A PÁGINA 4
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 4: UNIDAD 6 EN PROFUNDIDAD
    # =========================================================================
    story.append(Paragraph("3. Unidad 6 · Mantenimiento, backup y simulacro de desastre", h1_style))
    story.append(Paragraph("3.1 Mantenimiento preventivo en PostgreSQL (maintenance.sql)", h2_style))
    story.append(Paragraph(
        "En una base con 200,000 pedidos, el motor acumula miles de tuplas muertas por día debido al motor MVCC. Diseñé <code>maintenance.sql</code> con tres pilares:<br/>"
        "• <b><code>VACUUM (ANALYZE, VERBOSE)</code>:</b> Limpia tuplas muertas y actualiza el mapa de espacio libre (FSM) sin bloquear lecturas ni escrituras concurrentes.<br/>"
        "• <b><code>REINDEX TABLE CONCURRENTLY</code>:</b> Desfragmenta y compacta los índices B-Tree inflados (bloat) construyendo un índice paralelo sin bloquear el acceso comercial.<br/>"
        "• <b>Actualización de estadísticas:</b> Refresca las frecuencias en <code>pg_statistic</code> para que el planificador elija siempre index scans óptimos.<br/>"
        "• <b>Salud del motor (health_check.sql):</b> Monitoreo de <code>pg_statio_user_tables</code> verificando un <b>Cache Hit Ratio superior al 99.2%</b>.",
        body_style
    ))

    story.append(Paragraph("3.2 Estrategia de backups automatizados en PowerShell (backup_foodstore.ps1)", h2_style))
    story.append(Paragraph(
        "Programé un script en PowerShell para automatizar respaldos lógicos con nivel de producción:<br/>"
        "• Valida que el servicio PostgreSQL esté en ejecución y comprueba que el disco posea al menos 500 MB libres antes de iniciar.<br/>"
        "• Genera respaldos comprimidos con <code>pg_dump.exe -F c -b -v</code> (formato custom con compresión zlib, permitiendo restore selectivo y paralelo).<br/>"
        "• Verifica que el archivo generado exista y tenga tamaño mayor a cero.<br/>"
        "• Aplica rotación automática purgando backups con más de 7 días de antigüedad.",
        body_style
    ))

    story.append(Paragraph("3.3 Simulacro de desastre contra reloj: Medición de RTO y RPO", h2_style))
    story.append(Paragraph(
        "Para validar nuestro plan de contingencia programé <code>restore_test.ps1</code>, simulando la caída total del servidor desde el backup "
        "<code>foodstore_20261110_155502.dump</code> (11.2 MB comprimido, 96 MB en disco, con 200,001 pedidos y 50,002 productos):",
        body_style
    ))

    data_rto_box = [
        [Paragraph("Métrica de Continuidad", table_header_style), Paragraph("Valor Medido Real", table_header_style), Paragraph("SLA Objetivo", table_header_style), Paragraph("Estado de Cumplimiento", table_header_style)],
        [
            Paragraph("<b>RTO (Recovery Time Objective)</b>", table_cell_bold),
            Paragraph("<b>4.84 segundos</b>", table_cell_style),
            Paragraph("Menor a 15 minutos", table_cell_style),
            Paragraph("<b>SUPERADO AMPLIAMENTE</b>", table_cell_style)
        ],
        [
            Paragraph("<b>RPO (Recovery Point Objective)</b>", table_cell_bold),
            Paragraph("<b>1.70 minutos</b>", table_cell_style),
            Paragraph("Menor a 1 hora", table_cell_style),
            Paragraph("<b>SUPERADO AMPLIAMENTE</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Integridad Estructural</b>", table_cell_bold),
            Paragraph("0 claves foráneas rotas", table_cell_style),
            Paragraph("100% de tablas y órdenes", table_cell_style),
            Paragraph("<b>VALIDADO (validate_restore.sql)</b>", table_cell_style)
        ]
    ]
    t_rto = Table(data_rto_box, colWidths=[150, 110, 130, 150])
    t_rto.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_rto)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Esto demostró empíricamente que ante un incidente crítico, el sistema recupera su operatividad plena en menos de 5 segundos.",
        body_style
    ))

    # SALTO A PÁGINA 5
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 5: UNIDAD 7 EN PROFUNDIDAD
    # =========================================================================
    story.append(Paragraph("4. Unidad 7 · NoSQL y nuevas formas de almacenamiento (MongoDB)", h1_style))
    story.append(Paragraph("4.1 Rompiendo el molde relacional: Diseño documental de pedidos", h2_style))
    story.append(Paragraph(
        "En la Unidad 7 comprendí que migrar a NoSQL no es volcar tablas relacionales en colecciones separadas para después juntarlas con <code>$lookup</code>. "
        "Diseñé la colección <code>pedidos</code> en MongoDB bajo el concepto de <b>Agregado (DDD)</b> con líneas y cliente embebidos:",
        body_style
    ))
    story.append(Paragraph(
        "<code>{ _id: 2, fecha: ISODate(\"2026-11-10T12:00:00Z\"), estado: \"ENTREGADO\",<br/>"
        "&nbsp;&nbsp;cliente: { id_cliente: 201, nombre: \"Ana Gómez\", email: \"ana@example.com\" },<br/>"
        "&nbsp;&nbsp;lineas: [<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;{ producto_id: 1, nombre: \"Muzza\", cantidad: 2, precio_unitario: 100.00 },<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;{ producto_id: 2, nombre: \"Napolitana\", cantidad: 1, precio_unitario: 120.00 }<br/>"
        "&nbsp;&nbsp;], total: 320.00 }</code>",
        code_style
    ))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "<b>Ventajas del modelo:</b><br/>"
        "1. <b>Precio unitario congelado:</b> Si mañana la Muzza sube a $150 en la tabla maestra, la venta histórica de Ana sigue preservando los $100 originales.<br/>"
        "2. <b>Lectura atómica en un único viaje a disco:</b> La app móvil consulta un pedido completo con <code>findOne({ _id: 2 })</code> sin JOINs.",
        body_style
    ))

    story.append(Paragraph("4.2 Consultas analíticas y Validación Cruzada con PostgreSQL", h2_style))
    story.append(Paragraph(
        "Implementé en <code>consultas_mongodb.js</code> 4 consultas complejas y sus contrapartes en <code>consultas_postgresql.sql</code>, "
        "ejecutándolas con el runner autónomo en memoria <code>ejecutar_mongodb.js</code> (usando <code>mongodb-memory-server</code>):<br/>"
        "• <b>4.a (Pedidos entregados):</b> <code>find({ estado: 'ENTREGADO' })</code> &rarr; Retornó pedidos 2, 4 y 7 en ambos motores.<br/>"
        "• <b>4.b (Filtro en subdocumentos):</b> <code>find({ 'lineas.producto_id': 3 })</code> &rarr; Retornó pedidos 2, 4 y 6 en ambos motores.<br/>"
        "• <b>4.c (Total &gt; $2000):</b> Retornó pedidos 4 ($2050) y 6 ($3500) en ambos motores.<br/>"
        "• <b>4.d (Agrupación con $unwind y $group):</b> Ventas totales por producto.<br/>"
        "<b>Resultado: 100% de coincidencia exacta</b> en montos y cantidades entre el motor documental y el relacional.",
        body_style
    ))

    story.append(Paragraph("4.3 Decisión Arquitectónica: Enfoque Híbrido CQRS", h2_style))
    story.append(Paragraph(
        "No caí en el falso dilema 'relacional vs documental'. Adopté una arquitectura <b>CQRS (Command Query Responsibility Segregation)</b>:<br/>"
        "• <b>PostgreSQL es el Core Transaccional (OLTP):</b> Única Fuente de Verdad (SSoT). Controla inventario físico, estados fiscales y auditoría.<br/>"
        "• <b>MongoDB es el Read Model:</b> Almacena pedidos confirmados desnormalizados para responder consultas masivas desde apps web y móviles con tiempos de respuesta en milisegundos sin sobrecargar a PostgreSQL. Si MongoDB falla, se regenera desde el relacional.",
        body_style
    ))

    # SALTO A PÁGINA 6
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 6: UNIDAD 8 EN PROFUNDIDAD
    # =========================================================================
    story.append(Paragraph("5. Unidad 8 · Bases de datos móviles e integración (SQLite)", h1_style))
    story.append(Paragraph("5.1 Operatoria del Food Truck en la feria: Venta Offline-First", h2_style))
    story.append(Paragraph(
        "El Food Truck vende en una feria gastronómica sin señal celular ni Internet. Diseñé la base SQLite (`schema_sqlite.sql`) bajo 4 reglas:<br/>"
        "1. <b><code>PRAGMA foreign_keys = ON;</code>:</b> Activación obligatoria de integridad referencial.<br/>"
        "2. <b>Tablas <code>STRICT</code>:</b> Tipado estático forzado para impedir que el motor acepte strings en columnas de stock o precios.<br/>"
        "3. <b>Precios en centavos enteros (<code>INT</code>):</b> Elimina errores acumulativos de redondeo de punto flotante de los tipos `REAL`.<br/>"
        "4. <b>UUIDs v4 (<code>TEXT PRIMARY KEY</code>):</b> Si tres mozos toman pedidos en tres tablets desconectadas, usar autonuméricos generaría colisiones de IDs al reconectarse. Con UUID v4 cada pedido nace con un identificador unívoco a nivel mundial.",
        body_style
    ))

    story.append(Paragraph("5.2 Algoritmo del Semáforo de Sincronización", h2_style))
    story.append(Paragraph(
        "En <code>semaforo.sql</code> implementé una consulta atómica con CTE y <code>UPDATE ... FROM</code> que evalúa las solicitudes contra el snapshot del servidor:<br/>"
        "• <b>Rojo (<code>RECHAZADO</code>):</b> Si el producto no existe, fue dado de baja lógica (<code>eliminado = 't'</code>), está inactivo (<code>disponible = 'f'</code>) o si la cantidad pedida supera el stock del servidor.<br/>"
        "• <b>Amarillo (<code>CONFLICTO</code>):</b> Si hay stock y vigencia pero el precio del servidor cambió respecto al visto en la tablet. Permite renegociar con el cliente en mostrador.<br/>"
        "• <b>Verde (<code>SIMULADO_APROBADO</code>):</b> Si precio, stock y disponibilidad coinciden al 100%.<br/>"
        "<b>Regla de Oro: El móvil propone, el servidor dispone.</b> La tablet no altera stock ni confirma ventas fiscales.",
        body_style
    ))

    story.append(Paragraph("5.3 Simulación de Casos C1 a C7 y Verificación en PostgreSQL", h2_style))
    story.append(Paragraph(
        "En <code>simulador.py</code> ejecuté la batería completa de pruebas sobre <code>foodstore_movil.db</code>:<br/>"
        "• <b>C1 (Catálogo offline):</b> Consulta de productos con stock y activos sin conectarse a la red.<br/>"
        "• <b>C7 (Integridad estricta):</b> Intentos de cantidad en 0 y producto inexistente abortados por CHECK y FOREIGN KEY.<br/>"
        "• <b>C2 (Conflicto de precio):</b> Muzza sube de $100 a $125 &rarr; <code>CONFLICTO</code>; cliente acepta &rarr; reintento da <code>SIMULADO_APROBADO</code>.<br/>"
        "• <b>C3 (Quiebre de stock):</b> Pedido de 50 Napolitanas con stock 10 en servidor &rarr; <code>RECHAZADO</code>.<br/>"
        "• <b>C4 (Baja lógica / lápida):</b> Producto dado de baja &rarr; <code>RECHAZADO</code>; la fila física persiste en SQLite pero se oculta del catálogo activo.<br/>"
        "• <b>C5 (Aprobación limpia):</b> Coincidencia total en precio y stock &rarr; <code>SIMULADO_APROBADO</code>.<br/>"
        "• <b>C6 (Idempotencia):</b> Reenvío del mismo UUID rechazado por clave primaria; el semáforo no lo reevalúa.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Auditoría en PostgreSQL:</b> Al finalizar las pruebas, verifiqué que <code>total_pedidos</code> continuó en <b>200,001</b> y el stock físico de los productos no varió ni una sola unidad. La regla de oro se cumplió.",
        body_style
    ))

    # SALTO A PÁGINA 7
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 7: REVISIÓN CRÍTICA DE IA, DUIA Y CONCLUSIÓN FINAL
    # =========================================================================
    story.append(Paragraph("6. Revisión Crítica de Inteligencia Artificial y los 5 Descartes Técnicos", h1_style))
    story.append(Paragraph(
        "Utilicé Kiro (especificaciones EARS) y OpenCode/LLMs para acelerar desarrollo, pero mantuve una auditoría humana rigurosa. "
        "A continuación expongo los cinco descartes técnicos fundamentales donde la intervención humana corrigió propuestas peligrosas de la IA:",
        body_style
    ))

    data_ia_expanded = [
        [Paragraph("ID / Unidad", table_header_style), Paragraph("Componente", table_header_style), Paragraph("Propuesta de la IA", table_header_style), Paragraph("Decisión Humana", table_header_style), Paragraph("Fundamentación Técnica y Motivo de Rechazo", table_header_style)],
        [
            Paragraph("<b>CR-1</b><br/>Unidad 6", table_cell_bold),
            Paragraph("<code>maintenance.sql</code>", table_cell_style),
            Paragraph("Correr <code>VACUUM FULL ANALYZE</code> diariamente para compactar tablas.", table_cell_style),
            Paragraph("<b>DESCARTADO DE PLANO</b>", table_cell_style),
            Paragraph("<code>VACUUM FULL</code> solicita <code>ACCESS EXCLUSIVE LOCK</code>, bloqueando lecturas y escrituras durante minutos. En producción tiraría la tienda abajo. Mantuve <code>VACUUM (ANALYZE, VERBOSE)</code> concurrente.", table_cell_style)
        ],
        [
            Paragraph("<b>CR-2</b><br/>Unidad 8", table_cell_bold),
            Paragraph("<code>schema_sqlite.sql</code>", table_cell_style),
            Paragraph("Usar claves autonuméricas <code>INTEGER AUTOINCREMENT</code> en pedidos.", table_cell_style),
            Paragraph("<b>DESCARTADO DE PLANO</b>", table_cell_style),
            Paragraph("En múltiples tablets desconectadas, los enteros autonuméricos colisionan inevitablemente al sincronizar en el servidor central. Se impuso <b>UUID v4</b>.", table_cell_style)
        ],
        [
            Paragraph("<b>CR-3</b><br/>Unidad 8", table_cell_bold),
            Paragraph("Triggers móviles", table_cell_style),
            Paragraph("Triggers locales en SQLite para actualizar stock remoto en PG por socket.", table_cell_style),
            Paragraph("<b>DESCARTADO DE PLANO</b>", table_cell_style),
            Paragraph("Viola la premisa Offline-First: si no hay señal en la feria, la interfaz se colgaría esperando el timeout de red. La conciliación debe ser asíncrona mediante el semáforo.", table_cell_style)
        ],
        [
            Paragraph("<b>CR-4</b><br/>Unidad 7", table_cell_bold),
            Paragraph("Modelado NoSQL", table_cell_style),
            Paragraph("Afirmar que 'MongoDB carece de soporte para transacciones ACID'.", table_cell_style),
            Paragraph("<b>REFUTADO TÉCNICAMENTE</b>", table_cell_style),
            Paragraph("MongoDB soporta transacciones ACID multi-documento desde v4.0, y en agregados con líneas embebidas la atomicidad es nativa a nivel de documento sin overhead de coordinación.", table_cell_style)
        ],
        [
            Paragraph("<b>CR-5</b><br/>Unidad 5", table_cell_bold),
            Paragraph("<code>fn_autenticar</code>", table_cell_style),
            Paragraph("Conceder permisos directos de SELECT a <code>app_web</code> sobre <code>usuario</code>.", table_cell_style),
            Paragraph("<b>DESCARTADO</b>", table_cell_style),
            Paragraph("Viola el mínimo privilegio y expone hashes de contraseñas. Se resolvió convirtiendo la función a <code>SECURITY DEFINER</code> con search_path seguro.", table_cell_style)
        ]
    ]

    t_ia_exp = Table(data_ia_expanded, colWidths=[55, 75, 125, 95, 190])
    t_ia_exp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
    ]))
    story.append(t_ia_exp)
    story.append(Spacer(1, 4))

    story.append(Paragraph(
        "<b>Declaración de Uso de IA (DUIA):</b> Todas las interacciones, especificaciones en Kiro, prompts empleados y fundamentaciones de descarte "
        "fueron asentadas en las bitácoras (<code>BITACORA.md</code>) y declaraciones juradas (<code>DUIA.md</code>) de ambos repositorios, "
        "acreditando el dominio conceptual y técnico del estudiante para defender cada línea de código en la instancia oral.",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("7. Conclusión Final y Aprendizajes de Carrera", h1_style))
    story.append(Paragraph(
        "Haber completado este proyecto integrador a lo largo de las 8 unidades cambió totalmente mi perspectiva sobre lo que significa trabajar con bases de datos. "
        "Cuando uno recién arranca a programar, piensa que una base de datos es tirar un <code>CREATE TABLE</code>, un par de <code>INSERT</code> y hacer andar una aplicación. "
        "Hoy me doy cuenta de que la base de datos es el corazón de cualquier negocio: si la base se bloquea, la empresa no factura; si pierde datos por un desastre y no tiene backups probados, la empresa quiebra; "
        "y si expone datos por una mala política de permisos, la empresa enfrenta problemas legales gravísimos.",
        body_style
    ))
    story.append(Paragraph(
        "Aprendí que optimizar no es agregar índices sin medir sino estudiar el plan del optimizador con <code>EXPLAIN ANALYZE</code>; que la seguridad radica en el mínimo privilegio real "
        "y funciones securizadas con <code>SECURITY DEFINER</code>; que un plan de contingencia requiere pruebas cronometradas de restauración (RTO de 4.84 s y RPO de 1.70 min); que "
        "en arquitecturas modernas la complementariedad entre PostgreSQL (núcleo transaccional), MongoDB (read-models desnormalizados) y SQLite (borde desconectado) "
        "permite construir soluciones empresariales de alta disponibilidad; y fundamentalmente, que el verdadero valor de un programador radica en tener el criterio técnico "
        "para auditar la Inteligencia Artificial y tomar las decisiones correctas.",
        body_style
    ))

    # Construcción final del PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Informe compilado exitosamente: {pdf_path}")

if __name__ == "__main__":
    generar_pdf()
