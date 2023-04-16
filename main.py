import PyPDF2
from reportlab.graphics.barcode import code39
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PyPDF2 import Transformation
from datetime import date
import csv

#Día actual
today = date.today()

with open('logs.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # saltar la primera fila
    id = []
    for fila in reader:
        id.append(int(fila[1]))

newID = str(id[-1]+1)
newID = newID.zfill(3)

with open('archivo.pdf', 'rb') as archivo_pdf:
    pdf_reader = PyPDF2.PdfReader(archivo_pdf)
    pdf_writer = PyPDF2.PdfWriter()

    primera_pagina = pdf_reader.pages[0]

    barcode_value = "SS-MCH-{}-{}-".format(newID, today.year)
    barcode = code39.Standard39(barcode_value, barHeight=10*mm, humanReadable=True)

    c = canvas.Canvas('barcode.pdf', pagesize=letter)
    barcode.drawOn(c, x=150*mm, y=270*mm)
    c.save()

    with open('barcode.pdf', 'rb') as barcode_pdf:
        barcode_reader = PyPDF2.PdfReader(barcode_pdf)
        primera_pagina_barcode = barcode_reader.pages[0]

        primera_pagina_barcode.add_transformation(Transformation().scale(1).translate(-40, -150))
        primera_pagina.merge_page(primera_pagina_barcode, expand=True)

        pdf_writer.add_page(primera_pagina)

    for pagina in range(1, len(pdf_reader.pages)):
        pagina_actual = pdf_reader.pages[pagina]
        pdf_writer.add_page(pagina_actual)

    with open('sentDocuments/{}.pdf'.format(barcode_value), 'wb') as archivo_pdf:
        pdf_writer.write(archivo_pdf)

    # agregar el nuevo número al archivo CSV
    with open('logs.csv', 'a', newline='') as archivo:
        writer = csv.writer(archivo)
        writer.writerow(['{}.pdf'.format(barcode_value), id[-1]+1])