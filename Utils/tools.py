import base64
# from Utils.constants import BASE_PATH_TEMPLATE
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
# from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json
import os
import smtplib
from datetime import datetime
from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter, legal
from reportlab.pdfgen import canvas
from io import BytesIO
import textwrap
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from PIL import Image
from datetime import datetime



class Tools:

    def outputpdf(self, codigo, file_name, data={}):
        response = Response(
            status_code=codigo,
            content=data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={file_name}"
            }
        )
        return response


    """ Esta funcion permite darle formato a la respuesta de la API """
    def output(self, codigo, message, data={}):

        response = JSONResponse(
            status_code=codigo,
            content=jsonable_encoder({
                "code": codigo,
                "message": message,
                "data": data,
            }),
            media_type="application/json"
        )
        return response

    # """ Esta funcion permite obtener el template """
    # def get_content_template(self, template_name: str):
    #     template = f"{BASE_PATH_TEMPLATE}/{template_name}"

    #     content = ""
    #     with open(template, 'r') as f:
    #         content = f.read()

    #     return content

    def result(self, msg, code=400, error="", data=[]):
        return {
            "body": {
                "statusCode": code,
                "message": msg,
                "data": data,
                "Exception": error
            }
        }

    # Función para formatear las fechas    
    def format_date(self, date):
        fecha_objeto = datetime.strptime(date, "%d-%m-%Y")
        fecha_formateada = fecha_objeto.strftime("%Y-%m-%d")
        return fecha_formateada

    # Función para formatear los numeros    
    def format_number(self, numero):
        formateado = f"{numero:,.0f}".replace(",", ".")
        return formateado
    
    # Función para generar un pdf
    def gen_pdf(self, data):

        # Ruta del archivo PDF original
        original_pdf_path = os.path.join('Templates', 'Mtto_Template.pdf')

        # Cargar el PDF original
        reader = PdfReader(original_pdf_path)
        writer = PdfWriter()

        # Crear un buffer en memoria para el nuevo contenido
        packet  = BytesIO()

        # Crear un objeto canvas de ReportLab
        pdf = canvas.Canvas(packet , pagesize=letter)
        pdf.setFont('Helvetica', 10)

        # Escribir datos en el PDF
        pdf.drawString(140, 643, f"{data['activity_date']}")
        pdf.drawString(140, 630, f"{data['client_name']}")
        pdf.drawString(140, 617, f"{data['om']}")
        pdf.drawString(140, 603, f"{data['solped']}")
        pdf.drawString(140, 580, f"{data['person_receive_name']}")
        pdf.drawString(370, 642, f"{data['buy_order']}-{data['position']}")
        pdf.drawString(145, 545, f"{data['equipment_name']}")

        # Function for set the X mark on the report
        self.set_type_service(pdf, data["type_service"])

        # Ajustamos descripción dinamicamente
        y_position = 527
        y_position = self.ajust_long_text(
            pdf,
            "DESCRIPCIÓN DE LA ACTIVIDAD: ",
            data['service_description'], 
            32, 
            y_position, 
            510
        )

        # Ajustamos informatión dinamicamente
        y_position -= 30
        y_position = self.ajust_long_text(
            pdf,
            "",
            data['information'], 
            32, 
            y_position, 
            510
        )

        # Ajustar la lista de tareas justo debajo de la descripción
        tasks = data["tasks"]
        if tasks:
            y_position = self.ajust_list(pdf, tasks, x=28, y=y_position - 20)  # Ajusta el espaciado

        # Agregar las imágenes justo debajo de la lista de mantenimiento
        image_paths = data["files"]
        if image_paths:
            max_height = 170  # Altura mínima para imágenes
            y_position = self.ajust_images(pdf, image_paths, x=100, y=0, max_height=max_height, page_height=letter[1])

        # Guardar el PDF con los datos escritos en el buffer
        pdf.save()

        # Mover el buffer al principio
        packet.seek(0)

        # Leer el nuevo PDF con los datos
        new_pdf = PdfReader(packet)

        # Combinar cada página del PDF original con las páginas generadas
        for i, page in enumerate(reader.pages):
            if i == 0:  # Solo superponer en la primera página del original
                page.merge_page(new_pdf.pages[0])
                writer.add_page(page)
            else:
                writer.add_page(page)

        # Agregar las páginas adicionales del nuevo PDF (imágenes en este caso)
        for i in range(1, len(new_pdf.pages)):
            writer.add_page(new_pdf.pages[i])

        # Guardar el PDF final en memoria
        output_buffer = BytesIO()
        writer.write(output_buffer)

        # Mover el buffer al principio
        output_buffer.seek(0)

        return output_buffer.read()
    
    # Función para ajustar textos largos
    def ajust_long_text(self, can, title, text, x, y, max_width):
        """
        Función que ajusta el texto a varias líneas si es demasiado largo.
        :param can: El objeto canvas de ReportLab.
        :param text: El texto que se va a añadir.
        :param x: La posición x en el PDF.
        :param y: La posición y en el PDF.
        :param max_width: El ancho máximo en píxeles para una línea de texto.
        """
        # Margen de seguridad para evitar desbordamiento
        page_margin = 40  
        max_width = min(max_width, letter[0] - x - page_margin)

        # Dividir el texto por saltos de línea para conservar párrafos
        paragraphs = text.split("\n")

        # Formatear los párrafos con doble salto de línea en HTML
        formatted_text = "<br/><br/>".join(p.strip() for p in paragraphs if p.strip())

        # Crear un estilo personalizado para la justificación
        justified_style = ParagraphStyle(
            name='Justified',
            fontName='Helvetica',
            fontSize=11,
            leading=12,  # Espaciado entre líneas
            alignment=TA_JUSTIFY,  # 4 = Justificado
            spaceAfter=6,  # Espaciado después del párrafo
        )

        # Crear el párrafo justificado
        paragraph = Paragraph(f"<b>{title}</b>{formatted_text}", justified_style)

        # Calcular el tamaño del párrafo
        text_width, text_height = paragraph.wrapOn(can, max_width, 0)

        # Verificar si el texto cabe en la página actual
        if y - text_height < 50:  # Si no cabe en la página, mover a la siguiente
            can.showPage()
            y = letter[1] - 50  # Reiniciar la posición en la nueva página

        # Dibujar un rectángulo alrededor del texto
        can.setStrokeColor(colors.black)
        can.setLineWidth(1)
        can.rect(x - 5, y - text_height, max_width + 10, text_height + 10, stroke=1, fill=0)

        # Dibujar el texto justificado en el canvas
        paragraph.drawOn(can, x, y - text_height + 5)

        return y - text_height + 15  # Retornar la nueva posición Y

    # Función para ajustar la lista de tareas
    def ajust_list(self, can, tasks, x, y):
        """
        Función para agregar la lista de tareas justo debajo de la descripción.
        :param can: El objeto canvas de ReportLab.
        :param tasks: La lista de tareas a dibujar.
        :param x: La posición x en el PDF.
        :param y: La posición y en el PDF.
        :return: La nueva coordenada 'y' después de haber escrito la lista de tareas.
        """
        y -= 12  # Mover hacia arriba para la lista

        # Crear los títulos de la tabla
        table_data = [["Tarea", "SI", "NO", "Descripción"]]

        # Definir un estilo para ajustar el texto
        style = ParagraphStyle(name='TableParagraph', fontSize=10, leading=12)

        # Añadir los datos de las tareas
        for task in tasks:
            description_paragraph = Paragraph(task["description"], style)
            row = [
                task["name"],
                "✔" if task["positive"] == 1 else "",
                "✔" if task["negative"] == 1 else "",
                description_paragraph
            ]
            table_data.append(row)

        # Crear la tabla
        table = Table(table_data, colWidths=[230, 30, 30, 230])  # Ajusta los anchos de las columnas

        # Estilo de la tabla
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo gris para la fila del encabezado
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto blanco para el encabezado
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),  # Centrar "SI" y "NO"
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),  # Alinear a la izquierda la columna "Descripción"
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente en negrita para el encabezado
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Tamaño de fuente
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Espaciado inferior en el encabezado
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),  # Fondo blanco para las filas
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Líneas de la tabla
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alinear el texto superiormente
            ('WORDWRAP', (3, 1), (3, -1), 'CJK'),  # Ajuste automático de texto en la columna descripción
        ])
        table.setStyle(style)

        # Determinar el tamaño de la tabla
        table_width, table_height = table.wrapOn(can, x, y)

        # Verificar si la tabla cabe en la página actual
        if y - table_height < 50:  # Si no cabe, pasar a la siguiente página
            can.showPage()
            y = letter[1] - 50  # Reiniciar posición en nueva página

        # Dibujar la tabla en la posición especificada
        table.drawOn(can, x, y - table_height)

        return y - table_height  # Devuelve la nueva coordenada y después de la lista

    # Función para ajustar las imagenes
    def ajust_images(self, can, image_files, x, y, max_height, page_height):
        """
        Función para agregar imágenes al PDF, comenzando siempre desde la segunda página.
        :param can: El objeto canvas de ReportLab.
        :param image_paths: Lista de rutas de imágenes.
        :param x: Posición x en el PDF.
        :param y: Posición y en el PDF.
        :param max_height: Altura máxima de una imagen.
        :param page_height: Altura total de la página.
        :return: La nueva coordenada y después de agregar las imágenes.
        """
        # Forzar una nueva página al inicio
        can.showPage()  
        page_width, _ = letter  # Obtener el ancho de la página estándar 'letter'
        y = page_height - 50  # Reiniciar la posición 'y' en la nueva página

        # Configurar estilo para el texto
        styles = getSampleStyleSheet()
        text_style = styles["BodyText"]  # Usar un estilo estándar

        for image in image_files:
            image_path = image["path"]
            img_description = image["description"]
            if not image["description"]:
                img_description = ""

            try:

                # Obtener dimensiones reales de la imagen
                with Image.open(image_path) as img:
                    orig_width, orig_height = img.size

                # Calcular la escala para mantener la proporción
                scale_factor = min(300 / orig_width, max_height / orig_height) * 2.5

                # Calcular el nuevo tamaño proporcional
                img_width = orig_width * scale_factor
                img_height = orig_height * scale_factor

                # Calcular posición x centrada
                centered_x = (page_width - img_width) / 2

                # Dibujar un borde antes de la imagen
                border_margin = 5
                can.setStrokeColorRGB(0, 0, 0)  # Color negro para el borde
                can.rect(centered_x - border_margin, y - img_height - border_margin, 
                        img_width + (border_margin * 2), img_height + (border_margin * 2), 
                        stroke=1, fill=0)

                # Dibujar la imagen centrada
                can.drawImage(image_path, centered_x, y - img_height, width=img_width, height=img_height)

                # Crear un objeto Paragraph para manejar los saltos de línea
                paragraph = Paragraph(img_description, text_style)
                _, paragraph_height = paragraph.wrap(img_width, 100)  # Ajustar ancho

                # Dibujar la descripción centrada debajo de la imagen
                paragraph.drawOn(can, centered_x, y - img_height - paragraph_height - 5)

                # Actualizar la posición 'y'
                y -= img_height + 100  # Espaciado entre imágenes

                # Verificar si necesitamos una nueva página
                if y - img_height < 50:  # Si no hay espacio suficiente
                    can.showPage()
                    y = page_height - 50  # Reiniciar 'y' para la nueva página

            except Exception as e:
                print(f"Error al dibujar la imagen {image_path}: {e}")
                raise CustomException(f"Error al dibujar la imagen {image_path}: {e}")

        return y  # Devuelve la posición final de 'y'
    
    # Función para setear cuando un tipo de servicio fue elegido.
    def set_type_service(self, can, data):
        
        if data:
            for key in data:
                if key["id"] == 1:
                    can.drawString(532, 630, "✔")
                elif key["id"] == 2:
                    can.drawString(532, 615, "✔")
                elif key["id"] == 3:
                    can.drawString(532, 600, "✔")
                elif key["id"] == 4:
                    can.drawString(532, 585, "✔")
                elif key["id"] == 5:
                    can.drawString(532, 572, "✔")

    # Función para generar un pdf tipo acesco
    def gen_pdf_acesco(self, data):

        año, mes, dia = data['activity_date'].strftime("%Y-%m-%d").split("-")

        # Ruta del archivo PDF original
        original_pdf_path = os.path.join('Templates', 'Acesco_Template.pdf')

        # Cargar el PDF original
        reader = PdfReader(original_pdf_path)
        writer = PdfWriter()

        # Crear un buffer en memoria para el nuevo contenido
        packet  = BytesIO()

        # Crear un objeto canvas de ReportLab
        pdf = canvas.Canvas(packet , pagesize=legal)
        pdf.setFont('Helvetica', 7)

        # Escribir datos en el PDF
        pdf.setFillColorRGB(1, 1, 1)  # Blanco (RGB: 1,1,1)
        pdf.drawString(95, 681, f"{data['id']}")
        pdf.setFillColorRGB(0, 0, 0)  # Restaurar a negro después
        pdf.drawString(95, 671, f"{data['client_line']}")
        pdf.drawString(140, 652, f"{dia}")
        pdf.drawString(175, 652, f"{mes}")
        pdf.drawString(212, 652, f"{año}")
        pdf.drawString(290, 662, "ATLÁNTICO")
        pdf.drawString(290, 652, "MALAMBO")
        pdf.drawString(412, 662, f"{data['buy_order']}")
        pdf.drawString(382, 653, f"{data['position']}")
        pdf.drawString(382, 643, f"{data['solped']}")
        pdf.drawString(295, 671, f"{data['work_zone']}")
        pdf.drawString(382, 633, f"{data['om']}")
        pdf.drawString(95, 643, f"{data['client_name']}")
        pdf.drawString(100, 633, f"{data['person_receive_name'].upper()}")
        pdf.drawString(242, 642, f"{data['person_receive_name'].upper()}")
        pdf.drawString(134, 610, f"{data['service_description'].upper()}")
        pdf.drawString(404, 610, f"{self.format_number(data['service_value'])}")

        y_position = 596
        # Ajustamos informatión dinamicamente
        self.ajust_long_text_acesco(
            pdf,
            data['information'], 
            52, 
            y_position, 
            390
        )

        self.ajust_long_text_acesco(
            pdf,
            data['conclutions'], 
            52, 
            90, 
            390
        )

        self.ajust_long_text_acesco(
            pdf,
            data['recommendations'], 
            52, 
            50, 
            390
        )

        image_paths = data["files"]
        if image_paths:
            imagen_antes = image_paths[0]["path"]
            imagen_despues = image_paths[1]["path"]
            max_height = 60  # Altura mínima para imágenes

            self.ajust_images_acesco(pdf, imagen_antes, x=100, y=330, max_height=max_height, page_height=legal[1])
            self.ajust_images_acesco(pdf, imagen_despues, x=100, y=208, max_height=max_height, page_height=legal[1])

        # Guardar el PDF con los datos escritos en el buffer
        pdf.save()

        # Mover el buffer al principio
        packet.seek(0)

        # Leer el nuevo PDF con los datos
        new_pdf = PdfReader(packet)

        # Escribir en la segunda página del template
        packet_2 = BytesIO()
        pdf_2 = canvas.Canvas(packet_2, pagesize=legal)
        pdf_2.setFont('Helvetica', 7)

        # Escribir datos en la segunda página
        pdf_2.drawString(80, 570, f"{data['tech_1']}")
        pdf_2.drawString(315, 570, f"{data['tech_2']}")

        # Guardar los cambios en el buffer
        pdf_2.save()
        packet_2.seek(0)
        new_pdf_2 = PdfReader(packet_2)

        # --- Mezclar las páginas con el template ---
        for i, page in enumerate(reader.pages):
            if i == 0:
                page.merge_page(new_pdf.pages[0])  # Mezclar primera página
            elif i == 1:
                page.merge_page(new_pdf_2.pages[0])  # Mezclar segunda página

            writer.add_page(page)

        # Guardar el PDF final en memoria
        output_buffer = BytesIO()
        writer.write(output_buffer)

        # Mover el buffer al principio
        output_buffer.seek(0)

        # --- Agregar anexos como páginas nuevas ---
        anexos = data.get("anexos", [])
        if anexos:
            # Leer el PDF actual generado
            output_buffer.seek(0)
            final_reader = PdfReader(output_buffer)
            final_writer = PdfWriter()
            # Copiar las páginas existentes
            for page in final_reader.pages:
                final_writer.add_page(page)

            for anexo in anexos:
                packet_anexo = BytesIO()
                pdf_anexo = canvas.Canvas(packet_anexo, pagesize=legal)
                # Centrar y ajustar la imagen
                try:
                    from PIL import Image
                    with Image.open(anexo["path"]) as img:
                        orig_width, orig_height = img.size
                    max_height = legal[1] - 100
                    max_width = legal[0] - 100
                    scale_factor = min(max_width / orig_width, max_height / orig_height)
                    img_width = orig_width * scale_factor
                    img_height = orig_height * scale_factor
                    centered_x = (legal[0] - img_width) / 2
                    centered_y = (legal[1] - img_height) / 2
                    pdf_anexo.drawImage(anexo["path"], centered_x, centered_y, width=img_width, height=img_height)
                except Exception as e:
                    print(f"Error al agregar anexo {anexo['path']}: {e}")
                pdf_anexo.save()
                packet_anexo.seek(0)
                anexo_pdf = PdfReader(packet_anexo)
                final_writer.add_page(anexo_pdf.pages[0])

            # Guardar el PDF final con anexos
            output_buffer_final = BytesIO()
            final_writer.write(output_buffer_final)
            output_buffer_final.seek(0)
            return output_buffer_final.read()
        else:
            return output_buffer.read()
    
    # Función para ajustar textos largos del diseño de acesco
    def ajust_long_text_acesco(self, can, text, x, y, max_width):
        """
        Función que ajusta el texto a varias líneas si es demasiado largo.
        :param can: El objeto canvas de ReportLab.
        :param text: El texto que se va a añadir.
        :param x: La posición x en el PDF.
        :param y: La posición y en el PDF.
        :param max_width: El ancho máximo en píxeles para una línea de texto.
        """
        # Margen de seguridad para evitar desbordamiento
        page_margin = 40  
        max_width = min(max_width, legal[0] - x - page_margin)

        # Dividir el texto por saltos de línea para conservar párrafos
        paragraphs = text.split("\n")

        # Formatear los párrafos con doble salto de línea en HTML
        formatted_text = "<br/><br/>".join(p.strip() for p in paragraphs if p.strip())

        # Crear un estilo personalizado para la justificación
        justified_style = ParagraphStyle(
            name='Justified',
            fontName='Helvetica',
            fontSize=8,
            leading=9,  # Espaciado entre líneas
            alignment=TA_JUSTIFY,  # 4 = Justificado
            spaceAfter=6,  # Espaciado después del párrafo
        )

        # Crear el párrafo justificado
        paragraph = Paragraph(f"{formatted_text}", justified_style)

        # Calcular el tamaño del párrafo
        text_width, text_height = paragraph.wrapOn(can, max_width, 0)

        # Dibujar el texto justificado en el canvas
        paragraph.drawOn(can, x, y - text_height + 5)

        return y - text_height + 15  # Retornar la nueva posición Y

    # Función para ajustar las imagenes del diseño de acesco
    def ajust_images_acesco(self, can, imagen, x, y, max_height, page_height):
        """
        Función para agregar imágenes al PDF, comenzando siempre desde la segunda página.
        :param can: El objeto canvas de ReportLab.
        :param imagen: imágen.
        :param x: Posición x en el PDF.
        :param y: Posición y en el PDF.
        :param max_height: Altura máxima de una imagen.
        :param page_height: Altura total de la página.
        :return: La nueva coordenada y después de agregar las imágenes.
        """

        page_width, _ = legal  # Obtener el ancho de la página estándar 'legal'

        # Configurar estilo para el texto
        styles = getSampleStyleSheet()

        try:

            # Obtener dimensiones reales de la imagen
            with Image.open(imagen) as img:
                orig_width, orig_height = img.size

            # Calcular la escala para mantener la proporción
            scale_factor = min(300 / orig_width, max_height / orig_height) * 1.5

            # Calcular el nuevo tamaño proporcional
            img_width = orig_width * scale_factor
            img_height = orig_height * scale_factor

            # Calcular posición x centrada
            centered_x = (page_width - img_width) / 2.5

            # Dibujar un borde antes de la imagen
            border_margin = 5
            can.setStrokeColorRGB(0, 0, 0)  # Color negro para el borde
            can.rect(centered_x - border_margin, y - img_height - border_margin, 
                    img_width + (border_margin * 2), img_height + (border_margin * 2), 
                    stroke=1, fill=0)

            # Dibujar la imagen centrada
            can.drawImage(imagen, centered_x, y - img_height, width=img_width, height=img_height)

            # Actualizar la posición 'y'
            y -= img_height + 100  # Espaciado entre imágenes

            # Verificar si necesitamos una nueva página
            if y - img_height < 50:  # Si no hay espacio suficiente
                can.showPage()
                y = page_height - 50  # Reiniciar 'y' para la nueva página

        except Exception as e:
            print(f"Error al dibujar la imagen {imagen}: {e}")
            raise CustomException(f"Error al dibujar la imagen {imagen}: {e}")

        return y  # Devuelve la posición final de 'y'
    
    
    # """ Obtener archivo"""
    # def get_file_b64(self, file_path):
    #     with open(file_path, "rb") as file:
    #         # Leer el contenido binario del archivo PDF
    #         pdf_content = file.read()

    #         # Codificar el contenido binario en base64
    #         pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

    #         return pdf_base64

    # async def send_email_error(self, service_name, code, request, response):
    #     load_dotenv()
    #     # Obtener enviroment
    #     stage = os.getenv("STAGE")
    #     remitente = os.getenv("EMAIL_USER")
    #     destinatario = os.getenv("EMAIL_DEV")

    #     template_url = f"{BASE_PATH_TEMPLATE}/notificacion_error.html"
    #     # Preapar el asunto del correo
    #     subject = f"TOYO - Project: Error service - Stage: {stage}"
    #     # Preparar el contenido del correo
    #     data_correo = {
    #         "servicio": "TOYO",
    #         "status_code": code,
    #         "consumo": service_name,
    #         "id_gestion": "000",
    #         "url": "Toyo_dev",
    #         "request": request,
    #         "response": response
    #     }

    #     msg = MIMEMultipart()
    #     msg["Subject"] = subject
    #     msg["From"] = remitente
    #     msg["To"] = destinatario

    #     with open(template_url, 'r') as template_file:
    #         template = template_file.read()
    #         template = template.format(**data_correo)
    #     msg.attach(MIMEText(template, 'html'))

    #     # Configura la conexión al servidor SMTP de Gmail
    #     server = smtplib.SMTP('smtp.gmail.com', 587)
    #     server.starttls()
    #     server.login(remitente, os.getenv('EMAIL_PASSWORD'))

    #     # Envía el correo
    #     server.sendmail(remitente, destinatario, msg.as_string())

    #     # Cierra la conexión con el servidor SMTP
    #     server.quit()

    # async def send_email(self, recipients, subject, body, attachments=None):
    #     sender = os.getenv("EMAIL_USER")

    #     msg = MIMEMultipart()
    #     msg["Subject"] = subject
    #     msg["From"] = sender
    #     msg["To"] = recipients

    #     msg.attach(MIMEText(body, 'html'))
    #     # Agregar archivos adjuntos en formato base64 al mensaje MIME
    #     if attachments:
    #         for attachment in attachments:
    #             # Decodificar el contenido base64
    #             decoded_data = base64.b64decode(attachment["file"])

    #             # Crear un objeto MIMEBase y adjuntar el archivo decodificado
    #             attachment_part = MIMEBase('application', 'octet-stream')
    #             attachment_part.set_payload(decoded_data)
    #             encoders.encode_base64(attachment_part)

    #             # Establecer el encabezado del archivo adjunto
    #             attachment_part.add_header('Content-Disposition', f'attachment; filename={attachment["name"]}')
    #             msg.attach(attachment_part)

    #     # Configurar conexion con servidor SMTP
    #     server = smtplib.SMTP('smtp.gmail.com', 587)
    #     server.starttls()
    #     server.login(sender, os.getenv('EMAIL_PASSWORD'))
    #     server.sendmail(sender, recipients, msg.as_string())
    #     # Cerrar conexion Con servidor
    #     server.quit()


class CustomException(Exception):
    """ Esta clase hereda de la clase Exception y permite
        interrumpir la ejecucion de un metodo invocando una excepcion
        personalizada """
    def __init__(self, message="", codigo=400, data={}):
        self.codigo = codigo
        self.message = message
        self.data = data
        self.resultado = {
            "body": {
                "statusCode": codigo,
                "message": message,
                "data": data,
                "Exception": "CustomException"
            }
        }
