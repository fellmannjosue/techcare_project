from django import template

register = template.Library()

DAY_NAMES = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]

@register.filter
def weekday_name(value):
    """
    Devuelve el nombre del día según índice 0–6.
    0=Lunes ... 6=Domingo. Si no está en rango, muestra '—'.
    """
    try:
        i = int(value)
        return DAY_NAMES[i] if 0 <= i <= 6 else "—"
    except Exception:
        return "—"
