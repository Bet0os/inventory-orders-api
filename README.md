# API REST - Sistema de Gestión de Inventario y Pedidos

API REST desarrollada con **Django** y **Django REST Framework** para gestionar productos, categorías, proveedores, inventario, carritos de compra y órdenes de venta.

El proyecto implementa autenticación mediante **JWT**, permisos según rol de usuario, documentación automática con **Swagger / ReDoc**, consultas avanzadas utilizando el ORM de Django y pruebas automatizadas.

---

# Tecnologías utilizadas

- Python
- Django
- Django REST Framework
- Simple JWT
- drf-spectacular
- SQLite
- Coverage
- Git

---

# Funcionalidades principales

## Gestión de productos

La API permite:

- Listar productos.
- Consultar un producto específico.
- Crear productos.
- Actualizar productos.
- Eliminar productos.
- Buscar productos por nombre o SKU.
- Filtrar productos por categoría.
- Filtrar productos por precio mínimo y máximo.
- Filtrar productos por stock.
- Consultar el historial de inventario de un producto.

Las operaciones de modificación están protegidas mediante permisos para administradores.

---

## Gestión de categorías

La API permite crear, consultar, actualizar y eliminar categorías.

El listado de categorías utiliza paginación.

Por defecto se muestran:

```text
5 categorías por página
```

También puede modificarse utilizando:

```http
?page_size=10
```

---

## Gestión de proveedores

Permite administrar los proveedores asociados a los productos.

Cada proveedor puede contener:

- Nombre.
- Correo electrónico de contacto.
- Teléfono.

También existe un endpoint para consultar proveedores que tienen productos con stock menor a 10 unidades.

---

## Gestión de inventario

Cada cambio de inventario puede registrarse mediante un movimiento.

Los tipos de movimiento disponibles son:

```text
IN
OUT
```

Las razones disponibles son:

```text
PURCHASE
SALE
ADJUSTMENT
```

Cada movimiento puede almacenar:

- Producto.
- Tipo de movimiento.
- Razón.
- Cantidad.
- Proveedor.
- OrderItem relacionado.
- Fecha de creación.

El sistema actualiza automáticamente el stock del producto al crear, modificar o eliminar movimientos de inventario.

También valida que no pueda realizarse una salida superior al stock disponible.

---

## Carrito de compras

El sistema permite manejar un carrito asociado a un usuario.

También contempla el manejo de carrito mediante sesión.

Las funcionalidades principales son:

- Consultar el carrito actual.
- Agregar productos.
- Modificar cantidades.
- Eliminar productos.
- Calcular subtotales.
- Calcular el total del carrito.

No se permite tener el mismo producto duplicado dentro del mismo carrito.

---

## Órdenes

La API permite:

- Crear órdenes.
- Listar órdenes del usuario.
- Consultar una orden específica.
- Filtrar órdenes.
- Procesar devoluciones.
- Actualizar el inventario relacionado con una orden.

Los estados utilizados por las órdenes son:

```text
PENDING
COMPLETED
CANCELLED
RETURNED
```

Al crear una orden se valida la disponibilidad de los productos y se realizan las operaciones correspondientes sobre el inventario.

---

# Estructura del proyecto

```text
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
```

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
```

Entrar al proyecto:

```bash
cd gestion
```

---

## 2. Crear un entorno virtual

### Windows

```bash
python -m venv venv
```

Activarlo:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

Activarlo:

```bash
source venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 5. Crear un superusuario

Opcionalmente puede crearse un administrador mediante:

```bash
python manage.py createsuperuser
```

---

## 6. Ejecutar el servidor

```bash
python manage.py runserver
```

Por defecto, la aplicación estará disponible localmente en el puerto `8000`.

---

# Autenticación JWT

La API utiliza **JSON Web Tokens (JWT)** para autenticación.

## Obtener token

```http
POST /api/token/
```

Ejemplo del cuerpo:

```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

La respuesta contiene los tokens:

```json
{
  "refresh": "...",
  "access": "..."
}
```

Para acceder a endpoints protegidos se utiliza:

```http
Authorization: Bearer <access_token>
```

---

## Renovar token

```http
POST /api/token/refresh/
```

Ejemplo:

```json
{
  "refresh": "<refresh_token>"
}
```

---

# Roles y permisos

El sistema maneja dos roles principales:

```text
ADMIN
CUSTOMER
```

Los usuarios normales pueden realizar operaciones permitidas sobre sus propios recursos.

Los administradores tienen permisos adicionales para administrar productos.

En los productos se utiliza un permiso personalizado:

```text
IsAdminOrReadOnly
```

Esto permite operaciones de lectura mientras restringe las operaciones de modificación a los usuarios autorizados.

---

# Endpoints

## Productos

### Listar productos

```http
GET /api/products/
```

---

### Consultar un producto

```http
GET /api/products/{id}/
```

---

### Crear un producto

```http
POST /api/products/
```

Ejemplo:

```json
{
  "name": "Laptop",
  "sku": "LAP-001",
  "price": "15000.00",
  "stock": 20,
  "category": 1,
  "supplier": 1
}
```

El SKU debe ser único.

---

### Actualizar producto

```http
PUT /api/products/{id}/
PATCH /api/products/{id}/
```

---

### Eliminar producto

```http
DELETE /api/products/{id}/
```

---

# Filtros de productos

## Categoría

```http
GET /api/products/?category=1
```

## Precio mínimo

```http
GET /api/products/?min_price=100
```

## Precio máximo

```http
GET /api/products/?max_price=1000
```

## Rango de precio

```http
GET /api/products/?min_price=100&max_price=1000
```

## Stock

```http
GET /api/products/?stock=10
```

## Buscar por nombre o SKU

```http
GET /api/products/?search=laptop
```

Los filtros pueden combinarse.

Ejemplo:

```http
GET /api/products/?category=1&min_price=100&max_price=2000&search=laptop
```

---

# Historial de inventario

Para consultar el historial de movimientos de un producto:

```http
GET /api/products/{id}/inventory/
```

La respuesta incluye información del producto y sus movimientos de inventario.

Ejemplo:

```json
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
```

---

# Categorías

### Listar categorías

```http
GET /api/categories/
```

El endpoint utiliza paginación.

Ejemplo:

```http
GET /api/categories/?page=1
```

Cambiar el tamaño de página:

```http
GET /api/categories/?page_size=10
```

---

### Crear categoría

```http
POST /api/categories/
```

Ejemplo:

```json
{
  "name": "Electrónica",
  "description": "Productos electrónicos"
}
```

---

### Consultar categoría

```http
GET /api/categories/{id}/
```

---

### Actualizar categoría

```http
PUT /api/categories/{id}/
PATCH /api/categories/{id}/
```

---

### Eliminar categoría

```http
DELETE /api/categories/{id}/
```

---

# Proveedores

### Listar proveedores

```http
GET /api/suppliers/
```

### Crear proveedor

```http
POST /api/suppliers/
```

Ejemplo:

```json
{
  "name": "Proveedor Example",
  "contact_email": "proveedor@example.com",
  "phone": "1234567890"
}
```

### Consultar proveedor

```http
GET /api/suppliers/{id}/
```

### Actualizar proveedor

```http
PUT /api/suppliers/{id}/
PATCH /api/suppliers/{id}/
```

### Eliminar proveedor

```http
DELETE /api/suppliers/{id}/
```

---

# Proveedores con stock bajo

Permite consultar proveedores que tengan productos con menos de 10 unidades disponibles.

```http
GET /api/suppliers/low-stock/
```

---

# Movimientos de inventario

### Listar movimientos

```http
GET /api/movements/
```

### Crear movimiento

```http
POST /api/movements/
```

Ejemplo de entrada:

```json
{
  "movement_type": "IN",
  "reason": "PURCHASE",
  "quantity": 10,
  "product": 1,
  "supplier": 1
}
```

Ejemplo de salida:

```json
{
  "movement_type": "OUT",
  "reason": "SALE",
  "quantity": 2,
  "product": 1
}
```

El sistema valida automáticamente que una salida no sea superior al stock disponible.

---

# Carrito

## Consultar carrito actual

```http
GET /api/cart/
```

Devuelve el carrito actual junto con los productos agregados, cantidades y subtotales.

---

## Agregar producto al carrito

```http
POST /api/cart/
```

Permite agregar un producto al carrito.

---

## Modificar producto del carrito

```http
PUT /api/cart/items/{item_id}/
PATCH /api/cart/items/{item_id}/
```

Permite modificar la cantidad de un producto existente en el carrito.

---

## Eliminar producto del carrito

```http
DELETE /api/cart/items/{item_id}/
```

Elimina el producto indicado del carrito.

---

# Órdenes

## Listar órdenes

```http
GET /api/orders/
```

Permite consultar las órdenes correspondientes al usuario.

---

## Crear orden

```http
POST /api/orders/
```

Permite crear una nueva orden a partir del carrito.

Durante el proceso se valida el stock disponible y se realizan las operaciones correspondientes sobre el inventario.

---

## Filtrar órdenes

Las órdenes pueden filtrarse por estado.

Ejemplo:

```http
GET /api/orders/?status=PENDING
```

También pueden consultarse utilizando los filtros de fecha implementados por la API.

---

## Consultar una orden

```http
GET /api/orders/{order_id}/
```

Devuelve los detalles de una orden específica junto con sus productos.

---

## Actualizar una orden

```http
PATCH /api/orders/{order_id}/
```

Permite realizar las modificaciones autorizadas sobre la orden.

---

## Devolver una orden

```http
POST /api/orders/{order_id}/return/
```

Permite procesar la devolución de una orden.

La operación realiza los ajustes correspondientes sobre el inventario.

---

# Serialización avanzada

El proyecto utiliza serializers de Django REST Framework para transformar los modelos en representaciones JSON.

Se utilizan serializers anidados para representar información relacionada.

Por ejemplo, una orden puede incluir sus `OrderItem`.

También se utilizan campos calculados.

En `OrderItemSerializer` se encuentra:

```python
calculated_total = serializers.SerializerMethodField()
```

El valor se obtiene mediante:

```python
def get_calculated_total(self, obj):
    return obj.price * obj.quantity
```

Esto permite calcular dinámicamente el total correspondiente a cada elemento de la orden.

---

# Consultas avanzadas con Django ORM

El proyecto utiliza diferentes herramientas del ORM de Django.

## Q Objects

Se utilizan para realizar búsquedas complejas.

Por ejemplo, la búsqueda de productos permite buscar por nombre o SKU:

```python
Q(name__icontains=search) |
Q(sku__icontains=search)
```

---

## Aggregate

Se utiliza para generar información global del inventario.

Ejemplo:

```python
Sum('stock')
```

---

## Annotate

Se utiliza para calcular valores derivados para cada producto.

Por ejemplo:

```text
precio × stock
```

Esto permite conocer el valor de stock de cada producto.

---

## F Expressions

Se utilizan expresiones `F()` para realizar cálculos utilizando directamente campos de la base de datos.

Ejemplo:

```python
F('price') * F('stock')
```

---

# Reportes

## Resumen del inventario

```http
GET /api/reports/stock-summary/
```

Devuelve:

- Número total de productos.
- Cantidad total de unidades en stock.
- Valor monetario total del inventario.

Ejemplo:

```json
{
  "total_products": 10,
  "total_stock": 150,
  "inventory_value": 250000.00
}
```

---

## Valor de stock por producto

```http
GET /api/reports/product-stock-value/
```

Calcula el valor del inventario de cada producto mediante:

```text
price × stock
```

Ejemplo:

```json
[
  {
    "id": 1,
    "name": "Laptop",
    "price": "15000.00",
    "stock": 10,
    "stock_value": 150000.00
  }
]
```

---

# Transacciones e integridad del inventario

Las operaciones críticas de inventario utilizan transacciones atómicas mediante:

```python
@transaction.atomic
```

Esto ayuda a mantener la consistencia de los datos cuando se modifica el inventario.

Los movimientos de inventario actualizan automáticamente el stock.

Si se modifica un movimiento existente, el efecto anterior se revierte antes de aplicar el nuevo.

Si se elimina un movimiento, también se revierte su efecto sobre el stock.

---

# Documentación de la API

El proyecto utiliza **drf-spectacular** para generar automáticamente el esquema OpenAPI.

## Swagger UI

Con el servidor ejecutándose:

```text
/api/docs/
```

Swagger permite explorar y probar los endpoints de forma interactiva.

---

## ReDoc

También se encuentra disponible:

```text
/api/redoc/
```

---

## Schema OpenAPI

El esquema de la API puede consultarse mediante:

```text
/api/schema/
```

---

# Pruebas

El proyecto contiene pruebas automatizadas para validar la funcionalidad de la API.

Para ejecutar todas las pruebas:

```bash
python manage.py test
```

Estado actual:

```text
Found 32 test(s).
System check identified no issues (0 silenced).

Ran 32 tests

OK
```

---

# Cobertura de pruebas

Para ejecutar las pruebas utilizando Coverage:

```bash
coverage run manage.py test
```

Consultar el porcentaje de cobertura:

```bash
coverage report
```

Generar reporte HTML:

```bash
coverage html
```

El reporte se genera en:

```text
htmlcov/
```

Para visualizarlo puede abrirse:

```text
htmlcov/index.html
```

---

# Seguridad

El proyecto utiliza diferentes mecanismos proporcionados por Django y Django REST Framework:

- Autenticación JWT.
- Permisos según usuario y rol.
- Validación de datos mediante serializers.
- ORM de Django para interacción con la base de datos.
- Protección proporcionada por Django contra ataques comunes.
- Validación del stock antes de realizar determinadas operaciones.
- Transacciones atómicas para operaciones críticas de inventario.

---

# Variables de entorno

En un entorno de producción se recomienda almacenar información sensible mediante variables de entorno, especialmente:

```text
SECRET_KEY
DEBUG
DATABASE_URL
ALLOWED_HOSTS
```

Ejemplo de archivo `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

El archivo `.env` no debe subirse al repositorio.

---

# Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/token/` | Obtener JWT |
| POST | `/api/token/refresh/` | Renovar JWT |
| GET | `/api/products/` | Listar productos |
| POST | `/api/products/` | Crear producto |
| GET | `/api/products/{id}/` | Consultar producto |
| PUT/PATCH | `/api/products/{id}/` | Actualizar producto |
| DELETE | `/api/products/{id}/` | Eliminar producto |
| GET | `/api/products/{id}/inventory/` | Historial de inventario |
| GET | `/api/categories/` | Listar categorías |
| POST | `/api/categories/` | Crear categoría |
| GET | `/api/suppliers/` | Listar proveedores |
| POST | `/api/suppliers/` | Crear proveedor |
| GET | `/api/suppliers/low-stock/` | Proveedores con stock bajo |
| GET | `/api/movements/` | Listar movimientos |
| POST | `/api/movements/` | Crear movimiento |
| GET | `/api/cart/` | Consultar carrito |
| POST | `/api/cart/` | Agregar producto al carrito |
| PUT/PATCH | `/api/cart/items/{item_id}/` | Modificar producto del carrito |
| DELETE | `/api/cart/items/{item_id}/` | Eliminar producto del carrito |
| GET | `/api/orders/` | Listar órdenes |
| POST | `/api/orders/` | Crear orden |
| GET | `/api/orders/{order_id}/` | Consultar orden |
| PATCH | `/api/orders/{order_id}/` | Actualizar orden |
| POST | `/api/orders/{order_id}/return/` | Devolver orden |
| GET | `/api/reports/stock-summary/` | Resumen del inventario |
| GET | `/api/reports/product-stock-value/` | Valor de stock por producto |
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/redoc/` | ReDoc |
| GET | `/api/schema/` | OpenAPI Schema |

---

# Calidad del código

El proyecto busca mantener buenas prácticas de desarrollo mediante:

- Separación de responsabilidades por aplicaciones.
- Modelos relacionados mediante Foreign Keys.
- Serializers para validación y representación de datos.
- ViewSets y APIViews.
- Permisos personalizados.
- Transacciones atómicas.
- Consultas optimizadas mediante el ORM de Django.
- Pruebas automatizadas.
- Documentación mediante OpenAPI.

Para comprobar el estilo del código con `flake8`:

```bash
flake8 .
```

---

# Ejecución rápida

Una vez instalado el proyecto:

```bash
venv\Scripts\activate
python manage.py migrate
python manage.py runserver
```

Después puede accederse a Swagger desde:

```text
/api/docs/
```

Para ejecutar las pruebas:

```bash
python manage.py test
```

---

# Autor

Proyecto desarrollado como parte del **Week 4 Challenge - Backend**, implementando una API REST para un sistema de gestión de inventario, carrito de compras y pedidos.