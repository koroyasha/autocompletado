from django.contrib import admin
from .models import TextoAnalizado

@admin.register(TextoAnalizado)
class TextoAnalizadoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha_subida']
    list_filter = ['fecha_subida']
    search_fields = ['titulo']