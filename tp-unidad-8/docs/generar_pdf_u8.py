#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
GENERADOR DE INFORME TÉCNICO EN PDF - FOOD STORE UNIDAD 8 (UTN)
============================================================================
Autor: Fabrizio Simon
Herramienta: Python ReportLab / SimpleDocTemplate
Salida: informe.pdf (Máximo 6 páginas)
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
        # Encabezado sutil
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawString(36, 762, "UTN · TECNICATURA UNIVERSITARIA EN PROGRAMACIÓN | BASE DE DATOS II")
        self.setFont("Helvetica", 7.5)
        self.drawRightString(612 - 36, 762, "TP N.° 8: Food Store en la Feria (SQLite & PostgreSQL)")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(36, 756, 612 - 36, 756)

        # Pie de página
        self.line(36, 32, 612 - 36, 32)
        self.setFont("Helvetica", 8)
        self.drawString(36, 22, "Estudiante: Fabrizio Simon · Entrega Semana 13 (Cierre de Capa de Datos)")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(612 - 36, 22, page_str)
        self.restoreState()

def generar_pdf():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, "informe.pdf")

    # Margen de 36 pt (0.5 pulgada) para aprovechar al máximo el espacio de lectura
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=38
    )

    styles = getSampleStyleSheet()

    # Definición de estilos tipográficos con jerarquía visual y alta legibilidad
    primary_color = colors.HexColor("#0F2942")     # Azul marino profundo UTN
    secondary_color = colors.HexColor("#1E3A8A")   # Azul intermedio
    dark_text = colors.HexColor("#1A202C")         # Gris carbón para texto corrido
    border_color = colors.HexColor("#CBD5E1")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=primary_color,
        alignment=0,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'SectionHeading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=primary_color,
        spaceBefore=7,
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
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=dark_text,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1E3A8A")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
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
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#2D3748")
    )

    story = []

    # ENCABEZADO PRINCIPAL
    story.append(Paragraph("Trabajo Práctico N.º 8: Food Store en la Feria", title_style))
    story.append(Paragraph("La base de la tablet, sincronización con semáforo y cierre integral de la capa de datos", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=6))

    # =========================================================================
    # SECCIÓN 1: CONSIGNA 1.A - QUÉ DATOS VIAJAN
    # =========================================================================
    story.append(Paragraph("1. Consigna 1.a · Matriz de Transferencia de Datos hacia la Tablet Móvil", h1_style))
    story.append(Paragraph(
        "En un esquema <i>Offline-First</i> donde la tablet del Food Truck opera sin conexión confiable a Internet en la feria, "
        "se diseñó una instantánea mínima y desensibilizada. Solo viajan las columnas estrictamente requeridas para la toma de pedidos, "
        "impidiendo la exposición de datos sensibles o estratégicos ante eventuales robos o pérdidas físicas del dispositivo.",
        body_style
    ))

    # Tabla 1.a
    data_1a = [
        [Paragraph("Columna", table_header_style), Paragraph("¿Viaja?", table_header_style), Paragraph("Justificación Funcional y de Seguridad", table_header_style)],
        [Paragraph("<code>id</code>", table_cell_bold), Paragraph("<b>SÍ</b>", table_cell_style), Paragraph("Identificador numérico indispensable para relacionar los ítems del borrador con el catálogo descargado.", table_cell_style)],
        [Paragraph("<code>nombre</code>", table_cell_bold), Paragraph("<b>SÍ</b>", table_cell_style), Paragraph("Denominación visible en la interfaz para que el mozo identifique el producto en mostrador.", table_cell_style)],
        [Paragraph("<code>precio_centavos</code>", table_cell_bold), Paragraph("<b>SÍ</b>", table_cell_style), Paragraph("Precio de lista convertido a entero en centavos para calcular totales preliminares sin error de flotante.", table_cell_style)],
        [Paragraph("<code>stock_visto</code>", table_cell_bold), Paragraph("<b>SÍ</b>", table_cell_style), Paragraph("Existencia física al momento de la instantánea para alertar tempranamente si el producto ya estaba agotado.", table_cell_style)],
        [Paragraph("<code>disponible</code> (activo)", table_cell_bold), Paragraph("<b>SÍ</b>", table_cell_style), Paragraph("Bandera booleana (0/1) que habilita o deshabilita la selección del producto en el menú móvil.", table_cell_style)],
        [Paragraph("<code>eliminado</code> (lápida)", table_cell_bold), Paragraph("<b>SÍ</b>", table_cell_style), Paragraph("Mantiene integridad referencial local pero oculta el producto del catálogo comercial activo.", table_cell_style)],
        [Paragraph("<code>fecha_copia</code>", table_cell_bold), Paragraph("<b>SÍ</b>", table_cell_style), Paragraph("Marca temporal que permite a la aplicación móvil auditar la antigüedad de su caché local.", table_cell_style)],
        [Paragraph("Datos de usuarios (hash/mail)", table_cell_bold), Paragraph("<b>NO</b>", table_cell_style), Paragraph("Datos personales y credenciales sensibles (PII). No se requieren para armar borradores de venta.", table_cell_style)],
        [Paragraph("Costos de compra / márgenes", table_cell_bold), Paragraph("<b>NO</b>", table_cell_style), Paragraph("Secreto comercial del negocio. Si la tablet es sustraída en la feria, no se filtran costos ni proveedores.", table_cell_style)],
        [Paragraph("Historial de pedidos de otras tiendas", table_cell_bold), Paragraph("<b>NO</b>", table_cell_style), Paragraph("Saturaría el almacenamiento de la tablet y violaría el principio de mínimo privilegio.", table_cell_style)]
    ]

    t_1a = Table(data_1a, colWidths=[120, 45, 375])
    t_1a.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_1a)
    story.append(Spacer(1, 4))

    # Cuadro Regla de Oro
    data_oro = [[Paragraph(
        "<b>Regla de Oro: El móvil propone, el servidor dispone.</b><br/>"
        "PostgreSQL es la única Fuente de Verdad (Single Source of Truth). La tablet jamás confirma ventas fiscales ni altera stock; "
        "el estado <code>SIMULADO_APROBADO</code> es una pre-validación teórica, no una venta real.", callout_style
    )]]
    t_oro = Table(data_oro, colWidths=[540])
    t_oro.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#3B82F6")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_oro)
    story.append(Spacer(1, 6))

    # =========================================================================
    # SECCIÓN 2: CONSIGNA 2.C - LOS CASOS DE SINCRONIZACIÓN
    # =========================================================================
    story.append(Paragraph("2. Consigna 2.c · Resolución de Casos con el Semáforo de Sincronización", h1_style))
    story.append(Paragraph(
        "El semáforo evalúa atómicamente cada solicitud en estado <code>PENDIENTE</code> contra <code>snapshot_servidor</code> "
        "respetando la jerarquía obligatoria: <b>Rojo (RECHAZADO) > Amarillo (CONFLICTO) > Verde (SIMULADO_APROBADO)</b>.",
        body_style
    ))

    # Casos C2 a C6
    data_casos = [
        [Paragraph("Caso", table_header_style), Paragraph("Preparación y Comandos", table_header_style), Paragraph("Resultado Observado", table_header_style), Paragraph("Explicación Técnica y Justificación", table_header_style)],
        [
            Paragraph("<b>C2</b><br/>Subida de precio y aceptación", table_cell_bold),
            Paragraph("1. Borrador con Muzza a $100.00 (10000 centavos).<br/>2. Servidor sube precio a $125.00.<br/>3. Cliente acepta: se actualiza borrador a 12500 y se emite nueva solicitud.", code_style),
            Paragraph("Paso 1: <b>CONFLICTO</b><br/>Paso 2: <b>SIMULADO_APROBADO</b>", table_cell_style),
            Paragraph("El semáforo detecta discrepancia de precio sin problemas de stock. Al aceptar el cliente, se reintenta y aprueba limpiamente.", table_cell_style)
        ],
        [
            Paragraph("<b>C3</b><br/>Quiebre de stock", table_cell_bold),
            Paragraph("1. Borrador pidiendo 50 Napolitanas.<br/>2. Servidor tiene stock = 10.", code_style),
            Paragraph("<b>RECHAZADO</b><br/>(Stock insuficiente)", table_cell_style),
            Paragraph("La condición <code>cantidad > stock</code> activa inmediatamente la prioridad Roja, impidiendo sobreventas en la feria.", table_cell_style)
        ],
        [
            Paragraph("<b>C4</b><br/>Baja lógica (lápida)", table_cell_bold),
            Paragraph("1. Borrador con Producto 3 activo.<br/>2. Servidor marca <code>eliminado = 't'</code>.<br/>3. Recarga de catálogo en la tablet.", code_style),
            Paragraph("<b>RECHAZADO</b><br/>(Lápida activa)", table_cell_style),
            Paragraph("El producto dado de baja no se puede vender. La fila persiste en SQLite (integridad referencial) pero se oculta del catálogo activo.", table_cell_style)
        ],
        [
            Paragraph("<b>C5</b><br/>Aprobación limpia", table_cell_bold),
            Paragraph("1. Borrador con Producto 4 (2 un. a $4138.00). Coincide exactamente con el servidor.", code_style),
            Paragraph("<b>SIMULADO_APROBADO</b>", table_cell_style),
            Paragraph("Hay stock, el precio es idéntico y el producto está activo. Queda listo para su posterior confirmación transaccional.", table_cell_style)
        ],
        [
            Paragraph("<b>C6</b><br/>Reenvío / Idempotencia", table_cell_bold),
            Paragraph("1. Reenvío con el mismo <code>solicitud_uuid</code> de C5.<br/>2. Re-ejecución del semáforo.", code_style),
            Paragraph("<b>Error PRIMARY KEY</b><br/>(Estado C5 invariante)", table_cell_style),
            Paragraph("La clave primaria rechaza duplicados locales. El semáforo ignora solicitudes no pendientes, garantizando idempotencia.", table_cell_style)
        ]
    ]

    t_casos = Table(data_casos, colWidths=[70, 160, 110, 200])
    t_casos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_casos)
    story.append(Spacer(1, 4))

    # Párrafo Parada 8 y verificación PostgreSQL
    story.append(Paragraph(
        "<b>Protección real en sistema de producción (Parada 8):</b> En una arquitectura real, la protección de idempotencia reside "
        "en la API del backend mediante encabezados HTTP (<code>Idempotency-Key: &lt;UUID&gt;</code>) y una tabla central con restricción UNIQUE. "
        "Si la red se corta y el móvil reintenta, el servidor reconoce la clave y retorna la respuesta original sin volver a descontar stock ni duplicar cobros.",
        body_style
    ))

    # Auditoría PostgreSQL
    story.append(Paragraph(
        "<b>Comprobación de Invariabilidad en PostgreSQL:</b> Tras correr todas las simulaciones de la tablet, se ejecutó:<br/>"
        "<code>SELECT COUNT(*) FROM pedido;</code> &rarr; <b>200,001 pedidos</b> (0 ventas insertadas).<br/>"
        "<code>SELECT id_producto, stock FROM producto WHERE id_producto IN (1,2,3,4);</code> &rarr; "
        "Muzza: <b>5</b>, Napolitana: <b>10</b>, Prod. 3: <b>115</b>, Prod. 4: <b>130</b> (0 unidades descontadas).<br/>"
        "<i>Esto comprueba empíricamente que la operatoria móvil no altera la base transaccional central.</i>",
        body_style
    ))
    story.append(Spacer(1, 6))

    # =========================================================================
    # SECCIÓN 3: CONSIGNA 3.A - MAPA DE LA CAPA DE DATOS
    # =========================================================================
    story.append(Paragraph("3. Consigna 3.a · Mapa de la Capa de Datos del Ecosistema Food Store", h1_style))
    story.append(Paragraph(
        "A lo largo de la cursada integramos tres motores complementarios, asignando a cada uno una responsabilidad arquitectónica precisa:",
        body_style
    ))

    data_mapa = [
        [Paragraph("Motor de Base de Datos", table_header_style), Paragraph("Rol y Patrón Arquitectónico", table_header_style), Paragraph("¿Qué datos guarda?", table_header_style), Paragraph("¿Quién manda sobre cada dato? (Autoridad)", table_header_style)],
        [
            Paragraph("<b>PostgreSQL 18</b><br/>(Servidor Central)", table_cell_bold),
            Paragraph("<b>Núcleo Transaccional (OLTP)</b><br/>Single Source of Truth (SSoT)<br/>Consistencia ACID estricta", table_cell_style),
            Paragraph("• Usuarios, contraseñas y roles (RBAC).<br/>• Catálogo maestro de productos y precios oficiales.<br/>• Stock físico real e inventario.<br/>• Pedidos confirmados y facturación fiscal.<br/>• Auditoría forense y logs de conexiones.", table_cell_style),
            Paragraph("<b>AUTORIDAD ABSOLUTA</b> sobre precios, stock, ventas fiscales y usuarios. Ningún otro motor puede modificar estos datos directamente.", table_cell_style)
        ],
        [
            Paragraph("<b>MongoDB</b><br/>(Unidad 7)", table_cell_bold),
            Paragraph("<b>Read Model Documental</b><br/>Arquitectura CQRS<br/>Consultas masivas web", table_cell_style),
            Paragraph("• Pedidos desnormalizados con líneas de productos embebidas (<code>lineas</code>).<br/>• Instantáneas de clientes embebidos (<code>cliente</code>).<br/>• Catálogo JSON optimizado para APIs web.", table_cell_style),
            Paragraph("<b>AUTORIDAD SUBORDINADA (Lectura).</b> Si ocurre una discrepancia, PostgreSQL manda y la colección de MongoDB se regenera desde el origen.", table_cell_style)
        ],
        [
            Paragraph("<b>SQLite 3.50+</b><br/>(Unidad 8)", table_cell_bold),
            Paragraph("<b>Base Embebida de Borde (Edge)</b><br/>Tablet Móvil del Food Truck<br/>Operatoria Offline-First", table_cell_style),
            Paragraph("• Instantánea descargada (<code>snapshot_servidor</code>).<br/>• Catálogo en caché (<code>producto_cache</code>).<br/>• Borradores de pedidos tomados en la feria.<br/>• Ítems temporales y cola de sincronización.", table_cell_style),
            Paragraph("<b>AUTORIDAD LOCAL LIMITADA</b> a la interfaz del cajero y borradores locales. <b>CERO autoridad</b> sobre stock y precios del servidor central.", table_cell_style)
        ]
    ]

    t_mapa = Table(data_mapa, colWidths=[90, 110, 180, 160])
    t_mapa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_mapa)
    story.append(Spacer(1, 6))

    # =========================================================================
    # SECCIÓN 4: CONSIGNA 3.B - PLAN DE MANTENIMIENTO INTEGRADO
    # =========================================================================
    story.append(Paragraph("4. Consigna 3.b · Plan de Mantenimiento y Recuperación Integral", h1_style))
    story.append(Paragraph(
        "Como extensión directa del plan de contingencia probado en la Unidad 6 (RTO de 4.84 s y RPO de 1.70 min con <code>restore_test.ps1</code>):",
        body_style
    ))

    data_mantenimiento = [
        [Paragraph("Aspecto Operativo", table_header_style), Paragraph("Estrategia y Procedimiento de Mantenimiento", table_header_style)],
        [
            Paragraph("<b>¿Qué se respalda y cómo se prueba la restauración?</b>", table_cell_bold),
            Paragraph(
                "• <b>PostgreSQL:</b> Se respalda diariamente con <code>pg_dump</code> comprimido y archivado continuo de WALs (Point-In-Time Recovery). La restauración se valida de forma automática mediante <code>restore_test.ps1</code> en la base efímera <code>foodstore_restore_test</code> verificando la integridad de tablas y restricciones.<br/>"
                "• <b>MongoDB:</b> Backups semanales con <code>mongodump</code>. Si se corrompe, se regenera desde el catálogo relacional.<br/>"
                "• <b>SQLite (Tablets):</b> Las bases locales <b>NO</b> se respaldan. Su arquitectura es descartable (<i>ephemeral</i>): si una tablet se rompe o extravía, se provisiona una nueva, se descarga la instantánea fresca y se continúa operando. Solo se resguardan temporalmente los borradores no sincronizados vía USB o red local si la conexión falla.",
                table_cell_style
            )
        ],
        [
            Paragraph("<b>¿Qué hacen las tablets ante un restore viejo de PostgreSQL?</b>", table_cell_bold),
            Paragraph(
                "Cada instantánea exportada incluye una marca de época (<code>snapshot_epoch</code>). Si el servidor sufre un incidente y restaura un backup de 24 horas atrás, la tablet detecta que el epoch del servidor es menor al de su catálogo local. La tablet <b>invalida inmediatamente su caché local (<code>producto_cache</code>)</b>, bloquea la emisión de nuevos pedidos y pasa todas las solicitudes no sincronizadas a estado <code>CONFLICTO_RESTAURACION</code> para su re-evaluación en mostrador, previniendo sobreventas o tarifas desfasadas.",
                table_cell_style
            )
        ],
        [
            Paragraph("<b>¿Cada cuánto y quién revisa las solicitudes en CONFLICTO o RECHAZADO?</b>", table_cell_bold),
            Paragraph(
                "• <b>En tiempo real durante la feria:</b> El mozo/cajero que opera la tablet. Si da <code>CONFLICTO</code> (cambio de precio), consulta al cliente en mostrador si acepta la diferencia; si da <code>RECHAZADO</code> (sin stock), cancela el ítem de inmediato.<br/>"
                "• <b>Cierre de jornada (cada 24 horas):</b> El encargado de feria y el administrador de datos (<code>admin_datos</code>) auditan la tabla <code>cola_sync</code> para detectar quiebres sistemáticos de stock, productos descatalogados o fallas de conectividad.",
                table_cell_style
            )
        ]
    ]

    t_mantenimiento = Table(data_mantenimiento, colWidths=[150, 390])
    t_mantenimiento.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_mantenimiento)
    story.append(Spacer(1, 6))

    # =========================================================================
    # SECCIÓN 5: CONSIGNA 3.C - CODE REVIEW CON IA
    # =========================================================================
    story.append(Paragraph("5. Consigna 3.c · Code Review con IA sobre Scripts de la Cursada", h1_style))
    story.append(Paragraph(
        "Se solicitó a la herramienta de IA una revisión técnica de los scripts desarrollados en las Unidades 5, 6 y 8. "
        "A continuación se detallan los hallazgos con su evaluación crítica y la comprobación empírica en las bases:",
        body_style
    ))

    data_cr = [
        [Paragraph("ID / Unidad", table_header_style), Paragraph("Componente", table_header_style), Paragraph("Propuesta de la IA", table_header_style), Paragraph("Decisión Humana", table_header_style), Paragraph("Motivo Técnico y Comprobación en Base", table_header_style)],
        [
            Paragraph("<b>H-1</b><br/>Unidad 5", table_cell_bold),
            Paragraph("<code>fn_autenticar</code><br/>(Seguridad)", table_cell_style),
            Paragraph("Cambiar la función a <code>SECURITY DEFINER</code> con <code>search_path</code> seguro.", table_cell_style),
            Paragraph("<b>ACEPTADO Y CORREGIDO</b>", table_cell_style),
            Paragraph("Como <code>SECURITY INVOKER</code>, el usuario <code>app_web</code> (sin SELECT sobre <code>usuario</code>) recibía permiso denegado. Se corrigió a SECURITY DEFINER asignando el owner a <code>admin_datos</code>.", table_cell_style)
        ],
        [
            Paragraph("<b>H-2</b><br/>Unidad 6", table_cell_bold),
            Paragraph("<code>maintenance.sql</code><br/>(Optimización)", table_cell_style),
            Paragraph("Ejecutar <code>VACUUM FULL ANALYZE</code> diariamente para compactar espacio.", table_cell_style),
            Paragraph("<b>DESCARTADO CON FUNDAMENTO</b>", table_cell_style),
            Paragraph("<code>VACUUM FULL</code> adquiere bloqueo exclusivo (<code>ACCESS EXCLUSIVE LOCK</code>), impidiendo lecturas y escrituras durante minutos y destruyendo la disponibilidad de la tienda en producción.", table_cell_style)
        ],
        [
            Paragraph("<b>H-3</b><br/>Unidad 8", table_cell_bold),
            Paragraph("<code>schema_sqlite.sql</code><br/>(Móvil)", table_cell_style),
            Paragraph("Usar claves autonuméricas <code>INTEGER PRIMARY KEY</code> en borradores locales.", table_cell_style),
            Paragraph("<b>DESCARTADO CON FUNDAMENTO</b>", table_cell_style),
            Paragraph("En un entorno distribuido offline con múltiples tablets, los enteros autoincrementales colisionan inevitablemente al sincronizar. Se reemplazó por <b>UUID v4</b>.", table_cell_style)
        ]
    ]

    t_cr = Table(data_cr, colWidths=[55, 75, 125, 95, 190])
    t_cr.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_cr)
    story.append(Spacer(1, 4))

    # Desarrollo detallado del descarte crítico
    story.append(Paragraph(
        "<b>Desarrollo y Comprobación del Descarte Crítico (H-2 · VACUUM FULL):</b><br/>"
        "La IA propuso <code>VACUUM FULL</code> argumentando que recupera espacio en disco tras borrados masivos. "
        "Sin embargo, al verificar en la documentación de PostgreSQL y en el catálogo <code>pg_locks</code>, <code>VACUUM FULL</code> "
        "reescribe físicamente la tabla adquiriendo un <code>AccessExclusiveLock</code>. Esto bloquea absolutamente todas las consultas "
        "<code>SELECT</code> de los clientes en la tienda web y las transacciones de las tablets. En una base con 200,000 pedidos, "
        "esta operación degrada el SLA y paraliza la facturación. El descarte se fundamentó manteniendo el mantenimiento estándar "
        "con <code>VACUUM (ANALYZE, VERBOSE)</code>, el cual limpia tuplas muertas de forma concurrente sin bloquear lecturas ni escrituras.",
        body_style
    ))

    # Construcción final del documento
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Informe compilado exitosamente: {pdf_path}")

if __name__ == "__main__":
    generar_pdf()
