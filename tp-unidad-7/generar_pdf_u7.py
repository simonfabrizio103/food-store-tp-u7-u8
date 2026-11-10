import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
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
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(612 - 40, 25, page_str)
        self.drawString(40, 25, "Bases de Datos II — TP Unidad 7: NoSQL y nuevas formas de almacenamiento (Food Store)")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 35, 612 - 40, 35)
        self.restoreState()

def build_pdf():
    pdf_path = os.path.join(os.path.dirname(__file__), "informe_u7.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    primary = colors.HexColor("#1A365D")
    secondary = colors.HexColor("#2B6CB0")
    dark = colors.HexColor("#2D3748")
    accent_green = colors.HexColor("#22543D")
    table_bg = colors.HexColor("#EBF8FF")
    code_bg = colors.HexColor("#F7FAFC")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=primary,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=secondary,
        alignment=1
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=dark,
        alignment=1
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=secondary,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )
    
    body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=dark,
        spaceAfter=4
    )
    
    code_box = ParagraphStyle(
        'CodeBox',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor("#1A202C")
    )
    
    th_cell = ParagraphStyle(
        'THCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10,
        textColor=dark
    )
    
    td_cell = ParagraphStyle(
        'TDCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10,
        textColor=dark
    )
    
    td_green = ParagraphStyle(
        'TDGreen',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10,
        textColor=accent_green
    )

    story = []
    
    # Encabezado
    story.append(Paragraph("TECNICATURA UNIVERSITARIA EN PROGRAMACIÓN — BASES DE DATOS II (UTN FRM)", subtitle_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("Trabajo Práctico · Unidad 7: NoSQL y Nuevas Formas de Almacenamiento", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Proyecto:</b> Food Store | <b>Motores:</b> PostgreSQL 18 & MongoDB 7+ | <b>Alumno:</b> Fabrizio Simon | <b>Fecha:</b> 10/11/2026", meta_style))
    story.append(Spacer(1, 8))
    
    # ==========================================
    # SECCIÓN 1: MODELO DOCUMENTAL Y MIGRACIÓN
    # ==========================================
    story.append(Paragraph("1. Modelo Documental y Estrategia de Migración (Parte 1)", h1_style))
    story.append(Paragraph(
        "<b>Subconjunto seleccionado de Food Store:</b> Se tomó el módulo central de pedidos y ventas compuesto por "
        "las tablas relacionales <code>pedido</code>, <code>pedido_producto</code>, <code>cliente</code>, <code>producto</code> y <code>categoria</code>. "
        "En PostgreSQL, consultar un pedido implica vincular claves foráneas en cascada.", body
    ))
    story.append(Paragraph(
        "<b>Esquema documental en MongoDB (<code>foodstore_nosql.pedidos</code>):</b> Se adoptó el patrón de diseño orientado a agregados "
        "(<i>Aggregate-Oriented Design</i>), encapsulando el ciclo de vida completo del pedido en un único documento:", body
    ))
    
    json_sample = """{
  "_id": 2,  // Se conserva id_pedido de PostgreSQL
  "fecha": ISODate("2025-10-30T18:44:05.346Z"),
  "forma_pago": "EFECTIVO",
  "estado": "ENTREGADO",
  "cliente": { "id_cliente": 1, "nombre": "Juan", "email": "juan@test.com" },
  "lineas": [
    { "id_producto": 3, "nombre": "Producto masivo 3", "categoria": "Pizzas", "cantidad": 1, "precio_unitario": 500.00, "subtotal": 500.00 },
    { "id_producto": 4, "nombre": "Producto masivo 4", "categoria": "Categoria masiva 1", "cantidad": 2, "precio_unitario": 600.00, "subtotal": 1200.00 }
  ],
  "total": 1700.00
}"""
    t_code = Table([[Preformatted(json_sample, code_box)]], colWidths=[532])
    t_code.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), code_bg),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Justificación técnica de diseño (Embeber vs Referenciar):</b>", h2_style))
    story.append(Paragraph(
        "• <b>Líneas de pedido embebidas (1:N fuerte):</b> Las líneas de detalle carecen de sentido de negocio fuera del pedido. Siempre se consultan juntas "
        "para emitir comprobantes o preparar despachos. Embeberlas permite recuperarlas en un único acceso a disco (<i>single-document read</i>), sin latencia de JOINs, "
        "y garantiza atomicidad nativa en la inserción sin sobrecarga de transacciones distribuidas.", body
    ))
    story.append(Paragraph(
        "• <b>Cliente parcialmente embebido (Snapshot histórico):</b> Se embeben únicamente los atributos esenciales (<code>nombre</code>, <code>email</code>). "
        "Esto desacopla el pedido de cambios futuros en los datos maestros del cliente, congelando el comprobante de venta tal como ocurrió en ese instante.", body
    ))
    story.append(Paragraph(
        "• <b>Reglas de integridad conservadas:</b> Se preserva que <code>cantidad &gt; 0</code> y <code>precio_unitario &gt;= 0</code> en cada línea; "
        "el <code>total</code> del documento equivale exactamente a la suma de los subtotales; y los precios unitarios son históricos e inmutables.", body
    ))
    story.append(Spacer(1, 6))

    # ==========================================
    # SECCIÓN 2: CONSULTAS Y VERIFICACIÓN
    # ==========================================
    story.append(Paragraph("2. Consultas Ejecutadas y Evidencia de Resultados (Parte 2)", h1_style))
    story.append(Paragraph(
        "Se migraron 6 pedidos reales de Food Store (IDs del 2 al 7) con múltiples productos y distintos estados (<code>ENTREGADO</code>, "
        "<code>PENDIENTE</code>, <code>CANCELADO</code>). A continuación se contrastan las 4 consultas ejecutadas en ambos motores:", body
    ))

    q_data = [
        [Paragraph("Objetivo de Consulta", th_cell), Paragraph("Sintaxis en MongoDB", th_cell), Paragraph("Sintaxis en PostgreSQL", th_cell), Paragraph("Resultado Obtenido", th_cell)],
        [
            Paragraph("<b>4.a) Todos los pedidos con ID y estado</b>", td_cell),
            Paragraph("<code>db.pedidos.find({}, {_id: 1, estado: 1})</code>", td_cell),
            Paragraph("<code>SELECT id_pedido, estado FROM pedido WHERE id_pedido BETWEEN 2 AND 7</code>", td_cell),
            Paragraph("6 pedidos recuperados (IDs 2, 3, 4, 5, 6, 7). Estados idénticos.", td_green)
        ],
        [
            Paragraph("<b>4.b) Filtrar por estado 'ENTREGADO'</b>", td_cell),
            Paragraph("<code>db.pedidos.find({estado: 'ENTREGADO'})</code>", td_cell),
            Paragraph("<code>SELECT p.id_pedido, ... WHERE p.estado = 'ENTREGADO'</code>", td_cell),
            Paragraph("<b>3 pedidos:</b> IDs 2 ($1700), 4 ($2050), 7 ($500).", td_green)
        ],
        [
            Paragraph("<b>4.c) Buscar pedidos con producto ID 3</b>", td_cell),
            Paragraph("<code>db.pedidos.find({'lineas.id_producto': 3})</code>", td_cell),
            Paragraph("<code>SELECT DISTINCT ... JOIN pedido_producto pp WHERE pp.id_producto = 3</code>", td_cell),
            Paragraph("<b>3 pedidos:</b> IDs 2, 4, 6 (coincidencia exacta).", td_green)
        ],
        [
            Paragraph("<b>4.d) Pedidos con total &gt; $2000.00</b>", td_cell),
            Paragraph("<code>db.pedidos.find({total: {$gt: 2000}})</code>", td_cell),
            Paragraph("<code>SELECT ... GROUP BY p.id_pedido HAVING SUM(...) &gt; 2000</code>", td_cell),
            Paragraph("<b>2 pedidos:</b> IDs 4 ($2050) y 6 ($3500). Umbral segmenta compras mayoristas.", td_green)
        ],
    ]
    t_q = Table(q_data, colWidths=[120, 145, 155, 112])
    t_q.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), table_bg),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_q)
    story.append(Spacer(1, 6))

    # ==========================================
    # SECCIÓN 3: TABLA DE VERIFICACIÓN CRUZADA
    # ==========================================
    story.append(Paragraph("3. Tabla de Verificación Cruzada entre Motores (Consigna 5)", h1_style))
    t_verif_data = [
        [Paragraph("Consulta / Filtro Evaluado", th_cell), Paragraph("Cantidad en PostgreSQL", th_cell), Paragraph("Cantidad en MongoDB", th_cell), Paragraph("¿Coinciden los IDs?", th_cell), Paragraph("Detalle de IDs Recuperados", th_cell)],
        [Paragraph("<b>Estado seleccionado ('ENTREGADO')</b>", td_cell), Paragraph("<b>3</b>", td_cell), Paragraph("<b>3</b>", td_cell), Paragraph("<b>Sí</b>", td_green), Paragraph("IDs: [2, 4, 7]", td_green)],
        [Paragraph("<b>Producto seleccionado (ID = 3)</b>", td_cell), Paragraph("<b>3</b>", td_cell), Paragraph("<b>3</b>", td_cell), Paragraph("<b>Sí</b>", td_green), Paragraph("IDs: [2, 4, 6]", td_green)]
    ]
    t_verif = Table(t_verif_data, colWidths=[150, 95, 95, 80, 112])
    t_verif.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), table_bg),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_verif)
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "<i>Análisis de consistencia:</i> No se registró ninguna discrepancia. Al modelar el ID original como <code>_id</code> numérico e incorporar "
        "los precios históricos exactos, las consultas por estado y por producto en arreglo arrojaron conjuntos idénticos en ambos motores.", body
    ))
    story.append(Spacer(1, 6))

    # ==========================================
    # SECCIÓN 4: EVALUACIÓN DE TECNOLOGÍA E IA
    # ==========================================
    story.append(Paragraph("4. Evaluación Tecnológica y Contraste Crítico con la IA (Parte 3)", h1_style))
    story.append(Paragraph(
        "Se consultó a una herramienta de IA para comparar PostgreSQL y MongoDB en pedidos de Food Store, analizando accesos frecuentes a pedidos completos "
        "y necesidad de coherencia en importes y stock. Se contrastaron críticamente dos afirmaciones de la IA:", body
    ))

    c1_text = (
        "<b>Contraste 1 — Transacciones ACID en MongoDB:</b><br/>"
        "• <i>Afirmación de la IA:</i> «MongoDB no es recomendable para pedidos porque no soporta transacciones ACID y pueden quedar pedidos grabados sin stock».<br/>"
        "• <i>Contraste oficial:</i> <b>Falso y desactualizado.</b> El manual oficial de MongoDB (<i>MongoDB Manual - Transactions</i>) documenta que desde "
        "la versión 4.0 existen transacciones multi-documento con semántica ACID completa (<code>session.startTransaction()</code>). Además, al estar las líneas "
        "embebidas dentro del pedido, cualquier inserción o actualización es <b>atómica por naturaleza a nivel de documento</b> sin requerir transacciones distribuidas."
    )
    story.append(Paragraph(c1_text, body))
    story.append(Spacer(1, 2))

    c2_text = (
        "<b>Contraste 2 — Rendimiento de los JOINs en PostgreSQL:</b><br/>"
        "• <i>Afirmación de la IA:</i> «En PostgreSQL cada consulta de un pedido completo colapsa el rendimiento porque requiere 4 JOINs pesados obligatorios».<br/>"
        "• <i>Contraste de laboratorio:</i> <b>Exagerado.</b> En el laboratorio comprobé con <code>EXPLAIN ANALYZE</code> que un <code>JOIN</code> entre "
        "<code>pedido</code> y <code>pedido_producto</code> sobre clave foránea indexada toma <b>0.08 ms</b> sobre 200,000 registros. La ventaja real de MongoDB "
        "no es el tiempo de búsqueda, sino que entrega el objeto BSON/JSON ensamblado directamente a la API web, ahorrando la sobrecarga de mapeo relacional (ORM)."
    )
    story.append(Paragraph(c2_text, body))
    story.append(Spacer(1, 6))

    # ==========================================
    # SECCIÓN 5: CONCLUSIÓN TÉCNICA
    # ==========================================
    story.append(Paragraph("5. Conclusión Técnica Fundamentada (Consigna 7)", h1_style))
    concl_text = (
        "Para Food Store recomiendo adoptar una <b>arquitectura híbrida políglota</b> con separación de responsabilidades (patrón CQRS). "
        "<br/><br/>"
        "En el <b>módulo transaccional y de facturación</b>, <b>PostgreSQL</b> debe mantenerse como la fuente única de la verdad (<i>Single Source of Truth</i>). "
        "Criterio técnico 1: <b>Garantía estricta de integridad referencial y unicidad</b>: las claves foráneas y restricciones <code>CHECK</code> impiden inconsistencias "
        "contables, pedidos huérfanos o ventas de productos inexistentes, algo fundamental para auditoría fiscal. "
        "<br/><br/>"
        "En el <b>módulo de consulta de la tienda web y mobile</b>, <b>MongoDB</b> es la solución superior para almacenar los pedidos cerrados y el catálogo de productos. "
        "Criterio técnico 2: <b>Patrón de acceso orientado a agregados y escalabilidad de lectura</b>: la aplicación web consulta el pedido como un único bloque atómico "
        "(datos del cliente, líneas y total). Al estar embebidos en un solo documento BSON, MongoDB resuelve la lectura en un único acceso a disco (<code>findOne</code>), "
        "evitando la sobrecarga de ensamblado y permitiendo escalabilidad horizontal (<i>sharding</i>) sin degradar la base transaccional principal."
    )
    t_concl = Table([[Paragraph(concl_text, body)]], colWidths=[532])
    t_concl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#2B6CB0")),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_concl)

    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF de Unidad 7 generado exitosamente en:", pdf_path)

if __name__ == "__main__":
    build_pdf()
