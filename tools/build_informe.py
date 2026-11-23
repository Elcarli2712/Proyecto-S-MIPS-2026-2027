#!/usr/bin/env python3
"""Genera informe.pdf (requiere: pip install reportlab). Uso: python tools/build_informe.py
Antes de entregar, pon tu nombre completo en NOMBRE."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon, Ellipse, PolyLine
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
                                Preformatted, PageBreak)

NOMBRE = 'Carlos Zorrilla Gonzalez'
CURSO = 'Arquitectura de Computadoras — Curso 2026–2027'
ROOT = Path(__file__).resolve().parent.parent
SALIDA = ROOT / 'informe.pdf'

FONTS = Path('C:/Windows/Fonts')
if (FONTS / 'arial.ttf').exists():
    pdfmetrics.registerFont(TTFont('Sans', str(FONTS / 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Sans-Bold', str(FONTS / 'arialbd.ttf')))
    pdfmetrics.registerFont(TTFont('Mono', str(FONTS / 'consola.ttf')))
    SANS, BOLD, MONO = 'Sans', 'Sans-Bold', 'Mono'
else:
    SANS, BOLD, MONO = 'Helvetica', 'Helvetica-Bold', 'Courier'
from reportlab.lib.fonts import addMapping
addMapping(SANS, 0, 0, SANS); addMapping(SANS, 1, 0, BOLD)

INK = colors.HexColor('#1f2328'); MUTED = colors.HexColor('#57606a'); ACC = colors.HexColor('#0b5cad')
CTRL = colors.HexColor('#b3261e'); LINE = colors.HexColor('#d0d7de'); HEAD = colors.HexColor('#eef2f6')

ss = getSampleStyleSheet()
P = ParagraphStyle('p', parent=ss['Normal'], fontName=SANS, fontSize=9.5, leading=13, textColor=INK, spaceAfter=5)
SMALL = ParagraphStyle('s', parent=P, fontSize=8, leading=10, spaceAfter=0)
CELL = ParagraphStyle('c', parent=P, fontSize=8, leading=10, spaceAfter=0)
CELLB = ParagraphStyle('cb', parent=CELL, fontName=BOLD)
H1 = ParagraphStyle('h1', parent=P, fontName=BOLD, fontSize=13, leading=16, spaceBefore=10, spaceAfter=6, textColor=ACC,
                    keepWithNext=1)
H2 = ParagraphStyle('h2', parent=P, fontName=BOLD, fontSize=10.5, leading=13, spaceBefore=6, spaceAfter=4)
TITLE = ParagraphStyle('t', parent=P, fontName=BOLD, fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=4)
SUB = ParagraphStyle('st', parent=P, fontSize=10, alignment=TA_CENTER, textColor=MUTED)
CAP = ParagraphStyle('cap', parent=SMALL, textColor=MUTED, alignment=TA_CENTER, spaceBefore=3, spaceAfter=8)
CODE = ParagraphStyle('code', parent=P, fontName=MONO, fontSize=7.5, leading=9.5)


def table(rows, widths, header=True, mono_cols=()):
    data = []
    for i, r in enumerate(rows):
        st = CELLB if (header and i == 0) else CELL
        data.append([Paragraph(str(c), st) if not (j in mono_cols and i > 0) else
                     Paragraph(f'<font name="{MONO}">{c}</font>', CELL) for j, c in enumerate(r)])
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if header else 0)
    style = [('GRID', (0, 0), (-1, -1), 0.4, LINE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
             ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3),
             ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]
    if header:
        style.append(('BACKGROUND', (0, 0), (-1, 0), HEAD))
    t.setStyle(TableStyle(style))
    return t


# ------------------------------------------------------------------ diagrama de la ruta de datos
def box(d, x, y, w, h, text, fill=colors.white, dashed=False, size=7):
    d.add(Rect(x, y, w, h, fillColor=fill, strokeColor=INK, strokeWidth=0.8,
               strokeDashArray=[2, 2] if dashed else None))
    lines = text.split('\n')
    for i, l in enumerate(lines):
        d.add(String(x + w / 2, y + h / 2 + (len(lines) / 2 - i - 0.75) * (size + 1), l, fontName=BOLD,
                     fontSize=size, textAnchor='middle', fillColor=INK))


def mux(d, x, y, h, labels, sel, w=12):
    d.add(Polygon([x, y, x + w, y + 6, x + w, y + h - 6, x, y + h], fillColor=colors.white, strokeColor=INK,
                  strokeWidth=0.8))
    n = len(labels)
    for i, l in enumerate(labels):
        yy = y + h - (i + 0.5) * h / n
        d.add(String(x + 1.5, yy - 2, str(i), fontName=SANS, fontSize=5, fillColor=MUTED))
    d.add(String(x + w / 2, y + h + 3, sel, fontName=BOLD, fontSize=6, textAnchor='middle', fillColor=CTRL))
    return [(x, y + h - (i + 0.5) * h / n) for i in range(n)], (x + w, y + h / 2)


def wire(d, pts, color=INK, arrow=True):
    d.add(PolyLine([c for p in pts for c in p], strokeColor=color, strokeWidth=0.7))
    if arrow:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        if x1 != x0:
            s = 1 if x1 > x0 else -1
            d.add(Polygon([x1, y1, x1 - 4 * s, y1 + 2, x1 - 4 * s, y1 - 2], fillColor=color, strokeColor=color))
        else:
            s = 1 if y1 > y0 else -1
            d.add(Polygon([x1, y1, x1 - 2, y1 - 4 * s, x1 + 2, y1 - 4 * s], fillColor=color, strokeColor=color))


def lab(d, x, y, t, color=INK, size=6, anchor='start', bold=False):
    d.add(String(x, y, t, fontName=BOLD if bold else SANS, fontSize=size, fillColor=color, textAnchor=anchor))


def ctrl(d, x, y, t):
    lab(d, x, y, t, CTRL, 6, 'middle', True)


def datapath():
    d = Drawing(500, 330)
    # PC
    box(d, 8, 200, 30, 40, 'PC'); ctrl(d, 23, 244, 'PCEnable')
    ins, out = mux(d, 55, 190, 60, ['PC', 'ALUOut'], 'lorD')
    wire(d, [(38, 220), (46, 220), (46, ins[0][1]), (55, ins[0][1])])
    box(d, 85, 160, 48, 110, 'Memoria\n(placa)', fill=colors.HexColor('#f6f8fa'), dashed=True)
    wire(d, [out, (85, 220)]); lab(d, 61, 180, 'MEM_ADDR', MUTED, 5, 'middle')
    ctrl(d, 109, 274, 'MemWr / IsSb')
    lab(d, 109, 152, 'MEM_WDATA, MEM_BE', MUTED, 5, 'middle')
    # IR y MDR
    box(d, 160, 230, 32, 34, 'IR'); ctrl(d, 176, 268, 'IRwr')
    box(d, 143, 178, 30, 22, 'byte\nlb/lbu', size=5.5); ctrl(d, 158, 172, 'LoadType')
    box(d, 182, 175, 26, 28, 'MDR'); ctrl(d, 195, 207, 'MDRwr')
    wire(d, [(133, 245), (160, 245)]); lab(d, 147, 249, 'RDATA', MUTED, 5, 'middle')
    wire(d, [(133, 189), (143, 189)]); wire(d, [(173, 189), (182, 189)])
    # campos del IR
    lab(d, 196, 256, 'rs, rt, rd,', MUTED, 5); lab(d, 196, 249, 'shamt, imm,', MUTED, 5)
    lab(d, 196, 242, 'op/funct -> Decoder', MUTED, 5)
    # Register_File
    box(d, 245, 150, 55, 110, 'Register_File', fill=colors.HexColor('#eef5ff'))
    ctrl(d, 272, 264, 'REG_WR')
    for i, t in enumerate(['RA1 <- rs / 2', 'RA2 <- rt / 4', 'WA', 'WD']):
        lab(d, 247, 245 - 16 * i, t, MUTED, 5)
    ctrl(d, 230, 252, 'IsSysCall')
    wa_in, wa_out = mux(d, 222, 120, 26, ['WriteReg', '31'], 'IsJal', w=10)
    wire(d, [wa_out, (240, 133), (240, 197), (245, 197)])
    lab(d, 198, 129, 'rd/rt (RegDst)', MUTED, 5, 'end')
    wd_in, wd_out = mux(d, 222, 75, 26, ['WriteData', 'PC'], 'IsJal', w=10)
    wire(d, [wd_out, (236, 88), (236, 181), (245, 181)])
    lab(d, 198, 84, 'ALUOut / MDR (MemToReg)', MUTED, 5, 'end')
    wire(d, [(208, 189), (212, 189), (212, 80), (222, 80)], arrow=False)
    # A y B
    box(d, 318, 222, 26, 26, 'A'); ctrl(d, 331, 252, 'Awr')
    box(d, 318, 168, 26, 26, 'B'); ctrl(d, 331, 198, 'Bwr')
    wire(d, [(300, 235), (318, 235)]); lab(d, 302, 238, 'RD1', MUTED, 5)
    wire(d, [(300, 181), (318, 181)]); lab(d, 302, 184, 'RD2', MUTED, 5)
    # muxes de la ALU
    a_in, a_out = mux(d, 362, 215, 40, ['PC', 'A'], 'ALUSrcA')
    wire(d, [(344, 235), (352, 235), (352, a_in[1][1]), (362, a_in[1][1])])
    lab(d, 360, a_in[0][1] + 1, 'PC', MUTED, 5, 'end')
    b_in, b_out = mux(d, 362, 120, 76, ['4', 'B', 'Ext(imm)', 'Ext<<2'], 'ALUSrcB')
    wire(d, [(344, 181), (352, 181), (352, b_in[1][1]), (362, b_in[1][1])])
    for i, t in ((0, '4'), (2, 'Sign/ZeroExt'), (3, 'SignExt<<2')):
        lab(d, 360, b_in[i][1] - 2, t, MUTED, 5, 'end')
    # ALU
    d.add(Polygon([392, 120, 420, 145, 420, 225, 392, 250, 392, 195, 400, 185, 392, 175],
                  fillColor=colors.HexColor('#fff4e5'), strokeColor=INK, strokeWidth=0.8))
    lab(d, 407, 183, 'ALU', INK, 7, 'middle', True)
    ctrl(d, 406, 254, 'ALU_Control')
    lab(d, 406, 110, 'Shamt = IR[10:6]', MUTED, 5, 'middle')
    wire(d, [a_out, (392, a_out[1])]); wire(d, [b_out, (392, b_out[1])])
    lab(d, 424, 160, 'Zero -> Branch_Control', MUTED, 5)
    # lui y ALUOut
    l_in, l_out = mux(d, 430, 175, 30, ['ALU', 'imm<<16'], 'IsLui', w=10)
    wire(d, [(420, 185), (426, 185), (426, l_in[0][1]), (430, l_in[0][1])])
    box(d, 448, 178, 32, 24, 'ALUOut', size=6); ctrl(d, 464, 206, 'ALUwr')
    wire(d, [l_out, (448, 190)])
    # PCSource
    p_in, p_out = mux(d, 466, 255, 50, ['A', 'ALUOut', 'ALU', 'Jump'], 'PCSource')
    lab(d, 8, 300, 'PCSource: 0 = A (jr), 1 = ALUOut (destino de rama), 2 = ALU (PC+4), 3 = {PC[31:28], dir, 00} (j, jal)',
        MUTED, 5.5)
    wire(d, [(480, 190), (488, 190), (488, 225), (452, 225), (452, p_in[1][1]), (466, p_in[1][1])])
    wire(d, [(426, 205), (442, 205), (442, p_in[2][1]), (466, p_in[2][1])])
    wire(d, [p_out, (492, p_out[1]), (492, 318), (2, 318), (2, 220), (8, 220)])
    lab(d, 250, 321, 'PC_Next', MUTED, 5, 'middle')
    # ALUOut a lorD
    wire(d, [(488, 190), (488, 60), (50, 60), (50, ins[1][1]), (55, ins[1][1])])
    lab(d, 330, 63, 'ALUOut (dirección de lw/sw/lb/lbu/sb)', MUTED, 5, 'middle')
    lab(d, 8, 30, 'En rojo: señales de control (las genera Control_Unit o las da el Instruction_Decoder).', CTRL, 6)
    lab(d, 8, 20, 'Diagrama simplificado: los nombres son los de los túneles del circuito Datapath.', MUTED, 6)
    return d


# ------------------------------------------------------------------ diagrama de estados
def fsm():
    d = Drawing(515, 300)
    pos = {0: (250, 270), 1: (250, 215), 2: (45, 150), 3: (45, 95), 4: (45, 40), 5: (120, 95),
           6: (185, 150), 7: (185, 95), 8: (255, 150), 14: (255, 95), 9: (320, 150), 10: (378, 150),
           11: (433, 150), 12: (470, 215), 13: (470, 95)}
    names = {0: 'FETCH', 1: 'DECODE', 2: 'MEM_ADDR', 3: 'MEM_READ', 4: 'LOAD_WB', 5: 'STORE', 6: 'EXEC_R',
             7: 'R_WB', 8: 'EXEC_I', 14: 'I_WB', 9: 'BRANCH', 10: 'JUMP', 11: 'JR', 12: 'SYSCALL', 13: 'HALT'}
    rx, ry = 27, 14
    def edge(a, b, text='', dx=0, dy=0):
        (x0, y0), (x1, y1) = pos[a], pos[b]
        import math
        ang = math.atan2(y1 - y0, x1 - x0)
        sx, sy = x0 + rx * math.cos(ang), y0 + ry * math.sin(ang)
        ex, ey = x1 - rx * math.cos(ang), y1 - ry * math.sin(ang)
        d.add(Line(sx, sy, ex, ey, strokeColor=INK, strokeWidth=0.7))
        ax, ay = math.cos(ang), math.sin(ang)
        d.add(Polygon([ex, ey, ex - 5 * ax + 2 * ay, ey - 5 * ay - 2 * ax, ex - 5 * ax - 2 * ay, ey - 5 * ay + 2 * ax],
                      fillColor=INK, strokeColor=INK))
        if text:
            t = 0.72
            lab(d, sx + (ex - sx) * t + dx, sy + (ey - sy) * t + dy, text, ACC, 5.5, 'middle', True)
    edge(0, 1)
    edge(1, 2, 'Load/Store', 0, 5); edge(1, 6, 'RType', -14, 0); edge(1, 8, 'ImmALU', -14, 0)
    edge(1, 9, 'Branch', -14, 0); edge(1, 10, 'Jump', -10, 3); edge(1, 11, 'Jr', -4, 5)
    edge(1, 12, 'SysCall', 0, 4); edge(2, 3, 'Load', -12, 0); edge(2, 5, 'Store', 14, 0); edge(3, 4)
    edge(6, 7); edge(8, 14); edge(12, 13, '$v0 = 10', 18, 0)
    # ilegal: DECODE -> HALT, por arriba y por el borde derecho
    d.add(PolyLine([268, 225, 268, 245, 507, 245, 507, 95, 498, 95], strokeColor=CTRL, strokeWidth=0.7,
                   strokeDashArray=[2, 2]))
    d.add(Polygon([497, 95, 502, 97, 502, 93], fillColor=CTRL, strokeColor=CTRL))
    lab(d, 390, 248, 'Illegal', CTRL, 5.5, 'middle', True)
    for s, (x, y) in pos.items():
        fill = colors.HexColor('#eef5ff') if s in (0, 1) else (colors.HexColor('#fde8e6') if s == 13 else colors.white)
        d.add(Ellipse(x, y, rx, ry, fillColor=fill, strokeColor=INK, strokeWidth=0.8))
        lab(d, x, y + 1, f'S{s}', INK, 6.5, 'middle', True)
        lab(d, x, y - 7, names[s], INK, 5.2, 'middle')
    for s in (4, 5, 7, 14, 9, 10, 11):
        x, y = pos[s]
        lab(d, x, y - ry - 8, '-> S0', ACC, 5.5, 'middle', True)
    lab(d, 466, 215 - ry - 8, 'otro $v0 -> S0', ACC, 5.5, 'end', True)
    lab(d, 470, 95 - ry - 8, 'se queda en S13', CTRL, 5.5, 'middle', True)
    lab(d, 8, 8, 'RESET = 1 lleva a S0 (borrado asíncrono del registro ESTADO). "-> S0": vuelve a FETCH en el ciclo siguiente.', MUTED, 6)
    return d


def fit(d, width=170 * mm):
    k = width / d.width
    d.scale(k, k); d.width, d.height = d.width * k, d.height * k
    return d


def build():
    story = []
    story += [Paragraph('CPU multiciclo S-MIPS en Logisim Evolution', TITLE),
              Paragraph(f'{NOMBRE}<br/>{CURSO}', SUB), Spacer(1, 6)]

    # 1
    story.append(Paragraph('1. Estudiante y uso de VHDL', H1))
    story.append(Paragraph(
        f'<b>Estudiante:</b> {NOMBRE}. <b>Componentes en VHDL: ninguno.</b> Toda la CPU (incluidos '
        'Register_File, ALU e Instruction_Decoder) está construida con componentes nativos de Logisim 5.0.0. '
        'Así la simulación no necesita Questa, es más rápida y cada parte se puede ver y explicar sobre el '
        'propio circuito. Jerarquía: <b>CPU</b> contiene Instruction_Decoder, Control_Unit, Branch_Control y '
        'Datapath; <b>Datapath</b> contiene Register_File y ALU (R16). No se usan RAM ni ROM dentro de la CPU (R17).', P))

    # 2
    story.append(Paragraph('2. Ruta de datos', H1))
    story.append(Paragraph(
        'Una sola memoria para instrucciones y datos (R13) y una sola ALU (R14): PC+4, el destino de los saltos '
        'condicionales y las direcciones de memoria se calculan con la ALU en ciclos distintos. Fuera de la ALU no '
        'hay sumadores; los desplazamientos fijos (SignExt&lt;&lt;2, imm&lt;&lt;16 y la colocación del byte de sb) '
        'usan componentes Shifter. Registros intermedios: PC, IR, MDR, A, B y ALUOut, todos con reloj CLK directo y '
        'borrado asíncrono con RESET (R3, R6).', P))
    story.append(KeepTogether([fit(datapath()), Paragraph('Figura 1. Ruta de datos con las señales de control.', CAP)]))
    story.append(table([
        ['Señal', 'Bits', 'Efecto'],
        ['PCEnable', '1', 'Escribe PC (sale de Branch_Control)'],
        ['lorD', '1', 'Dirección de memoria: 0 = PC, 1 = ALUOut'],
        ['IRwr, MDRwr, Awr, Bwr, ALUwr', '1', 'Habilitan la escritura de IR, MDR, A, B y ALUOut'],
        ['REG_WR', '1', 'Escribe WD en el registro WA del Register_File'],
        ['RegDst', '1', 'Registro destino: 0 = rd, 1 = rt (con IsJal el destino es 31)'],
        ['MemToReg', '1', 'Dato a escribir: 0 = ALUOut, 1 = MDR (con IsJal es el PC)'],
        ['ALUSrcA', '1', 'Operando A de la ALU: 0 = PC, 1 = A'],
        ['ALUSrcB', '2', 'Operando B: 00 = 4, 01 = B, 10 = inmediato extendido, 11 = SignExt(imm)&lt;&lt;2'],
        ['ALU_Control', '3', 'Operación de la ALU (tabla de la sección 5)'],
        ['PCSource', '2', 'Próximo PC: 00 = A (jr), 01 = ALUOut (rama), 10 = ALU (PC+4), 11 = {PC[31:28], dir, 00}'],
        ['MemWr', '1', 'MEM_WE: escribe en memoria (sw/sb)'],
        ['TTY', '1', 'TTY_WE: imprime TTY_DATA = B[6:0] (= $a0)'],
        ['LoadType', '2', 'Del decodificador. 00 = lb (signo), 01 = lbu (ceros), 10 = lw'],
        ['IsSb', '1', 'Del decodificador. MEM_BE = un bit según dirección[1:0] y byte desplazado a su carril; si no, 1111'],
        ['IsAndi, IsOri', '1', 'Del decodificador. Inmediato extendido con ceros (si no, con signo)'],
        ['IsLui, IsJal, IsSysCall', '1', 'Del decodificador. lui: ALUOut = {imm, 0}; jal: WA = 31 y WD = PC; '
                                         'syscall: se leen $v0 (RA1 = 2) y $a0 (RA2 = 4)'],
    ], [38, 10, 122]))

    # 3
    story.append(Paragraph('3. Máquina de estados', H1))
    story.append(Paragraph(
        'Control_Unit es una máquina de Moore. El estado se guarda en un registro de 4 bits (ESTADO); un '
        'decodificador lo convierte en las líneas S0…S15 y un multiplexor de 16 entradas, elegido por ESTADO, da el '
        'próximo estado. Solo dependen de la instrucción las transiciones desde DECODE (según la clase que da el '
        'decodificador), MEM_ADDR (carga o almacenamiento) y SYSCALL (valor de $v0, comparado con 10 y 11).', P))
    story.append(KeepTogether([fit(fsm()), Paragraph('Figura 2. Diagrama de estados.', CAP)]))
    story.append(table([
        ['Estado', 'Acciones', 'Siguiente'],
        ['S0 FETCH', 'IR ← M[PC]; PC ← PC + 4', 'S1'],
        ['S1 DECODE', 'A ← R[rs], B ← R[rt] ($v0 y $a0 si syscall); ALUOut ← PC + (SignExt(imm)&lt;&lt;2)',
         'Load/Store S2, RType S6, ImmALU S8, Branch S9, Jump S10, Jr S11, SysCall S12, Illegal S13'],
        ['S2 MEM_ADDR', 'ALUOut ← A + SignExt(imm)', 'Load S3, Store S5'],
        ['S3 MEM_READ', 'MDR ← palabra o byte extendido de M[ALUOut]', 'S4'],
        ['S4 LOAD_WB', 'R[rt] ← MDR', 'S0'],
        ['S5 STORE', 'M[ALUOut] ← B (sb: un byte)', 'S0'],
        ['S6 EXEC_R', 'ALUOut ← A op B (sll/srl: B desplazado shamt)', 'S7'],
        ['S7 R_WB', 'R[rd] ← ALUOut', 'S0'],
        ['S8 EXEC_I', 'ALUOut ← A op Ext(imm) (lui: {imm, 0})', 'S14'],
        ['S14 I_WB', 'R[rt] ← ALUOut', 'S0'],
        ['S9 BRANCH', 'A − B; si (Zero XOR IsBne): PC ← ALUOut', 'S0'],
        ['S10 JUMP', 'PC ← {PC[31:28], dir, 00}; jal: R[31] ← PC (ya es PC+4)', 'S0'],
        ['S11 JR', 'PC ← A', 'S0'],
        ['S12 SYSCALL', '$v0 = 11: TTY_WE = 1, TTY_DATA = $a0[6:0]', '$v0 = 10: S13; si no, S0'],
        ['S13 HALT', 'HALT = 1; nada se escribe', 'S13 hasta RESET'],
    ], [24, 88, 58]))

    # 4
    story.append(Paragraph('4. Señales de control en cada estado', H1))
    story.append(Paragraph('Valores de las señales de Control_Unit. Una celda vacía vale 0 (o no importa en los '
                           'selectores de multiplexor). PCWriteCond activa la escritura condicional del PC en '
                           'Branch_Control.', P))
    sig = ['PCWrite', 'PCWriteCond', 'IRwr', 'lorD', 'ALUSrcA', 'ALUSrcB', 'ALU_Control', 'PCSource', 'Awr/Bwr',
           'ALUwr', 'MDRwr', 'RegDst', 'MemToReg', 'REG_WR', 'MemWr', 'TTY', 'HALT']
    rows = {
        'S0': dict(PCWrite=1, IRwr=1, ALUSrcA=0, ALUSrcB='00', ALU_Control='000', PCSource='10'),
        'S1': dict(**{'Awr/Bwr': 1}, ALUwr=1, ALUSrcA=0, ALUSrcB='11', ALU_Control='000'),
        'S2': dict(ALUSrcA=1, ALUSrcB='10', ALU_Control='000', ALUwr=1),
        'S3': dict(lorD=1, MDRwr=1),
        'S4': dict(RegDst=1, MemToReg=1, REG_WR=1),
        'S5': dict(lorD=1, MemWr=1),
        'S6': dict(ALUSrcA=1, ALUSrcB='01', ALU_Control='ALUOp', ALUwr=1),
        'S7': dict(RegDst=0, MemToReg=0, REG_WR=1),
        'S8': dict(ALUSrcA=1, ALUSrcB='10', ALU_Control='ALUOp', ALUwr=1),
        'S14': dict(RegDst=1, MemToReg=0, REG_WR=1),
        'S9': dict(PCWriteCond=1, ALUSrcA=1, ALUSrcB='01', ALU_Control='001', PCSource='01'),
        'S10': dict(PCWrite=1, PCSource='11', REG_WR='IsJal'),
        'S11': dict(PCWrite=1, PCSource='00'),
        'S12': dict(TTY='$v0=11'),
        'S13': dict(HALT=1),
    }
    short = ['PCW', 'PCWC', 'IRwr', 'lorD', 'SrcA', 'SrcB', 'ALUCtl', 'PCSrc', 'A/Bwr', 'ALUwr', 'MDRwr', 'RegDst',
             'M2R', 'REG_WR', 'MemWr', 'TTY', 'HALT']
    data = [['Estado'] + short] + [[s] + [str(r.get(k, '')) for k in sig] for s, r in rows.items()]
    t = Table(data, colWidths=[11 * mm] + [9.3 * mm] * len(sig), repeatRows=1)
    t.setStyle(TableStyle([('FONT', (0, 0), (-1, -1), SANS, 6.3), ('FONT', (0, 0), (-1, 0), BOLD, 5.8),
                           ('FONT', (0, 1), (0, -1), BOLD, 6.3), ('GRID', (0, 0), (-1, -1), 0.4, LINE),
                           ('BACKGROUND', (0, 0), (-1, 0), HEAD), ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                           ('TOPPADDING', (0, 0), (-1, -1), 1.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
                           ('LEFTPADDING', (0, 0), (-1, -1), 1), ('RIGHTPADDING', (0, 0), (-1, -1), 1)]))
    story.append(t)
    story.append(Paragraph('PCW = PCWrite, PCWC = PCWriteCond, SrcA/SrcB = ALUSrcA/ALUSrcB, ALUCtl = ALU_Control, '
                           'M2R = MemToReg. ALUOp es la operación que da el decodificador. En S10, REG_WR = IsJal.',
                           SMALL))
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>Branch_Control</b> (combinacional): PCEnable = PCWrite OR (PCWriteCond AND '
                           '(Zero XOR IsBne)). En beq el PC se escribe si A = B; en bne, si A ≠ B.', P))

    # 5
    story.append(Paragraph('5. Codificación de la ALU y del decodificador', H1))
    story.append(Paragraph('La ALU recibe A, B, ALUOp (3 bits) y Shamt (5 bits, IR[10:6]); devuelve Result y '
                           'ZeroF (1 si Result = 0). Dentro tiene sumador, restador, AND, OR, comparador con signo y '
                           'dos Shifter; un multiplexor de 8 entradas elige el resultado.', P))
    story.append(table([
        ['ALUOp', 'Operación', 'Instrucciones'],
        ['000', 'A + B', 'add, addu, addi, addiu, lui, lw, sw, lb, lbu, sb, PC+4, destino de rama'],
        ['001', 'A − B', 'sub, beq, bne'],
        ['010', 'A AND B', 'and, andi'],
        ['011', 'A OR B', 'or, ori'],
        ['100', '1 si A &lt; B con signo', 'slt, slti'],
        ['101', 'B &lt;&lt; shamt', 'sll'],
        ['110', 'B &gt;&gt; shamt (lógico)', 'srl'],
    ], [16, 40, 114], mono_cols=(0,)))
    story.append(Spacer(1, 5))
    story.append(Paragraph('Instruction_Decoder: dos decodificadores de 6 bits (op y funct). Las instrucciones R son '
                           'op = 0 AND funct (R11); puertas OR forman las clases y los bits de ALUOp. Illegal = '
                           'ninguna clase (R10).', P))
    story.append(table([
        ['Salida', 'Bits', 'Vale 1 / valor'],
        ['RType', '1', 'add, addu, sub, and, or, slt, sll, srl'],
        ['ImmALU', '1', 'addi, addiu, slti, andi, ori, lui'],
        ['Load / Store', '1', 'lw, lb, lbu / sw, sb'],
        ['Branch / Jump', '1', 'beq, bne / j, jal'],
        ['Jr / SysCall', '1', 'jr / syscall'],
        ['Illegal', '1', 'NOT (cualquiera de las clases anteriores)'],
        ['ALUOp', '3', 'bit0 = sub|beq|bne|or|ori|sll; bit1 = and|andi|or|ori|srl; bit2 = slt|slti|sll|srl'],
        ['LoadType', '2', '00 lb, 01 lbu, 10 lw'],
        ['IsSb, IsAndi, IsOri, IsLui, IsJal, IsBne', '1', 'la instrucción correspondiente'],
    ], [52, 10, 108]))

    # 6
    story.append(Paragraph('6. Ciclos por instrucción', H1))
    story.append(table([
        ['Clase', 'Estados', 'Ciclos'],
        ['add, addu, sub, and, or, slt, sll, srl', 'S0 S1 S6 S7', '4'],
        ['addi, addiu, slti, andi, ori, lui', 'S0 S1 S8 S14', '4'],
        ['lw, lb, lbu', 'S0 S1 S2 S3 S4', '5'],
        ['sw, sb', 'S0 S1 S2 S5', '4'],
        ['beq, bne', 'S0 S1 S9', '3'],
        ['j, jal', 'S0 S1 S10', '3'],
        ['jr', 'S0 S1 S11', '3'],
        ['syscall', 'S0 S1 S12 (S13 si $v0 = 10)', '3'],
    ], [80, 60, 30]))

    # 7
    story.append(Paragraph('7. Cobertura de los programas de tests/', H1))
    story.append(Paragraph('Cada programa imprime una letra por grupo y los valores calculados en hexadecimal; si una '
                           'instrucción falla, la salida cambia. Usan solo S-MIPS, li, la, move, blt y los servicios 11 '
                           'y 10. Entre paréntesis, la línea de la salida donde se ve cada caso.', P))
    story.append(table([
        ['Instrucciones', 'Caso', 'Programa'],
        ['add, sub', 'Positivos y con un operando negativo', 'alu.asm (A)'],
        ['and, or', 'Unos en los 16 bits altos', 'alu.asm (L)'],
        ['slt, slti', '1 y 0; −7 &lt; 25 y 25 &lt; −1 (con y sin signo difieren)', 'alu.asm (C)'],
        ['sll, srl', 'shamt = 0 y ≠ 0; srl de un negativo', 'alu.asm (D)'],
        ['addi', 'Inmediato negativo (−150)', 'alu.asm (I)'],
        ['addiu, addu', 'li (−32768, 32767, −7…) y move', 'alu.asm (I)'],
        ['andi, ori', 'Inmediato con bit 15 = 1', 'alu.asm (L)'],
        ['lui', 'Inmediato con bit 15 = 1', 'alu.asm (Z)'],
        ['lw, sw', 'Desplazamiento positivo y negativo', 'memoria.asm (W, S)'],
        ['lb, lbu', 'Bit 7 = 1 en d[1:0] = 2 y 3', 'memoria.asm (B, U)'],
        ['sb', 'd[1:0] = 0, 1, 2, 3 y lw después de cada uno', 'memoria.asm (X)'],
        ['beq, bne', 'Tomado y no tomado; saltos hacia atrás', 'saltos.asm (Q, R)'],
        ['j', 'Salta sobre una instrucción', 'saltos.asm (J)'],
        ['jal, jr', 'Procedimiento recursivo y uno no hoja; $ra en la pila; $sp vuelve a 0x3FFC', 'saltos.asm (P)'],
        ['syscall', 'Servicios 11 y 10', 'todos'],
        ['$zero', 'addi, add y lui sobre $zero; después vale 0', 'alu.asm (Z)'],
    ], [26, 104, 40]))

    # 8
    story.append(Paragraph('8. Resultados y limitaciones', H1))
    story.append(Paragraph('Salida de <font name="%s">python tools/run_tests.py</font> (también en salida-tests.txt):' % MONO, P))
    res = (ROOT / 'salida-tests.txt').read_text(encoding='utf-8-sig').strip()
    story.append(Preformatted(res, CODE))
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>Limitaciones conocidas</b>', H2))
    for t in [
        'Una instrucción ilegal se detecta en DECODE, después de FETCH: el PC ya vale PC+4 y en DECODE se cargan los '
        'registros internos A, B y ALUOut. No se modifica ningún registro del banco, ni la memoria, ni el TTY. Con '
        'syscall 10 ocurre lo mismo que en MARS: el PC ya apunta a la instrucción siguiente.',
        'Mientras RESET vale 1 el estado es S0, cuyas salidas IRwr y PCWrite valen 1; el PC sigue en 0 porque el borrado '
        'asíncrono tiene prioridad. MEM_WE, TTY_WE y HALT valen 0 (R6).',
        'Como permite la especificación, no se tratan los accesos no alineados, los saltos a direcciones no múltiplo '
        'de 4 ni el desbordamiento (add/addi/sub dan la suma módulo 2<super>32</super>).',
        'No se conocen errores: los 10 programas dan la misma salida que MARS.',
    ]:
        story.append(Paragraph('• ' + t, P))
    return story


def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont(SANS, 7.5); canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 10 * mm, 'CPU multiciclo S-MIPS — informe')
    canvas.drawRightString(190 * mm, 10 * mm, f'Página {doc.page}')
    canvas.restoreState()


if __name__ == '__main__':
    doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=16 * mm,
                            bottomMargin=16 * mm, title='CPU multiciclo S-MIPS', author=NOMBRE)
    doc.build(build(), onFirstPage=pie, onLaterPages=pie)
    print(f'OK: {SALIDA}')
