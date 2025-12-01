# Wishlist simple (Flask)

Pequeña aplicación para que dos (o más) personas guarden su wishlist y vean lo que otros han añadido.

Requisitos
- Python 3.10+ recomendado
- pip

Instalación rápida
1. Clona o copia los archivos en una carpeta.
2. (Opcional) Crea y activa un entorno virtual:
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows

3. Instala dependencias:
   pip install -r requirements.txt

4. (Opcional) Cambia la variable SECRET_KEY:
   export SECRET_KEY="cambia-esta-clave"  # Mac/Linux
   set SECRET_KEY=cambia-esta-clave       # Windows (cmd)

5. Ejecuta:
   python app.py

6. Abre en el navegador:
   http://127.0.0.1:5000

Uso
- Regístrate con dos cuentas (tú y tu novia).
- Cada uno añade items.
- "Mis items" muestra lo que tú añadiste.
- "Lo que añade la otra persona" muestra items cuyo owner no eres tú.

Notas de seguridad y mejoras
- Para producción: usar HTTPS y una SECRET_KEY segura.
- Validar/filtrar URLs de imagen si vas a aceptar enlaces externos.
- Limitar tamaño de subida y hacer escaneo/validación de imágenes.
- Si quieres remover la visibilidad pública, puedes implementar permisos para compartir solo con una cuenta específica (por ejemplo, elegir el partner).
- Puedes desplegar en un servicio como Render, Railway, Heroku o un VPS.
