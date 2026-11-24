"""Genera informe.pdf a partir de informe.md usando reportlab."""

import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ARCHIVO_ENTRADA = "informe.md"
ARCHIVO_SALIDA = "informe.pdf"
ANCHO = A4[0] - 120  # 60 pt de margen a cada lado


def limpiar(texto):
    """Sustituye caracteres que las fuentes estándar de PDF no soportan."""
    reemplazos = {
        "→": "->", "—": "-", "–": "-", "…": "...",
        "“": '"', "”": '"', "‘": "'", "’": "'",
        "✅": "", "❌": "", "🔥": "", "📄": "", "👋": "",
    }
    for original, nuevo in reemplazos.items():
        texto = texto.replace(original, nuevo)
    return texto


def enriquecer(texto):
    """Escapa el texto y aplica negritas y código suplementario."""
    resultado = html.escape(limpiar(texto))
    resultado = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", resultado)
    resultado = re.sub(
        r"`([^`]+)`", r'<font face="Courier" size="8.5">\1</font>', resultado
    )
    return resultado


def crear_estilos():
    """Define los estilos tipográficos del documento."""
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle(
            "Titulo", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=20, leading=26, alignment=TA_CENTER,
            textColor=colors.HexColor("#1F3864"), spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=13, leading=17, spaceBefore=10, spaceAfter=8,
            textColor=colors.HexColor("#1F3864"),
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=11, leading=15, spaceBefore=8, spaceAfter=5,
            textColor=colors.HexColor("#2E5496"),
        ),
        "normal": ParagraphStyle(
            "Normal", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10, leading=15, alignment=TA_JUSTIFY, spaceAfter=7,
        ),
        "lista": ParagraphStyle(
            "Lista", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10, leading=15, leftIndent=14, spaceAfter=4,
        ),
        "th": ParagraphStyle(
            "Th", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
            textColor=colors.white,
        ),
        "td": ParagraphStyle(
            "Td", fontName="Helvetica", fontSize=8.5, leading=11,
        ),
    }


def hacer_tabla(filas, estilos):
    """Convierte filas de Markdown en una tabla de reportlab."""
    columnas = len(filas[0])
    if columnas == 2:
        pesos = [0.30, 0.70]
    elif columnas == 3:
        pesos = [0.16, 0.34, 0.50]
    else:
        pesos = [1 / columnas] * columnas

    datos = []
    for indice, fila in enumerate(filas):
        estilo = estilos["th"] if indice == 0 else estilos["td"]
        datos.append([Paragraph(enriquecer(celda), estilo) for celda in fila])

    tabla = Table(datos, colWidths=[ANCHO * p for p in pesos], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3864")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#EEF2F8")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9AA7BC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tabla


def decorar(canvas, documento):
    """Dibuja encabezado y número de página en cada hoja."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(60, A4[1] - 32, "Software FJ - Fase 4: manejo de excepciones")
    canvas.drawRightString(A4[0] - 60, A4[1] - 32, "UNAD")
    canvas.drawCentredString(A4[0] / 2, 28, f"Pagina {documento.page}")
    canvas.restoreState()


def main():
    """Lee el Markdown, construye el flujo y escribe el PDF."""
    with open(ARCHIVO_ENTRADA, encoding="utf-8") as archivo:
        lineas = archivo.read().splitlines()

    estilos = crear_estilos()
    historia = []
    indice = 0

    while indice < len(lineas):
        linea = lineas[indice].strip()
        indice += 1

        if not linea:
            continue

        # Tablas: bloques consecutivos de filas iniciadas con |
        if linea.startswith("|"):
            bloque = [linea]
            while indice < len(lineas) and lineas[indice].strip().startswith("|"):
                bloque.append(lineas[indice].strip())
                indice += 1

            filas = []
            for fila in bloque:
                celdas = [c.strip() for c in fila.strip("|").split("|")]
                if all(re.fullmatch(r":?-{2,}:?", c) for c in celdas):
                    continue  # fila separadora |---|---|
                filas.append(celdas)

            if filas:
                historia.append(hacer_tabla(filas, estilos))
                historia.append(Spacer(1, 10))
            continue

        if linea.startswith("### "):
            historia.append(Paragraph(enriquecer(linea[4:]), estilos["h2"]))
        elif linea.startswith("## "):
            titulo = linea[3:]
            if titulo == "Portada":
                historia.append(Spacer(1, 12))
            else:
                if titulo.startswith("1. Introducción"):
                    historia.append(PageBreak())  # la portada ocupa la página 1
                historia.append(Paragraph(enriquecer(titulo), estilos["h1"]))
        elif linea.startswith("# "):
            historia.append(Spacer(1, 55))
            historia.append(Paragraph(enriquecer(linea[2:]), estilos["titulo"]))
            historia.append(Spacer(1, 8))
        elif linea.startswith("---"):
            historia.append(HRFlowable(width="100%", color=colors.HexColor("#BBBBBB")))
            historia.append(Spacer(1, 6))
        elif linea.startswith("- "):
            historia.append(Paragraph("• " + enriquecer(linea[2:]), estilos["lista"]))
        elif re.match(r"^\d+\. ", linea):
            historia.append(Paragraph(enriquecer(linea), estilos["lista"]))
        else:
            historia.append(Paragraph(enriquecer(linea), estilos["normal"]))

    documento = SimpleDocTemplate(
        ARCHIVO_SALIDA,
        pagesize=A4,
        leftMargin=60, rightMargin=60, topMargin=50, bottomMargin=50,
        title="Software FJ - Fase 4: Manejo de excepciones",
        author="Grupo de trabajo - UNAD",
        subject="Componente practico - Actividad 4",
    )
    documento.build(
        historia, onFirstPage=decorar, onLaterPages=decorar
    )
    print(f"PDF generado correctamente: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
