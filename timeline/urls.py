from django.urls import path

from . import views

urlpatterns = [
    path('', views.show_images, name='show_images'),
    path('autoimport', views.autoimport, name='import'),
]
