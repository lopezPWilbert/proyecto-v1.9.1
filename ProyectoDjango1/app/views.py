"""
Definition of views.
"""

from django.shortcuts import render

from django.views.generic import FormView,CreateView,TemplateView, ListView,UpdateView
from django.core.urlresolvers import reverse_lazy
from .models import *
from .forms import *
from django.core import serializers
from django.http import HttpResponse,HttpResponseRedirect
from allauth.account.views import *
from allauth.account.models import *
from allauth.socialaccount.models import SocialAccount

from django.db import connection,transaction
from django.contrib.auth.models import User
#1.7 reportes
from django.db.models import Q

#1.8.1 CIrculos
import math
import time

def Distancia(x1,y1,x2,y2):
	distancia=math.sqrt(abs(((x2**2)-(x1**2))+((y2**2)-(y1**2))))
	return distancia

def coordenadas(queryset):
	denuncia=[]
	for x in queryset:
		denuncia.append([x.id,x.titulo, x.latitud,x.longitud])
	V=[]
	Vv=[]
	Vmax=[]
	V2=[]
	mismo=False
	for x in denuncia:
		Vv=[]
		for y in denuncia:
			if Distancia(y[2],y[3],x[2],x[3])<=1.6:
			
			
				if denuncia.index(y)!=denuncia.index(x):
					Vv.append(y)
		if len(Vv)!=0:
			V.append(Vv)

	for x in V:
	
		Vmax.append(len(x))
	m=max(Vmax)

	for x in V:
		if (len(x)==m):
			V2.append(x)
	coord_x=0
	coord_y=0
	v_promedios=[]
	#obtener prom de cada v2
	for a in V2:
		for b in a:
			coord_x+=b[2]
			coord_y+=b[3]
		entre=len(a)
		v_promedios+=[[(coord_x/len(a)),(coord_y/len(a))]]
		coord_x=0
		coord_y=0

	coord_x=0
	coord_y=0
	for a in v_promedios:
		coord_x+=a[0]
		coord_y+=a[1]
	FinalX=(coord_x/len(v_promedios))
	FinalY=(coord_y/len(v_promedios))
	return FinalX,FinalY, m

def crear_circulo():
	circulos=Circulos_m.objects.filter(fecha=(time.strftime("%Y-%m-%d")))
	if len(circulos)==0:
		a=Denuncia_m.objects.filter(Q(estado=True)|Q(estado=None))
		_x,_y,m=coordenadas(a)
		Circulos_m.objects.create(x=_x, y=_y, cantidad=m)
def Zonas(request):
	
	if request.POST:
		fechaDesde= request.POST['fechaDesde']
		fechaHasta= request.POST['fechaHasta']
		circulos=Circulos_m.objects.filter(fecha__range=[fechaDesde,fechaHasta])
	else:
		circulos=Circulos_m.objects.filter(fecha=(time.strftime("%Y-%m-%d")))
	return render(request, 'app/zonas.html', {'circulos':circulos})
#fin 1.8.1

@login_required(login_url=reverse_lazy('account_login'), redirect_field_name=None)
def Denuncia(request):
	form=Denuncia_Form(request.POST or None)
	form2=imagenes_f(request.POST or None,request.FILES or None)
	form3=videos_f(request.POST or None,request.FILES or None)
	if(request.method=='POST' and form.is_valid):
		#horas=request.POST['horas']
		formResult=form.save()
		#formResult.hasta=horas
		if(form2.is_valid()):
			idDenuncia=formResult.id
			for x in request.FILES.getlist('imagenes'):
				imagenes_m.objects.create(imagen=x, denunciaA_id=idDenuncia)
			if(form3.is_valid()):
				formResult3=form3.save(commit=False)
				formResult3.denunciaB_id=formResult.id
				formResult3.save()

	return render(request, 'app/denuncia.html',{'form':form,'form2':form2, 'form3':form3})

#1.7 Reportes
def MasVotadas():
    object_list=Denuncia_m.objects.raw("select count(f.denuncia_id) as x, f.id as y, f.denuncia_id as w,f.usuario_id as z, f.fecha as q,d.* from app_favor_m f, app_denuncia_m d where f.denuncia_id=d.id group by f.denuncia_id order by x desc,f.fecha desc limit 0,10")
    ctx=Denuncia_m.objects.raw("select * from app_denuncia_m o where o.id='%s'"%(10))
    return object_list
#Fin 1.7

#1.6 Filtros

def Filtro(request, cat):
	if cat=="100":
		object_list=MasVotadas()
	else:
		object_list=Denuncia_m.objects.filter(categoria=cat)
	return render(request, 'app/mapa.html', {'object_list':object_list})

#Fin ver 1.6


class Mapa(ListView):
	template_name='app/mapa.html'
	model=Denuncia_m
	#1.7 reportes
	def get_queryset(self):
		crear_circulo()
		queryset = super(Mapa, self).get_queryset()
		return queryset.filter(Q(estado=True)|Q(estado=None))

class contador(ListView):
    template_name='app/contador.html'
    model=Denuncia_m

def Noticia(request,pk):
    
    ctx=Denuncia_m.objects.raw("select * from app_denuncia_m o where o.id='%s'"%(pk))
    ctx2=imagenes_m.objects.raw("select * from app_imagenes_m o where o.denunciaA_id='%s'"%(pk))
    ctx3=videos_m.objects.raw("select * from app_videos_m o where o.denunciaB_id='%s'"%(pk))
    ctx4=Comentario_m.objects.raw("select * from app_comentario_m o where o.denuncia_id='%s'"%(pk))
    #ctx5=Usuario_m.objects.raw("select * from app_usuario_m")
    ctx5=Usuario_m.objects.raw("select u.id,c.id,a.id, u.username,c.comentario,a.Avatar,a.Nombre_id from  auth_user u, app_comentario_m c,app_usuario_m a where c.denuncia_id='%s' and a.Nombre_id=c.user_id  and u.id=a.Nombre_id"%(pk))
    cont=0

    form=Comentario_form(request.POST or None,request.FILES or None)
    if request.method == "POST":
            if form.is_valid():
                instance=form.save(commit=False)
                #user=user.id
                user = form.cleaned_data.get("user")
                denuncia = form.cleaned_data.get("denuncia")
                #denuncia=pk
                comentario = form.cleaned_data.get("comentario")
                form.save()
    #1.6.3 Reportes
    reputacion(request, pk)
    #fin reportes
    #1.6.1 Likes, rangos

    x,ninguno,favor,ob_favor, ob_contra, reportado=consultaVotos(request, pk)

    favor_form=Favor_f(request.POST or None)
    contra_form=Contra_f(request.POST or None)
    #1.6.3 Reportes
    reportes_form=Reportados_f(request.POST or None)
    #Fin 1.6.3
    if request.method == "POST":
        user = User.objects.get(id=request.user.id)

        if 'favor' in request.POST:
            if favor_form.is_valid():
                if not ob_contra:
                    f=favor_form.save(commit=False)
                    f.denuncia_id=pk
                    f.usuario_id=request.user.id
                    f.save()
                else:
                    Contra_m.objects.filter(usuario=request.user.id, denuncia=pk).delete() 
                    f=favor_form.save(commit=False)
                    f.denuncia_id=pk
                    f.usuario_id=request.user.id
                    f.save()
        if 'contra' in request.POST:
            if contra_form.is_valid():
                if not ob_favor:

                    c=contra_form.save(commit=False)
                    c.denuncia_id=pk
                    c.usuario_id=request.user.id
                    c.save()
                else:
                    Favor_m.objects.filter(usuario=request.user.id, denuncia=pk).delete()
                    c=contra_form.save(commit=False)
                    c.denuncia_id=pk
                    c.usuario_id=request.user.id
                    c.save()
        if 'reportar' in request.POST:
            if reportes_form.is_valid():
                r=reportes_form.save(commit=False)
                r.denuncia_id=pk
                r.usuario_id=request.user.id
                r.save()
                Denuncia_m.objects.filter(pk=pk).update(reportado=True)
    x,ninguno,favor,ob_favor, ob_contra, reportado=consultaVotos(request, pk)
    #fin 1.6.2
    #1.6.3 Reportes
    nivel=reputacion(request, pk)
    #fin reportes
    return render(request,'app/noticia.html',{'ctx':ctx,'ctx2':ctx2,'ctx3':ctx3,'ctx4':ctx4,'ctx5':ctx5,'form':form,'pk':pk, 'favor_f':favor_form, 'contra_f':contra_form, 'x':x, 'ninguno':ninguno, 'favor':favor, 'reportado':reportado, 'reportes_f':reportes_form,'nivel':nivel})
#1.6.2 Votos

    return render(request,'app/noticia.html',{'ctx':ctx,'ctx2':ctx2,'ctx3':ctx3,'ctx4':ctx4,'ctx5':ctx5,'form':form,'pk':pk,'cont':cont})

def consultaVotos(request, pk):
    #1.6.3 Reportes
    ob_reportes=Reportados_m.objects.filter(usuario=request.user.id, denuncia=pk)
    #fin 1.6.3
    ob_favor=Favor_m.objects.filter(usuario=request.user.id, denuncia=pk)
    ob_contra=Contra_m.objects.filter(usuario=request.user.id, denuncia=pk)
    ninguno=True
    favor=True
    reportado=False
    if not  ob_favor and not ob_contra:
        x=1
        ninguno=False
    else:
        if not ob_contra:
            if ob_favor[0].usuario_id == request.user.id:
                x=2
                favor=True
        else:
            if ob_contra[0].usuario_id == request.user.id:
                x=3
                favor=False
    if not ob_reportes:
        reportado=False
    elif ob_reportes[0].usuario_id == request.user.id:
        reportado=True
        
    return x,ninguno, favor, ob_favor, ob_contra, reportado
#Fin 1.6.2
#1.6.3 Reportes
def reputacion(request, pk):
    usuario_reportado=Denuncia_m.objects.filter(id=pk)
    usuario_r_id=usuario_reportado[0].user_id
    buenos=Favor_m.objects.filter(denuncia__user=usuario_r_id).count()
    malos_contra=Contra_m.objects.filter(denuncia__user=usuario_r_id).count()
    malos_reportados=Reportados_m.objects.filter(denuncia__user=usuario_r_id).count()
    malos=malos_contra+(malos_reportados*10)

    try:
        nivel=buenos*100/(malos+buenos)
    except:
        nivel=0
    return nivel
#fin 1.6.3

def PerfilUser(request):
    ctx=Usuario_m.objects.raw("select * from app_usuario_m o where o.Nombre_id='%s'"%(request.user.id))
    actualizar=Usuario_m.objects.filter(Nombre_id=request.user.id)
    return render(request,'app/perfiluser.html',{'ctx':ctx,'actualizar':actualizar})
    

def Perfil(request,pk):
    
    if str(pk)==str(request.user.id):
        return HttpResponseRedirect(reverse("perfilUser_view"))

    usuario=Usuario_m.objects.raw("select o.id,o.first_name,o.last_name,o.email,o.username,a.id,a.Avatar from auth_user o, app_usuario_m a where o.id='%s' and a.Nombre_id='%s'"%(pk,pk))

    publicaciones=Denuncia_m.objects.raw("select * from app_denuncia_m d, app_imagenes_m i where d.user_id='%s' and i.denunciaA_id=d.id"%(pk))

    return render(request,'app/perfil.html',{'usuario':usuario,'publicaciones':publicaciones})


def Perfil_respaldo(request,pk):
    ctx=Comentario_m.objects.raw("select * from auth_user o where o.id='%s'"%(pk))
    ctx2=Usuario_m.objects.raw("select * from app_usuario_m o where o.nombre_id='%s'"%(pk))
    ctx3=Denuncia_m.objects.all()
    
    
    desicion=False		
    
    for a in ctx:
        for b in ctx2:
            if str(a.id)==str(pk) and str(b.Nombre_id)==str(pk):
                desicion=True #Actualizar
            else:
                desicion=False # Registrar

    
    return render(request,'app/perfil.html',{'ctx':ctx,'ctx2':ctx2,'ctx3':ctx3,'desicion':desicion})


#Sirve para actualizar el perfil pero ya debe de estar creado
class UpdatePerfil(UpdateView):
    template_name='app/actualizar.html'
    model=Usuario_m
    fields=['Telefono','Direccion','Avatar']
    success_url = reverse_lazy("perfilUser_view")


''' class RegisterPerfil(CreateView):
    template_name='app/registrar.html'
    model=Usuario_m
    fields= "__all__"
    success_url = reverse_lazy("mapa_view") '''

def insertar(request):
    id_usuario=request.user.id
    consulta=Usuario_m.objects.filter(Nombre=id_usuario)
    
    if not consulta:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO app_usuario_m(Telefono,Direccion,Avatar,Nombre_id) VALUES ('%s','%s','%s','%s')"%( None,None ,None ,id_usuario))

    return HttpResponseRedirect(reverse("mapa_view"))
    

''' 

def insertar_respaldo(request):
    id_usuario=request.user.id
    consulta=Usuario_m.objects.filter(Nombre=id_usuario)
    
    if not consulta:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO app_usuario_m(Telefono,Direccion,Avatar,Nombre_id) VALUES ('%s','%s','%s','%s')"%('NULL','NULL','NULL',id_usuario))

    return HttpResponseRedirect(reverse("mapa_view"))


     '''
        
