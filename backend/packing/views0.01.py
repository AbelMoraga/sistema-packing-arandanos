from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.db.models import Q, Sum, Count, DecimalField, Value, F
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.functions import Coalesce




from .forms import PalletForm
from .models import (
    Pallet,
    GrupoProceso,
    Distribuidor,
    TipoPocillo,
    Linea,
    PalletTerminado,
    IQFDescarte
)


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        print(f"Intentando login con: {username}")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f"Autenticado como: {user.username}")
            print(f"Grupos: {user.groups.all()}")

            if user.groups.filter(name="Frio").exists():
                messages.success(request, "Bienvenido al área de Frío ❄️")
                return redirect("menu_frio")
            elif user.groups.filter(name="Procesos").exists():
                messages.success(request, "Bienvenido al área de Procesos ⚙️")
                return redirect("menu_procesos")
            elif user.groups.filter(name="Control").exists():
                messages.success(request, "Bienvenido al área de Control 📊")
                return redirect("menu_control")
            elif user.groups.filter(name="Admin_local").exists():
                return redirect("admin:index")
            else:
                messages.error(request, "No tienes un rol asignado.")
                return redirect("login")
        else:
            messages.error(request, "Usuario o contraseña incorrectos ❌")
            return redirect("login")

    return render(request, "packing/base.html")


# Rp
def registrar_pallets_entrada(request):
    if request.method == 'POST':
        form = PalletForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'packing/success.html')
    else:
        form = PalletForm()
    return render(request, 'packing/registrar_pallets_entrada.html', {'form': form})

def success(request):
    return render(request, 'packing/success.html')

def lista_pallets(request):
    pallets = Pallet.objects.all().order_by('bloqueado_recepcion', '-id')
    return render(request, 'packing/lista_pallets.html', {'pallets': pallets})

#ACTUALIZAR ESTADOS
def actualizar_estado(request, id):
    pallet = get_object_or_404(Pallet, id=id)
    accion = request.GET.get('accion')
    origen = request.GET.get('origen', 'pallets')


    if origen == 'pallets' and not pallet.bloqueado_recepcion:
        if accion == 'enfriado':
            pallet.enfriado = not pallet.enfriado
        elif accion == 'fumigado' and not pallet.organico:
            pallet.fumigado = not pallet.fumigado
        elif accion == 'preprocesos':
            pallet.pre_procesos = not pallet.pre_procesos
        elif accion == 'organico':
            pallet.organico = True
            pallet.fumigado = False
        elif accion == 'guardar':
            pallet.bloqueado_recepcion = True  
        pallet.save()
        return redirect('lista_pallets')

    #PROCESOS
    elif origen == 'procesos':
        if not pallet.bloqueado_proceso:
            if accion == 'procesado':
                pallet.procesado = not pallet.procesado
                pallet.save()
                return redirect(request.META.get('HTTP_REFERER', 'lista_procesos'))
            elif accion == 'guardar_proceso':
                if pallet.procesado:
                    pallet.bloqueado_proceso = True  
                    pallet.save()
                    return redirect('lista_procesos')

    return redirect('lista_procesos' if origen == 'procesos' else 'lista_pallets')

#procesos
def lista_procesos(request):
    pallets = Pallet.objects.filter(pre_procesos=True).order_by('bloqueado_proceso', 'procesado', '-id')
    return render(request, 'packing/lista_procesos.html', {'pallets': pallets})

def crear_grupo_proceso(request):
    if request.method == 'POST':
        seleccionados = request.POST.getlist('pallets_seleccionados')

        if not seleccionados:
            messages.error(request, "Debes seleccionar al menos un pallet.")
            return redirect('lista_procesos')

        pallets = Pallet.objects.filter(id__in=seleccionados)
        if any(p.grupo for p in pallets):
            messages.error(request, "Uno o más pallets ya pertenecen a un grupo existente.")
            return redirect('lista_procesos')

        productores = set(p.productor for p in pallets)
        variedades = set(p.variedad for p in pallets)

        if len(productores) > 1 or len(variedades) > 1:
            messages.error(request, "Solo puedes agrupar pallets con el mismo productor y variedad.")
            return redirect('lista_procesos')

        grupo = GrupoProceso.objects.create(
            productor=pallets[0].productor,
            variedad=pallets[0].variedad
        )

        for p in pallets:
            p.grupo = grupo
            p.save()

        messages.success(request, f"✅ Grupo {grupo.id_grupo} creado correctamente con {len(pallets)} pallets.")
        return redirect('lista_procesos')

    return redirect('lista_procesos')


def menu_frio(request):
    return render(request, 'packing/menu_frio.html')

def menu_procesos(request):
    return render(request, 'packing/menu_procesos.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente 👋")
    return redirect("login")


def pallet_terminado(request):
    distribuidores = Distribuidor.objects.all()
    tipos_pocillo = TipoPocillo.objects.all()
    lineas = Linea.objects.all()
    grupos = GrupoProceso.objects.all()

    if request.method == 'POST':
        distribuidor_id = request.POST.get('distribuidor')
        tipo_pocillo_id = request.POST.get('tipo_pocillo')
        linea_id = request.POST.get('linea')
        cantidad = request.POST.get('cantidad')
        calidad_color = request.POST.get('calidad')

        if not (distribuidor_id and tipo_pocillo_id and linea_id and cantidad and calidad_color):
            messages.error(request, "⚠️ Todos los campos son obligatorios.")
            return render(request, 'packing/pallet_terminado.html', {
                'distribuidores': distribuidores,
                'tipos_pocillo': tipos_pocillo,
                'lineas': lineas,
                'grupos': grupos,
            })

        calidad_dict = {
            'rojo': 'Rechazado',
            'amarillo': 'Baja',
            'verde': 'Buena',
            'azul': 'Excelente'
        }
        calidad = calidad_dict.get(calidad_color, 'Sin definir')

        PalletTerminado.objects.create(
            distribuidor_id=distribuidor_id,
            tipo_pocillo_id=tipo_pocillo_id,
            linea_id=linea_id,
            cantidad_cajas=cantidad,
            calidad=calidad
        )

        messages.success(request, f"✅ Pallet registrado con calidad: {calidad}")
        return redirect('pallet_terminado')

    return render(request, 'packing/pallet_terminado.html', {
        'distribuidores': distribuidores,
        'tipos_pocillo': tipos_pocillo,
        'lineas': lineas,
        'grupos': grupos,
    })


def registrar_iqf_descarte(request):
    grupos_disponibles = GrupoProceso.objects.filter(iqfdescarte__isnull=True)

    if request.method == 'POST':
        print("📦 Datos POST recibidos:", request.POST)

        grupo_id = request.POST.get('grupo_proceso', '').strip()
        peso_iqf = request.POST.get('peso_iqf', '').strip()
        peso_descarte = request.POST.get('peso_descarte', '').strip()

        if not grupo_id or not peso_iqf or not peso_descarte:
            messages.error(request, "⚠️ Completa todos los campos antes de guardar.")
            return render(request, 'packing/iqf.html', {'grupos': grupos_disponibles})

        try:
            grupo = GrupoProceso.objects.get(id_grupo=grupo_id)

            peso_iqf = float(peso_iqf.replace(',', '.'))
            peso_descarte = float(peso_descarte.replace(',', '.'))

            IQFDescarte.objects.create(
                grupo_proceso=grupo,
                peso_iqf=peso_iqf,
                peso_descarte=peso_descarte
            )

            messages.success(
                request,
                f"✅ IQF y Descarte registrados correctamente para el Grupo {grupo.id_grupo}"
            )

            grupos_disponibles = GrupoProceso.objects.filter(iqfdescarte__isnull=True)

            return render(
                request,
                'packing/iqf.html',
                {
                    'grupos': grupos_disponibles,
                    'peso_iqf': '',
                    'peso_descarte': ''
                }
            )

        except ValueError:
            messages.error(request, "⚠️ Los pesos deben ser números válidos (usa punto o coma).")

        except GrupoProceso.DoesNotExist:
            messages.error(request, "❌ El grupo seleccionado no existe.")

    return render(request, 'packing/iqf.html', {'grupos': grupos_disponibles})


def lista_pallets_terminados(request):
    pallets = PalletTerminado.objects.all().order_by('fecha')

    
    estado = request.GET.get('estado')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    buscar = request.GET.get('buscar', '').strip()  # ID o distribuidor

    if estado and estado != 'Todos':
        pallets = pallets.filter(estado__iexact=estado)
    if fecha_inicio:
        pallets = pallets.filter(fecha__date__gte=parse_date(fecha_inicio))
    if fecha_fin:
        pallets = pallets.filter(fecha__date__lte=parse_date(fecha_fin))
    if buscar:
        pallets = pallets.filter(
            Q(id__icontains=buscar) | Q(distribuidor__nombre__icontains=buscar)
        )
    

    cambiar_id = request.GET.get('cambiar_id')
    if cambiar_id:
        p = PalletTerminado.objects.get(id=cambiar_id)
        if p.estado == 'Por enviar':
            p.estado = 'Enviado'
            p.save()
        return redirect('lista_pallets_terminados')

    distribuidores = Distribuidor.objects.all()

    return render(request, 'packing/lista_pallets_terminados.html', {
        'pallets': pallets,
        'distribuidores': distribuidores,
    })

def es_control(user):
    """Verifica si el usuario pertenece al grupo 'Control'."""
    return user.groups.filter(name="Control").exists()

@login_required
@user_passes_test(es_control)
def menu_control(request):
    """Muestra el menú principal del área de Control."""
    return render(request, 'packing/menu_control.html')


#  GERENCIA 

@login_required
@user_passes_test(es_control)
def control_graficos(request):
    return render(request, 'packing/control/graficos.html')

@login_required
@user_passes_test(es_control)
def control_iqf(request):
    return render(request, 'packing/control/iqf.html')

@login_required
@user_passes_test(es_control)
def control_pallets(request):
    return render(request, 'packing/control/pallets.html')




@login_required
@user_passes_test(es_control)
def control_reportes(request):

    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    filtros = {}
    if fecha_inicio:
        filtros["fecha__date__gte"] = fecha_inicio
    if fecha_fin:
        filtros["fecha__date__lte"] = fecha_fin

    # RESÚMENES
    total_pallets = Pallet.objects.filter(**filtros).count()
    total_procesados = Pallet.objects.filter(procesado=True, **filtros).count()
    total_grupos = GrupoProceso.objects.filter(**filtros).count()
    total_terminados = PalletTerminado.objects.filter(**filtros).count()

    total_iqf = IQFDescarte.objects.filter(**filtros).aggregate(
        total=Sum("peso_iqf")
    )["total"] or 0

    total_descarte = IQFDescarte.objects.filter(**filtros).aggregate(
        total=Sum("peso_descarte")
    )["total"] or 0

    # GRÁFICO CALIDAD
    calidad_terminados = (
        PalletTerminado.objects.filter(**filtros)
        .values("calidad")
        .annotate(total=Count("id"))
    )

    # TABLA PRODUCTOR
    pallets_por_productor = (
        Pallet.objects.filter(**filtros)
        .values("productor__nombre")
        .annotate(total=Count("id"))
        .order_by("productor__nombre")
    )

    return render(request, "packing/control/reportes_partial.html", {
        "total_pallets": total_pallets,
        "total_procesados": total_procesados,
        "total_grupos": total_grupos,
        "total_terminados": total_terminados,
        "total_iqf": total_iqf,
        "total_descarte": total_descarte,
        "calidad_terminados": calidad_terminados,
        "pallets_por_productor": pallets_por_productor,
    })


    # --------------------------
    # SI ES AJAX → devolver parcial
    # --------------------------
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "packing/control/reportes_partial.html", context)

    # --------------------------
    # SI ES NORMAL → devolver página completa
    # --------------------------
    return render(request, "packing/control/reportes.html", context)

#parte compleja---------------------------------------------------------------------------------------------------


def iqf_lista(request):

    iqf = IQF.objects.all().order_by('-id')

    # ---- FILTROS ----
    
    # Buscar por grupo
    grupo = request.GET.get('grupo')
    if grupo:
        iqf = iqf.filter(grupo__id__icontains=grupo)

    # Estado
    estado = request.GET.get('estado')
    if estado == "en_iqf":
        iqf = iqf.filter(estado="EN_IQF")
    elif estado == "retirado":
        iqf = iqf.filter(estado="RETIRADO")

    # Variedad
    variedad = request.GET.get('variedad')
    if variedad and variedad != "todas":
        iqf = iqf.filter(variedad=variedad)

    # Rango de fechas
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    if fecha_inicio and fecha_fin:
        iqf = iqf.filter(fecha_ingreso__date__range=[fecha_inicio, fecha_fin])

    # En riesgo (+10 días)
    riesgo = request.GET.get('riesgo')
    if riesgo == "true":
        limite = datetime.now() - timedelta(days=10)
        iqf = iqf.filter(fecha_ingreso__lte=limite, estado="EN_IQF")

    # Dashboard
    total_en_iqf = IQF.objects.filter(estado="EN_IQF").count()
    total_retirados = IQF.objects.filter(estado="RETIRADO").count()
    total_riesgo = IQF.objects.filter(
        estado="EN_IQF",
        fecha_ingreso__lte=datetime.now() - timedelta(days=10)
    ).count()

    context = {
        'iqf': iqf,
        'total_en_iqf': total_en_iqf,
        'total_retirados': total_retirados,
        'total_riesgo': total_riesgo,
    }

    return render(request, 'iqf/iqf_lista.html', context)

def iqf_detalles(request, id):
    iqf = get_object_or_404(IQF, id=id)
    return render(request, 'iqf/iqf_detalles.html', {'i': iqf})