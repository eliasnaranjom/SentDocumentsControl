import PyPDF2
from reportlab.graphics.barcode import code39
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PyPDF2 import Transformation
from datetime import date
import csv
import tkinter
from tkinter import *
from tkinter import ttk
import customtkinter
import os
import subprocess

#Día actual
today = date.today()

def idDocuments():
    with open('logs.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # saltar la primera fila
        id = []
        log=[]
        for fila in reader:
            log.append(fila)
            id.append(int(fila[1]))
        
        return log, id
    

class TabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create tabs
        self.add("Generar código")
        self.add("Documentos enviados")

        logs, ids = idDocuments()

        # add widgets on tabs
        self.label = customtkinter.CTkLabel(master=self.tab("Generar código"), text='Documentos enviados: {}'.format(ids[-1]))
        self.label.grid(row=10, column=10, padx=20, pady=10)

        self.button_file = customtkinter.CTkButton(master=self.tab("Generar código"), text="Subir archivo", command=self.button_callback_file)
        self.button_file.grid(row=11, column=10, padx=20, pady=10)

        # self.button_1 = customtkinter.CTkButton(master=self.tab("tab 1"), text="Archivo a enviar", command=lambda: print(customtkinter.filedialog.askopenfile()))
        # self.button_1.pack(pady=10)

        self.tree = ttk.Treeview(master=self.tab("Documentos enviados"), columns=("id", "archivo"), show="headings")
        self.tree.column("id", width=100)
        self.tree.heading("id", text="ID")
        self.tree.column("archivo", width=400)
        self.tree.heading("archivo", text="Archivo")

        # add sample data to table
        for log in logs:
            self.tree.insert("", tkinter.END, values=(log[1], log[0]))

        self.tree.pack()

    def button_callback_file(self):
        self.link_label = customtkinter.CTkLabel(master=self.tab("Generar código"), text=customtkinter.filedialog.askopenfile().name)
        self.link_label.grid(row=12, column=10, padx=20, pady=10)

        print(self.link_label._text)

        self.button_file = customtkinter.CTkButton(master=self.tab("Generar código"), text="Enviar", command=self.sentDocument)
        self.button_file.grid(row=13, column=10, padx=20, pady=10)

    def sentDocument(self):
        document = self.link_label._text
        logs, ids = idDocuments()
        newID = str(ids[-1]+1)
        newID = newID.zfill(3)

        with open(document, 'rb') as archivo_pdf:
            pdf_reader = PyPDF2.PdfReader(archivo_pdf)
            pdf_writer = PyPDF2.PdfWriter()
            primera_pagina = pdf_reader.pages[0]

            barcode_value = "SS-MCH-{}-{}".format(newID, today.year)
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
                writer.writerow(['{}.pdf'.format(barcode_value), ids[-1]+1])
                print('Documento procesado y generado correctamente')
            
            logs, ids = idDocuments()
            self.label.configure(text='Documentos enviados: {}'.format(len(ids)))
            self.link_label.grid_remove()
            self.button_file.grid_remove()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        logs, ids = idDocuments()

        self.title("Control de documentos enviados")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Control de documentos", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.label = customtkinter.CTkLabel(master=self, text='Documentos enviados: {}'.format(ids[-1]))
        self.label.grid(row=2, column=0, padx=20, pady=10)
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Tema:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="Escala:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.entry_file = customtkinter.CTkEntry(self, placeholder_text="Seleccione un archivo")
        self.entry_file.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.entry_file.configure(state='disabled')

        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2,text='Seleccionar archivo', text_color=("gray10", "#DCE4EE"), command=self.button_callback_file)
        self.main_button_1.grid(row=3, column=3, padx=20, pady=20, sticky="nsew")

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=1, rowspan=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Oficios enviados")
        self.tabview.tab("Oficios enviados").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs

        self.tree = ttk.Treeview(self.tabview.tab("Oficios enviados"), columns=("id", "archivo", "generado"), show="headings", height=25)
        self.tree.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.tree.column("id", width=200)
        self.tree.heading("id", text="ID")
        self.tree.column("archivo", width=250)
        self.tree.heading("archivo", text="Archivo")
        self.tree.column("generado", width=250)
        self.tree.heading("generado", text="Generado")

        # add sample data to table
        for log in logs:
            self.tree.insert("", tkinter.END, values=(log[1], log[0], log[0]))

        # add button for open file explorer
        self.button_file = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text='Abrir carpeta', text_color=("gray10", "#DCE4EE"), command=self.open_folder)
        self.button_file.grid(row=0, column=3, padx=20, pady=20)

    def open_folder(self):
        folder_path = os.getcwd() + "\sentDocuments"
        print(folder_path)
        subprocess.Popen(f'explorer "{folder_path}"')

    def button_callback_file(self):

        self.entry_file.configure(state='normal')
        self.entry_file.insert("end", customtkinter.filedialog.askopenfile().name)
        self.entry_file.configure(state='disabled')

        self.button_file = customtkinter.CTkButton(master=self, text="Enviar", command=self.sentDocument)
        self.button_file.grid(row=3, column=3, padx=20, pady=10)

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sentDocument(self):
        document = self.entry_file.get()
        logs, ids = idDocuments()
        newID = str(ids[-1]+1)
        newID = newID.zfill(3)

        with open(document, 'rb') as archivo_pdf:
            pdf_reader = PyPDF2.PdfReader(archivo_pdf)
            pdf_writer = PyPDF2.PdfWriter()
            primera_pagina = pdf_reader.pages[0]

            barcode_value = "SS-MCH-{}-{}".format(newID, today.year)
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
                writer.writerow(['{}.pdf'.format(barcode_value), ids[-1]+1])
            
            logs, ids = idDocuments()
            self.label.configure(text='Documentos enviados: {}'.format(len(ids)))
            self.entry_file.configure(state='normal')
            self.entry_file.delete(0,'end')
            self.entry_file.insert('end', '¡Documento procesado y generado correctamente!, puede encontrar el archivo dando click en "Abrir carpeta"')
            self.entry_file.configure(state='disabled')
            self.button_file.grid_remove()
            self.tree.insert("", tkinter.END, values=(ids[-1], barcode_value + ".pdf", barcode_value + ".pdf"))

if __name__ == "__main__":
    app = App()
    app.mainloop()