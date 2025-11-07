from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('menu/', views.menu_frio, name='menu_frio'),
    path('registrar/', views.registrar_pallets_entrada, name='registrar_pallets_entrada'),
    path('success/', views.success, name='success'),
    path('pallets/', views.lista_pallets, name='lista_pallets'),
    path('actualizar/<int:id>/', views.actualizar_estado, name='actualizar_estado'),
    path('procesos/', views.lista_procesos, name='lista_procesos'),
    path('procesos/crear_grupo/', views.crear_grupo_proceso, name='crear_grupo_proceso'),
    path('menu_procesos/', views.menu_procesos, name='menu_procesos'),
    path('pallet_terminado/', views.pallet_terminado, name='pallet_terminado'),
    
]
