from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages

from .models import ( City, Country, Directed, Title, Sponsor, Correspondence, Income, Godfather
)
from .forms import (CityForm, CountryForm, DirectedForm, TitleForm,SponsorForm, CorrespondenceForm, IncomeForm, GodfatherForm
)

def sponsors_dashboard(request):
    """Vista principal del Dashboard de Sponsors."""
    return render(request, 'sponsors/dashboard.html')

def add_city(request):
    """Maneja la creación de una nueva ciudad."""
    city_list = City.objects.all()

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ciudad agregada correctamente.')
            return redirect('sponsors:add_city')
        else:
            messages.error(request, 'Error al agregar la ciudad.')
    else:
        form = CityForm()

    return render(request, 'sponsors/form_city.html', {'form': form, 'city_list': city_list})

def add_country(request):
    """Maneja la creación de un nuevo país."""
    countries = Country.objects.all()

    if request.method == 'POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'País agregado correctamente.')
            return redirect('sponsors:add_country')
        else:
            messages.error(request, 'Error al agregar el país.')
    else:
        form = CountryForm()

    return render(request, 'sponsors/form_country.html', {'form': form, 'countries': countries})

def add_directed(request):
    """Maneja la creación de un registro en Directed."""
    directed_list = Directed.objects.all()

    if request.method == 'POST':
        form = DirectedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro agregado correctamente.')
            return redirect('sponsors:add_directed')
        else:
            messages.error(request, 'Error al agregar el registro.')
    else:
        form = DirectedForm()

    return render(request, 'sponsors/form_directed.html', {'form': form, 'directed_list': directed_list})

def add_title(request):
    """Maneja la creación de un registro en Title."""
    title_list = Title.objects.all()

    if request.method == 'POST':
        form = TitleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Título agregado correctamente.')
            return redirect('sponsors:add_title')
        else:
            messages.error(request, 'Error al agregar el título.')
    else:
        form = TitleForm()

    return render(request, 'sponsors/form_title.html', {'form': form, 'title_list': title_list})

def sponsor_list(request):
    """Muestra la lista de todos los sponsors registrados."""
    sponsors = Sponsor.objects.all()
    return render(request, "sponsors/form_sponsor.html", {"sponsors": sponsors})

def get_sponsor_data(request):
    """Retorna en JSON todos los datos de un Sponsor, para llenar el formulario."""
    sponsor_id = request.GET.get('id', None)
    if not sponsor_id:
        return JsonResponse({'error': 'ID no proporcionado'}, status=400)

    try:
        sponsor = Sponsor.objects.select_related('city').get(id=sponsor_id)
    except Sponsor.DoesNotExist:
        return JsonResponse({'error': 'Sponsor no encontrado'}, status=404)

    data = {
        'id': sponsor.id,
        'title_id': sponsor.title_id if sponsor.title else '',
        'directed_id': sponsor.directed_id if sponsor.directed else '',
        'last_name_1': sponsor.last_name_1 or '',
        'last_name_2': sponsor.last_name_2 or '',
        'first_name_1': sponsor.first_name_1 or '',
        'first_name_2': sponsor.first_name_2 or '',
        'free_union': sponsor.free_union,
        'contact': sponsor.contact or '',
        'annex': sponsor.annex or '',
        'address': sponsor.address or '',
        'street': sponsor.street or '',
        'phone_1': sponsor.phone_1 or '',
        'phone_2': sponsor.phone_2 or '',
        'email': sponsor.email or '',
        'email_2': sponsor.email_2 or '',
        'language': sponsor.language or '',
        'profession': sponsor.profession or '',
        'date_of_birth': sponsor.date_of_birth.strftime('%Y-%m-%d') if sponsor.date_of_birth else '',
        'gender': sponsor.gender or '',
        'nationality': sponsor.nationality or '',
        'civil_status': sponsor.civil_status or '',
        'addressed_to': sponsor.addressed_to or '',
        'first_contact': sponsor.first_contact.strftime('%Y-%m-%d') if sponsor.first_contact else '',
        'last_contact': sponsor.last_contact.strftime('%Y-%m-%d') if sponsor.last_contact else '',
        'note_1': sponsor.note_1 or '',
        'note_2': sponsor.note_2 or '',
        'deceased': sponsor.deceased,
        'deactivated': sponsor.deactivated,
        'bad_address': sponsor.bad_address,
        'private': sponsor.private,
        'godfather': sponsor.godfather,
        'sponsor': sponsor.sponsor,
        'member': sponsor.member,
        'former_volunteer': sponsor.former_volunteer,
        'member': sponsor.member,
    }

    # Ciudad => zip_code, country
    if sponsor.city:
        data['city_id'] = sponsor.city.id
        data['zip_code'] = sponsor.city.zip_code or ''
        data['country'] = sponsor.city.country.name if sponsor.city.country else ''
    else:
        data['city_id'] = ''
        data['zip_code'] = ''
        data['country'] = ''

    return JsonResponse(data, safe=False)

def add_sponsor(request):
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

    cities = City.objects.select_related('country').all()
    
    # 🔽 Ordenar sponsors por nombre y apellido
    sponsors = Sponsor.objects.select_related('city').order_by('first_name_1', 'last_name_1')

    return render(
        request,
        "sponsors/form_sponsor.html",
        {
            "form": form,
            "cities": cities,
            "sponsors": sponsors,
        },
    )

def edit_sponsor(request, sponsor_id):
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

    cities = City.objects.select_related('country').all()
    sponsors = Sponsor.objects.select_related('city').all()

    return render(
        request,
        "sponsors/form_sponsor.html",
        {
            "form": form,
            "edit_mode": True,
            "sponsor": sponsor,
            "cities": cities,
            "sponsors": sponsors,  # 👈 mismo truco para buscadores aquí
        },
    )

def delete_sponsor(request, sponsor_id):
    """Maneja la eliminación de un sponsor."""
    sponsor = get_object_or_404(Sponsor, id=sponsor_id)
    sponsor.delete()
    messages.success(request, "Sponsor eliminado correctamente.")
    return redirect("sponsors:sponsor_list")

def add_correspondence(request):
    """Formulario para agregar Correspondencia."""
    if request.method == "POST":
        form = CorrespondenceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Correspondencia agregada correctamente.")
            return redirect('sponsors:sponsors_dashboard')
        else:
            messages.error(request, "Error al agregar correspondencia.")
    else:
        form = CorrespondenceForm()

    return render(request, 'sponsors/form_correspondence.html', {'form': form})

def add_godfather(request):
    """Formulario para agregar un Godfather (Padrino)."""
    if request.method == "POST":
        form = GodfatherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Godfather agregado correctamente.")
            return redirect('sponsors:sponsors_dashboard')
        else:
            messages.error(request, "Error al agregar Godfather.")
    else:
        form = GodfatherForm()

    return render(request, 'sponsors/form_godfather.html', {'form': form})

def add_income(request):
    """Formulario para agregar Income (Ingreso)."""
    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Income agregado correctamente.")
            return redirect('sponsors:sponsors_dashboard')
        else:
            messages.error(request, "Error al agregar Income.")
    else:
        form = IncomeForm()

    return render(request, 'sponsors/form_income.html', {'form': form})

def search_name(request):
    """Retorna lista con el primer nombre de sponsors que coincidan con la búsqueda."""
    query = request.GET.get('q', '')
    results = Sponsor.objects.filter(first_name_1__icontains=query).values_list('first_name_1', flat=True)
    return JsonResponse(list(results), safe=False)

def search_lastname(request):
    """Retorna lista con el primer apellido de sponsors que coincidan con la búsqueda."""
    query = request.GET.get('q', '')
    results = Sponsor.objects.filter(last_name_1__icontains=query).values_list('last_name_1', flat=True)
    return JsonResponse(list(results), safe=False)

def search_id(request):
    """Retorna lista con el ID de sponsors que coincidan con la búsqueda."""
    query = request.GET.get('q', '')
    results = Sponsor.objects.filter(id__icontains=query).values_list('id', flat=True)
    return JsonResponse(list(results), safe=False)