from django import forms
from .models import City, Country, Directed, Title, Sponsor, Godfather, Correspondence,Income

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name', ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del país'}),
        }

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['zip_code', 'name', 'country']
        widgets = {
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el código postal'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre de la ciudad'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
        }

class DirectedForm(forms.ModelForm):
    class Meta:
        model = Directed
        fields = ['description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción'}),
        }

class TitleForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = ['description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el título'}),
        }

class SponsorForm(forms.ModelForm):
    class Meta:
        model = Sponsor
        exclude = ['city']  # ✅ EXCLUIMOS city para manejarlo manualmente en la vista

        widgets = {
            "title": forms.Select(attrs={"class": "form-control"}),
            "directed": forms.Select(attrs={"class": "form-control"}),
            "last_name_1": forms.TextInput(attrs={"class": "form-control"}),
            "last_name_2": forms.TextInput(attrs={"class": "form-control"}),
            "first_name_1": forms.TextInput(attrs={"class": "form-control"}),
            "first_name_2": forms.TextInput(attrs={"class": "form-control"}),
            "free_union": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "street": forms.TextInput(attrs={"class": "form-control"}),

            # "city" ya no está aquí 👇
            # "city": forms.Select(attrs={"class": "form-control"}),

            "phone_1": forms.TextInput(attrs={"class": "form-control"}),
            "phone_2": forms.TextInput(attrs={"class": "form-control"}),
            "fax": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "email_2": forms.EmailInput(attrs={"class": "form-control"}),
            "email_3": forms.EmailInput(attrs={"class": "form-control"}),

            "language": forms.TextInput(attrs={"class": "form-control"}),
            "annex": forms.TextInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
            "addressed_to": forms.TextInput(attrs={"class": "form-control"}),
            "addressed_to_2": forms.TextInput(attrs={"class": "form-control"}),
            "padrino_ch_d": forms.Select(attrs={"class": "form-control"}),

            "visitor_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "volunt_dep_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "first_contact": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "last_contact": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "date_of_birth_2": forms.DateInput(attrs={"class": "form-control", "type": "date"}),

            "note_1": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "note_2": forms.Textarea(attrs={"class": "form-control", "rows": 2}),

            "gender": forms.Select(choices=[
                ("", "---------"),
                ("M", "Masculino"),
                ("F", "Femenino"), 
                ("NA", "No aplica")],
                  attrs={"class": "form-control"}),
            "civil_status": forms.Select(choices=[
                ("", "---------"),
                ("Soltero", "Soltero"),
                ("Casado", "Casado"),
                ("Divorciado", "Divorciado"),
                ("Viudo", "Viudo"),
                ("No aplica", "No aplica")
            ], attrs={"class": "form-control"}),
            "nationality": forms.Select(choices=[
                ("", "---------"),
    ("Alemana", "Alemana"),
    ("Suiza", "Suiza"),
    ("Española", "Española"),
    ("Austríaca", "Austríaca"),
    ("Francesa", "Francesa"),
    ("USA", "USA"),
    ("Hondureña", "Hondureña"),
    ("Guatemalteca", "Guatemalteca")
            ], attrs={"class": "form-control"}),
            "report_email": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "only_email": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "only_easter_rep": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "financial_report": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "visitor": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "sponsor": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "godfather": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "member": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "former_volunteer": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "no_correspondence": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "deceased": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "deactivated": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "expect_reaction": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "bad_address": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "private": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "imprimir": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "deactivate_soon": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "recog_2010": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "recog_2020_blanket": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "recog_2020_plate": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

        labels = {
            "last_name_1": "Apellido 1",
            "last_name_2": "Apellido 2",
            "first_name_1": "Nombre 1",
            "first_name_2": "Nombre 2",
            "free_union": "Unión Libre",
            "profession": "Profesión",
            "address": "Dirección",
            "street": "Calle",
            # "city": "Ciudad",  # Ya no se muestra directamente desde el formulario
            "phone_1": "Teléfono 1",
            "phone_2": "Teléfono 2",
            "fax": "Fax",
            "email": "Correo Electrónico",
            "email_2": "Correo Electrónico 2",
            "email_3": "Correo Electrónico 3",
            "language": "Idioma",
            "contact": "Contacto",
            "addressed_to": "Dirigido Carta",
            "addressed_to_2": "Dirigido Carta Aled",
            "visitor": "Visitante",
            "sponsor": "Padrino",
            "godfather": "Bienhechor",
            "sponsorship": "Padrinazgo",
            "member": "Miembro",
            "former_volunteer": "Ex Voluntario",
            "note_1": "Nota 1",
            "note_2": "Nota 2",
            "gender": "Sexo",
            "civil_status": "Estado Civil",
            "nationality": "Nacionalidad",
            "padrino_ch_d": "Padrino CH/D",
        }

class GodfatherForm(forms.ModelForm):
    class Meta:
        model = Godfather
        fields = ['sponsor', 'number', 'start_date', 'diploma', 'money_code', 'amount', 'desactivated']
        labels = {
            'sponsor': 'Sponsor',
            'number': 'Número',
            'start_date': 'Fecha de Inicio',
            'diploma': 'Diploma',
            'money_code': 'Código de Dinero',
            'amount': 'Monto',
            'desactivated': 'Desactivado'
        }
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'diploma': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'money_code': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'desactivated': forms.CheckboxInput(),
        }

class CorrespondenceForm(forms.ModelForm):
    class Meta:
        model = Correspondence
        fields = ['sponsor', 'date', 'description']
        labels = {
            'sponsor': 'Sponsor',
            'date': 'Fecha',
            'description': 'Descripción'
        }
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = [
            'sponsor', 'origin', 'currency_code', 'amount', 'date',
            'receipt', 'check_number', 'text1', 'text2',
            'receipt_number', 'payment_mail'
        ]
        
        labels = {
            'sponsor': 'Sponsor',
            'origin': 'Origen',
            'currency_code': 'Código de Moneda',
            'amount': 'Monto',
            'date': 'Fecha de Ingreso',
            'receipt': 'Recibo',
            'check_number': 'Número de Cheque',
            'text1': 'Texto 1',
            'text2': 'Texto 2',
            'receipt_number': 'Número de Recibo',
            'payment_mail': 'Correo de Pago',
        }

        widgets = {
            'sponsor': forms.Select(attrs={'class': 'form-control'}),
            'origin': forms.TextInput(attrs={'class': 'form-control'}),
            'currency_code': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'receipt': forms.TextInput(attrs={'class': 'form-control'}),
            'check_number': forms.TextInput(attrs={'class': 'form-control'}),
            'text1': forms.TextInput(attrs={'class': 'form-control'}),
            'text2': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt_number': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'payment_mail': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
