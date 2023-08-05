from django.urls import path

from .views import dashboard, actions
from .apps import get_app_label

app_name = get_app_label()

urlpatterns = [
    path('import/process', actions.process_import, name='process_import'),
    path('import', actions.start_import, name='start_import'),
    path('', dashboard.dashboard, name='dashboard'),
]
