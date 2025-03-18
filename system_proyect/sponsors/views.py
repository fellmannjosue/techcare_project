from django.shortcuts import render, redirect,get_object_or_404
from .models import City, Country, Directed, Title,Sponsor,Correspondence,Income,Godfather
from .forms import CityForm, CountryForm, DirectedForm, TitleForm,SponsorForm,CorrespondenceForm,IncomeForm, GodfatherForm

from django.contrib import messages

def sponsors_dashboard(request):
    """ Vista principal del Dashboard de Sponsors """
    return render(request, 'sponsors/dashboard.html')

def add_city(request):
    city_list = City.objects.all()  # Obtener todas las ciudades

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ciudad agregada correctamente.')
            return redirect('sponsors:add_city')  # Recargar la página
        else:
            messages.error(request, 'Error al agregar la ciudad.')

    else:
        form = CityForm()

    return render(request, 'sponsors/form_city.html', {'form': form, 'city_list': city_list})

def add_country(request):
    countries = Country.objects.all()  # Obtener todos los registros de la BD

    if request.method == 'POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'País agregado correctamente.')
            return redirect('sponsors:add_country')  # Recargar la página para ver el nuevo país
        else:
            messages.error(request, 'Error al agregar el país.')

    else:
        form = CountryForm()

    return render(request, 'sponsors/form_country.html', {'form': form, 'countries': countries})

def add_directed(request):
    directed_list = Directed.objects.all()  # Obtener todos los registros de la BD

    if request.method == 'POST':
        form = DirectedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro agregado correctamente.')
            return redirect('sponsors:add_directed')  # Recargar la página para ver los nuevos datos
        else:
            messages.error(request, 'Error al agregar el registro.')

    else:
        form = DirectedForm()

    return render(request, 'sponsors/form_directed.html', {'form': form, 'directed_list': directed_list})

def add_title(request):
    title_list = Title.objects.all()  # Obtener todos los registros de la BD

    if request.method == 'POST':
        form = TitleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Título agregado correctamente.')
            return redirect('sponsors:add_title')  # Recargar la página
        else:
            messages.error(request, 'Error al agregar el título.')

    else:
        form = TitleForm()

    return render(request, 'sponsors/form_title.html', {'form': form, 'title_list': title_list})


def sponsor_list(request):
    """Muestra la lista de todos los sponsors registrados."""
    sponsors = Sponsor.objects.all()
    return render(request, "sponsors/form_sponsor.html", {"sponsors": sponsors})

def add_sponsor(request):
    """Maneja la creación de un nuevo sponsor."""
    if request.method == "POST":
        form = SponsorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sponsor agregado correctamente.")
            return redirect("sponsors:sponsor_list")
        else:
            messages.error(request, "Error al agregar el sponsor. Revisa los campos.")
    else:
        form = SponsorForm()

    return render(request, "sponsors/form_sponsor.html", {"form": form})

def edit_sponsor(request, sponsor_id):
    """Maneja la edición de un sponsor existente."""
    sponsor = get_object_or_404(Sponsor, id=sponsor_id)
    
    if request.method == "POST":
        form = SponsorForm(request.POST, instance=sponsor)
        if form.is_valid():
            form.save()
            messages.success(request, "Sponsor actualizado correctamente.")
            return redirect("sponsors:sponsor_list")
        else:
            messages.error(request, "Error al actualizar el sponsor.")
    else:
        form = SponsorForm(instance=sponsor)

    return render(request, "sponsors/form_sponsor.html", {"form": form, "edit_mode": True, "sponsor": sponsor})

def delete_sponsor(request, sponsor_id):
    """Maneja la eliminación de un sponsor."""
    sponsor = get_object_or_404(Sponsor, id=sponsor_id)
    sponsor.delete()
    messages.success(request, "Sponsor eliminado correctamente.")
    return redirect("sponsors:sponsor_list")

# Formulario para agregar Correspondencia
def add_correspondence(request):
    if request.method == "POST":
        form = CorrespondenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sponsors:sponsors_dashboard')  # Redirige al dashboard
    else:
        form = CorrespondenceForm()

    return render(request, 'sponsors/form_correspondence.html', {'form': form})

# Formulario para agregar un Godfather (Padrino)
def add_godfather(request):
    if request.method == "POST":
        form = GodfatherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sponsors:sponsors_dashboard')  # Redirige al dashboard
    else:
        form = GodfatherForm()

    return render(request, 'sponsors/form_godfather.html', {'form': form})

# Formulario para agregar Income (Ingreso)
def add_income(request):
    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sponsors:sponsors_dashboard')  # Redirige al dashboard
    else:
        form = IncomeForm()

    return render(request, 'sponsors/form_income.html', {'form': form})