import os
from io import BytesIO

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

LOGO_PATH = "assets/logo.jpg"
PAGE_W, PAGE_H = letter
LM = RM = 1.5 * cm
TM = BM = 1.5 * cm
AW = PAGE_W - LM - RM  # ~527 pts

NAVY   = colors.HexColor("#4472C4")   # azul office
GRAY  = colors.HexColor("#4472C4")
GREEN  = colors.HexColor("#1a7f3c")
LGRAY  = colors.HexColor("#f2f2f2")
GRAY  = colors.HexColor("#d6dce4")
WHITE  = colors.white
BLACK  = colors.black


def _fc(value):
    try:
        v = round(float(value or 0))
        return f"${v:,}".replace(",", ".")
    except Exception:
        return "$0"


def _p(text, style):
    return Paragraph(str(text or ""), style)


class QuotationPDF:

    def __init__(self, data: dict):
        self.d = data
        self._build_styles()

    def _build_styles(self):
        base = dict(fontName="Helvetica", fontSize=7, leading=9)
        self.s   = ParagraphStyle("s",  **base)
        self.sb  = ParagraphStyle("sb", fontName="Helvetica-Bold", fontSize=7,  leading=9)
        self.sc  = ParagraphStyle("sc", alignment=TA_CENTER, **base)
        self.scb = ParagraphStyle("scb",fontName="Helvetica-Bold", fontSize=7,  leading=9, alignment=TA_CENTER)
        self.sw  = ParagraphStyle("sw", fontName="Helvetica-Bold", fontSize=7,  leading=9, textColor=BLACK, alignment=TA_CENTER)
        self.swl = ParagraphStyle("swl",fontName="Helvetica-Bold", fontSize=7,  leading=9, textColor=BLACK)
        self.sr  = ParagraphStyle("sr", alignment=TA_RIGHT, **base)
        self.srb = ParagraphStyle("srb",fontName="Helvetica-Bold", fontSize=7,  leading=9, alignment=TA_RIGHT)
        self.big = ParagraphStyle("big",fontName="Helvetica-Bold", fontSize=13, leading=16, alignment=TA_CENTER)
        self.ttl = ParagraphStyle("ttl",fontName="Helvetica-Bold", fontSize=8,  leading=10, alignment=TA_CENTER)
        self.sh9 = ParagraphStyle("sh9",fontName="Helvetica-Bold", fontSize=9,  leading=11, alignment=TA_CENTER)

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC
    # ─────────────────────────────────────────────────────────────────────────
    def generate(self) -> bytes:
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter,
                                leftMargin=LM, rightMargin=RM,
                                topMargin=TM,  bottomMargin=BM)
        story = []
        self._header(story)
        story.append(Spacer(1, 3))
        self._info_table(story)
        story.append(Spacer(1, 3))
        self._items_table(story)
        self._apu_sections(story)
        self._photos(story)
        doc.build(story)
        return buf.getvalue()

    # ─────────────────────────────────────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────────────────────────────────────
    def _header(self, story):
        logo_w, logo_h = 3.8 * cm, 1.6 * cm
        if os.path.exists(LOGO_PATH):
            left_cell = Image(LOGO_PATH, width=logo_w, height=logo_h)
        else:
            left_cell = _p("MEGA HYDRAULIC S.A.S", self.scb)

        right_cell = _p("FORMATO DE COTIZACION - SUMINISTRO DE SERVICIOS",
                        ParagraphStyle("ht", fontName="Helvetica-Bold",
                                       fontSize=11, leading=13, alignment=TA_CENTER))
        t = Table([[left_cell, right_cell]], colWidths=[logo_w + 0.4 * cm, AW - logo_w - 0.4 * cm])
        t.setStyle(TableStyle([
            ("BOX",        (0, 0), (-1, -1), 1, BLACK),
            ("LINEAFTER",  (0, 0), (0, -1),  1, BLACK),
            ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",      (0, 0), (0,  0),  "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ]))
        story.append(t)

    # ─────────────────────────────────────────────────────────────────────────
    # INFO TABLE  (orden exacto según imagen de referencia)
    # ─────────────────────────────────────────────────────────────────────────
    def _info_table(self, story):
        d = self.d
        # 6 columnas: label | ciudad/resp | fecha | señores | der1 | der2
        C = [80, 110, 80, 52, 100, 105]   # = 527

        def lbl(txt):  return _p(txt, self.swl)   # blanco bold izq (fondo azul)
        def val(txt):  return _p(txt, self.s)
        def valb(txt): return _p(txt, self.sb)

        fecha_str   = str(d.get("activity_date") or "")
        subtotal    = _fc(d.get("subtotal") or 0)
        big_value   = _p(f"{subtotal} + IVA", self.big)
        nro_cot     = str(d.get("quotation_number") or "")
        directed    = (d.get("directed_to") or "").strip()
        responsible = (d.get("responsible_name") or "").strip()
        if directed and responsible:
            dirigido_cell = f"{directed}  //  INTERVENTOR: {responsible}"
        elif directed:
            dirigido_cell = directed
        else:
            dirigido_cell = responsible

        rows = [
            # 0 – Ciudad | city | Fecha+date | SEÑORES | ClientName(span 4-5)
            [lbl("Ciudad:"),
             val(d.get("city") or ""),
             _p(f"Fecha:  {fecha_str}", self.sb),
             _p("SEÑORES", self.sb),
             valb(d.get("client_name") or ""),
             ""],

            # 1 – DIRIGIDO A | dirigido // INTERVENTOR: responsable (span 1-3) | N°COT+num(span 4-5)
            [lbl("DIRIGIDO A"),
             val(dirigido_cell),
             "", "",
             _p(f"N° COTIZACION  {nro_cot}", self.sb),
             ""],

            # 2 – COTIZANTE | MEGA(span 1-3) | TEL(4) | NIT(5)
            [lbl("COTIZANTE"),
             val("MEGA HYDRAULIC S.A.S"),
             "", "",
             _p(f"TEL:{d.get('phone') or ''}", self.sb),
             _p(f"NIT:{d.get('nit') or ''}", self.sb)],

            # 3 – AREA | línea(span 1-5)
            [lbl("AREA"),
             val(d.get("client_line_name") or ""),
             "", "", "", ""],

            # 4 – ALCANCE | scope(span 1-5)
            [lbl("ALCANCE DE\nLA ACTIVIDAD"),
             _p(d.get("scope") or "", self.s),
             "", "", "", ""],

            # 5 – TIEMPO DE ENTREGA | delivery(span 1-5)
            [lbl("TIEMPO DE\nENTREGA"),
             val(d.get("delivery_time") or ""),
             "", "", "", ""],

            # 6 – VALOR | big(span 1-3) | DONDE SE EJECUTA(span 4-5)
            [lbl("VALOR DE\nLA ACTIVIDAD"),
             big_value,
             "", "",
             _p(f"DONDE SE EJECUTA:  {d.get('execution_place') or ''}", self.sb),
             ""],

            # 7 – DESCRIPCION | texto(span 1-5)
            [lbl("DESCRIPCION\nDE LA ACTIVIDAD"),
             val(d.get("activity_description") or ""),
             "", "", "", ""],
        ]

        cmds = [
            ("BOX",          (0, 0), (-1, -1), 0.5, BLACK),
            ("INNERGRID",    (0, 0), (-1, -1), 0.5, BLACK),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",   (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 2),
            ("LEFTPADDING",  (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            # Col 0: azul (labels en blanco)
            ("BACKGROUND",   (0, 0), (0, -1), WHITE),
            # Row 0: ClientName span 4-5
            ("SPAN", (4, 0), (5, 0)),
            # Row 1: responsable span 1-3; N°COT span 4-5
            ("SPAN", (1, 1), (3, 1)),
            ("SPAN", (4, 1), (5, 1)),
            # Row 2: MEGA span 1-3
            ("SPAN", (1, 2), (3, 2)),
            # Rows 3-5: valor span 1-5
            ("SPAN", (1, 3), (5, 3)),
            ("SPAN", (1, 4), (5, 4)),
            ("SPAN", (1, 5), (5, 5)),
            # Row 6: big span 1-3; DONDE span 4-5
            ("SPAN", (1, 6), (3, 6)),
            ("SPAN", (4, 6), (5, 6)),
            # Row 7: description span 1-5
            ("SPAN", (1, 7), (5, 7)),
            # Big value row
            ("ALIGN",        (1, 6), (3, 6), "CENTER"),
            ("TOPPADDING",   (0, 6), (-1, 6), 5),
            ("BOTTOMPADDING",(0, 6), (-1, 6), 5),
        ]

        t = Table(rows, colWidths=C)
        t.setStyle(TableStyle(cmds))
        story.append(t)

    # ─────────────────────────────────────────────────────────────────────────
    # ITEMS / CUADRO DE CANTIDADES
    # ─────────────────────────────────────────────────────────────────────────
    def _items_table(self, story):
        d = self.d
        # ITEM | SAP | DESCRIPCION | UN | CANT | V/UNIT | VTOTAL | (no accion)
        C = [32, 45, 196, 38, 38, 84, 84]  # = 517  (leaving ~10 extra for inner padding)
        # Adjust to exactly AW
        C[2] += AW - sum(C)   # absorb rounding into description col

        # ── Section title ──────────────────────────────────────────────────
        title = Table([[_p("CUADROS DE CANTIDADES DE OBRA", self.sw)]],
                      colWidths=[AW])
        title.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), GRAY),
            ("BOX",          (0,0), (-1,-1), 0.5, BLACK),
            ("TOPPADDING",   (0,0), (-1,-1), 3),
            ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ]))
        story.append(title)

        # ── Table header ────────────────────────────────────────────────────
        th = [
            [_p("DESCRIPCION DE LAS ACTIVIDADES DEL SERVICIO", self.sw),
             "", "",
             _p("UN",        self.sw),
             _p("CANT",      self.sw),
             _p("VALOR/UNIT",self.sw),
             _p("VR/TOTAL",  self.sw)],
            [_p("ITEM",       self.sw),
             _p("Código SAP", self.sw),
             "", "", "", "", ""],
        ]
        thead = Table(th, colWidths=C)
        thead.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), GRAY),
            ("BOX",          (0,0), (-1,-1), 0.5, BLACK),
            ("INNERGRID",    (0,0), (-1,-1), 0.5, BLACK),
            ("TOPPADDING",   (0,0), (-1,-1), 2),
            ("BOTTOMPADDING",(0,0), (-1,-1), 2),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("SPAN",         (0,0), (2, 0)),  # DESCRIPCION spans cols 0-2 in row 0
            ("SPAN",         (3,0), (3, 1)),  # UN spans rows 0-1
            ("SPAN",         (4,0), (4, 1)),  # CANT spans rows 0-1
            ("SPAN",         (5,0), (5, 1)),  # V/UNIT spans rows 0-1
            ("SPAN",         (6,0), (6, 1)),  # VTOTAL spans rows 0-1
            ("SPAN",         (2,1), (2, 1)),  # empty description col row 1
        ]))
        story.append(thead)

        # ── Data rows ───────────────────────────────────────────────────────
        all_items = d.get("items", [])
        # Separate by type
        regular = [i for i in all_items if i["item_type"] in ("item", "auto_labor", "auto_materials")]
        logistics = next((i for i in all_items if i["item_type"] == "logistics"), None)
        surcharge = next((i for i in all_items if i["item_type"] == "surcharge"), None)

        body_rows = []
        for idx, item in enumerate(regular, start=1):
            body_rows.append([
                _p(str(idx),              self.sc),
                _p(item.get("sap_code") or "", self.sc),
                _p(item.get("description") or "", self.s),
                _p(item.get("unit") or "UND", self.sc),
                _p(str(round(float(item.get("quantity") or 0))), self.sc),
                _p(_fc(item.get("unit_price") or 0), self.sr),
                _p(_fc(item.get("total_price") or 0), self.sr),
            ])

        # Logistica fixed row
        log_qty  = round(float((logistics or {}).get("quantity") or 0))
        log_up   = _fc((logistics or {}).get("unit_price") or 0)
        log_tot  = _fc((logistics or {}).get("total_price") or 0)
        body_rows.append([
            _p("LOGISTICA\nADICIONAL", self.sb),
            "",
            _p("LOGÍSTICA Y TRANSPORTE", self.sc),
            _p((logistics or {}).get("unit") or "UND", self.sc),
            _p(str(log_qty), self.sc),
            _p(log_up,  self.sr),
            _p(log_tot, self.sr),
        ])
        log_row_idx = len(body_rows) - 1

        # Recargos fixed row
        rec_qty = round(float((surcharge or {}).get("quantity") or 0))
        rec_up  = _fc((surcharge or {}).get("unit_price") or 0)
        rec_tot = _fc((surcharge or {}).get("total_price") or 0)
        body_rows.append([
            _p("RECARGOS\nALTURA", self.sb),
            "",
            _p("TRABAJO EN ALTURA", self.sc),
            _p((surcharge or {}).get("unit") or "UND", self.sc),
            _p(str(rec_qty), self.sc),
            _p(rec_up,  self.sr),
            _p(rec_tot, self.sr),
        ])
        rec_row_idx = len(body_rows) - 1

        # Subtotal row
        subtotal_val = _fc(d.get("subtotal") or 0)
        body_rows.append([
            _p("SUBTOTAL ACTIVIDADES", self.sw),
            "", "", "", "", "",
            _p(subtotal_val, ParagraphStyle("sv", fontName="Helvetica-Bold",
                                            fontSize=8, leading=10,
                                            textColor=BLACK, alignment=TA_RIGHT)),
        ])
        sub_row_idx = len(body_rows) - 1

        tbody = Table(body_rows, colWidths=C)
        cmds = [
            ("BOX",          (0,0), (-1,-1), 0.5, BLACK),
            ("INNERGRID",    (0,0), (-1,-1), 0.5, BLACK),
            ("TOPPADDING",   (0,0), (-1,-1), 2),
            ("BOTTOMPADDING",(0,0), (-1,-1), 2),
            ("LEFTPADDING",  (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            # Logistica and recargos: merge cols 0-1
            ("SPAN",  (0, log_row_idx), (1, log_row_idx)),
            ("SPAN",  (0, rec_row_idx), (1, rec_row_idx)),
            # Subtotal: merge cols 0-5
            ("SPAN",  (0, sub_row_idx), (5, sub_row_idx)),
            ("BACKGROUND", (0, sub_row_idx), (-1, sub_row_idx), GREEN),
            ("ROWBACKGROUNDS", (0,0), (-1, sub_row_idx - 1), [WHITE, LGRAY]),
        ]
        tbody.setStyle(TableStyle(cmds))
        story.append(tbody)

    # ─────────────────────────────────────────────────────────────────────────
    # APU SECTIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _apu_section_title(self, title_text):
        t = Table([[_p(title_text, self.sw)]], colWidths=[AW])
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), GRAY),
            ("BOX",          (0,0), (-1,-1), 0.5, BLACK),
            ("TOPPADDING",   (0,0), (-1,-1), 3),
            ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ]))
        return t

    def _apu_sections(self, story):
        d = self.d
        story.append(Spacer(1, 6))

        # ── MANO DE OBRA ────────────────────────────────────────────────────
        labor_items = d.get("labor_items", [])
        story.append(self._apu_section_title("ANALISIS APU.  MANO DE OBRA"))
        # cols: COD | DESC | UND | CANT | VALOR Miles | SUBTOTAL | DESARROLLO
        Cl = [45, 145, 35, 38, 62, 62, 140]  # sum = 527
        Cl[1] += AW - sum(Cl)

        lh = [[_p("CODIGO",    self.sw), _p("DESCRIPCION", self.sw),
               _p("UND.",      self.sw), _p("CANT.",       self.sw),
               _p("VALOR\nMiles", self.sw), _p("SUBTOTAL", self.sw),
               _p("DESARROLLO DE LA ACTIVIDAD", self.sw)]]
        sub_row = [["", _p("Miles", self.sc), "", "", "", "", ""]]

        labor_body = []
        for item in labor_items:
            qty   = float(item.get("quantity") or 0)
            up    = float(item.get("unit_price") or 0)
            total = float(item.get("total_price") or 0)
            labor_body.append([
                _p(item.get("code") or "", self.sc),
                _p(item.get("description") or "", self.s),
                _p(item.get("unit") or "HR", self.sc),
                _p(str(round(qty)), self.sc),
                _p(_fc(up), self.sr),
                _p(_fc(total), self.sr),
                _p(item.get("row_description") or "", self.s),
            ])

        labor_total = sum(float(i.get("total_price") or 0) for i in labor_items)
        labor_body.append([
            _p("VALOR TOTAL", self.sw), "", "", "", "",
            _p(_fc(labor_total), ParagraphStyle("lt", fontName="Helvetica-Bold",
                                                fontSize=7, leading=9, textColor=BLACK,
                                                alignment=TA_RIGHT)), ""
        ])
        vt_row = len(labor_body) - 1

        all_rows = lh + sub_row + labor_body
        header_rows_count = len(lh) + len(sub_row)

        t = Table(all_rows, colWidths=Cl)
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, header_rows_count - 1), GRAY),
            ("BACKGROUND",   (0, len(all_rows)-1), (-1, len(all_rows)-1), GRAY),
            ("BOX",          (0,0), (-1,-1), 0.5, BLACK),
            ("INNERGRID",    (0,0), (-1,-1), 0.5, BLACK),
            ("TOPPADDING",   (0,0), (-1,-1), 2),
            ("BOTTOMPADDING",(0,0), (-1,-1), 2),
            ("LEFTPADDING",  (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, header_rows_count), (-1, len(all_rows)-2), [WHITE, LGRAY]),
            ("SPAN", (0, len(all_rows)-1), (4, len(all_rows)-1)),
            ("SPAN", (6, len(all_rows)-1), (6, len(all_rows)-1)),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

        # ── MATERIALES ──────────────────────────────────────────────────────
        mat_items = d.get("material_items", [])
        story.append(self._apu_section_title("ANALISIS APU.  MATERIALES"))
        Cm = [45, 145, 40, 40, 65, 65, 127]
        Cm[1] += AW - sum(Cm)

        mh = [[_p("CODIGO", self.sw), _p("DESCRIPCION", self.sw),
               _p("UND", self.sw), _p("CANT.", self.sw),
               _p("VALOR\nMiles", self.sw), _p("SUBTOTAL", self.sw),
               _p("DESARROLLO DE LA ACTIVIDAD", self.sw)]]

        mat_body = []
        for item in mat_items:
            qty   = float(item.get("quantity") or 0)
            up    = float(item.get("unit_price") or 0)
            total = float(item.get("total_price") or 0)
            mat_body.append([
                _p(item.get("sap_code") or "", self.sc),
                _p(item.get("description") or "", self.s),
                _p(item.get("unit") or "UND", self.sc),
                _p(str(qty) if qty else "1", self.sc),
                _p(_fc(up), self.sr),
                _p(_fc(total), self.sr),
                _p(item.get("row_description") or "", self.s),
            ])

        mat_total = sum(float(i.get("total_price") or 0) for i in mat_items)
        mat_body.append([
            _p("VALOR TOTAL", self.sw), "", "", "", "",
            _p(_fc(mat_total), ParagraphStyle("mt", fontName="Helvetica-Bold",
                                              fontSize=7, leading=9, textColor=BLACK,
                                              alignment=TA_RIGHT)), ""
        ])
        vt_mat = len(mh) + len(mat_body) - 1

        mat_all = mh + mat_body
        t = Table(mat_all, colWidths=Cm)
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), GRAY),
            ("BACKGROUND",   (0, vt_mat), (-1, vt_mat), GRAY),
            ("BOX",          (0,0), (-1,-1), 0.5, BLACK),
            ("INNERGRID",    (0,0), (-1,-1), 0.5, BLACK),
            ("TOPPADDING",   (0,0), (-1,-1), 2),
            ("BOTTOMPADDING",(0,0), (-1,-1), 2),
            ("LEFTPADDING",  (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, vt_mat - 1), [WHITE, LGRAY]),
            ("SPAN", (0, vt_mat), (4, vt_mat)),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

        # ── EQUIPOS Y HERRAMIENTAS ──────────────────────────────────────────
        eq_items = d.get("equipment_items", [])
        story.append(self._apu_section_title("ANALISIS APU.  EQUIPOS Y HERRAMIENTAS"))
        Ce = [45, 145, 40, 40, 65, 65, 127]
        Ce[1] += AW - sum(Ce)

        eq_body = []
        for item in eq_items:
            qty   = float(item.get("quantity") or 0)
            up    = float(item.get("unit_price") or 0)
            total = float(item.get("total_price") or 0)
            eq_body.append([
                _p("", self.sc),
                _p(item.get("description") or "", self.s),
                _p(item.get("unit") or "HRS", self.sc),
                _p(str(round(qty)), self.sc),
                _p(_fc(up), self.sr),
                _p(_fc(total), self.sr),
                _p(item.get("row_description") or "", self.s),
            ])

        eq_total = sum(float(i.get("total_price") or 0) for i in eq_items)
        eq_body.append([
            _p("VALOR TOTAL", self.sw), "", "", "", "",
            _p(_fc(eq_total), ParagraphStyle("et", fontName="Helvetica-Bold",
                                             fontSize=7, leading=9, textColor=BLACK,
                                             alignment=TA_RIGHT)), ""
        ])
        vt_eq = len(eq_body) - 1
        eq_all = [mh[0]] + eq_body
        t = Table(eq_all, colWidths=Ce)
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), GRAY),
            ("BACKGROUND",   (0, vt_eq + 1), (-1, vt_eq + 1), GRAY),
            ("BOX",          (0,0), (-1,-1), 0.5, BLACK),
            ("INNERGRID",    (0,0), (-1,-1), 0.5, BLACK),
            ("TOPPADDING",   (0,0), (-1,-1), 2),
            ("BOTTOMPADDING",(0,0), (-1,-1), 2),
            ("LEFTPADDING",  (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, vt_eq), [WHITE, LGRAY]),
            ("SPAN", (0, vt_eq + 1), (4, vt_eq + 1)),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

        # ── RECARGO HORAS ADICIONAL ─────────────────────────────────────────
        hs_items = d.get("hourly_surcharge_items", [])
        story.append(self._apu_section_title("ANALISIS APU.  RECARGO HORAS ADICIONAL"))
        # CODIGO | DESC | UND | CANT | VALOR | RECARGO | SUBTOTAL | DESARROLLO
        Ch = [40, 120, 35, 35, 55, 50, 55, 137]
        Ch[1] += AW - sum(Ch)

        hh = [[_p("CODIGO",      self.sw), _p("DESCRIPCION",   self.sw),
               _p("UND.",        self.sw), _p("CANT.",         self.sw),
               _p("VALOR",       self.sw), _p("RECARGO",       self.sw),
               _p("SUBTOTAL",    self.sw), _p("DESARROLLO DE LA ACTIVIDAD", self.sw)]]

        hs_body = []
        for item in hs_items:
            qty   = float(item.get("quantity") or 0)
            up    = float(item.get("unit_price") or 0)
            pct   = float(item.get("surcharge_percent") or 0)
            total = float(item.get("total_price") or 0)
            hs_body.append([
                _p("", self.sc),
                _p(item.get("description") or "", self.s),
                _p(item.get("unit") or "HRS", self.sc),
                _p(str(round(qty)), self.sc),
                _p(_fc(up), self.sr),
                _p(f"{round(pct)}%", self.sc),
                _p(_fc(total), self.sr),
                _p(item.get("row_description") or "", self.s),
            ])

        hs_total = sum(float(i.get("total_price") or 0) for i in hs_items)
        hs_body.append([
            _p("VALOR TOTAL", self.sw), "", "", "", "", "",
            _p(_fc(hs_total), ParagraphStyle("ht2", fontName="Helvetica-Bold",
                                             fontSize=7, leading=9, textColor=BLACK,
                                             alignment=TA_RIGHT)), ""
        ])
        vt_hs = len(hs_body) - 1
        hs_all = hh + hs_body
        t = Table(hs_all, colWidths=Ch)
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), GRAY),
            ("BACKGROUND",   (0, vt_hs + 1), (-1, vt_hs + 1), GRAY),
            ("BOX",          (0,0), (-1,-1), 0.5, BLACK),
            ("INNERGRID",    (0,0), (-1,-1), 0.5, BLACK),
            ("TOPPADDING",   (0,0), (-1,-1), 2),
            ("BOTTOMPADDING",(0,0), (-1,-1), 2),
            ("LEFTPADDING",  (0,0), (-1,-1), 3),
            ("RIGHTPADDING", (0,0), (-1,-1), 3),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, vt_hs), [WHITE, LGRAY]),
            ("SPAN", (0, vt_hs + 1), (5, vt_hs + 1)),
        ]))
        story.append(t)

    # ─────────────────────────────────────────────────────────────────────────
    # PHOTOS
    # ─────────────────────────────────────────────────────────────────────────
    def _photos(self, story):
        photos = self.d.get("photos", [])
        if not photos:
            return

        story.append(Spacer(1, 8))
        story.append(self._apu_section_title("REGISTRO FOTOGRÁFICO"))
        story.append(Spacer(1, 4))

        IMG_W = (AW - 2 * 4) / 3   # 3 per row with 4pt gap
        IMG_H = IMG_W * 0.75        # 4:3 ratio

        row = []
        rows = []
        for i, photo in enumerate(photos):
            path = photo.get("path", "")
            cell = ""
            if os.path.exists(path):
                try:
                    img = Image(path, width=IMG_W, height=IMG_H)
                    cell = img
                except Exception:
                    cell = _p("[foto]", self.sc)
            else:
                cell = _p("[foto no disponible]", self.sc)
            row.append(cell)
            if len(row) == 3:
                rows.append(row)
                row = []

        if row:
            while len(row) < 3:
                row.append("")
            rows.append(row)

        t = Table(rows, colWidths=[IMG_W + 4, IMG_W + 4, IMG_W + 4])
        t.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN",        (0,0), (-1,-1), "CENTER"),
            ("TOPPADDING",   (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("LEFTPADDING",  (0,0), (-1,-1), 2),
            ("RIGHTPADDING", (0,0), (-1,-1), 2),
        ]))
        story.append(t)
