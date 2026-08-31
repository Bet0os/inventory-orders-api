API REST - Sistema de Gestión de Inventario y Pedidos

API REST desarrollada con Django y Django REST Framework para gestionar productos, categorías, proveedores, inventario, carritos de compra y órdenes de venta.

El proyecto implementa autenticación mediante JWT, permisos según rol de usuario, documentación automática con Swagger / ReDoc, consultas avanzadas utilizando el ORM de Django y pruebas automatizadas.

Tecnologías utilizadas

Python

Django

Django REST Framework

Simple JWT

drf-spectacular

SQLite

Coverage

Flake8

autopep8

Git

Funcionalidades principales

Gestión de productos

La API permite:

Listar productos.

Consultar un producto específico.

Crear productos.

Actualizar productos.

Eliminar productos.

Buscar productos por nombre o SKU.

Filtrar productos por categoría.

Filtrar productos por precio mínimo y máximo.

Filtrar productos por stock.

Consultar el historial de inventario de un producto.

Las operaciones de modificación están protegidas mediante permisos para administradores.

Gestión de categorías

La API permite crear, consultar, actualizar y eliminar categorías.

El listado de categorías utiliza paginación.

Por defecto se muestran:

5 categorías por página


También puede modificarse utilizando:

?page_size=10

Gestión de proveedores

Permite administrar los proveedores asociados a los productos.

Cada proveedor puede contener:

Nombre.

Correo electrónico de contacto.

Teléfono.

También existe un endpoint para consultar proveedores que tienen productos con stock menor a 10 unidades.

Gestión de inventario

Cada cambio de inventario puede registrarse mediante un movimiento.

Los tipos de movimiento disponibles son:

IN
OUT


Las razones disponibles son:

PURCHASE
SALE
ADJUSTMENT


Cada movimiento puede almacenar:

Producto.

Tipo de movimiento.

Razón.

Cantidad.

Proveedor.

OrderItem relacionado.

Fecha de creación.

El sistema actualiza automáticamente el stock del producto al crear, modificar o eliminar movimientos de inventario.

También valida que no pueda realizarse una salida superior al stock disponible.

La consulta y administración directa de movimientos de inventario requiere un usuario staff.

Carrito de compras

El sistema permite manejar un carrito asociado a un usuario.

El acceso al carrito requiere autenticación y cada carrito se asocia al usuario autenticado.

Las funcionalidades principales son:

Consultar el carrito actual.

Agregar productos.

Modificar cantidades.

Eliminar productos.

Calcular subtotales.

Calcular el total del carrito.

No se permite tener el mismo producto duplicado dentro del mismo carrito.

Los endpoints del carrito requieren autenticación.

Órdenes

La API permite:

Crear órdenes.

Listar órdenes del usuario.

Consultar una orden específica.

Filtrar órdenes.

Procesar devoluciones.

Actualizar el inventario relacionado con una orden.

Los estados utilizados por las órdenes son:

PENDING
COMPLETED
CANCELLED
RETURNED


Al crear una orden se valida la disponibilidad de los productos y se realizan las operaciones correspondientes sobre el inventario.

Estructura del proyecto

gestion/
│
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
│
├── tienda_en_linea/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── products/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── cart/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── orders/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
└── users/
    ├── migrations/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── tests.py
    ├── urls.py
    └── views.py


Instalación

1. Clonar el repositorio

git clone https://github.com/Bet0os/inventory-orders-api.git

Entrar al proyecto:

cd inventory-orders-api

2. Crear un entorno virtual

Windows

python -m venv venv

Activarlo:

venv\Scripts\activate

Linux / macOS

python3 -m venv venv

Activarlo:

source venv/bin/activate

3. Instalar dependencias

pip install -r requirements.txt

4. Aplicar migraciones

python manage.py makemigrations
python manage.py migrate

5. Crear un superusuario

Opcionalmente puede crearse un administrador mediante:

python manage.py createsuperuser

6. Ejecutar el servidor

python manage.py runserver

Por defecto, la aplicación estará disponible localmente en el puerto 8000.

Autenticación JWT

La API utiliza JSON Web Tokens (JWT) para autenticación.

Obtener token

POST /api/token/

Ejemplo del cuerpo:

{
  "username": "usuario",
  "password": "contraseña"
}

La respuesta contiene los tokens:

{
  "refresh": "...",
  "access": "..."
}

Para acceder a endpoints protegidos se utiliza:

Authorization: Bearer <access_token>

Renovar token

POST /api/token/refresh/

Ejemplo:

{
  "refresh": "<refresh_token>"
}

Roles y permisos

El sistema maneja dos roles principales:

ADMIN
CUSTOMER


Los usuarios normales pueden realizar operaciones permitidas sobre sus propios recursos.

Los administradores (is_staff=True) tienen permisos adicionales para administrar productos, categorías, proveedores y movimientos de inventario. Los usuarios autenticados pueden gestionar su propio carrito y sus propias órdenes. Los movimientos de inventario están restringidos a usuarios staff.

En productos, categorías y proveedores se utiliza el permiso personalizado:

IsAdminOrReadOnly


Esto permite operaciones de lectura mientras restringe las operaciones de modificación a los usuarios autorizados.

Endpoints

Productos

Listar productos

GET /api/products/

Consultar un producto

GET /api/products/{id}/

Crear un producto

POST /api/products/

Ejemplo:

{
  "name": "Laptop",
  "sku": "LAP-001",
  "price": "15000.00",
  "stock": 20,
  "category": 1,
  "supplier": 1
}

El SKU debe ser único.

Actualizar producto

PUT /api/products/{id}/
PATCH /api/products/{id}/

Eliminar producto

DELETE /api/products/{id}/

Filtros de productos

Categoría

GET /api/products/?category=1

Precio mínimo

GET /api/products/?min_price=100

Precio máximo

GET /api/products/?max_price=1000

Rango de precio

GET /api/products/?min_price=100&max_price=1000

Stock

GET /api/products/?stock=10

Buscar por nombre o SKU

GET /api/products/?search=laptop

Los filtros pueden combinarse.

Ejemplo:

GET /api/products/?category=1&min_price=100&max_price=2000&search=laptop

Historial de inventario

Para consultar el historial de movimientos de un producto:

GET /api/products/{id}/inventory/

La respuesta incluye información del producto y sus movimientos de inventario.

Ejemplo:

{
  "product": {
    "id": 1,
    "name": "Laptop",
    "sku": "LAP-001",
    "price": "15000.00",
    "stock": 10,
    "category": 1,
    "supplier": 1
  },
  "inventory_history": []
}

Categorías

Listar categorías

GET /api/categories/

El endpoint utiliza paginación.

Ejemplo:

GET /api/categories/?page=1

Cambiar el tamaño de página:

GET /api/categories/?page_size=10

Crear categoría

POST /api/categories/

Ejemplo:

{
  "name": "Electrónica",
  "description": "Productos electrónicos"
}

Consultar categoría

GET /api/categories/{id}/

Actualizar categoría

PUT /api/categories/{id}/
PATCH /api/categories/{id}/

Eliminar categoría

DELETE /api/categories/{id}/

Proveedores

Listar proveedores

GET /api/suppliers/

Crear proveedor

POST /api/suppliers/

Ejemplo:

{
  "name": "Proveedor Example",
  "contact_email": "proveedor@example.com",
  "phone": "1234567890"
}

Consultar proveedor

GET /api/suppliers/{id}/

Actualizar proveedor

PUT /api/suppliers/{id}/
PATCH /api/suppliers/{id}/

Eliminar proveedor

DELETE /api/suppliers/{id}/

Proveedores con stock bajo

Permite consultar proveedores que tengan productos con menos de 10 unidades disponibles.

GET /api/suppliers/low-stock/

Movimientos de inventario

Los endpoints de movimientos de inventario requieren un usuario staff.

Listar movimientos

GET /api/movements/

Crear movimiento

POST /api/movements/

Ejemplo de entrada:

{
  "movement_type": "IN",
  "reason": "PURCHASE",
  "quantity": 10,
  "product": 1,
  "supplier": 1
}

Ejemplo de salida:

{
  "movement_type": "OUT",
  "reason": "SALE",
  "quantity": 2,
  "product": 1
}

El sistema valida automáticamente que una salida no sea superior al stock disponible.

Carrito

Consultar carrito actual

GET /api/cart/

Devuelve el carrito actual junto con los productos agregados, cantidades y subtotales.

Agregar producto al carrito

POST /api/cart/

Permite agregar un producto al carrito.

Modificar producto del carrito

PATCH /api/cart/items/{item_id}/

Permite modificar la cantidad de un producto existente en el carrito.

Eliminar producto del carrito

DELETE /api/cart/items/{item_id}/

Elimina el producto indicado del carrito.

Órdenes

Listar órdenes

GET /api/orders/

Permite consultar las órdenes correspondientes al usuario.

Crear orden

POST /api/orders/

Permite crear una nueva orden a partir del carrito.

Durante el proceso se valida el stock disponible y se realizan las operaciones correspondientes sobre el inventario.

Filtrar órdenes

Las órdenes pueden filtrarse por estado.

Ejemplo:

GET /api/orders/?status=PENDING

También pueden consultarse utilizando los filtros de fecha implementados por la API.

Consultar una orden

GET /api/orders/{order_id}/

Devuelve los detalles de una orden específica junto con sus productos.

Actualizar una orden

PATCH /api/orders/{order_id}/

Permite realizar las modificaciones autorizadas sobre la orden.

Devolver una orden

POST /api/orders/{order_id}/return/

Permite procesar la devolución de una orden.

La operación realiza los ajustes correspondientes sobre el inventario.

Serialización avanzada

El proyecto utiliza serializers de Django REST Framework para transformar los modelos en representaciones JSON.

Se utilizan serializers anidados para representar información relacionada.

Por ejemplo, una orden puede incluir sus OrderItem.

También se utilizan campos calculados.

En OrderItemSerializer se encuentra:

calculated_total = serializers.SerializerMethodField()

El valor se obtiene mediante:

def get_calculated_total(self, obj):
    return obj.price * obj.quantity

Esto permite calcular dinámicamente el total correspondiente a cada elemento de la orden.

Consultas avanzadas con Django ORM

El proyecto utiliza diferentes herramientas del ORM de Django.

Q Objects

Se utilizan para realizar búsquedas complejas.

Por ejemplo, la búsqueda de productos permite buscar por nombre o SKU:

Q(name__icontains=search) |
Q(sku__icontains=search)

Aggregate

Se utiliza para generar información global del inventario.

Ejemplo:

Sum('stock')

Annotate

Se utiliza para calcular valores derivados para cada producto.

Por ejemplo:

precio × stock


Esto permite conocer el valor de stock de cada producto.

F Expressions

Se utilizan expresiones F() para realizar cálculos utilizando directamente campos de la base de datos.

Ejemplo:

F('price') * F('stock')

Reportes

Resumen del inventario

GET /api/reports/stock-summary/

Devuelve:

Número total de productos.

Cantidad total de unidades en stock.

Valor monetario total del inventario.

Ejemplo:

{
  "total_products": 10,
  "total_stock": 150,
  "inventory_value": 250000.00
}

Valor de stock por producto

GET /api/reports/product-stock-value/

Calcula el valor del inventario de cada producto mediante:

price × stock


Ejemplo:

[
  {
    "id": 1,
    "name": "Laptop",
    "price": "15000.00",
    "stock": 10,
    "stock_value": 150000.00
  }
]

Transacciones e integridad del inventario

Las operaciones críticas de inventario utilizan transacciones atómicas mediante:

@transaction.atomic

Esto ayuda a mantener la consistencia de los datos cuando se modifica el inventario.

Los movimientos de inventario actualizan automáticamente el stock.

Si se modifica un movimiento existente, el efecto anterior se revierte antes de aplicar el nuevo.

Si se elimina un movimiento, también se revierte su efecto sobre el stock.

Documentación de la API

El proyecto utiliza drf-spectacular para generar automáticamente el esquema OpenAPI.

Swagger UI

Con el servidor ejecutándose:

/api/docs/


Swagger permite explorar y probar los endpoints de forma interactiva.

ReDoc

También se encuentra disponible:

/api/redoc/


Schema OpenAPI

El esquema de la API puede consultarse mediante:

/api/schema/


Pruebas

El proyecto contiene pruebas automatizadas para validar la funcionalidad de la API.

Para ejecutar todas las pruebas:

python manage.py test

Estado actual:

Found 32 test(s).
System check identified no issues (0 silenced).

Ran 32 tests

OK


Cobertura de pruebas

Para ejecutar las pruebas utilizando Coverage:

coverage run manage.py test

Consultar el porcentaje de cobertura:

coverage report

Generar reporte HTML:

coverage html

El reporte se genera en:

htmlcov/


Para visualizarlo puede abrirse:

htmlcov/index.html


Seguridad

El proyecto utiliza diferentes mecanismos proporcionados por Django y Django REST Framework:

Autenticación JWT.

Permisos según usuario y rol.

Validación de datos mediante serializers.

ORM de Django para interacción con la base de datos.

Protección proporcionada por Django contra ataques comunes.

Validación del stock antes de realizar determinadas operaciones.

Transacciones atómicas para operaciones críticas de inventario.

Variables de entorno

En un entorno de producción se recomienda almacenar información sensible mediante variables de entorno, especialmente:

SECRET_KEY
DEBUG
DATABASE_URL
ALLOWED_HOSTS


Ejemplo de archivo .env:

SECRET_KEY=your-secret-key
DEBUG=True

El archivo .env no debe subirse al repositorio.

Endpoints principales

MétodoEndpointDescripción





POST

/api/token/

Obtener JWT

POST

/api/token/refresh/

Renovar JWT

GET

/api/products/

Listar productos

POST

/api/products/

Crear producto

GET

/api/products/{id}/

Consultar producto

PUT/PATCH

/api/products/{id}/

Actualizar producto

DELETE

/api/products/{id}/

Eliminar producto

GET

/api/products/{id}/inventory/

Historial de inventario

GET

/api/categories/

Listar categorías

POST

/api/categories/

Crear categoría

GET

/api/suppliers/

Listar proveedores

POST

/api/suppliers/

Crear proveedor

GET

/api/suppliers/low-stock/

Proveedores con stock bajo

GET

/api/movements/

Listar movimientos

POST

/api/movements/

Crear movimiento

GET

/api/cart/

Consultar carrito

POST

/api/cart/

Agregar producto al carrito

PATCH

/api/cart/items/{item_id}/

Modificar producto del carrito

DELETE

/api/cart/items/{item_id}/

Eliminar producto del carrito

GET

/api/orders/

Listar órdenes

POST

/api/orders/

Crear orden

GET

/api/orders/{order_id}/

Consultar orden

PATCH

/api/orders/{order_id}/

Actualizar orden

POST

/api/orders/{order_id}/return/

Devolver orden

GET

/api/reports/stock-summary/

Resumen del inventario

GET

/api/reports/product-stock-value/

Valor de stock por producto

GET

/api/docs/

Swagger UI

GET

/api/redoc/

ReDoc

GET

/api/schema/

OpenAPI Schema

Calidad del código

El proyecto busca mantener buenas prácticas de desarrollo mediante:

Separación de responsabilidades por aplicaciones.

Modelos relacionados mediante Foreign Keys.

Serializers para validación y representación de datos.

ViewSets y APIViews.

Permisos personalizados.

Transacciones atómicas.

Consultas optimizadas mediante el ORM de Django.

Pruebas automatizadas.

Documentación mediante OpenAPI.

Para comprobar el estilo del código con flake8:

flake8 .

Ejecución rápida

Una vez instalado el proyecto:

venv\Scripts\activate
python manage.py migrate
python manage.py runserver

Después puede accederse a Swagger desde:

/api/docs/


Para ejecutar las pruebas:

python manage.py test

Autor

Proyecto desarrollado como parte del Week 4 Challenge - Backend, implementando una API REST para un sistema de gestión de inventario, carrito de compras y pedidos.