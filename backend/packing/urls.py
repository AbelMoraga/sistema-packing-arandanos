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
    path('pallets_terminados/', views.lista_pallets_terminados, name='lista_pallets_terminados'),
    path('iqf/', views.registrar_iqf_descarte, name='registrar_iqf_descarte'),
    path('menu_control/', views.menu_control, name='menu_control'),
    path('control/reportes/', views.control_reportes, name='control_reportes'),
    path('control/graficos/', views.control_graficos, name='control_graficos'),
    path('control/pallets/', views.control_pallets, name='control_pallets'),
    path("control/pallets_terminados/", views.control_pallets_terminados, name="control_pallets_terminados"),
    path("panel-admin/", views.panel_admin, name="panel_admin"),
    path("panel-admin/editar/<str:modelo>/<int:id>/", views.panel_admin_editar, name="panel_admin_editar"),
    path("panel/admin/usuarios/", views.panel_admin_usuarios, name="panel_admin_usuarios"),
    path("panel/admin/usuarios/crear/", views.panel_admin_crear_usuario, name="panel_admin_crear_usuario"),
    path("panel/admin/usuarios/eliminar/<int:id>/", views.panel_admin_eliminar_usuario, name="panel_admin_eliminar_usuario"),
    path("panel/admin/usuarios/editar/<int:id>/", views.panel_admin_editar_usuario, name="panel_admin_editar_usuario"),
    path("control/iqf/dashboard/", views.iqf_dashboard, name="iqf_dashboard"),
    path("control/iqf/lista/", views.lista_iqf_full, name="lista_iqf_full"),
    path("control/iqf/<int:id>/", views.detalles_iqf, name="detalles_iqf"),
    path("control/iqf/lista/", views.control_iqf_lista, name="control_iqf_lista"),
    path(
    "panel-admin/actividad/",
    views.panel_admin_actividad,
    name="panel_admin_actividad"
    ),
    path(
    "control/pallets-terminados/",
    views.control_pallets_terminados,
    name="control_pallets_terminados"
    ),
    path("control/exportar/", views.control_exportar, name="control_exportar"),
    path("control/exportar/pallets/", views.exportar_pallets_terminados_excel, name="exportar_pallets_terminados_excel"),
    path("control/exportar/iqf/", views.exportar_iqf_excel, name="exportar_iqf_excel"),
    path("control/exportar/recepcion/", views.exportar_recepcion_excel, name="exportar_recepcion_excel"),
    path("control/exportar/procesos/", views.exportar_procesos_csv, name="exportar_procesos_csv"),
    path("control/graficos/", views.control_graficos, name="control_graficos"),
    path("frio/iqf/", views.lista_iqf_frio, name="lista_iqf_frio"),
    path("frio/iqf/despachar/<int:id>/", views.despachar_iqf_frio, name="despachar_iqf_frio"),


]
