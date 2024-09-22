

### Estas son las dependencias principales del proyecto y sus usos:

1. **cloudinary:** Biblioteca para la integración con Cloudinary, un servicio de gestión de imágenes y videos, permitiendo su carga, transformación y entrega.

2. **django-cors-headers:** Middleware de Django que permite la configuración de CORS (Cross-Origin Resource Sharing), habilitando la interacción del frontend con la API. 

3. **django-filter:** Biblioteca para facilitar la creación de filtros en vistas basadas en clases de Django, permitiendo filtrar querysets. 

4. **django-jazzmin:** Tema de administración para Django que mejora la interfaz de usuario del panel de administración con un diseño más moderno. 

5. **djangorestframework-simplejwt:** Extensión para Django REST Framework que implementa autenticación JWT (JSON Web Tokens), permitiendo la autenticación basada en tokens. 

6. **drf-yasg:** Generador de documentación para APIs construidas con Django REST Framework, generando una interfaz Swagger para explorar y probar las APIs. 

7. **hashids:** Biblioteca para la codificación y decodificación de números en formato Hashids, útil para ofuscar IDs en URLs. 

8. **pillow:** Biblioteca de imágenes para Python, utilizada para la manipulación de imágenes como redimensionar, recortar y más.

9. **psycopg2-binary:** Conector de PostgreSQL para Python, necesario para que Django interactúe con bases de datos PostgreSQL. 

10. **requests:** Biblioteca HTTP popular para hacer solicitudes de red, usada para interactuar con APIs externas.


### Aplicaciones
Aquí tienes una versión mejorada y más estructurada para la presentación del proyecto e-commerce, detallando las aplicaciones y sus funcionalidades de manera clara y profesional:

---

## Proyecto E-commerce: Aplicaciones y Funcionalidades

### Aplicaciones Principales

### 1. **Autenticación (`Authentication`)**
Esta aplicación maneja la autenticación de los usuarios, permitiendo el registro, inicio de sesión, y verificación de correo electrónico

- **POST Endpoint: `auth_register_create`**  
  Funcionalidad: Registra a nuevos usuarios en la plataforma, creando una cuenta con sus datos personales y envia un codigo de verificacion al correo del usuario.

- **POST Endpoint: `auth_login_create`**  
  Funcionalidad: Permite a los usuarios autenticarse en la plataforma utilizando su correo y su contraseña, el view responde con los tokens (access_token), (refresh_token) .

- **POST Endpoint `/auth/verify-email/`**  
  Funcionalidad: Verifica la dirección de correo electrónico del usuario para completar su registro y activa su cuenta.

- **POST Endpoint: `auth_resend-code_create`**  
  Funcionalidad: Reenvía el código de verificación al correo del usuario, asegurando que puedan completar la verificación de su cuenta.

### 2: proyecto purchases: se define para manejar órdenes para el sistema de compras de productos.
- OrderModel: Representa la orden principal con campos como código, total, descuento, precio de entrega, estado, y fechas de creación y actualización.

- OrderDetailModel: items de producto que intenta comprar el cliente, incluyendo cantidad, precio unitario, subtotal, descuento, y relación con la orden principal (OrderModel) y el producto (ProductModel).

- OrderIdentificationModel: Contiene los datos de identificación del cliente, como email, nombre, apellido, documento, teléfono, y RUC. Está vinculado de manera única a una orden.

- OrderDeliveryModel: Información de entrega, incluyendo departamento, provincia, distrito, dirección, y referencia. Está relacionado de manera única con una orden.

- OrderStoreModel: Información sobre la tienda asociada a la orden, vinculada de manera única.

- OrderPaymentModel: se guarda el metodo de pago que uso el cliente al realizar el pago, como el monto, método de pago, número de pago, tipo de tarjeta, nombre del titular, y número de cuotas. Relacionado de manera única con una orden.

- OrderUserTempModel: Información temporal del usuario, como email, vinculada de manera única con una orden.
---

### 3. **Pasarela de Pagos (`Payment Gateway`)**
Esta aplicación se encarga de procesar los pagos y gestionar la facturación de las órdenes generadas por los usuarios. para el proceso del pago se uso Culqi y Nubefact para la emisión de facturas

- **POST Endpoint: `order_create_create`**  
  Funcionalidad:  
  Crea una nueva orden con los datos proporcionados por el cliente, incluyendo detalles de entrega, identificación del cliente, y los productos a comprar. el view responde con un código de orden que identifica la transacción  
  **Parámetros del Request:**
  ```json
  {
    "opciones_entrega": "string",
    "isuser": {
      "isuser": true,
      "token": "string"
    },
    "order_identification": {
      "email": "user@example.com",
      "name": "string",
      "last_name": "string",
      "document_number": "string",
      "phone": "string",
      "ruc": "string"
    },
    "order_store": {
      "store_name": "string"
    },
    "order_delivery": {
      "department": "string",
      "province": "string",
      "district": "string",
      "address": "string",
      "street": "string",
      "street_number": "string",
      "reference": "string"
    },
    "order_payment": {
      "amount": 0,
      "payment_method": "string"
    },
    "order_details": [
      {
        "quantity": 0,
        "price_unit": 0,
        "product_id": 0
      }
    ]
  }
  ```

- **POST Endpoint: `process_payment_create`**  
  Funcionalidad:  
  Procesa el pago de la orden utilizando Culqi, recibe un `token_id`, un `código de orden` y de manera opcional un `token de usuario`. Si el pago es exitoso, responde con un enlace PDF de la factura electrónica generada por Nubefact.  
  **Parámetros del Request:**
  ```json
  {
    "token_id": "string",
    "order_code": "string",
    "user_token": "string"
  }
  ```
