import sys
import os
import time
import locale
import textwrap

import win32api
import win32print

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.colors import black

from PyQt5 import uic
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect, QMessageBox, QWidget, QAbstractItemView, QDialog
from PyQt5 import QtGui
from PyQt5.QtSql import QSqlQuery, QSqlTableModel
from PyQt5.QtCore import Qt, QDate, QLocale
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QDoubleValidator, QPainter, QFont, QImage

from Consultas_db import obtener_ultimo_codigo, generar_nuevo_codigo,\
    insertar_nueva_cotizacion, insertar_nuevo_detalle_cotizacion,\
    quitar_detalle_cotizacion, obtener_codigo_cotizacion, generar_nuevo_codigo_cotizacion, convertir_cot_a_factura

class VentanaCotizaciones(QMainWindow):
    ventana_abierta = False     
    def __init__(self):
        self.se_llamo_activar_botones = False
        super().__init__()        
        uic.loadUi('Sistema_de_ventas/ui/FrmCotizacion.ui',self)
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------        
                
        # Configuraiones de la ventana principal.
        self.setWindowTitle('.:. Mantenimiento de Cotizaciones .:.')
        self.setFixedSize(self.size())
        self.setWindowIcon(QtGui.QIcon('Sistema_de_ventas/imagenes/login.jpg'))
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------   
        # Establece las fechas en los txtFechas que estan en el formulario
        self.txtFecha.setDate(QDate.currentDate())
        self.txtFechaInicio.setDate(QDate.currentDate())
        self.txtFechaFin.setDate(QDate.currentDate())
        
        # Establecer la configuración regional en español.
        spanish_locale = QLocale(QLocale.Spanish)
        QLocale.setDefault(spanish_locale)
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------           
        # Crear un efecto de sombra        
        tabWidget_shadow = QGraphicsDropShadowEffect()
        tabWidget_shadow.setBlurRadius(20)
        tabWidget_shadow.setColor(Qt.black)# type: ignore #QColor(200, 200, 200))        
        self.tabWidget.setGraphicsEffect(tabWidget_shadow)
        
        groupBox_shadow = QGraphicsDropShadowEffect()
        groupBox_shadow.setBlurRadius(20)
        groupBox_shadow.setColor(Qt.black)# type: ignore #QColor(200, 200, 200))        
        self.groupBox.setGraphicsEffect(groupBox_shadow)
        
        groupBox3_shadow = QGraphicsDropShadowEffect()
        groupBox3_shadow.setBlurRadius(20)
        groupBox3_shadow.setColor(Qt.black)# type: ignore #QColor(200, 200, 200))        
        self.groupBox_3.setGraphicsEffect(groupBox3_shadow)
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
        # Botones del formulario y sus funciones
        self.txtIdCliente.mouseDoubleClickEvent = self.abrirFrmBuscarCliente
        self.txtCodArticulo.mouseDoubleClickEvent = self.abrirFrmBuscarArticulo        
        self.cmbCliente.mouseDoubleClickEvent = self.abrirFrmBuscarCliente
        self.cmbArticulo.mouseDoubleClickEvent = self.abrirFrmBuscarArticulo        
        self.cmbArticulo.currentIndexChanged.connect(self.cargar_precios_venta)
        self.cmbArticulo.currentIndexChanged.connect(self.actualizar_existencia_producto) 

        self.btnRegistrar.clicked.connect(self.insertar_datos_cotiacion)
        
        
        self.btnImprimir.clicked.connect(self.imprimir_impresora)
        self.btnPdf.clicked.connect(self.imprimir_pdf)

        self.btnAgregar.clicked.connect(self.insertar_detalle_cotizacion)
        self.btnQuitar.clicked.connect(self.quitar_datos_detalle_cotizacion)

        self.btnBuscar.clicked.connect(self.visualizar_datos_cotizacion)
        
        self.btnConvertir.clicked.connect(self.convertir_cotizacion)

        # Controles de fecha conectados a la funcion visualizar_datos_cotizacion para buscar datos entre fechas seleccionadas.
        self.txtFechaInicio.dateChanged.connect(self.visualizar_datos_cotizacion)
        self.txtFechaFin.dateChanged.connect(self.visualizar_datos_cotizacion)
        
        # Establecer el texto de referencia a la caja de texto buscar
        # Conectar el evento de clic para borrar el texto
        self.txtBuscar.setPlaceholderText('Buscar')        
        self.txtBuscar.mousePressEvent = self.borrarTexto 

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
        # Evita que se inserte letras en los campos donde solo lleva numeros 0.0
        double_validator = QDoubleValidator()
        self.txtDescuento.setValidator(double_validator)
        self.cmbPrecioVent.setValidator(double_validator)
        self.txtCantidad.setValidator(double_validator)        
        self.txtItbis.setValidator(double_validator)

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    # Abrir los form para buscar e insertar los clientes y y articulos a las cotizaciones.
    def abrirFrmBuscarCliente(self, event):
        if event.button() == Qt.LeftButton: # type: ignore
            from FrmBuscarClienteCotizacion import VentanaBuscarClienteCotizacion
            if not VentanaBuscarClienteCotizacion.ventana_abierta:
                VentanaBuscarClienteCotizacion.ventana_abierta = True
                self.llamar_ventana = VentanaBuscarClienteCotizacion(self)
                self.llamar_ventana.show()
                
            else:
                #mensaje al usuario
                mensaje = QMessageBox()
                mensaje.setIcon(QMessageBox.Critical)
                mensaje.setWindowTitle("Ventana duplicada")
                mensaje.setText("La ventana ya esta abierta.")
                mensaje.exec_()

    def abrirFrmBuscarArticulo(self, event):
        if event.button() == Qt.LeftButton: # type: ignore
            from FrmBuscarArticuloCotizacion import VentanaBuscarArticuloCotizacion
            if not VentanaBuscarArticuloCotizacion.ventana_abierta:
                VentanaBuscarArticuloCotizacion.ventana_abierta = True
                self.llamar_ventana = VentanaBuscarArticuloCotizacion(self)
                self.llamar_ventana.show()
            
            else:
                #mensaje al usuario
                mensaje = QMessageBox()
                mensaje.setIcon(QMessageBox.Critical)
                mensaje.setWindowTitle("Ventana duplicada")
                mensaje.setText("La ventana ya esta abierta.")
                mensaje.exec_()
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    
    # Trae el resultado y los inserta en los txt y cmb correspondientes
    def traer_cliente(self, id, nombre, apellido):
        nombre_apellidos = nombre +" "+ apellido 
        
        self.txtIdCliente.setText(str(id))
        self.cmbCliente.clear()
        self.cmbCliente.addItem(str(nombre_apellidos))
        
    def traer_articulo(self, id_articulo, nombre_articulo):
        
        self.txtCodArticulo.setText(str(id_articulo))
        self.cmbArticulo.clear()
        self.cmbArticulo.addItem(str(nombre_articulo))
        
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    # Coloca el id de cotizacion en su txt actulizado para el proximo registro
    def actualizar_ID_cotizacion(self):
        ultimo_codigo = obtener_ultimo_codigo("cotizacion","idcotizacion")
        nuevo_codigo = generar_nuevo_codigo(ultimo_codigo)
        self.txtCodigo.setText(nuevo_codigo)
        
    # Coloca el id de cotizacion en su txt actulizado para el proximo registro
    def actualizar_num_cotizacion(self):
        ultimo_codigo = obtener_codigo_cotizacion("cotizacion")
        nuevo_codigo = generar_nuevo_codigo_cotizacion("COT", ultimo_codigo)
        self.txtSerie.setText(nuevo_codigo)

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------        
    # Oculta los bototnes de los detalles para obligar al usuario a que coloque la cotizacion antes que los detalles
    
    # Oculta los botones cuando la ventana de cotizacion carga
    def ocultar_botones_detalle(self):
        if not self.se_llamo_activar_botones:
            for widget in self.groupBox_2.findChildren(QWidget):
                widget.setVisible(False)
            self.se_llamo_activar_botones = False
        return self.se_llamo_activar_botones
    
    # Activa los botones cuando se inserta la cotizacion en el boton 'Registrar'.
    def activar_botones_detalle(self):
        if not self.se_llamo_activar_botones:
            for widget in self.groupBox_2.findChildren(QWidget):
                widget.setVisible(True)
            self.se_llamo_activar_botones = True
        return self.se_llamo_activar_botones
    
    # Oculta los botones cuando se eliminan todos los detalles de la cotizacion y esta queda anulada.
    def ocultar_botones_detalle_al_anular_cotizacion(self):
        if self.se_llamo_activar_botones:
            for widget in self.groupBox_2.findChildren(QWidget):
                widget.setVisible(False)
            self.se_llamo_activar_botones = False
        return self.se_llamo_activar_botones       
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    def desactivar_botones_cotizacion(self):
        self.txtCodigo.setEnabled(False)
        self.cmbComprobante.setEnabled(False)
        self.txtIdCliente.setEnabled(False)
        self.cmbCliente.setEnabled(False)
        self.txtSerie.setEnabled(False)
        self.txtFecha.setEnabled(False)
        self.txtItbis.setEnabled(False)
        self.btnRegistrar.setEnabled(False)
        self.txtComentario.setEnabled(False)

    def activar_botones_cotizacion(self):
        self.txtCodigo.setEnabled(True)
        self.cmbComprobante.setEnabled(True)
        self.txtIdCliente.setEnabled(True)
        self.cmbCliente.setEnabled(True)
        self.txtSerie.setEnabled(True)
        self.txtFecha.setEnabled(True)
        self.txtItbis.setEnabled(True)
        self.btnRegistrar.setEnabled(True)
        self.txtComentario.setEnabled(True)

        self.cmbCliente.clear()
        self.txtIdCliente.setText("")
        self.txtSerie.setText("")
        self.txtItbis.setText("")
        self.txtComentario.setPlainText("")
        self.txtFecha.setDate(QDate.currentDate())
        
    

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    def convertir_cotizacion(self):
        
        if self.se_llamo_activar_botones:
            QMessageBox.warning(self, "ERROR", "TIENE UNA COTIZACION ABIERTA, FAVOR TERMINAR DE INGRESAR LOS ARTICULOS.")
            
        else:
            # Obtener el índice de la fila seleccionada
            indexes = self.tbDatos.selectedIndexes()
            
            if indexes:
                
                # Obtener el numero (int) de la fila al seleccionar una celda de la tabla detalle_cotizacion
                index = indexes[0]
                row = index.row()
                
                self.obtener_id_fila_cotizacion(row)
                id_cotizacion = self.bd_id_cotizacion
                
                if not self.verificar_cantidad_cotizacion_stock():
                    #QMessageBox.warning(self, "ERROR", "La cantidad en la cotización supera la cantidad en stock.")
                    return
                
                # Preguntar si el usuario está seguro de convertir la cotizacion seleccionada
                confirmacion = QMessageBox.question(self, "CONVERITR?", "¿QUIERE CONVERTIR ESTA COTIZACION A FACTURA?",
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                
                
                # Si el usuario hace clic en el botón "Sí", convierte la cotizacion en factura
                if confirmacion == QMessageBox.Yes:
                    convertir_cot_a_factura(id_cotizacion)
                    QMessageBox.warning(self, "FACTURADO", "COTIZACION CONVERTIDA A FACTURA.")
                    
            else:
                QMessageBox.warning(self, "ERROR", "SELECCIONA LA COTIZACION A CONVERTIR.")
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------        
    def imprimir_pdf(self):
        # Verifica si se ha terminado de ingresar los articulos para proceder a crear el pdf
        if self.se_llamo_activar_botones:
            QMessageBox.warning(self, "ERROR", "TIENE UNA COTIZACION ABIERTA, FAVOR TERMINAR DE INGRESAR LOS ARTICULOS.")
            
        else:
            # Obtener el índice de la fila seleccionada
            indexes = self.tbDatos.selectedIndexes()

            # Obtiene la fecha actual para usar en el pdf
            fecha = QDate.currentDate()
            fecha_formato = fecha.toString("dd-MMMM-yyyy")
            
            if indexes:
                try:    
                    # Obtener el numero (int) de la fila al seleccionar una celda de la tabla detalle_cotizacion
                    index = indexes[0]
                    row = index.row()
                    
                    # Con el parametro row como int se obtienen todos los datos de la fila seleccionada, datos 
                    # que seran usados para la creacion del pdf.
                    self.obtener_id_fila_cotizacion(row) 
                    
                    
                    # Preguntar si el usuario está seguro de convertir la cotizacion seleccionada
                    confirmacion = QMessageBox.question(self, "MENSAJE", "¿ESTA SEGURO QUE QUIERE CONTINUAR?",
                                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        
                        
                    # Si el usuario hace clic en el botón "Sí", convierte la cotizacion en pdf
                    if confirmacion == QMessageBox.Yes:
                        
                        c = canvas.Canvas(f"Sistema_de_ventas/pdf/Cotizaciones/Cotizacion {self.bd_serie}.pdf", pagesize=letter)

                        # Agregar el logo de la empresa
                        c.drawImage("Sistema_de_ventas/imagenes/Logo.jpg", 400, 700, width=150, height=75)

                        # Datos de la empresa
                        data = [
                            ["Ferremar"],
                            ["Ave. Ind. km 12 1/2 # 23."],
                            ["809-534-2323"]
                        ]

                        table = Table(data)

                        # Establecer el estilo de la tabla para datos de la empresa
                        style = TableStyle([
                            ('BACKGROUND', (0,0), (-1,-1), colors.lightgrey),
                            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),

                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                            ('FONTSIZE', (0,0), (-1,-1), 12),

                            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                            ('GRID', (0,0), (-1,-1), 1, colors.black)
                        ])
                        table.setStyle(style)

                        # Agregar la tabla de datos de la empresa al canvas
                        table.wrapOn(c, 50, 750)
                        table.drawOn(c, 50, 700)

                        # No. Cotización y fecha
                        c.setFont("Helvetica-Bold", 15)
                        c.drawString(390,680,"Cotización: " + str(self.bd_serie))
                        c.setFont("Helvetica", 10)
                        c.drawString(390,660,"Fecha Cot.: " + f"{self.bd_fecha}")

                        # Datos del cliente
                        c.setFont("Helvetica-Bold", 15)
                        c.drawString(50,680,"Cliente: " + str(self.bd_cliente))
                        c.setFont("Helvetica", 10)
                        c.drawString(50,660,"Fecha de impresion: " + str(fecha_formato))
                        
                        # Dibujar una línea debajo de los datos de la empresa y logo.
                        c.line(50, 695, 550, 695)

                        # Dibujar una línea debajo de los datos del cliente
                        c.line(50, 650, 550, 650)
                        
                        # Cabecera de los datos de los artículos
                        c.setFont("Helvetica-Bold", 12)
                        #c.drawString(50, 630, "ID")
                        c.drawString(50, 630, "CODIGO")
                        c.drawString(120, 630, "CANT.") 
                        c.drawString(170, 630, "ARTICULO")                 
                        c.drawString(340, 630, "PRECIO")
                        c.drawString(410, 630, "VENTA POR")
                        c.drawString(495, 630, "TOTAL")

                        # Datos de los artículos.
                        detalles = self.obtener_detalles_cotizacion(self.bd_id_cotizacion)
                        y = 610
                        for detalle in detalles:
                            c.setFont("Helvetica", 10)
                            #c.drawString(50, y, str(detalle['idarticulo']))
                            c.drawString(50, y, self.obtener_codigo_articulo(detalle['idarticulo']))
                            c.drawString(120, y, str(detalle['cantidad']))

                            # Guardar la posición "y" (up/down) antes de dibujar el nombre del artículo
                            # esta posicion la uso para que si el nombre del articulo tiene varias lineas
                            # las demas columnas queden alineadas con la primera linea del nombre de articulo.
                            alinear_columnas = y

                            # Obtener el nombre del artículo y dividirlo en varias líneas si es demasiado largo
                            nombre_articulo = self.obtener_nombre_articulo(detalle['idarticulo']) # obtengo el nombre del articulo en la variable nombre_articulo
                            lineas_nombre_articulo = textwrap.wrap(nombre_articulo, width=30)  # Ajusta el ancho a un espacio de 30 caracteres.

                            # Revisa cada nombre de articulo si alguno pasa de 30 caracteres crea un salto de linea.
                            for linea in lineas_nombre_articulo:
                                c.drawString(170, y, linea)
                                y -= 15
                                
                            c.drawString(340, alinear_columnas, "$" + "{:,.2f}".format(detalle['precio_venta']))
                            c.drawString(410, alinear_columnas, self.obtener_presentacion_articulo(self.obtener_codigo_articulo(detalle['idarticulo'])))
                            c.drawString(495, alinear_columnas, "$" + "{:,.2f}".format(detalle['cantidad'] * detalle['precio_venta']))
                            y -= 15

                            # Si los articulos llegan a la línea 40, se crea una nueva página
                            # para seguir imprimiendo en ella
                            if y <= 30:
                                c.showPage()
                                y = 750  # Posición inicial en "y" (up/down) de la nueva pagina creada.

                        # Totales, subtotales, impuestos, etc.
                        c.setFont("Helvetica-Bold", 16)
                        c.drawString(50,120,"Subtotal: " + str(self.bd_sub_total))
                        c.drawString(50,100,"Impuesto: " + str(int(self.bd_impuesto)) + "%")
                        c.drawString(50,80,"Descuento: " + str(int(self.bd_descuento)) + "%")
                        c.drawString(50,60,"Total: " + str(self.bd_total))

                        # Nombre del empleado que crea la cotizacion
                        c.setFont("Helvetica", 10)
                        c.drawString(50,40,"Le atendió: " + str(self.obtener_nombre_empleado(self.bd_id_cotizacion)).title())

                        # Comentario de la cotizacion al pie de la hoja
                        c.setFont("Helvetica", 10)
                        c.drawString(50, 20,"Comentario: " + "**" + str(self.bd_comentario).capitalize() + "**") 

                        c.save()

                        # Ruta completa del archivo PDF para ser usada para imprimir el pdf creado.
                        pdf_file_name = os.path.abspath(f"Sistema_de_ventas/pdf/Cotizaciones/Cotizacion {self.bd_serie}.pdf")

                        # Abrir el cuadro de diálogo de impresión de Windows, open crea y abre el pdf, print
                        # imprime el archivo por la impresora predeterminada.
                        
                        win32api.ShellExecute(0, "open", pdf_file_name, None, ".", 0) # type: ignore
                        
                        #win32api.ShellExecute(0, "print", pdf_file_name, None, ".", 0) # type: ignore

                        QMessageBox.warning(self, "MENSAJE", "HECHO SATISCAFTORIAMENTE")
                except Exception as e:
                    # Manejar otros errores, mostrar un mensaje de error o realizar otra acción necesaria
                    mensaje_error = QMessageBox()
                    mensaje_error.setIcon(QMessageBox.Critical)
                    mensaje_error.setWindowTitle("Llamar al administrador")
                    mensaje_error.setText(f"Error al intentar imprimir: {str(e)}")
                    mensaje_error.exec_()
            else:
                QMessageBox.warning(self, "ERROR", "SELECCIONA LA COTIZACION PARA CONTINUAR.")


    # Obtiene datos importante de la tabla detalle_cotizacion para imprimirlos en el pdf de la cotizacion    
    def obtener_detalles_cotizacion(self, id_cotizacion):
        query = QSqlQuery()
        query.prepare("SELECT * FROM detalle_cotizacion WHERE idcotizacion = :idcotizacion")
        query.bindValue(":idcotizacion", id_cotizacion)
        query.exec_()

        detalles = []
        while query.next():
            detalles.append({
                    'idarticulo': query.value('idarticulo'),
                    #'comentario': query.value('comentario'),
                    'cantidad': query.value('cantidad'),
                    'precio_venta': query.value('precio_venta'),
                    'descuento': query.value('descuento')
                })

        return detalles

    # Obtiene el nombre del articulo mediante el idarticulo insertado en la tabla detalle_cotizacion
    # para imprimirlo en el pdf de la cotizacion.
    def obtener_nombre_articulo(self, id_articulo):
        query = QSqlQuery()
        query.prepare("SELECT nombre FROM articulo WHERE idarticulo = :idarticulo")
        query.bindValue(":idarticulo", id_articulo)
        query.exec_()

        if query.next():
            return query.value('nombre')

        return ""
        
    # Obtiene la descripcion de la tabla presentacion mediante el codigo del articulo (no idarticulo) que esta en la tabla cotizacion
    # primero obtengo el codigo del articulo mediante la funcion obtener_codigo_articulo() para luego sacar la presentacion del mismo.
    def obtener_presentacion_articulo(self, codigo_articulo):
        query = QSqlQuery()
        query.prepare("DECLARE @idpresentacion INT "
                        "SELECT @idpresentacion = idpresentacion FROM articulo WHERE codigo = :codigo "
                        "SELECT descripcion FROM presentacion WHERE idpresentacion = @idpresentacion")
        query.bindValue(":codigo", codigo_articulo)
        query.exec_()

        if query.next():
            return query.value('descripcion')

        return ""

    # obtener el codigo del articulo (no idarticulo) para imprimirlo en los de talle del articulos del pdf
    # y tambien se usa este codigo para obtener la descripcion de la presentacion para imprimirla en el pdf. 
    def obtener_codigo_articulo(self, id_articulo):
        query = QSqlQuery()
        query.prepare("SELECT codigo FROM articulo WHERE idarticulo = :idarticulo")
        query.bindValue(":idarticulo", id_articulo)
        query.exec_()

        if query.next():
            return query.value('codigo')

        return ""
    
    # obtiene el nombre y apellido del empleado que creo la cotizacion mediante el
    # idcotizacion sabemos el idempleado que luego utilizamos para tener el nombre completo
    def obtener_nombre_empleado(self, id_cotizacion):
        query = QSqlQuery()
        query.prepare("SELECT CONCAT(e.nombre, ' ', e.apellidos) "
                      "FROM empleado e "
                      "INNER JOIN cotizacion c ON e.idempleado = c.idempleado "
                      "WHERE c.idcotizacion = :idcotizacion")
        query.bindValue(":idcotizacion", id_cotizacion)
        query.exec_()

        if query.next():
            return query.value(0)

        return ""
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    def imprimir_impresora(self):      
        # Verifica si se ha terminado de ingresar los articulos para proceder a imprimir.
        if self.se_llamo_activar_botones:
            QMessageBox.warning(self, "ERROR", "TIENE UNA COTIZACION ABIERTA, FAVOR TERMINAR DE INGRESAR LOS ARTICULOS.")
            
        else:
            # Obtener el índice de la fila seleccionada
            indexes = self.tbDatos.selectedIndexes()

            # Obtiene la fecha actual para imprimirlas
            fecha = QDate.currentDate()
            fecha_formato = fecha.toString("dd-MMMM-yyyy")           
            
            if indexes:
                try:
                    # Obtener el numero (int) de la fila al seleccionar una celda de la tabla detalle_cotizacion
                    index = indexes[0]
                    row = index.row()
                    
                    # Con el parametro row como int se obtienen todos los datos de la fila seleccionada, datos 
                    # que seran usados al imprimir.
                    self.obtener_id_fila_cotizacion(row) 
                    
                    
                    # Preguntar si el usuario está seguro de convertir la cotizacion seleccionada
                    confirmacion = QMessageBox.question(self, "MENSAJE", "¿ESTA SEGURO QUE QUIERE CONTINUAR?",
                                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                        
                        
                    # Si el usuario hace clic en el botón "Sí", imprime la cotizacion
                    if confirmacion == QMessageBox.Yes:
                        
                        # Crear objeto QPrinter y configurar opciones de impresión
                        printer = QPrinter(QPrinter.HighResolution)
                        printer.setPageSize(QPrinter.A4)
                        printer.setOutputFormat(QPrinter.NativeFormat)
                        
                        # Muestra el diálogo de impresión y obtiene las configuraciones de usuario
                        dialog = QPrintDialog(printer, self)
                        if dialog.exec_() == QDialog.Accepted:
                            
                            # Crea un objeto QPainter y establece el objeto QPrinter como el dispositivo de pintura
                            painter = QPainter()
                            painter.begin(printer)

                            # Fuente para los titulos principales
                            fuente_titulos = QFont()
                            fuente_titulos.setPointSize(13)
                            fuente_titulos.setBold(True)                           
                            
                            # Fuente para los contenido debajo de los titulos
                            fuente_articulos = QFont()
                            fuente_articulos.setPointSize(11)
                            
                            # Fuente para el comentario y empleado
                            fuente_empl_coment = QFont()
                            fuente_empl_coment.setPointSize(10)
                            
                            # Fuente para las fechas de cabecera
                            fuente_fechas = QFont()
                            fuente_fechas.setPointSize(11)

                            # Datos de la empresa
                            data = [
                                ["Ferremar"],
                                ["Ave. Ind. km 12 1/2 # 23."],
                                ["809-534-2323"]
                            ]

                            # Dibuja los datos de la empresa
                            for i, row in enumerate(data):
                                painter.setFont(fuente_titulos)
                                painter.drawText(300, 300 + i * 250, row[0])

                            # Carga la imagen del logo
                            logo_image = QImage("Sistema_de_ventas/imagenes/Logo.jpg")

                            # Redimensiona el tamaño de la imagen del logo al deseado
                            logo_image = logo_image.scaled(1500, 750)

                            # Dibuja y posiciona el logo en la página
                            painter.drawImage(3175, 200, logo_image)
                            
                            
                            # Cabecera de los datos de los artículos
                            painter.setFont(fuente_titulos)
                            painter.drawText(300, 1500, "CODIGO")
                            painter.drawText(900, 1500, "CANT.") 
                            painter.drawText(1300, 1500, "ARTICULO")                 
                            painter.drawText(2700, 1500, "PRECIO")
                            painter.drawText(3400, 1500, "VENTA POR")
                            painter.drawText(4200, 1500, "TOTAL")
                            
                            # Dibujar una línea debajo de los datos de la empresa.
                            painter.drawLine(300, 1000, 4700, 1000)
                            
                            # Dibujar una línea debajo de los datos del cliente y num cotizacion.
                            painter.drawLine(300, 1350, 4700, 1350)

                            # Datos del cliente
                            painter.setFont(fuente_titulos)
                            painter.drawText(300,1150,"Cliente: " + str(self.bd_cliente))
                            painter.setFont(fuente_fechas)
                            painter.drawText(300,1300,"Fecha de impresion: " + str(fecha_formato))

                            # No. Cotización y fecha
                            painter.setFont(fuente_titulos)
                            painter.drawText(3300,1150,"Cotización: " + str(self.bd_serie))
                            painter.setFont(fuente_fechas)
                            painter.drawText(3300,1300,"Fecha Cot.: " + f"{self.bd_fecha}")

                            # Datos de los artículos.
                            detalles = self.obtener_detalles_cotizacion(self.bd_id_cotizacion)
                            y = 1700
                            for detalle in detalles:
                                painter.setFont(fuente_articulos)
                                painter.drawText(300, y, self.obtener_codigo_articulo(detalle['idarticulo']))
                                painter.drawText(900, y, str(detalle['cantidad']))
                                

                                # Guardar la posición "y" (up/down) antes de dibujar el nombre del artículo
                                # esta posicion la uso para que si el nombre del articulo tiene varias lineas
                                # las demas columnas queden alineadas con la primera linea del nombre de articulo.
                                alinear_columnas = y

                                # Obtener el nombre del artículo y dividirlo en varias líneas si es demasiado largo
                                nombre_articulo = self.obtener_nombre_articulo(detalle['idarticulo']) # obtengo el nombre del articulo en la variable nombre_articulo
                                lineas_nombre_articulo = textwrap.wrap(nombre_articulo, width=30)  # Ajusta el ancho a un espacio de 30 caracteres.

                                # Revisa cada nombre de articulo si alguno pasa de 30 caracteres crea un salto de linea.
                                for linea in lineas_nombre_articulo:
                                    painter.drawText(1300, y, linea)
                                    y += 100
                                    
                                painter.drawText(2700, alinear_columnas, "$" + "{:,.2f}".format(detalle['precio_venta']))
                                painter.drawText(3400, alinear_columnas, self.obtener_presentacion_articulo(self.obtener_codigo_articulo(detalle['idarticulo'])))
                                painter.drawText(4200, alinear_columnas, "$" + "{:,.2f}".format(detalle['cantidad'] * detalle['precio_venta']))
                                y += 100
                                
                                # Si los articulos llegan a la línea 6100, se crea una nueva página
                                # para seguir imprimiendo en ella
                                if y >= 6100:
                                    printer.newPage()
                                    y = 400  # Posición inicial en "y" (up/down) de la nueva pagina creada.
                                    
                                    

                            # Dibujar los datos de la cotización
                            painter.setFont(fuente_titulos)
                            painter.drawText(300, 5650, "Subtotal: " + str(self.bd_sub_total))
                            painter.drawText(300, 5800, "Impuesto: " + str(int(self.bd_impuesto)) + "%")
                            painter.drawText(300, 5950, "Descuento: " + str(int(self.bd_descuento)) + "%")
                            painter.drawText(300, 6100, "Total: " + str(self.bd_total))

                            
                            # Dibujar el nombre del empleado
                            painter.setFont(fuente_empl_coment)
                            painter.drawText(300, 6250, "Le atendió: " + str(self.obtener_nombre_empleado(self.bd_id_cotizacion)).title())
                            # Dibujar el comentario de la cotización
                            painter.drawText(300, 6400, "Comentario: " + "**" + str(self.bd_comentario).capitalize() + "**")                           

                            # Finaliza la pintura y cierra el objeto QPainter
                            painter.end()

                        QMessageBox.warning(self, "MENSAJE", "HECHO SATISCAFTORIAMENTE")
                except Exception as e:
                    # Manejar otros errores, mostrar un mensaje de error o realizar otra acción necesaria
                    mensaje_error = QMessageBox()
                    mensaje_error.setIcon(QMessageBox.Critical)
                    mensaje_error.setWindowTitle("Llamar al administrador")
                    mensaje_error.setText(f"Error al intentar imprimir: {str(e)}")
                    mensaje_error.exec_()
            else:
                QMessageBox.warning(self, "ERROR", "SELECCIONA LA COTIZACION PARA CONTINUAR.")
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    # Verifica que antes de convertir la cotizacion en factura (venta) que  haya stock disponoble de cada uno de los articulos a cotizar
    # Si en la cotizacion a convertir hay uno o varios articulos sin stock le manda un aviso al usuario mostrando dichos articulos.
    def verificar_cantidad_cotizacion_stock(self):
        id_cotizacion = self.bd_id_cotizacion
        query = QSqlQuery()
        query.exec_(f"SELECT dc.idarticulo, SUM(dc.cantidad) AS cantidad, a.nombre AS nombre_articulo \
                    FROM detalle_cotizacion dc \
                    INNER JOIN articulo a ON dc.idarticulo = a.idarticulo \
                    WHERE dc.idcotizacion = {id_cotizacion} GROUP BY dc.idarticulo, a.nombre")

        cantidades_cotizacion = {}
        nombres_articulos_excedentes = ""

        while query.next():
            id_articulo = query.value(0)
            cantidad = query.value(1)
            nombre_articulo = query.value(2)
            cantidades_cotizacion[id_articulo] = (cantidad, nombre_articulo)  # Almacena el nombre del artículo junto con su cantidad

        # Realiza una consulta para obtener las cantidades de stock
        cantidades_stock = {}
        query.exec_("SELECT idarticulo, disponible FROM stock")

        while query.next():
            id_articulo = query.value(0)
            disponible = query.value(1)
            cantidades_stock[id_articulo] = disponible

        # Realiza la comparación de cantidades
        for id_articulo, (cantidad_cotizacion, nombre_articulo) in cantidades_cotizacion.items():  # Desempaqueta la cantidad y el nombre del artículo
            if id_articulo in cantidades_stock:
                cantidad_stock = cantidades_stock[id_articulo]
                if cantidad_cotizacion > cantidad_stock:
                    # Agrega el nombre del artículo a la cadena de excedentes
                    nombres_articulos_excedentes += f"{id_articulo, nombre_articulo}\n"
                
        if nombres_articulos_excedentes:
            mensaje = "Los siguientes artículos exceden la cantidad disponible:\n"
            mensaje += nombres_articulos_excedentes

            mensaje_info = QMessageBox()
            mensaje_info.setIcon(QMessageBox.Information)
            mensaje_info.setWindowTitle("Artículos Excedentes")
            mensaje_info.setText(mensaje)
            mensaje_info.exec_()
            return False
        else:
            # Si todas las comparaciones son exitosas, se puede convertir la cotización
            return True
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------           
    # Pasando como parametro el numero de fila el cual obtengo al seleccionar una celda en el QTableView obtengo datos que necesito
    # estos datos son usado con varios propositos como la impresion de informacion al crear un pdf por ejemplo.
    # los SELECT usados aqui son los mismo que muestran informacion al crear las cotizaciones, son los datos mas relevantes.
    def obtener_id_fila_cotizacion(self, num_fila):
        FechaInicio = self.txtFechaInicio.date().toString("yyyy-MM-dd")
        FechaFinal = self.txtFechaFin.date().toString("yyyy-MM-dd")
        Buscar = self.txtBuscar.text()

        if not Buscar:
            if FechaInicio > FechaFinal:
                QMessageBox.warning(self, "ERROR ENTRE FECHAS", "LA PRIMERA FECHA NO PUEDE SER MAYOR A LA SEGUNDA.")
                                        
                return
            else:
                query = QSqlQuery()
                query.exec_(f"SELECT\
                                    co.idcotizacion as 'ID',\
                                    UPPER(FORMAT(co.fecha, 'dd MMMM yyyy', 'es-ES')) AS 'FECHA',\
                                    CONCAT(cl.nombre, ' ', cl.apellidos) as 'CLIENTE',\
                                    dc.descuento as 'DESCUENTO %',\
                                    co.itbis as 'IMPUESTOS %',\
                                    co.serie as 'NO. COTIZACION',\
                                    em.nombre as 'VENDEDOR',\
                                    FORMAT(SUM(dc.cantidad * dc.precio_venta), 'C', 'en-US') as 'SUB TOTAL',\
                                    FORMAT(SUM((dc.cantidad * dc.precio_venta * (1 - (dc.descuento / 100))) * (1 + (co.itbis / 100))), 'C', 'en-US') as 'TOTAL',\
                                    co.comentario as 'COMENTARIO'\
                                FROM cotizacion co\
                                INNER JOIN cliente cl ON co.idcliente = cl.idcliente\
                                INNER JOIN detalle_cotizacion dc ON co.idcotizacion = dc.idcotizacion\
                                INNER JOIN empleado em ON co.idempleado = em.idempleado\
                                WHERE co.fecha BETWEEN '{FechaInicio}' AND '{FechaFinal}'\
                                GROUP BY co.idcotizacion, co.fecha, CONCAT(cl.nombre, ' ', cl.apellidos),\
                                dc.descuento, co.itbis, co.serie, em.nombre, co.comentario;")
                model = QSqlTableModel()    
                model.setQuery(query)
                self.tbDatos.setModel(model)
                
                # Obtener el modelo de datos del QTableView
                modelo = self.tbDatos.model()
                if modelo is not None and 0 <= num_fila < modelo.rowCount():
                    
                    # Obtener los datos de las columnas de la fila seleccionada
                    self.bd_id_cotizacion = modelo.index(num_fila, 0).data()
                    self.bd_fecha = modelo.index(num_fila, 1).data()
                    self.bd_cliente = modelo.index(num_fila, 2).data()
                    self.bd_descuento = modelo.index(num_fila, 3).data()
                    self.bd_impuesto = modelo.index(num_fila, 4).data()
                    self.bd_serie = modelo.index(num_fila, 5).data()
                    self.bd_sub_total = modelo.index(num_fila, 7).data()
                    self.bd_total = modelo.index(num_fila, 8).data()
                    self.bd_comentario = modelo.index(num_fila, 9).data()

        else:
            if FechaInicio > FechaFinal:
                QMessageBox.warning(self, "ERROR ENTRE FECHAS", "LA PRIMERA FECHA NO PUEDE SER MAYOR A LA SEGUNDA.")
                return
            else:
                query = QSqlQuery()
                query.exec_(f"SELECT\
                                co.idcotizacion as 'ID',\
                                UPPER(FORMAT(co.fecha, 'dd MMMM yyyy', 'es-ES')) AS 'FECHA',\
                                CONCAT(cl.nombre, ' ', cl.apellidos) as 'CLIENTE',\
                                dc.descuento as 'DESCUENTO %',\
                                co.itbis as 'IMPUESTOS %',\
                                co.serie as 'NO. COTIZACION',\
                                em.nombre as 'VENDEDOR',\
                                FORMAT(SUM(dc.cantidad * dc.precio_venta), 'C', 'en-US') as 'SUB TOTAL',\
                                FORMAT(SUM((dc.cantidad * dc.precio_venta * (1 - (dc.descuento / 100))) * (1 + (co.itbis / 100))), 'C', 'en-US') as 'TOTAL',\
                                co.comentario as 'COMENTARIO'\
                            FROM cotizacion co\
                            INNER JOIN cliente cl ON co.idcliente = cl.idcliente\
                            INNER JOIN detalle_cotizacion dc ON co.idcotizacion = dc.idcotizacion\
                            INNER JOIN empleado em ON co.idempleado = em.idempleado\
                            WHERE co.fecha BETWEEN '{FechaInicio}' AND '{FechaFinal}' AND co.serie LIKE '%{Buscar}%'\
                            GROUP BY co.idcotizacion, co.fecha, CONCAT(cl.nombre, ' ', cl.apellidos),\
                            dc.descuento, co.itbis, co.serie, em.nombre, co.comentario;")
                model = QSqlTableModel()    
                model.setQuery(query)
                self.tbDatos.setModel(model)
                
                # Obtener el modelo de datos del QTableView
                modelo = self.tbDatos.model()
                if modelo is not None and 0 <= num_fila < modelo.rowCount():
                    
                    # Obtener los datos de las columnas de la fila seleccionada
                    self.bd_id_cotizacion = modelo.index(num_fila, 0).data()
                    self.bd_fecha = modelo.index(num_fila, 1).data()
                    self.bd_cliente = modelo.index(num_fila, 2).data()
                    self.bd_descuento = modelo.index(num_fila, 3).data()
                    self.bd_impuesto = modelo.index(num_fila, 4).data()
                    self.bd_serie = modelo.index(num_fila, 5).data()
                    self.bd_sub_total = modelo.index(num_fila, 7).data()
                    self.bd_total = modelo.index(num_fila, 8).data()
                    self.bd_comentario = modelo.index(num_fila, 9).data()

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    def visualizar_datos_cotizacion(self):
        FechaInicio = self.txtFechaInicio.date().toString("yyyy-MM-dd")
        FechaFinal = self.txtFechaFin.date().toString("yyyy-MM-dd")
        Buscar = self.txtBuscar.text()

        if not Buscar:
            if FechaInicio > FechaFinal:
                        
                        QMessageBox.warning(self, "ERROR ENTRE FECHAS", "LA PRIMERA FECHA NO PUEDE SER MAYOR A LA SEGUNDA.")
                                        
                        return
            else:
                query = QSqlQuery()
                query.exec_(f"SELECT\
                                    co.idcotizacion as 'ID',\
                                    UPPER(FORMAT(co.fecha, 'dd MMMM yyyy', 'es-ES')) AS 'FECHA',\
                                    CONCAT(cl.nombre, ' ', cl.apellidos) as 'CLIENTE',\
                                    dc.descuento as 'DESCUENTO %',\
                                    co.itbis as 'IMPUESTOS %',\
                                    co.serie as 'NO. COTIZACION',\
                                    CONCAT(em.nombre, ' ', em.apellidos) as 'VENDEDOR',\
                                    FORMAT(SUM(dc.cantidad * dc.precio_venta), 'C', 'en-US') as 'SUB TOTAL',\
                                    FORMAT(SUM((dc.cantidad * dc.precio_venta * (1 - (dc.descuento / 100))) * (1 + (co.itbis / 100))), 'C', 'en-US') as 'TOTAL',\
                                    co.comentario as 'COMENTARIO'\
                                FROM cotizacion co\
                                INNER JOIN cliente cl ON co.idcliente = cl.idcliente\
                                INNER JOIN detalle_cotizacion dc ON co.idcotizacion = dc.idcotizacion\
                                INNER JOIN empleado em ON co.idempleado = em.idempleado\
                                WHERE co.fecha BETWEEN '{FechaInicio}' AND '{FechaFinal}'\
                                GROUP BY co.idcotizacion, co.fecha, CONCAT(cl.nombre, ' ', cl.apellidos),\
                                dc.descuento, co.itbis, co.serie, CONCAT(em.nombre, ' ', em.apellidos), co.comentario;")
                
                # Crear un modelo de tabla SQL ejecuta el query y establecer el modelo en la tabla
                model = QSqlTableModel()    
                model.setQuery(query)        
                self.tbDatos.setModel(model)

                # Ajustar el tamaño de las columnas para que se ajusten al contenido
                self.tbDatos.resizeColumnsToContents()
                self.tbDatos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            if FechaInicio > FechaFinal:
                        
                        QMessageBox.warning(self, "ERROR ENTRE FECHAS", "LA PRIMERA FECHA NO PUEDE SER MAYOR A LA SEGUNDA.")
                                        
                        return
            else:
                query = QSqlQuery()
                query.exec_(f"SELECT\
                                co.idcotizacion as 'ID',\
                                UPPER(FORMAT(co.fecha, 'dd MMMM yyyy', 'es-ES')) AS 'FECHA',\
                                CONCAT(cl.nombre, ' ', cl.apellidos) as 'CLIENTE',\
                                dc.descuento as 'DESCUENTO %',\
                                co.itbis as 'IMPUESTOS %',\
                                co.serie as 'NO. COTIZACION',\
                                CONCAT(em.nombre, ' ', em.apellidos) as 'VENDEDOR',\
                                FORMAT(SUM(dc.cantidad * dc.precio_venta), 'C', 'en-US') as 'SUB TOTAL',\
                                FORMAT(SUM((dc.cantidad * dc.precio_venta * (1 - (dc.descuento / 100))) * (1 + (co.itbis / 100))), 'C', 'en-US') as 'TOTAL',\
                                co.comentario as 'COMENTARIO'\
                            FROM cotizacion co\
                            INNER JOIN cliente cl ON co.idcliente = cl.idcliente\
                            INNER JOIN detalle_cotizacion dc ON co.idcotizacion = dc.idcotizacion\
                            INNER JOIN empleado em ON co.idempleado = em.idempleado\
                            WHERE co.fecha BETWEEN '{FechaInicio}' AND '{FechaFinal}' AND co.serie LIKE '%{Buscar}%'\
                            GROUP BY co.idcotizacion, co.fecha, CONCAT(cl.nombre, ' ', cl.apellidos),\
                            dc.descuento, co.itbis, co.serie, CONCAT(em.nombre, ' ', em.apellidos), co.comentario;")
                
                # Crear un modelo de tabla SQL ejecuta el query y establecer el modelo en la tabla
                model = QSqlTableModel()    
                model.setQuery(query)        
                self.tbDatos.setModel(model)
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    def visualizar_datos_detalle_cotizacion(self):
        idcotizacion = self.txtCodigo.text()
        query = QSqlQuery()
        query.exec_(f"SELECT dc.iddetalle_cotizacion as 'ID DETALLE',\
                        dc.idcotizacion as 'ID COTIZACION',\
                        CONCAT(cl.nombre, ' ', cl.apellidos) as 'CLIENTE',\
                        ar.nombre as 'ARTICULO',\
                        FORMAT(dc.precio_venta, 'C', 'en-US') as 'PRECIO',\
                        dc.cantidad as 'CANTIDAD',\
                        dc.descuento as 'DESCUENTO %',\
                        co.itbis as 'IMPUESTOS %',\
                        co.serie as 'NO. COTIZACION',\
                        em.nombre as 'VENDEDOR'\
                    FROM cotizacion co\
                    INNER JOIN cliente cl ON co.idcliente = cl.idcliente\
                    INNER JOIN detalle_cotizacion dc ON co.idcotizacion = dc.idcotizacion\
                    INNER JOIN articulo ar ON dc.idarticulo = ar.idarticulo\
                    INNER JOIN empleado em ON co.idempleado = em.idempleado\
                    WHERE dc.idcotizacion = {idcotizacion};")
        
        # Crear un modelo de tabla SQL ejecuta el query y establecer el modelo en la tabla
        model = QSqlTableModel()    
        model.setQuery(query)        
        self.tbDatos2.setModel(model)

        # Ajustar el tamaño de las columnas para que se ajusten al contenido
        self.tbDatos2.resizeColumnsToContents()
        self.tbDatos2.setEditTriggers(QAbstractItemView.NoEditTriggers)
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    def insertar_datos_cotiacion(self):
        try:
            # llamada de funciones que obtienen el id del ultimo usuario que inicio sesion.
            # Ese dato es usado para saber quien esta registrando datos de ingreso/ventas etc.
            id_ultima_sesion = self.ultima_sesion()
            fila = self.obtener_id_sesion(id_ultima_sesion)
            self.obtener_datos_de_fila(fila)
            id_empleado = self.valor_columna_1


            #Almacena en las variables los valores insertados en los controles inputs txt y cmb.
            idempleado = id_empleado
            idcliente = self.txtIdCliente.text()
            fecha = self.txtFecha.date().toString("yyyy-MM-dd")
            tipo_comprobante = self.cmbComprobante.currentText()            
            num_comprobante = self.txtSerie.text()
            itbis = self.txtItbis.text()
            comentario = self.txtComentario.toPlainText().upper()

            if not itbis:                
                itbis = 0
            
            if not all([idempleado, idcliente, idempleado, fecha, tipo_comprobante, num_comprobante]):
        
                mensaje = QMessageBox()
                mensaje.setIcon(QMessageBox.Critical)
                mensaje.setWindowTitle("Hay un error en los datos")
                mensaje.setText("Por favor, complete todos los campos correctamente.")
                mensaje.exec_()
                
                
            else:           

                # Preguntar si el usuario está seguro de empezar a insertar los datos.
                confirmacion = QMessageBox.question(self, "INSERTAR LOS DETALLES", "¿ESTAS SEGURO QUE DESEA CONTINUAR?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            
                # Si el usuario hace clic en el botón "Sí", se activa detalle_ingreso.
                if confirmacion == QMessageBox.Yes:
                    
                    insertar_nueva_cotizacion(idcliente, idempleado, fecha, tipo_comprobante, num_comprobante, itbis, comentario)
                    
                    self.activar_botones_detalle()
                    self.desactivar_botones_cotizacion()


                    # Limpiar componentes antes de empesar a insertar detalles
                    self.cmbArticulo.clear()
                    self.txtCodArticulo.setText("")
                    self.txtCantidad.setText("")
                    self.cmbPrecioVent.clear()
                    self.txtDescuento.setText("")
                    self.txtCantidad.setFocus()

        except Exception as e:
            # Maneja la excepción aquí, puedes mostrar un mensaje de error o hacer lo que necesites.
            mensaje = QMessageBox()
            mensaje.setIcon(QMessageBox.Critical)
            mensaje.setWindowTitle("Error")
            mensaje.setText(f"Se produjo un error en cotizacion: {str(e)}")
            mensaje.exec_()
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    def insertar_detalle_cotizacion(self):
        try:
            idoctizacion = self.txtCodigo.text()
            idarticulo = self.txtCodArticulo.text()
            catidad = self.txtCantidad.text()
            precio_venta = self.cmbPrecioVent.currentText()
            descuento = self.txtDescuento.text()

            if not descuento:                
                descuento = 0

            if not all([idoctizacion, idarticulo, catidad, precio_venta]):
    
                mensaje = QMessageBox()
                mensaje.setIcon(QMessageBox.Critical)
                mensaje.setWindowTitle("Hay un error en los datos")
                mensaje.setText("Por favor, complete todos los campos correctamente.")
                mensaje.exec_()
            
            
            else:
                insertar_nuevo_detalle_cotizacion(idoctizacion, idarticulo, catidad, precio_venta, descuento)

                self.visualizar_datos_cotizacion()
                self.visualizar_datos_detalle_cotizacion()
                
                self.obtener_id_fila_cotizacion(idoctizacion)
                self.lblDescuento.setText(self.bd_descuento)
                self.lblTotal.setText(self.bd_total)
                
                # Limpia los TexBox
                self.txtCantidad.setText("")
                self.txtCantidad.setFocus()
        except Exception as e:
            # Maneja la excepción aquí, puedes mostrar un mensaje de error o hacer lo que necesites.
            mensaje = QMessageBox()
            mensaje.setIcon(QMessageBox.Critical)
            mensaje.setWindowTitle("Error")
            mensaje.setText(f"Se produjo un error en detalle: {str(e)}")
            mensaje.exec_()
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    def quitar_datos_detalle_cotizacion(self):
        # Obtener el índice de la fila seleccionada
        indexes = self.tbDatos2.selectedIndexes()
        
        if indexes:
            
            # Obtener el numero (int) de la fila al seleccionar una celda de la tabla detalle_cotizacion
            index = indexes[0]
            row = index.row()
            
            self.obtener_datos_de_fila_detalle_cotizacion(row)
            id_detalle_cotizacion = self.bd_id_detalle_cotizacion
            
            
            
            # Preguntar si el usuario está seguro de inhabilitar el ingreso de la fila seleccionada
            confirmacion = QMessageBox.question(self, "ELIMINAR?", "¿QUIERE ELIMINAR ESTE ARTICULO DE LA LISTA?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            
            # Si el usuario hace clic en el botón "Sí", elimina el detalle
            if confirmacion == QMessageBox.Yes:
                quitar_detalle_cotizacion(id_detalle_cotizacion)
                QMessageBox.warning(self, "ELIMINADO", "ARTICULO ELIMINADO.")
                self.visualizar_datos_detalle_cotizacion()
                self.visualizar_datos_cotizacion()
                self.verificar_y_ocultar_botones()
        else:
            QMessageBox.warning(self, "ERROR", "SELECCIONA EL ARTICULO QUE VAS A ELIMINAR.")
            
        # Pasando como parametro el numero de fila, obtengo el id de la cotizacion.
    def obtener_datos_de_fila_detalle_cotizacion(self, num_fila):
        idcotizacion = self.txtCodigo.text()
        query = QSqlQuery()
        query.exec_(f"SELECT dc.iddetalle_cotizacion as 'ID DETALLE',\
                        dc.idcotizacion as 'ID COTIZACION',\
                        CONCAT(cl.nombre, ' ', cl.apellidos) as 'CLIENTE',\
                        ar.nombre as 'ARTICULO',\
                        FORMAT(dc.precio_venta, 'C', 'en-US') as 'PRECIO',\
                        dc.cantidad as 'CANTIDAD',\
                        dc.descuento as 'DESCUENTO %',\
                        co.itbis as 'IMPUESTOS %',\
                        co.serie as 'NO. COTIZACION',\
                        em.nombre as 'VENDEDOR'\
                    FROM cotizacion co\
                    INNER JOIN cliente cl ON co.idcliente = cl.idcliente\
                    INNER JOIN detalle_cotizacion dc ON co.idcotizacion = dc.idcotizacion\
                    INNER JOIN articulo ar ON dc.idarticulo = ar.idarticulo\
                    INNER JOIN empleado em ON co.idempleado = em.idempleado\
                    WHERE dc.idcotizacion = {idcotizacion};")
        model = QSqlTableModel()    
        model.setQuery(query)
        self.tbDatos2.setModel(model)
        
        # Obtener el modelo de datos del QTableView
        modelo = self.tbDatos2.model()
        if modelo is not None and 0 <= num_fila < modelo.rowCount():
            
            # Obtener los datos de la fila seleccionada
            columna_id = modelo.index(num_fila, 0).data()
            
            self.bd_id_detalle_cotizacion = columna_id
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    # si se elimina el ultimo detalle_cotizacion se inhabilitan los botones de insertar detalles
    def verificar_y_ocultar_botones(self):
        idcotizacion = self.txtCodigo.text()
        
        query = QSqlQuery()
        query.prepare(f"SELECT comentario from cotizacion where idcotizacion = :idcotizacion")
        query.bindValue(":idcotizacion", idcotizacion)
        
        if query.exec_() and query.next():
            comentario = query.value(0)
        
            if comentario == "COTIZACION ANULADA":
                mensaje = QMessageBox()
                mensaje.setIcon(QMessageBox.Critical)
                mensaje.setWindowTitle("SE ELIMINARON TODOS LOS ARTICULOS")
                mensaje.setText("INGRESO DE ARTICULOS FINALIZADO, SE BLOQUEARAN LAS FUNICONES.")
                mensaje.exec_()
                self.ocultar_botones_detalle_al_anular_cotizacion()  # Llama a la función para ocultar botones.
                self.actualizar_ID_cotizacion() # Actualiza el idcotizacion por si el usuario quiere volver a insertar detalles
                self.activar_botones_cotizacion() # Activo los botones para insertar cotizacion nueva.
                self.actualizar_num_cotizacion() # Actualiza el codigo de cotizacion por si el usuario quiere volver a insertar detalles
                
                # Refrescar los datos de las cotizaciones y los de detalle_cotizacion.
                self.visualizar_datos_cotizacion()
                self.visualizar_datos_detalle_cotizacion()
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    # Estas 3 funciones obtienen el id de empleado que inicio sesion.
    # Este id de empleado se usa para saber quien ingreso dato a la base de datos
    
    # Obtengo el id del ultimo inicio de sesion, lo usao para buscar el id del usuario que inició.
    def ultima_sesion(self):
        query = QSqlQuery()
        query.exec_(f"SELECT max(idsesion) FROM sesiones")
        
        # Almacena en una variable el resultado del select que es de tipo int
        resultado = 0
        if query.next():
            resultado = query.value(0)
        
        # Crear un modelo de tabla SQL ejecuta el query y establecer el modelo en la tabla
        model = QSqlTableModel()    
        model.setQuery(query)
        self.tbSesiones.setModel(model)

        # Ajustar el tamaño de las columnas para que se ajusten al contenido
        self.tbSesiones.resizeColumnsToContents()    
        
        return resultado
        
    # Pasando como parametro el numero de fila, obtengo el id del empleado
    def obtener_datos_de_fila(self, fila_id):
        query = QSqlQuery()
        query.exec_(f"SELECT * FROM sesiones")
        model = QSqlTableModel()    
        model.setQuery(query)
        self.tbSesiones.setModel(model)
        
        # Obtener el modelo de datos del QTableView
        modelo = self.tbSesiones.model()
        if modelo is not None and 0 <= fila_id < modelo.rowCount():
            
            # Obtener los datos de la fila seleccionada
            columna_1 = modelo.index(fila_id, 1).data()
            
            self.valor_columna_1 = columna_1
            
    # obtengo el numero de fila correspondiente a la sesion, el numero de la fila es igual al idsesion        
    def obtener_id_sesion(self, idsesion):
        model = QSqlTableModel()
        model.setTable('sesiones')
        model.select()
        
            
        # Encuentra el índice de la columna "idsesion"
        idsesion_column_index = model.fieldIndex("idsesion")
        
        # Itera a través de las filas para encontrar el idsesion
        for row in range(model.rowCount()):
            
            index = model.index(row, idsesion_column_index)
            if model.data(index) == idsesion:
                # Si se encuentra el idsesion, devuelve el número de fila
                return row
    
        # Si no se encuentra el idsesion, devuelve -1.
        return -1
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

    # Cargar los precios de venta de los articulos en cmbPrecioVent
    def cargar_precios_venta(self):
        idarticulo = self.txtCodArticulo.text()
        
        query = QSqlQuery()
        query.prepare(f"SELECT top 1 precio_venta, precio_venta1, precio_venta2 from detalle_ingreso where idarticulo = {idarticulo} ORDER BY iddetalle_ingreso DESC")
        query.bindValue(":idarticulo", int(idarticulo))
        
        
        
        if query.exec_():
            self.cmbPrecioVent.clear()
            while query.next():
                precio = query.value(0)
                precio1 = query.value(1)
                precio2 = query.value(2)
                self.cmbPrecioVent.addItem(str(precio))
                self.cmbPrecioVent.addItem(str(precio1))
                self.cmbPrecioVent.addItem(str(precio2))
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------         
    # Actualiza el stock disponible del articulo seleccionado
    def actualizar_existencia_producto(self):
        idarticulo = self.txtCodArticulo.text()
        model = QSqlTableModel()
        model.setTable('stock')
        model.setFilter(f"idarticulo='{idarticulo}'")
        model.select()

        stock_disponible = ""
        if model.rowCount() > 0:
            stock_disponible = model.data(model.index(0, 2))

            self.txtStock.setText(str(stock_disponible)) 
        else:
            self.txtStock.setText("0")
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------        
    def closeEvent(self, event):        
        # Verifica si se ha terminado de ingresar los articulos para cerrar la ventana.
        #if self.se_llamo_activar_botones:
            #QMessageBox.warning(self, "ERROR", "TIENE UNA COTIZACION ABIERTA, FAVOR TERMINAR DE INGRESAR LOS ARTICULOS.")
            
        #else:
        
            # Preguntar si el usuario está seguro de cerrar la ventana
            confirmacion = QMessageBox.question(self, "¿ESTAS SEGURO QUE DESEA SALIR?", "Cotinue solo ha terminado de insertar todos los ariculos",
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                
                                                                    
            # Si el usuario hace clic en el botón "Sí", cierra la ventana
            if confirmacion == QMessageBox.No:
                event.ignore()
            else:
                VentanaCotizaciones.ventana_abierta = False  # Cuando se cierra la ventana, se establece en False
                event.accept()
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    # Elimina el textp de referencia que tiene la casilla buscar
    def borrarTexto(self, event):
        # Borrar el texto cuando se hace clic
        self.txtBuscar.clear()
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
    def showEvent(self, event):
        super().showEvent(event)

        self.tbSesiones.hide()
        self.visualizar_datos_cotizacion()
        self.actualizar_ID_cotizacion()
        self.actualizar_num_cotizacion()
        self.ocultar_botones_detalle()

        
if __name__ == '__main__':
    app = QApplication(sys.argv)       
    GUI = VentanaCotizaciones()
    GUI.show()
    sys.exit(app.exec_())