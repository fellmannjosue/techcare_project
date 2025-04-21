from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages

from .models import ( City, Country, Directed, Title, Sponsor, Correspondence, Income, Godfather,Sponsored,Descr_Godfather
)
from .forms import (CityForm, CountryForm, DirectedForm, TitleForm,SponsorForm, CorrespondenceForm, IncomeForm, GodfatherForm, SponsoredForm, DescrGodfatherForm
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
    sponsor_id = request.GET.get('id', None)
    if not sponsor_id:
        return JsonResponse({'error': 'ID no proporcionado'}, status=400)

    try:
        sponsor = Sponsor.objects.select_related('city', 'city__country').get(id=sponsor_id)
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
        'profession': sponsor.profession or '',
        'address': sponsor.address or '',
        'street': sponsor.street or '',
        'phone_1': sponsor.phone_1 or '',
        'phone_2': sponsor.phone_2 or '',
        'fax': sponsor.fax or '',
        'email': sponsor.email or '',
        'email_2': sponsor.email_2 or '',
        'email_3': sponsor.email_3 or '',

        'report_email': sponsor.report_email,
        'only_email': sponsor.only_email,
        'only_easter_rep': sponsor.only_easter_rep,
        'financial_report': sponsor.financial_report,

        'language': sponsor.language or '',
        'annex': sponsor.annex or '',
        'contact': sponsor.contact or '',
        'addressed_to': sponsor.addressed_to or '',
        'addressed_to_2': sponsor.addressed_to_2 or '',

        'visitor': sponsor.visitor,
        'visitor_date': sponsor.visitor_date.strftime('%Y-%m-%d') if sponsor.visitor_date else '',
        'sponsor_bool': sponsor.sponsor,
        'godfather': sponsor.godfather,
        'member': sponsor.member,
        'former_volunteer': sponsor.former_volunteer,
        'volunt_dep_date': sponsor.volunt_dep_date.strftime('%Y-%m-%d') if sponsor.volunt_dep_date else '',

        'no_correspondence': sponsor.no_correspondence,
        'deceased': sponsor.deceased,
        'deactivated': sponsor.deactivated,
        'expect_reaction': sponsor.expect_reaction,
        'bad_address': sponsor.bad_address,
        'private': sponsor.private,

        'first_contact': sponsor.first_contact.strftime('%Y-%m-%d') if sponsor.first_contact else '',
        'last_contact': sponsor.last_contact.strftime('%Y-%m-%d') if sponsor.last_contact else '',

        'note_1': sponsor.note_1 or '',
        'note_2': sponsor.note_2 or '',

        'date_of_birth': sponsor.date_of_birth.strftime('%Y-%m-%d') if sponsor.date_of_birth else '',
        'date_of_birth_2': sponsor.date_of_birth_2.strftime('%Y-%m-%d') if sponsor.date_of_birth_2 else '',

        'gender': sponsor.gender or '',
        'civil_status': sponsor.civil_status or '',
        'nationality': sponsor.nationality or '',

        'imprimir': sponsor.imprimir,
        'deactivate_soon': sponsor.deactivate_soon,
        'recog_2010': sponsor.recog_2010,
        'recog_2020_blanket': sponsor.recog_2020_blanket,
        'recog_2020_plate': sponsor.recog_2020_plate,
        'padrino_ch_d': sponsor.padrino_ch_d or '',
    }

    # Ciudad + Código Postal + País
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

def add_sponsored(request):
    """Formulario para agregar un Sponsored (Apadrinado)."""
    if request.method == "POST":
        form = SponsoredForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Apadrinado agregado correctamente.")
            return redirect('sponsors:sponsors_dashboard')
        else:
            messages.error(request, "Error al agregar Apadrinado.")
    else:
        form = SponsoredForm()

    return render(request, 'sponsors/form_sponsored.html', {'form': form})

def add_descr_godfather(request):
    """Formulario para agregar una Descripción de Padrino."""
    if request.method == "POST":
        form = DescrGodfatherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Descripción de Padrino agregada correctamente.")
            return redirect('sponsors:sponsors_dashboard')
        else:
            messages.error(request, "Error al agregar Descripción de Padrino.")
    else:
        form = DescrGodfatherForm()

    return render(request, 'sponsors/form_descr_godfather.html', {'form': form})

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