from .models import RegistroActividad

def registrar_actividad(request, accion, modulo, detalle=""):
    RegistroActividad.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        accion=accion,
        modulo=modulo,
        detalle=detalle
    )
