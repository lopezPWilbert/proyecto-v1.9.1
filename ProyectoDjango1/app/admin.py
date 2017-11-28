from django.contrib import admin
from app.models import *

admin.site.register(Usuario_m) 
admin.site.register(Comentario_m)
admin.site.register(imagenes_m)
admin.site.register(videos_m)

#1.7 reportes
class Admin:
    list_filter = ('publisher', 'publication_date')
#fin 1.7

class ImgInline(admin.StackedInline):
	model = imagenes_m
	extra=3

class VideoInline(admin.StackedInline):
	model = videos_m
	extra=3
#1.7 reportes
def desactivar(modeladmin, request, queryset):
	queryset.update(estado=False)
def reactivar(modeladmin, request, queryset):
	queryset.update(estado=True)
#desactivar.short_description ="Desactivar denuncias"
#fin 1.7
class DenunciaAdmin(admin.ModelAdmin):
	fieldsets=[
		('Usuario',{'fields':['user']}),
		('Informacion de Denuncia',{'fields':['titulo','descripcion']}),
		('Coordenadas',{'fields':['latitud','longitud']}),
		#('Evidencia Obligatoria',{'fields':['img','video']})
		#1.7 reportes
		('Reportado',{'fields':['reportado']}),
		('Activo',{'fields':['estado']})
		]
	inlines=[ImgInline,VideoInline]
	#1.7 reportes
	actions=[desactivar, reactivar]
	list_filter = ['reportado','estado']
	#fin 1.7

#https://docs.djangoproject.com/es/1.11/intro/tutorial07/
admin.site.register(Denuncia_m,DenunciaAdmin)