from django.urls import path
from . import views

urlpatterns = [
    path('subir/', views.subir_texto, name='subir_texto'),
    path('', views.lista_textos, name='lista_textos'),
    path('analizar/<int:texto_id>/', views.analizar_texto, name='analizar_texto'),
    path('analizar/<int:texto_id>/<int:n_grama>/', views.analizar_texto, name='analizar_texto_ngrama'),
    path('procesamiento/<int:texto_id>/', views.ver_procesamiento, name='ver_procesamiento'),
    # NUEVAS RUTAS PARA AUTOCOMPLETADO 
    path('autocompletado/', views.autocompletado_view, name='autocompletado'),
    path('api/sugerencias/', views.obtener_sugerencias, name='obtener_sugerencias'),
    path('entrenar-modelo/', views.entrenar_modelo, name='entrenar_modelo'),
]