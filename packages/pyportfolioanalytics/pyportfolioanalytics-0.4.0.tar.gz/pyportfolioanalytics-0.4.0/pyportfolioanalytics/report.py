# # Librerías para importar las funciones que serán necesarias para la construcción del reporte
# from utils import get_stock_price_close
# from utils import get_name_columns
# from utils import get_date_start
# from utils import get_date_end
# from utils import plot_return_log
# from utils import histogram_stock_returns
# from utils import return_log_mean_and_standard_deviation
# from utils import plot_covariance_matrix
# from utils import plot_correlation_matrix
# from utils import return_positive_negative
# from utils import BuySellStocks

# # Importación de las instancias de la clase de la librería REPORTLAB
# from reportlab.lib.pagesizes import A4, inch
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageTemplate, Frame
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
# from reportlab.lib.utils import ImageReader

# # Importación de librería de Python
# import os


# class ReportFinancial:
    
#     def __init__(self, stock, start, end, weights, investment):
#         self.stock = stock
#         self.start = start
#         self.end = end
#         self.investment = investment
#         self.weights = weights
        
#     def report(self):
#         plot_precio_cierre = get_stock_price_close(self.stock, self.start, self.end)
#         get_start_date = get_date_start(self.stock, self.start, self.end)
#         get_date_ends = get_date_end(self.stock, self.start, self.end)
#         plot_rendimiento = plot_return_log(self.stock, self.start, self.end)
#         histogram_stock_return = histogram_stock_returns(self.stock, self.start, self.end)
#         return_log_mean_and_standard_deviatio = return_log_mean_and_standard_deviation(self.stock, self.start, self.end)
#         plot_covariance_matri = plot_covariance_matrix(self.stock, self.start, self.end)
#         plot_correlation_matri = plot_correlation_matrix(self.stock, self.start, self.end)
        
#         bs = BuySellStocks(self.stock, self.start, self.end, self.weights, self.investment)
#         first = bs.first_price_stock()
#         final = bs.last_price_stock()
#         plot = bs.plot_income_outcome_benefits()
#         investment = self.investment
#         benefits = bs.benefits_buy_sell_stock()
#         benefits_str = return_positive_negative(benefits)
        
#         author = 'Sebastian Marat Urdanegui Bisalaya'

#         proyect_directory = os.getcwd()
#         path_dir = os.path.join(proyect_directory, 'pdfs')
#         os.makedirs(path_dir, exist_ok=True)
#         report_path = 'report.pdf'
#         report_paths = os.path.join(path_dir, report_path)
#         pdf = SimpleDocTemplate(report_paths, pagesize = A4)
#         estilos = getSampleStyleSheet()
#         estilo_titulo = ParagraphStyle(name = 'centrado', parent = estilos['Title'],
#                                     alignment = TA_CENTER)
#         estilo_titulo.fontSize = 10

#         estilo_subtitulo = estilos['Heading2']
#         estilo_subtitulo.alignment = TA_CENTER

#         estilo_texto = estilos["Normal"]
#         estilo_texto.alignment = TA_JUSTIFY

#         estilo_linea = ParagraphStyle(name = 'linea', parent = estilo_titulo, borderWidth = 2,
#                                     borderColor = colors.black, spaceBefore = 5,
#                                     spaceAfter = 5)

#         titulo = Paragraph(f'{author}', estilo_titulo)
#         pdf_title = [titulo, Spacer(1,0.05)]

#         subtitulo = Paragraph("Reporte Financiero - Introducción a los Mercados Bursátiles", estilo_subtitulo)
#         pdf_title.append(subtitulo)
#         pdf_title.append(Spacer(1, 0.05))

#         pdf_title.append(Spacer(1, 0.05))
#         pdf_title.append(Paragraph('<hr width="50%" align="center" color="black">', estilo_texto))
#         pdf_title.append(Spacer(1, 0.05))
#         linea = Paragraph('<hr width="50%" align="center" size="5">', estilo_linea)
#         pdf_title.append(linea)

#         data = [['', ''],
#                 ['', '']]

#         imagen1 = ImageReader("./plots/precios_cierre.png")
#         data[0][0] = Image(open(imagen1.fileName, 'rb'), width=3.5*inch,
#                         height=3.5*inch)


#         imagen2 = ImageReader("./plots/rendimiento_log.png")
#         data[0][1] = Image(open(imagen2.fileName, 'rb'), width=3.5*inch,
#                         height=3.5*inch)

#         imagen3 = ImageReader("./plots/precios_histograma.png")
#         data[1][0] = Image(open(imagen3.fileName, 'rb'), width=3.5*inch,
#                         height=3.5*inch)

#         imagen4 = ImageReader("./plots/rendimiento_volatilidad_anualizada.png")
#         data[1][1] = Image(open(imagen4.fileName, 'rb'), width=3.5*inch,
#                         height=3.5*inch)


#         tabla = Table(data, colWidths=250, rowHeights=300)
#         estilo_tabla = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                                 ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
#                                 ('BOX', (0, 0), (-1, -1), 1, colors.white)])
#         tabla.setStyle(estilo_tabla)

#         pdf_content = [tabla]


#         data_2 = [[''],
#                 ['']]

#         imagen5 = ImageReader("./plots/variaza_covarianza.png")
#         data_2[0][0] = Image(open(imagen5.fileName, 'rb'), width=5.6*inch,
#                         height=5*inch)

#         imagen6 = ImageReader("./plots/matriz_correlacion.png")
#         data_2[1][0] = Image(open(imagen6.fileName, 'rb'), width=5.6*inch,
#                         height=5*inch)

#         tabla_2 = Table(data_2, colWidths=500, rowHeights=340)
#         tabla_2.setStyle(estilo_tabla)
#         pdf_content.append(tabla_2)

#         estilo_subtitulo2 = estilos['Heading2']
#         estilo_subtitulo2.alignment = TA_CENTER
#         subtitulo2 = Paragraph("Análisis de Compra y Venta de las Acciones", estilo_subtitulo2)
#         pdf_content.append(subtitulo2)
#         pdf_content.append(Spacer(1, 0.05))
#         estilo_linea2 = ParagraphStyle(name = 'linea2', parent = estilo_titulo, borderWidth = 2,
#                                     borderColor = colors.black, spaceBefore = 5,
#                                     spaceAfter = 5)
#         linea2 = Paragraph('<hr width="50%" align="center" size="5">', estilo_linea2)
#         pdf_content.append(linea2)
#         pdf_content.append(Spacer(1, 0.25*inch))
#         estilo_texto2 = estilos["Normal"]
#         estilo_texto2.alignment = TA_JUSTIFY
#         texto2 = Paragraph(f'''A continuación, se muestra el resumen de la adquisición de 
#                         acciones tomando como referencia la inversión inicial de S/. {investment} con el 
#                         obtejivo de obtener el número de acciones necesarias para optimizar el rendimiento 
#                         del portafolio de inversión en función del peso que representa cada compañía.''', estilo_texto2)
#         pdf_content.append(texto2)
#         pdf_content.append(Spacer(1, 0.25*inch))

#         datos_tablas_estilos = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                                 ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
#                                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                                 ('FONTSIZE', (0, 0), (-1, 0), 6),
#                                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                                 ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                                 ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#                                 ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
#                                 ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                                 ('FONTSIZE', (0, 1), (-1, -1), 5),
#                                 ('BOX', (0, 0), (-1, -1), 1, colors.black)])

#         data_tabla_1 = [list(first.columns)]
#         for row in first.itertuples(index = False):
#                 data_tabla_1.append(list(row))
#         tabla_3 = Table(data_tabla_1)
#         tabla_3.setStyle(datos_tablas_estilos)
#         pdf_content.append(tabla_3)
#         pdf_content.append(Spacer(1, 0.25*inch))

#         estilo_texto3 = estilos["Normal"]
#         estilo_texto3.alignment = TA_JUSTIFY
#         texto3 = Paragraph(f'''La siguiente tabla ofrece información con respecto a la venta de las acciones
#                         que estaban en nuestro portafolio. Reflejando el precio de la fecha de venta para calcular
#                         los ingresos parciales con respecto al número de acciones que el inversor había adquirido.''', estilo_texto2)
#         pdf_content.append(texto3)
#         pdf_content.append(Spacer(1, 0.25*inch))

#         data_tabla_2 = [list(final.columns)]
#         for row in final.itertuples(index = False):
#                 data_tabla_2.append(list(row))
#         tabla_4 = Table(data_tabla_2)
#         tabla_4.setStyle(datos_tablas_estilos)
#         pdf_content.append(tabla_4)
#         pdf_content.append(Spacer(1, 0.25*inch))

#         estilo_texto4 = estilos["Normal"]
#         estilo_texto4.alignment = TA_JUSTIFY
#         texto4 = Paragraph(f'''Luego de la venta de acciones del portafolio, se obtiene un beneficio neto (reduciendo el costo
#                         de adquisición) de S/. {benefits}. En este caso, el ejercicio muestra una {benefits_str} en el
#                         flujo de efectivo.''', estilo_texto4)
#         pdf_content.append(texto4)
#         pdf_content.append(Spacer(1, 0.1*inch))

#         data_3 = [['']]
#         imagen7 = ImageReader("./plots/beneficio_ingreso_inversion.png")
#         data_3[0][0] = Image(open(imagen7.fileName, 'rb'), width=3.5*inch,
#                         height=2*inch)
#         tabla_5 = Table(data_3, colWidths=500, rowHeights=150)
#         tabla_5.setStyle(estilo_tabla)
#         pdf_content.append(tabla_5)


#         pdf.build(pdf_title + pdf_content)
        

# if __name__ == '__main__':
#     reporte = ReportFinancial(["AAPL", "AMZN", "META", "TSLA", "AMD", "NFLX"], '2022-01-01', '2023-01-01', [0.2,0.2,0.3, 0.1, 0.1, 0.1], 1000000)
#     reporte.report()