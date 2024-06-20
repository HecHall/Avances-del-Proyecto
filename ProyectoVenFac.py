from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Table
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import sessionmaker
from reportlab.lib.pagesizes import letter
from sqlalchemy import create_engine
from reportlab.pdfgen import canvas
from sqlalchemy.sql import select
from tkinter import messagebox
from datetime import datetime
from sqlalchemy import or_
import tkinter as tk
import sqlalchemy
import getpass
import hashlib
import sys
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Define el motor de la base de datos
engine = create_engine('sqlite:///ProyectoVenFac.db')
Base = declarative_base()

class Producto(Base):
    __tablename__ = 'Productos'
    ProductoID = Column(Integer, primary_key=True)
    Nombre = Column(String)
    Descripcion = Column(String)
    Precio = Column(Float)
    Cantidad_en_inventario = Column(Integer)
    ProveedorID = Column(Integer, ForeignKey('Proveedores.ProveedorID'))
    ImpuestoID = Column(Integer, ForeignKey('Impuestos.ImpuestoID'))
    DescuentoID = Column(Integer, ForeignKey('Descuentos.DescuentoID'))

class Venta(Base):
    __tablename__ = 'Ventas'
    VentaID = Column(Integer, primary_key=True)
    Fecha = Column(Date, default=datetime.now().date())
    Total = Column(Float)
    EmpleadoID = Column(Integer, ForeignKey('Empleados.EmpleadoID'))
    TiendaID = Column(Integer, ForeignKey('Tiendas.TiendaID'))

    @classmethod
    def agregar_venta(cls, session, fecha, total, empleado_id, tienda_id):
        nueva_venta = cls(Fecha=fecha, Total=total, EmpleadoID=empleado_id, TiendaID=tienda_id)
        session.add(nueva_venta)
        session.commit()
        return nueva_venta.VentaID

class DetalleVenta(Base):
    __tablename__ = 'DetalleVenta'
    DetalleVentaID = Column(Integer, primary_key=True)
    VentaID = Column(Integer, ForeignKey('Ventas.VentaID'))
    ProductoID = Column(Integer, ForeignKey('Productos.ProductoID'))
    Cantidad = Column(Integer)
    PrecioUnitario = Column(Float)

class Factura(Base):
    __tablename__ = 'Facturas'
    FacturaID = Column(Integer, primary_key=True)
    VentaID = Column(Integer, ForeignKey('Ventas.VentaID'))
    ClienteID = Column(Integer, ForeignKey('Clientes.ClienteID'))
    Fecha = Column(Date, default=datetime.now().date())
    Total = Column(Float)
    ImpuestoID = Column(Integer, ForeignKey('Impuestos.ImpuestoID'))

    @classmethod
    def imprimir_todas_las_facturas(cls, session):
        facturas = session.query(cls).order_by(cls.Fecha).all()
        if facturas:
            print("Facturas existentes:")
            for factura in facturas:
                print(f"ID: {factura.FacturaID}, Fecha: {factura.Fecha}, Total: {factura.Total}")
        else:
            print("No hay facturas existentes en la base de datos.")

class Cliente(Base):
    __tablename__ = 'Clientes'
    ClienteID = Column(Integer, primary_key=True)
    Nombre = Column(String)
    Apellido = Column(String)
    Direccion = Column(String)
    Ciudad = Column(String)
    Telefono = Column(String)
    Correo_electronico = Column(String)

class Empleado(Base):
    __tablename__ = 'Empleados'
    EmpleadoID = Column(Integer, primary_key=True)
    Nombre = Column(String)
    Apellido = Column(String)
    Usuario = Column(String)
    Contrasena = Column(String)
    Nivel_de_acceso = Column(String)
    TiendaID = Column(Integer, ForeignKey('Tiendas.TiendaID'))

class Proveedor(Base):
    __tablename__ = 'Proveedores'
    ProveedorID = Column(Integer, primary_key=True)
    Nombre = Column(String)
    Direccion = Column(String)
    Ciudad = Column(String)
    Telefono = Column(String)
    Correo_electronico = Column(String)

class Tienda(Base):
    __tablename__ = 'Tiendas'
    TiendaID = Column(Integer, primary_key=True)
    Nombre = Column(String)
    Direccion = Column(String)
    Ciudad = Column(String)
    Telefono = Column(String)
    Correo_electronico = Column(String)

class Categoria(Base):
    __tablename__ = 'Categorias'
    CategoriaID = Column(Integer, primary_key=True)
    Nombre = Column(String)
    Descripcion = Column(String)

class Impuesto(Base):
    __tablename__ = 'Impuestos'
    ImpuestoID = Column(Integer, primary_key=True)
    Nombre = Column(String)
    Tasa = Column(Float)

class Descuento(Base):
    __tablename__ = 'Descuentos'
    DescuentoID = Column(Integer, primary_key=True)
    Nombre = Column(String)
    Porcentaje = Column(Float)

# Crea todas las tablas
Base.metadata.create_all(engine)
# Crea una sesión
Session = sessionmaker(bind=engine)
session = Session()

def imprimir_factura(nombre_archivo, fecha_hora_venta, nombre_vendedor, nombre_cliente, apellido_cliente, direccion_cliente, ciudad_cliente, telefono_cliente, correo_cliente, productos_vendidos, total_venta, isv, descuento_aplicado=None):
    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    c.drawString(100, 750, "FACTURA")
    c.drawString(100, 730, f"Fecha y hora de la venta: {fecha_hora_venta}")
    c.drawString(100, 710, f"Nombre del vendedor: {nombre_vendedor}")
    c.drawString(100, 690, f"Cliente: {nombre_cliente} {apellido_cliente}")
    c.drawString(100, 670, f"Dirección: {direccion_cliente}")
    c.drawString(100, 650, f"Ciudad: {ciudad_cliente}")
    c.drawString(100, 630, f"Teléfono: {telefono_cliente}")
    if correo_cliente:
        c.drawString(100, 610, f"Correo electrónico: {correo_cliente}")
    c.drawString(100, 590, "PRODUCTOS VENDIDOS:")
    y = 570
    for producto in productos_vendidos:
        c.drawString(120, y, f"Nombre: {producto[0]}, Descripción: {producto[1]}")
        y -= 20
        c.drawString(120, y, f"Precio: {producto[2]}, Cantidad: {producto[3]}, Subtotal: {producto[4]}")
        y -= 20
    y -= 20
    c.drawString(100, y, f"Total de la venta (antes de impuestos y descuentos): {total_venta:.2f}")
    y -= 20
    if descuento_aplicado:
        c.drawString(100, y, f"Descuento aplicado: {descuento_aplicado.Nombre} - {descuento_aplicado.Porcentaje}%")
        y -= 20
    c.drawString(100, y, f"Impuesto sobre la venta (ISV): {isv:.2f}")
    y -= 20
    c.drawString(100, y, f"Total final (con impuestos y descuentos): {total_venta + isv:.2f}")
    c.save()
    print(f"\nFactura guardada como PDF: {nombre_archivo}")

class Inventario:
    def __init__(self, session):
        self.session = session

    def agregar_producto(self, producto):
        self.session.add(producto)
        self.session.commit()
        print("Producto agregado correctamente.")

    def buscar_producto(self, nombre):
        return self.session.query(Producto).filter_by(Nombre=nombre).first()

    def actualizar_inventario(self, nombre, cantidad):
        producto = self.buscar_producto(nombre)
        if producto:
            producto.Cantidad_en_inventario += cantidad
            self.session.commit()
            print(f"Inventario actualizado: {producto.Nombre}, Nueva cantidad: {producto.Cantidad_en_inventario}")
        else:
            print("Producto no encontrado")

    def realizar_venta(self, nombre_producto, cantidad):
        producto = self.buscar_producto(nombre_producto)
        if producto:
            if producto.Cantidad_en_inventario >= cantidad:
                producto.Cantidad_en_inventario -= cantidad
                self.session.commit()
                print(f"Venta realizada: {cantidad} {producto.Nombre}(s)")
                return True
            else:
                print("No hay suficiente stock para realizar la venta.")
        else:
            print("Producto no encontrado")
        return False

    def reporte_inventario(self):
        print("Reporte de inventario:")
        productos = self.session.query(Producto).all()
        for producto in productos:
            print(f"CodigoProd: {producto.ProductoID}, Producto: {producto.Nombre}, Descripción: {producto.Descripcion}, Precio: {producto.Precio}, Cantidad: {producto.Cantidad_en_inventario}")

def menu():
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("CONTROL DE INVENTARIOS Y FACTURACION")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    print("1... Mostrar reporte de inventario")
    print("2... Agregar producto")
    print("3... Actualizar inventario")
    print("4... Realizar venta")
    print("5... Buscar producto por código")
    print("6... Buscar facturas")
    print("7... Imprimir factura")
    print("8... Gestión de clientes")
    print("9... Gestión de proveedores")
    print("10. Registro de transacciones")
    print("11. Generar informes financieros")
    print("12. Gestión de empleados")
    print("13. Configuración del sistema")
    print("14. Salir")

def imprimir_factura_individual(session):
    factura_id = int(input("Ingrese el ID de la factura a imprimir: "))
    factura = session.query(Factura).filter_by(FacturaID=factura_id).first()
    
    if factura:
        # Obtener los detalles de la factura
        venta = session.query(Venta).filter_by(VentaID=factura.VentaID).first()
        if not venta:
            print(f"No se encontró una venta con el ID {factura.VentaID} asociada a la factura.")
            return
        
        cliente = session.query(Cliente).filter_by(ClienteID=factura.ClienteID).first()
        vendedor = session.query(Empleado).filter_by(EmpleadoID=venta.EmpleadoID).first()
        if not vendedor:
            print(f"No se encontró un empleado con el ID {venta.EmpleadoID} asociado a la venta.")
            return
        
        # Imprimir los detalles de la factura en la consola
        print("---------------------------------------------------------")
        print(" INFORMACIÓN DE LA FACTURA")
        print("---------------------------------------------------------")
        print(f"ID de la factura: {factura.FacturaID}")
        print(f"Fecha de facturación: {factura.Fecha}")
        print("---------------------------------------------------------")
        print("DATOS DEL VENDEDOR:")
        print(f"Nombre: {vendedor.Nombre} {vendedor.Apellido}")
        print("---------------------------------------------------------")
        print("DATOS DEL CLIENTE:")
        print(f"Nombre: {cliente.Nombre} {cliente.Apellido}")
        print(f"Dirección: {cliente.Direccion}")
        print(f"Ciudad: {cliente.Ciudad}")
        print(f"Teléfono: {cliente.Telefono}")
        print(f"Correo electrónico: {cliente.Correo_electronico}")
        print("---------------------------------------------------------")
        print("Detalles de los productos vendidos:")
        # Aquí se puede agregar el código para mostrar los detalles de los productos vendidos y otros datos de la factura
        
        # Guardar los detalles de la factura en un archivo de texto
        nombre_archivo_txt = f'factura_{factura_id}.txt'
        with open(nombre_archivo_txt, 'w') as archivo:
            archivo.write("---------------------------------------------------------\n")
            archivo.write("           INFORMACIÓN DE LA FACTURA\n")
            archivo.write("---------------------------------------------------------\n")
            archivo.write(f"ID de la factura: {factura.FacturaID}\n")
            archivo.write(f"Fecha de facturación: {factura.Fecha}\n")
            archivo.write("---------------------------------------------------------\n")
            archivo.write("DATOS DEL VENDEDOR:\n")
            archivo.write(f"Nombre: {vendedor.Nombre} {vendedor.Apellido}\n")
            archivo.write("---------------------------------------------------------\n")
            archivo.write("DATOS DEL CLIENTE:\n")
            archivo.write(f"Nombre: {cliente.Nombre} {cliente.Apellido}\n")
            archivo.write(f"Dirección: {cliente.Direccion}\n")
            archivo.write(f"Ciudad: {cliente.Ciudad}\n")
            archivo.write(f"Teléfono: {cliente.Telefono}\n")
            archivo.write(f"Correo electrónico: {cliente.Correo_electronico}\n")
            archivo.write("---------------------------------------------------------\n")
            archivo.write("Detalles de los productos vendidos:\n")
            # Agrega más detalles según sea necesario
            
            print(f"Factura guardada como archivo de texto: {nombre_archivo_txt}")

        # Guardar la factura como archivo PDF
        nombre_archivo_pdf = f'factura_{factura_id}.pdf'
        c = canvas.Canvas(nombre_archivo_pdf, pagesize=letter)
        ancho, alto = letter

        c.drawString(30, alto - 50, "---------------------------------------------------------")
        c.drawString(30, alto - 70, "           INFORMACIÓN DE LA FACTURA")
        c.drawString(30, alto - 90, "---------------------------------------------------------")
        c.drawString(30, alto - 110, f"ID de la factura: {factura.FacturaID}")
        c.drawString(30, alto - 130, f"Fecha de facturación: {factura.Fecha}")
        c.drawString(30, alto - 150, "---------------------------------------------------------")
        c.drawString(30, alto - 170, "DATOS DEL VENDEDOR:")
        c.drawString(30, alto - 190, f"Nombre: {vendedor.Nombre} {vendedor.Apellido}")
        c.drawString(30, alto - 210, "---------------------------------------------------------")
        c.drawString(30, alto - 230, "DATOS DEL CLIENTE:")
        c.drawString(30, alto - 250, f"Nombre: {cliente.Nombre} {cliente.Apellido}")
        c.drawString(30, alto - 270, f"Dirección: {cliente.Direccion}")
        c.drawString(30, alto - 290, f"Ciudad: {cliente.Ciudad}")
        c.drawString(30, alto - 310, f"Teléfono: {cliente.Telefono}")
        c.drawString(30, alto - 330, f"Correo electrónico: {cliente.Correo_electronico}")
        c.drawString(30, alto - 350, "---------------------------------------------------------")
        c.drawString(30, alto - 370, "Detalles de los productos vendidos:")
        # Aquí se puede agregar más detalles sobre los productos vendidos
        c.save()
        
        print(f"Factura guardada como archivo PDF: {nombre_archivo_pdf}")
        
    else:
        print("Factura no encontrada o no existente.")


def main():
    # Crear una clase de sesión de SQLAlchemy para interactuar con la base de datos
    Session = sessionmaker(bind=engine)
    session = Session() # Crear una instancia de sesión
    
    # Crear una instancia de la clase Inventario usando la sesión creada
    inventario = Inventario(session)

    while True:  # Iniciar un bucle infinito para el menú
        menu()  # Llamar a la función para mostrar el menú
        opcion = input("\nIngrese el número de la opción deseada: ")  # Obtener la opción del usuario

        if opcion == "1":
            print("________________________________________________________________________________________________________")
            inventario.reporte_inventario()   # Mostrar el reporte de inventario
            print("________________________________________________________________________________________________________")

        elif opcion == "2":
             # Obtener los datos del nuevo producto del usuario
            productoid = input("Ingrese el codigo del producto: ")
            nombre = input("Ingrese el nombre del producto: ")
            descripcion = input("Ingrese la descripción del producto: ")
            precio = float(input("Ingrese el precio del producto: "))
            cantidad_en_inventario = int(input("Ingrese la cantidad del producto: "))
            
            # Crear una instancia de Producto con los datos ingresados
            nuevo_producto = Producto(ProductoID=productoid, Nombre=nombre, Descripcion=descripcion, Precio=precio, Cantidad_en_inventario=cantidad_en_inventario)
            
            # Agregar el nuevo producto al inventario
            inventario.agregar_producto(nuevo_producto)

        elif opcion == "3":
            # Obtener el ID del producto a actualizar
            ProductoID = input("Ingrese el Codigo de Producto: ")
            # Buscar el producto en la base de datos
            producto_actualizar = session.query(Producto).filter_by(ProductoID=ProductoID).first()
            if producto_actualizar:  # Si se encuentra el producto
                # Obtener los nuevos datos del producto del usuario
                NuevoNombre = input("Ingrese el nuevo nombre del producto: ")
                producto_actualizar.Nombre = NuevoNombre
                NuevaCantidad = int(input("Ingrese la nueva cantidad en inventario: "))
                producto_actualizar.Cantidad_en_inventario = NuevaCantidad
                NuevoPrecio = float(input("Ingrese el nuevo precio del producto: "))
                producto_actualizar.Precio = NuevoPrecio
                
                # Confirmar los cambios en la base de datos
                session.commit()
                print("¡Producto actualizado correctamente!")
            else:
                print("No se encontró ningún producto con ese ID.")

        elif opcion == "4":
            # Obtener el ID del empleado que realiza la venta
            empleado_id = input("Ingrese el ID del empleado que realizara la venta: ")

            continuar_venta = True  # Variable para controlar el bucle de venta
            total_venta = 0.0   # Inicializar el total de la venta
            productos_vendidos = []  # Lista para almacenar los productos vendidos

            while continuar_venta:  # Bucle para agregar productos a la venta
                # Obtener el código del producto a vender
                codigo_producto = input("Ingrese el código del producto a vender: ")
                # Buscar el producto en la base de datos
                producto = inventario.session.query(Producto).filter_by(ProductoID=codigo_producto).first()

                if producto:  # Si se encuentra el producto
                    print("Nombre:", producto.Nombre)
                    print("Descripción:", producto.Descripcion)
                    print("Precio:", producto.Precio)
                    
                    # Obtener la cantidad a vender
                    cantidad_venta = int(input("Ingrese la cantidad del producto a vender: "))
                    
                    # Realizar la venta y actualizar el inventario
                    if inventario.realizar_venta(producto.Nombre, cantidad_venta):
                        
                        # Calcular el subtotal y agregarlo al total de la venta
                        subtotal = producto.Precio * cantidad_venta
                        total_venta += subtotal
                        
                        # Agregar los detalles del producto vendido a la lista
                        productos_vendidos.append((producto.Nombre, producto.Descripcion, producto.Precio, cantidad_venta, subtotal))
                        # Preguntar si se desean agregar más productos a la venta
                        respuesta = input("¿Desea agregar más productos para la venta? (si/no): ")
                        if respuesta.lower() != "si":
                            continuar_venta = False  # Salir del bucle de venta
                    else:
                        print("Error al realizar la venta.")
                else:
                    print("Producto no encontrado.")

            # Buscar al empleado por su ID en la base de datos
            empleado = session.query(Empleado).filter_by(EmpleadoID=empleado_id).first()  # Paso 3
            if empleado:
                nombre_vendedor = empleado.Nombre  # Obtener el nombre del empleado
            else:
                print("Empleado no encontrado.")
                continue  # Continuar al siguiente ciclo del bucle principal

            # Solicitar los datos del cliente
            nombre_cliente = input("Ingrese el nombre del cliente: ")
            apellido_cliente = input("Ingrese el apellido del cliente: ")
            direccion_cliente = input("Ingrese la dirección del cliente: ")
            ciudad_cliente = input("Ingrese la ciudad del cliente: ")
            telefono_cliente = input("Ingrese el teléfono del cliente: ")
            correo_cliente = input("Ingrese el correo electrónico del cliente (opcional): ")

            # Verificar si el cliente ya existe en la base de datos
            cliente_existente = session.query(Cliente).filter_by(Nombre=nombre_cliente, Apellido=apellido_cliente).first()

            if cliente_existente:
                cliente_id = cliente_existente.ClienteID  # Obtener el ID del cliente existente
                print("Cliente encontrado en la base de datos.")
            else:
                # Crear un nuevo cliente si no existe
                nuevo_cliente = Cliente(Nombre=nombre_cliente, Apellido=apellido_cliente, Direccion=direccion_cliente, Ciudad=ciudad_cliente, Telefono=telefono_cliente, Correo_electronico=correo_cliente)
                session.add(nuevo_cliente)  # Agregar el nuevo cliente a la base de datos
                session.commit()  # Confirmar los cambios en la base de datos
                cliente_id = nuevo_cliente.ClienteID  # Obtener el ID del nuevo cliente
                print("Nuevo cliente creado y guardado en la base de datos.")

            # Calcular total con impuesto
            isv = total_venta * 0.15  # Suponiendo un impuesto fijo del 15%
            descuento_aplicado = None  # Esta línea se agrega para inicializar la variable descuento_aplicado

            #////////////////////////////////////////////////////////////////////////////////////////////////////////////
            tienda = session.query(Tienda).first()  # Buscar la primera tienda en la base de datos
            if tienda:
                tienda_id = tienda.TiendaID  # Si se encuentra la tienda, obtener el ID de la tienda
            else:
                print("Tienda no encontrada.")  # Si no se encuentra la tienda, imprimir un mensaje de error
                continue  # Continuar al siguiente ciclo del bucle principal
            
            # Crear un nuevo registro de venta con los detalles de la venta actual
            nueva_venta = Venta(Fecha=datetime.now().date(), Total=total_venta, EmpleadoID=empleado_id, TiendaID=tienda_id)
            session.add(nueva_venta)  # Agregar la nueva venta a la base de datos
            session.commit()  # Confirmar los cambios en la base de datos

            # Aquí capturamos el ID de la nueva venta
            venta_id = nueva_venta.VentaID

            #////////////////////////////////////////////////////////////////////////////////////////////////////////////
            
            # Crear un nuevo registro en la tabla de facturas----------------------------
            nueva_factura = Factura(VentaID=venta_id, ClienteID=cliente_id, Fecha=datetime.now().date(), Total=total_venta, ImpuestoID=1)  # Ajusta el ImpuestoID según tu base de datos
            session.add(nueva_factura)  # Agregar la nueva factura a la base de datos
            session.commit()   # Confirmar los cambios en la base de datos
            
            #factura_id = nueva_factura.FacturaID
            #nueva_factura = Factura(VentaID=None, ClienteID=cliente_id, Fecha=datetime.now().date(), Total=total_venta, ImpuestoID=1)  # Ajusta el ImpuestoID según tu base de datos
            #session.add(nueva_factura)
            #session.commit()
            #factura_id = nueva_factura.FacturaID

            aplicar_descuento = input("¿Desea aplicar un descuento? (si/no): ")  # Preguntar al usuario si desea aplicar un descuento
            descuento_aplicado = None  # Inicializar la variable de descuento aplicado
            if aplicar_descuento.lower() == "si":  # Si el usuario desea aplicar un descuento
                descuentos_disponibles = session.query(Descuento).all()  # Obtener todos los descuentos disponibles de la base de datos
                for descuento in descuentos_disponibles:  # Iterar a través de los descuentos disponibles
                    print(f"{descuento.DescuentoID}: {descuento.Nombre} - {descuento.Porcentaje}%")  # Mostrar los descuentos disponibles
                
                id_descuento = int(input("Ingrese el ID del descuento a aplicar: "))   # Pedir al usuario el ID del descuento a aplicar
                descuento_aplicado = session.query(Descuento).filter_by(DescuentoID=id_descuento).first()  # Buscar el descuento en la base de datos
                if descuento_aplicado:  # Si el descuento se encuentra
                    # Aplicar descuento sobre el total de la venta
                    porcentaje_descuento = float(descuento_aplicado.Porcentaje.rstrip('%')) / 100  # Convertir el porcentaje de descuento a un valor decimal
                    #porcentaje_descuento = descuento_aplicado.Porcentaje / 100
                    total_venta -= total_venta * porcentaje_descuento  # Restar el descuento del total de la venta

            total_final = total_venta + isv  # Calcular el total final sumando el impuesto (ISV) al total de la venta
            fecha_hora_venta = datetime.now()   # Obtener la fecha y hora actuales para la venta
            #tienda = session.query(Tienda).first() ////////////////////////////////////////////////////////////////////

            print("\nFACTURA")
            print("---------------------------------------------------------")
            print(f"Fecha y hora de la venta: {fecha_hora_venta}")  # Imprimir la fecha y hora de la venta
            print(f"Nombre del vendedor: {nombre_vendedor}")  # Imprimir el nombre del vendedor
            print("---------------------------------------------------------")
            print("PRODUCTOS VENDIDOS:")
            for producto in productos_vendidos:  # Iterar a través de los productos vendidos
                print(f"Nombre: {producto[0]}, Descripción: {producto[1]}, Precio: {producto[2]}, Cantidad: {producto[3]}, Subtotal: {producto[4]}")   # Imprimir los detalles de cada producto vendido
            print("---------------------------------------------------------")
            print(f"Total de la venta: {total_final}")  # Imprimir el total de la venta
            if descuento_aplicado:   # Si se aplicó un descuento
                print(f"Descuento aplicado: {descuento_aplicado.Nombre} - {descuento_aplicado.Porcentaje}%")  # Imprimir los detalles del descuento aplicado
            print(f"Impuesto sobre la venta (ISV): {isv:.2f}")  # Imprimir el impuesto sobre la venta (ISV)
            print("---------------------------------------------------------")
            # Generar el nombre del archivo PDF de la factura usando la fecha y hora de la venta
            nombre_archivo = f'factura_{fecha_hora_venta.strftime("%Y%m%d%H%M%S")}.pdf'
            # Llamar a la función imprimir_factura para generar el PDF de la factura
            imprimir_factura(nombre_archivo, fecha_hora_venta, nombre_vendedor, nombre_cliente, apellido_cliente, direccion_cliente, ciudad_cliente, telefono_cliente, correo_cliente, productos_vendidos, total_venta, isv, descuento_aplicado)

        elif opcion == "5":  # Opción para buscar un producto por su ID
            ProductoID = input("Ingrese el código del producto a buscar: ")  # Pedir al usuario el ID del producto
            producto = session.query(Producto).filter_by(ProductoID=ProductoID).first()  # Buscar el producto en la base de datos
            if producto:  # Si se encuentra el producto
                print("Producto encontrado:")  
                print(f"Nombre: {producto.Nombre}")  # Imprimir el nombre del producto
                print(f"Descripción: {producto.Descripcion}")  # Imprimir la descripción del producto
                print(f"Precio: {producto.Precio}")   # Imprimir el precio del producto
                print(f"Cantidad en inventario: {producto.Cantidad_en_inventario}")  # Imprimir la cantidad en inventario del producto
            else:
                print("Producto no encontrado.")  # Imprimir un mensaje si el producto no se encuentra

        elif opcion == "6":
            # Obtener todas las facturas ordenadas por fecha de facturación
            facturas = session.query(Factura).order_by(Factura.Fecha).all()
            #Factura.imprimir_todas_las_facturas(session)
            # Verificar si se encontraron facturas
            if facturas:
                print("Facturas encontradas:")
                for factura in facturas:
                    print(f"ID de la factura: {factura.FacturaID}, Fecha de la factura: {factura.Fecha}")
            # Puedes imprimir más información según tus necesidades
            else:
                print("No se encontraron facturas.")

        elif opcion == "7":
            imprimir_factura_individual(session)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        elif opcion == "8":
            while True:
                print("\nGESTIÓN DE CLIENTES")
                print("1. Agregar cliente")
                print("2. Buscar cliente")
                print("3. Mostrar todos los clientes")
                print("4. Volver al menú principal")

                opcion_cliente = input("\nIngrese el número de la opción deseada: ")

                if opcion_cliente == "1":
                    # Agregar nuevo cliente
                    nombre_cliente = input("Ingrese el nombre del cliente: ")
                    apellido_cliente = input("Ingrese el apellido del cliente: ")
                    direccion_cliente = input("Ingrese la dirección del cliente: ")
                    ciudad_cliente = input("Ingrese la ciudad del cliente: ")
                    telefono_cliente = input("Ingrese el teléfono del cliente: ")
                    correo_cliente = input("Ingrese el correo electrónico del cliente (opcional): ")

                    nuevo_cliente = Cliente(Nombre=nombre_cliente, Apellido=apellido_cliente, Direccion=direccion_cliente, Ciudad=ciudad_cliente, Telefono=telefono_cliente, Correo_electronico=correo_cliente)
                    session.add(nuevo_cliente)
                    session.commit()
                    print("Cliente agregado correctamente.")

                elif opcion_cliente == "2":
                    # Buscar cliente por nombre o apellido
                    criterio_busqueda = input("Ingrese el nombre o apellido del cliente: ")
                    clientes_encontrados = session.query(Cliente).filter(or_(Cliente.Nombre.like(f'%{criterio_busqueda}%'), Cliente.Apellido.like(f'%{criterio_busqueda}%'))).all()
                    if clientes_encontrados:
                        print("Clientes encontrados:")
                        for cliente in clientes_encontrados:
                            print(f"ID: {cliente.ClienteID}, Nombre: {cliente.Nombre}, Apellido: {cliente.Apellido}, Teléfono: {cliente.Telefono}")
                    else:
                        print("No se encontraron clientes con ese criterio de búsqueda.")

                elif opcion_cliente == "3":
                    # Mostrar todos los clientes
                    clientes = session.query(Cliente).all()
                    if clientes:
                        print("Lista de clientes:")
                        for cliente in clientes:
                            print(f"ID: {cliente.ClienteID}, Nombre: {cliente.Nombre}, Apellido: {cliente.Apellido}, Teléfono: {cliente.Telefono}")
                    else:
                        print("No hay clientes registrados en la base de datos.")

                elif opcion_cliente == "4":
                    # Volver al menú principal
                    break

                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif opcion == "9":
            while True:
                print("\nGESTIÓN DE PROVEEDORES")
                print("1. Agregar proveedor")
                print("2. Buscar proveedor")
                print("3. Mostrar todos los proveedores")
                print("4. Volver al menú principal")

                opcion_proveedor = input("\nIngrese el número de la opción deseada: ")

                if opcion_proveedor == "1":
                    # Agregar nuevo proveedor
                    nombre_proveedor = input("Ingrese el nombre del proveedor: ")
                    direccion_proveedor = input("Ingrese la dirección del proveedor: ")
                    ciudad_proveedor = input("Ingrese la ciudad del proveedor: ")
                    telefono_proveedor = input("Ingrese el teléfono del proveedor: ")
                    correo_proveedor = input("Ingrese el correo electrónico del proveedor (opcional): ")

                    nuevo_proveedor = Proveedor(Nombre=nombre_proveedor, Direccion=direccion_proveedor, Ciudad=ciudad_proveedor, Telefono=telefono_proveedor, Correo_electronico=correo_proveedor)
                    session.add(nuevo_proveedor)
                    session.commit()
                    print("Proveedor agregado correctamente.")

                elif opcion_proveedor == "2":
                    # Buscar proveedor por ID
                    id_proveedor = input("Ingrese el ID del proveedor: ")
                    proveedor_encontrado = session.query(Proveedor).filter_by(ProveedorID=id_proveedor).first()
                    if proveedor_encontrado:
                        print("Proveedor encontrado:")
                        print(f"ID: {proveedor_encontrado.ProveedorID}, Nombre: {proveedor_encontrado.Nombre}, Teléfono: {proveedor_encontrado.Telefono}")
                    else:
                        print("Proveedor no encontrado.")

                elif opcion_proveedor == "3":
                    # Mostrar todos los proveedores
                    proveedores = session.query(Proveedor).all()
                    if proveedores:
                        print("Lista de proveedores:")
                        for proveedor in proveedores:
                            print(f"ID: {proveedor.ProveedorID}, Nombre: {proveedor.Nombre}, Teléfono: {proveedor.Telefono}")
                    else:
                        print("No hay proveedores registrados en la base de datos.")

                elif opcion_proveedor == "4":
                    # Volver al menú principal
                    break

                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif opcion == "10":
            while True:
                print("\nREGISTRO DE TRANSACCIONES")
                print("1. Registrar compra a proveedor")
                print("2. Registrar pago a proveedor")
                print("3. Registrar otro tipo de transacción")
                print("4. Volver al menú principal")

                opcion_transaccion = input("\nIngrese el número de la opción deseada: ")

                if opcion_transaccion == "1":
                    # Registrar compra a proveedor
                    id_proveedor = input("Ingrese el ID del proveedor: ")
                    proveedor = session.query(Proveedor).filter_by(ProveedorID=id_proveedor).first()
                    if proveedor:
                        cantidad = int(input("Ingrese la cantidad comprada: "))
                        monto_total = float(input("Ingrese el monto total de la compra: "))
                        # Aquí podrías agregar la lógica para registrar la compra en tu base de datos
                        print("Compra registrada correctamente.")
                    else:
                        print("Proveedor no encontrado.")

                elif opcion_transaccion == "2":
                    # Registrar pago a proveedor
                    id_proveedor = input("Ingrese el ID del proveedor: ")
                    proveedor = session.query(Proveedor).filter_by(ProveedorID=id_proveedor).first()
                    if proveedor:
                        monto_pago = float(input("Ingrese el monto del pago: "))
                        # Aquí podrías agregar la lógica para registrar el pago en tu base de datos
                        print("Pago registrado correctamente.")
                    else:
                        print("Proveedor no encontrado.")

                elif opcion_transaccion == "3":
                    # Registrar otro tipo de transacción
                    # Aquí se puede agregar lógica para registrar otros tipos de transacciones, según tus necesidades
                    print("Esta opción aún no está implementada.")

                elif opcion_transaccion == "4":
                    # Volver al menú principal
                    break

                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif opcion == "11":
            while True:
                print("\nGENERAR INFORMES FINANCIEROS")
                print("1. Generar informe de ventas por período")
                print("2. Generar informe de gastos por período")
                print("3. Generar balance general")
                print("4. Volver al menú principal")

                opcion_informe = input("\nIngrese el número de la opción deseada: ")

                if opcion_informe == "1":
                    # Generar informe de ventas por período
                    fecha_inicio = input("Ingrese la fecha de inicio del período (YYYY-MM-DD): ")
                    fecha_fin = input("Ingrese la fecha de fin del período (YYYY-MM-DD): ")
                    # Aquí se puede agregar la lógica para generar el informe de ventas por período

                elif opcion_informe == "2":
                    # Generar informe de gastos por período
                    fecha_inicio = input("Ingrese la fecha de inicio del período (YYYY-MM-DD): ")
                    fecha_fin = input("Ingrese la fecha de fin del período (YYYY-MM-DD): ")
                    # Aquí se puede agregar la lógica para generar el informe de gastos por período

                elif opcion_informe == "3":
                    # Generar balance general
                    # Obtener todos los activos
                    #activos = session.query(func.sum(Producto.Precio * Producto.Cantidad_en_inventario)).scalar()
                    # Obtener todos los pasivos (por ejemplo, deudas)
                    #pasivos = session.query(func.sum(Deuda.monto)).scalar()
                    # Obtener el patrimonio neto
                    #patrimonio_neto = activos - pasivos
                    # Imprimir el balance general
                    """print("\nBALANCE GENERAL")
                    print(f"Activos totales: {activos}")
                    print(f"Pasivos totales: {pasivos}")
                    print(f"Patrimonio neto: {patrimonio_neto}") """
                    print("Esta opción aún no está implementada.")

                elif opcion_transaccion == "4":
                    # Volver al menú principal
                    break

                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")
                    
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif opcion == "12":
            while True:
                print("\nGESTIÓN DE EMPLEADOS")
                print("1. Agregar empleado")
                print("2. Buscar empleado por ID")
                print("3. Mostrar todos los empleados")
                print("4. Volver al menú principal")

                opcion_empleado = input("\nIngrese el número de la opción deseada: ")

                if opcion_empleado == "1":
                    # Agregar empleado
                    nombre = input("Ingrese el nombre del empleado: ")
                    apellido = input("Ingrese el apellido del empleado: ")
                    usuario = input("Ingrese el nombre de usuario del empleado: ")
                    contrasena = getpass.getpass("Ingrese la contraseña del empleado: ")
                    nivel_de_acceso = input("Ingrese el nivel de acceso del empleado: ")
                    tienda_id = input("Ingrese el ID de la tienda a la que pertenece el empleado: ")
                    
                    nuevo_empleado = Empleado(Nombre=nombre, Apellido=apellido, Usuario=usuario, Contrasena=hashlib.md5(contrasena.encode()).hexdigest(), Nivel_de_acceso=nivel_de_acceso, TiendaID=tienda_id)
                    session.add(nuevo_empleado)
                    session.commit()
                    
                    print("Empleado agregado correctamente.")

                elif opcion_empleado == "2":
                    # Buscar empleado por ID
                    empleado_id = input("Ingrese el ID del empleado: ")
                    empleado = session.query(Empleado).filter_by(EmpleadoID=empleado_id).first()
                    if empleado:
                        print("Empleado encontrado:")
                        print(f"Nombre: {empleado.Nombre}")
                        print(f"Apellido: {empleado.Apellido}")
                        print(f"Usuario: {empleado.Usuario}")
                        print(f"Nivel de acceso: {empleado.Nivel_de_acceso}")
                    else:
                        print("Empleado no encontrado.")

                elif opcion_empleado == "3":
                    # Mostrar todos los empleados
                    empleados = session.query(Empleado).all()
                    if empleados:
                        print("Lista de empleados:")
                        for empleado in empleados:
                            print(f"ID: {empleado.EmpleadoID}, Nombre: {empleado.Nombre}, Apellido: {empleado.Apellido}, Usuario: {empleado.Usuario}, Nivel de acceso: {empleado.Nivel_de_acceso}")
                    else:
                        print("No hay empleados registrados.")

                elif opcion_empleado == "4":
                    # Volver al menú principal
                    break

                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif opcion == "13":
            while True:
                print("\nCONFIGURACIÓN DEL SISTEMA")
                print("1. Configurar información de la tienda")
                print("2. Configurar información de impuestos")
                print("3. Configurar información de descuentos")
                print("4. Volver al menú principal")

                opcion_configuracion = input("\nIngrese el número de la opción deseada: ")

                if opcion_configuracion == "1":
                    # Configurar información de la tienda
                    print("Configuración de la tienda:")
                    nombre_tienda = input("Ingrese el nombre de la tienda: ")
                    direccion_tienda = input("Ingrese la dirección de la tienda: ")
                    telefono_tienda = input("Ingrese el teléfono de la tienda: ")
                    correo_tienda = input("Ingrese el correo electrónico de la tienda: ")
                    # Aquí se puede actualizar la información de la tienda en la base de datos

                elif opcion_configuracion == "2":
                    # Configurar información de impuestos
                    print("Configuración de impuestos:")
                    tasa_impuesto = float(input("Ingrese la tasa de impuesto (%): "))
                    # Aquí se puede actualizar la tasa de impuesto en la base de datos

                elif opcion_configuracion == "3":
                    # Configurar información de descuentos
                    print("Configuración de descuentos:")
                    nombre_descuento = input("Ingrese el nombre del descuento: ")
                    porcentaje_descuento = float(input("Ingrese el porcentaje de descuento (%): "))
                    # Aquí se puede agregar el nuevo descuento a la base de datos

                elif opcion_configuracion == "4":
                    # Volver al menú principal
                    break

                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif opcion == "14":
            print("¡Hasta luego!")
            break

        else:
            print("Opción inválida. Por favor, ingrese un número válido.")

    session.close()

if __name__ == "__main__":
    main()




 










