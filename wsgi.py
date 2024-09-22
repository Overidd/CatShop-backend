import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catshop.settings')  # Asegúrate de que esto sea correcto

application = get_wsgi_application()
