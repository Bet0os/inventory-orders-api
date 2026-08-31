# API REST - Sistema de Gestión de Inventario y Pedidos

API REST desarrollada con **Django** y **Django REST Framework** para gestionar productos, categorías, proveedores, inventario, carrito de compra y órdenes de venta.

El proyecto implementa autenticación mediante **JWT**, permisos según rol de usuario, documentación automática con **Swagger / ReDoc**, consultas avanzadas utilizando el ORM de Django y pruebas automatizadas.

---

## Tecnologías utilizadas

- Python
- Django
- Django REST Framework
- Simple JWT
- drf-spectacular
- SQLite
- Coverage
- Flake8
- autopep8
- Git

---

## Funcionalidades principales

### Gestión de productos

La API permite:

- Listar productos.
- Consultar un producto específico.
- Crear productos.
- Actualizar productos.
- Eliminar productos.
- Filtrar productos por categoría.
- Filtrar productos por precio mínimo y máximo.
- Filtrar productos por stock.
- Buscar productos por nombre o SKU.
- Consultar el historial de inventario de un producto.

Ejemplos:

```http
GET /api/products/
GET /api/products/1/
GET /api/products/?category=1
GET /api/products/?min_price=100
GET /api/products/?max_price=1000
GET /api/products/?search=laptop
GET /api/products/1/inventory/
```

---

### Gestión de categorías

Permite realizar operaciones CRUD sobre las categorías.

```http
GET /api/categories/
POST /api/categories/
GET /api/categories/{id}/
PUT /api/categories/{id}/
PATCH /api/categories/{id}/
DELETE /api/categories/{id}/
```

Las categorías utilizan paginación.

Por defecto:

```text
5 categorías por página
```

También puede modificarse mediante:

```http
GET /api/categories/?page_size=10
```

---

### Gestión de proveedores

Permite administrar los proveedores registrados en el sistema.

```http
GET /api/suppliers/
POST /api/suppliers/
GET /api/suppliers/{id}/
PUT /api/suppliers/{id}/
PATCH /api/suppliers/{id}/
DELETE /api/suppliers/{id}/
```

También existe una consulta para obtener proveedores relacionados con productos con bajo stock:

```http
GET /api/suppliers/low-stock/
```

---

## Gestión de inventario

El sistema registra movimientos de entrada y salida de productos.

Los movimientos permiten mantener un historial de los cambios realizados sobre el inventario.

```http
GET /api/movements/
POST /api/movements/
GET /api/movements/{id}/
PUT /api/movements/{id}/
PATCH /api/movements/{id}/
DELETE /api/movements/{id}/
```

Los endpoints de movimientos de inventario están restringidos a usuarios **staff**.

El sistema actualiza automáticamente el stock al registrar movimientos de inventario y valida que no pueda realizarse una salida superior al stock disponible.

---

## Carrito de compras

Los usuarios autenticados pueden administrar su propio carrito.

```http
GET /api/cart/
POST /api/cart/
PATCH /api/cart/items/{item_id}/
DELETE /api/cart/items/{item_id}/
```

El carrito permite:

- Agregar productos.
- Modificar cantidades.
- Eliminar productos.
- Validar disponibilidad de stock.
- Calcular subtotales.
- Calcular el total del carrito.

Cada carrito pertenece al usuario autenticado.

---

## Gestión de órdenes

Los usuarios pueden generar órdenes a partir de los productos agregados a su carrito.

```http
GET /api/orders/
POST /api/orders/
GET /api/orders/{id}/
PATCH /api/orders/{id}/status/
POST /api/orders/{id}/return/
```

Al crear una orden:

1. Se verifican los productos del carrito.
2. Se valida la disponibilidad de stock.
3. Se crea la orden.
4. Se crean los detalles correspondientes.
5. Se registran movimientos de inventario.
6. Se actualiza el stock.
7. Se vacía el carrito.

El proceso utiliza transacciones para evitar inconsistencias en caso de error.

---

## Estados de una orden

Las órdenes pueden manejar diferentes estados durante su ciclo de vida.

Ejemplos:

```text
PENDING
PROCESSING
COMPLETED
CANCELLED
RETURNED
```

El sistema valida las transiciones permitidas entre estados.

Cuando una orden completada es devuelta, los productos correspondientes regresan al inventario y se generan los movimientos de ajuste necesarios.

---

## Autenticación JWT

La API utiliza **JSON Web Tokens (JWT)** mediante Simple JWT.

### Obtener token

```http
POST /api/token/
```

Ejemplo:

```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

Respuesta:

```json
{
  "refresh": "token_refresh",
  "access": "token_access"
}
```

### Renovar token

```http
POST /api/token/refresh/
```

Para acceder a endpoints protegidos se utiliza:

```http
Authorization: Bearer <access_token>
```

---

## Permisos y seguridad

El proyecto utiliza permisos para separar las operaciones disponibles según el tipo de usuario.

### Usuario autenticado

Puede realizar operaciones relacionadas con su propia actividad, como:

- Consultar productos.
- Administrar su carrito.
- Crear órdenes.
- Consultar sus órdenes.

### Usuario staff

Además de las operaciones anteriores, puede realizar tareas administrativas como:

- Crear productos.
- Modificar productos.
- Eliminar productos.
- Administrar categorías.
- Administrar proveedores.
- Consultar y administrar movimientos de inventario.

Esto evita que usuarios normales puedan modificar directamente información crítica del inventario.

---

## Consultas avanzadas con Django ORM

El proyecto utiliza herramientas del ORM de Django como:

- `Q`
- `F`
- `Sum`
- `ExpressionWrapper`
- `annotate`
- `aggregate`
- `distinct`

Estas herramientas permiten realizar búsquedas, filtros, cálculos y reportes directamente desde la base de datos.

---

## Reportes

### Resumen de inventario

```http
GET /api/stock-summary/
```

Permite obtener información como:

- Total de productos.
- Cantidad total de unidades.
- Valor total del inventario.

### Valor de stock por producto

```http
GET /api/stock-value/
```

Calcula:

```text
precio × stock
```

para cada producto.

### Productos con bajo stock

También se incluyen consultas para identificar productos o proveedores relacionados con niveles bajos de inventario.

---

## Documentación de la API

La documentación se genera automáticamente utilizando **drf-spectacular**.

### Swagger UI

```text
http://127.0.0.1:8000/api/docs/
```

Swagger permite visualizar y probar los endpoints disponibles directamente desde el navegador.

### ReDoc

```text
http://127.0.0.1:8000/api/redoc/
```

### Esquema OpenAPI

```text
http://127.0.0.1:8000/api/schema/
```

---

# Instalación y configuración

## 1. Clonar el repositorio

```bash
git clone https://github.com/Bet0os/inventory-orders-api.git
```

Entrar al proyecto:

```bash
cd inventory-orders-api
```

---

## 2. Crear un entorno virtual

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

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
python manage.py migrate
```

---

## 5. Crear un superusuario

```bash
python manage.py createsuperuser
```

---

## 6. Ejecutar el servidor

```bash
python manage.py runserver
```

La API estará disponible en:

```text
http://127.0.0.1:8000/
```

---

# Variables de entorno

Para la ejecución local de esta versión del proyecto no es necesario configurar variables de entorno adicionales.

La aplicación utiliza **SQLite** como base de datos local y la configuración de desarrollo se encuentra definida en:

```text
tienda_en_linea/settings.py
```

Para un despliegue en producción se recomienda mover valores sensibles y configurables a variables de entorno, especialmente:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- Configuración de la base de datos

En caso de utilizar un archivo `.env`, este no debe subirse al repositorio y debe agregarse al `.gitignore`.

---

# Pruebas automatizadas

El proyecto incluye pruebas automatizadas para comprobar las funcionalidades principales.

Para ejecutar todas las pruebas:

```bash
python manage.py test
```

El proyecto cuenta con **32 pruebas automatizadas**.

---

## Cobertura de código

Para generar un reporte de cobertura:

```bash
coverage run manage.py test
```

Después:

```bash
coverage report
```

También puede generarse un reporte HTML:

```bash
coverage html
```

El reporte se genera en:

```text
htmlcov/index.html
```

---

# Calidad de código

Para verificar el estilo del código se utiliza **Flake8**.

```bash
flake8 products cart orders users tienda_en_linea --exclude=migrations,__pycache__ --max-line-length=100
```

Durante el desarrollo también se utilizó **autopep8** para corregir automáticamente problemas de formato y mantener un código consistente.

Ejemplo:

```bash
autopep8 --in-place archivo.py
```

Después de aplicar correcciones con autopep8 se recomienda ejecutar nuevamente Flake8 y las pruebas automatizadas.

---

# Ejemplos de uso

## Consultar productos

```http
GET /api/products/
```

## Buscar un producto

```http
GET /api/products/?search=laptop
```

## Filtrar por precio

```http
GET /api/products/?min_price=100&max_price=1000
```

## Consultar resumen de inventario

```http
GET /api/stock-summary/
```

## Consultar carrito

```http
GET /api/cart/
Authorization: Bearer <access_token>
```

## Crear una orden

```http
POST /api/orders/
Authorization: Bearer <access_token>
```

---

# Estructura del proyecto

```text
gestion/
│
├── cart/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── orders/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── products/
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── users/
│
├── tienda_en_linea/
│   ├── settings.py
│   └── urls.py
│
├── manage.py
├── requirements.txt
└── README.md
```

---

# Autor

**Alberto Camacho**

Proyecto desarrollado como parte de **Residencias Profesionales 2026**.

## Objetivo del proyecto

Desarrollar una API REST estructurada y segura para la gestión de inventario y pedidos, aplicando conceptos de desarrollo backend con Django REST Framework, autenticación, permisos, validación de datos, pruebas automatizadas, documentación y control de versiones.