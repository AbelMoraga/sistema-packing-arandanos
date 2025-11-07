from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import PalletForm
from .models import Pallet, GrupoProceso, Distribuidor, TipoPocillo, Linea, GrupoProceso, GrupoTerminado
from django.contrib.auth import logout



# LOGIN
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

    return render(request, "packing/base.html")

#  Registrar pallets (Recepción)
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


#  Vista de recepción (pallets registrados)
def lista_pallets(request):
    pallets = Pallet.objects.all().order_by('bloqueado_recepcion', '-id')
    return render(request, 'packing/lista_pallets.html', {'pallets': pallets})


#  Actualizar estados de recepción o proceso
def actualizar_estado(request, id):
    pallet = get_object_or_404(Pallet, id=id)
    accion = request.GET.get('accion')
    origen = request.GET.get('origen', 'pallets')

    # --- BLOQUEO RECEPCIÓN ---
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

    #  BLOQUEO PROCESOS 
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


def lista_procesos(request):
    pallets = Pallet.objects.filter(pre_procesos=True).order_by('bloqueado_proceso', 'procesado', '-id')
    return render(request, 'packing/lista_procesos.html', {'pallets': pallets})


#  Crear grupo manualmente
def crear_grupo_proceso(request):
    if request.method == 'POST':
        seleccionados = request.POST.getlist('pallets_seleccionados')

       
        if not seleccionados:
            messages.error(request, "Debes seleccionar al menos un pallet.")
            return redirect('lista_procesos')

        pallets = Pallet.objects.filter(id__in=seleccionados)

      
        if any(p.grupo for p in pallets):
            messages.error(request, "Uno o más pallets ya pertenecen a un grupo existente. No se pueden reagrupar.")
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

#procesos
def menu_procesos(request):
    return render(request, 'packing/menu_procesos.html')
#salir
def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente 👋")
    return redirect("login")



#pallets tereminados



def pallet_terminado(request):
    if request.method == 'POST':
        grupo_proceso_id = request.POST.get('grupo_proceso')
        distribuidor_id = request.POST.get('distribuidor')
        tipo_pocillo_id = request.POST.get('tipo_pocillo')
        linea_id = request.POST.get('linea')
        cantidad_cajas = request.POST.get('cantidad')

        grupo_proceso = GrupoProceso.objects.get(id=grupo_proceso_id)
        distribuidor = Distribuidor.objects.get(id=distribuidor_id)
        tipo_pocillo = TipoPocillo.objects.get(id=tipo_pocillo_id)
        linea = Linea.objects.get(id=linea_id)

        GrupoTerminado.objects.create(
            grupo_proceso=grupo_proceso,
            distribuidor=distribuidor,
            tipo_pocillo=tipo_pocillo,
            linea=linea,
            cantidad_cajas=cantidad_cajas,
        )

        messages.success(request, "✅ Pallet terminado registrado correctamente.")
        return redirect('menu_procesos')

    # Si es GET 
    grupos = GrupoProceso.objects.all()
    distribuidores = Distribuidor.objects.all()
    tipos_pocillo = TipoPocillo.objects.all()
    lineas = Linea.objects.all()

    return render(request, 'packing/pallet_terminado.html', {
        'grupos': grupos,
        'distribuidores': distribuidores,
        'tipos_pocillo': tipos_pocillo,
        'lineas': lineas
    })