from django.conf.urls import url
from . import views

app_name = 'DataFactory'
urlpatterns = [
    url(r'^$', views.data_factory, name='DataFactory'),
]
