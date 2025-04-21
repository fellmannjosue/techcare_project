from django.db import models

# -------------------------- COUNTRY -------------------------- #
class Country(models.Model):
    id = models.AutoField(primary_key=True, db_column='gen_country_id')
    name = models.CharField(max_length=100, db_column='country', verbose_name="Nombre del País")

    class Meta:
        db_table = 'tbl_gen_country'
        managed = False  

    def __str__(self):
        return self.name

# -------------------------- CITY -------------------------- #
class City(models.Model):
    id = models.AutoField(primary_key=True, db_column='gen_city_id')
    zip_code = models.CharField(max_length=10, db_column='zip_code', verbose_name="Código Postal", null=True, blank=True)
    name = models.CharField(max_length=100, db_column='city', verbose_name="Nombre de la Ciudad", null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='gen_country_id', verbose_name="País")

    class Meta:
        db_table = 'tbl_gen_city'
        managed = False  

    def __str__(self):
        return f"{self.name} ({self.zip_code})"

# -------------------------- DIRECTED -------------------------- #
class Directed(models.Model):
    id = models.AutoField(primary_key=True, db_column='gen_directed_id')
    description = models.CharField(max_length=50, db_column='description', verbose_name="Descripción")

    class Meta:
        db_table = 'tbl_gen_directed'
        managed = False  
        verbose_name = "Directed"
        verbose_name_plural = "Directed"

    def __str__(self):
        return self.description

# -------------------------- TITLE -------------------------- #
class Title(models.Model):
    id = models.AutoField(primary_key=True, db_column='gen_title_id')
    description = models.CharField(max_length=50, db_column='description', verbose_name="Descripción")

    class Meta:
        db_table = 'tbl_gen_title'
        managed = False  
        verbose_name = "Title"
        verbose_name_plural = "Titles"

    def __str__(self):
        return self.description

# -------------------------- SPONSOR -------------------------- #
class Sponsor(models.Model):
    id = models.AutoField(primary_key=True, db_column='spn_sponsors_id')
    title = models.ForeignKey("Title", on_delete=models.SET_NULL, null=True, db_column='gen_title_id', verbose_name="Título")
    directed = models.ForeignKey("Directed", on_delete=models.SET_NULL, null=True, db_column='gen_directed_id', verbose_name="Dirigido a")
    city = models.ForeignKey("City", on_delete=models.CASCADE, db_column='gen_city_id', verbose_name="Ciudad")

    last_name_1 = models.CharField(max_length=100, db_column='last_name_1', verbose_name="Apellido 1")
    last_name_2 = models.CharField(max_length=50, db_column='last_name_2', verbose_name="Apellido 2", null=True, blank=True)
    first_name_1 = models.CharField(max_length=50, db_column='first_name_1', verbose_name="Nombre 1", null=True, blank=True)
    first_name_2 = models.CharField(max_length=50, db_column='first_name_2', verbose_name="Nombre 2", null=True, blank=True)

    free_union = models.BooleanField(default=False, db_column='free_union', verbose_name="Unión Libre")
    profession = models.CharField(max_length=50, db_column='profession', verbose_name="Profesión", null=True, blank=True)
    address = models.CharField(max_length=100, db_column='address', verbose_name="Dirección", null=True, blank=True)
    street = models.CharField(max_length=100, db_column='street', verbose_name="Calle", null=True, blank=True)

    phone_1 = models.CharField(max_length=50, db_column='phone_1', verbose_name="Teléfono 1", null=True, blank=True)
    phone_2 = models.CharField(max_length=50, db_column='phone_2', verbose_name="Teléfono 2", null=True, blank=True)
    fax = models.CharField(max_length=50, db_column='fax', verbose_name="Fax", null=True, blank=True)
    email = models.EmailField(max_length=50, db_column='email', verbose_name="Correo Electrónico", null=True, blank=True)
    email_2 = models.EmailField(max_length=50, db_column='email_2', verbose_name="Correo Electrónico 2", null=True, blank=True)
    email_3 = models.EmailField(max_length=50, db_column='email_3', verbose_name="Correo Electrónico 3", null=True, blank=True)

    report_email = models.BooleanField(default=False, db_column='report_email', verbose_name="Reporte Email (si no paga 3 años)")
    only_email = models.BooleanField(default=False, db_column='only_email', verbose_name="Solo Email (no quiere correo)")
    only_easter_rep = models.BooleanField(default=False, db_column='only_easter_rep', verbose_name="Solo Email OB (solo para Alemania)")
    financial_report = models.BooleanField(default=False, db_column='financial_report', verbose_name="Reporte Financiero (solo Insiders)")

    language = models.CharField(max_length=50, db_column='language', verbose_name="Idioma Reporte", null=True, blank=True)
    annex = models.CharField(max_length=100, db_column='annex', verbose_name="Anexo", null=True, blank=True)
    contact = models.CharField(max_length=100, db_column='contact', verbose_name="Contacto", null=True, blank=True)

    addressed_to = models.CharField(max_length=100, db_column='addressed_to', verbose_name="Dirigido Carta", null=True, blank=True)
    addressed_to_2 = models.CharField(max_length=100, db_column='addressed_to_2', verbose_name="Dirigido Carta Aled", null=True, blank=True)

    visitor = models.BooleanField(default=False, db_column='visitor', verbose_name="Visitante")
    visitor_date = models.DateTimeField(null=True, blank=True, db_column='visitor_date', verbose_name="Fecha de Visita")
    sponsor = models.BooleanField(default=False, db_column='sponsor', verbose_name="Padrino")
    godfather = models.BooleanField(default=False, db_column='godfather', verbose_name="Bienhechor")
    sponsorship = models.CharField(max_length=50, db_column='sponsorship', verbose_name="Padrinazgo", null=True, blank=True)

    member = models.BooleanField(default=False, db_column='member', verbose_name="Miembro")
    former_volunteer = models.BooleanField(default=False, db_column='former_volunteer', verbose_name="Ex Voluntario")
    volunt_dep_date = models.DateTimeField(null=True, blank=True, db_column='volunt_dep_date', verbose_name="Fecha Egr Vol")

    no_correspondence = models.BooleanField(default=False, db_column='no_correspondence', verbose_name="No Corresp")
    deceased = models.BooleanField(default=False, db_column='deceased', verbose_name="Fallecido")
    deactivated = models.BooleanField(default=False, db_column='deactivated', verbose_name="Desactivado")
    expect_reaction = models.BooleanField(default=False, db_column='expect_reaction', verbose_name="Esperar Reac.")
    bad_address = models.BooleanField(default=False, db_column='bad_address', verbose_name="Dirección Mala")
    private = models.BooleanField(default=False, db_column='private', verbose_name="Privado")

    first_contact = models.DateTimeField(null=True, blank=True, db_column='first_contact', verbose_name="Primer Contacto")
    last_contact = models.DateTimeField(null=True, blank=True, db_column='last_contact', verbose_name="Último Contacto")

    note_1 = models.TextField(db_column='note_1', verbose_name="Nota 1", null=True, blank=True)
    note_2 = models.TextField(db_column='note_2', verbose_name="Nota 2", null=True, blank=True)

    date_of_birth = models.DateTimeField(null=True, blank=True, db_column='date_of_birth', verbose_name="Fecha de Nacim 1")
    date_of_birth_2 = models.DateTimeField(null=True, blank=True, db_column='date_of_birth_2', verbose_name="Fecha de Nacim 2")

    gender = models.CharField(max_length=10, db_column='gender', verbose_name="Sexo", null=True, blank=True)
    civil_status = models.CharField(max_length=12, db_column='civil_status', verbose_name="Estado Civil", null=True, blank=True)
    nationality = models.CharField(max_length=50, db_column='nationality', verbose_name="Nacionalidad", null=True, blank=True)

    imprimir = models.BooleanField(default=False, db_column='imprimir', verbose_name="Imprimir")
    deactivate_soon = models.BooleanField(default=False, db_column='deactivate_soon', verbose_name="Desact Prox")

    recog_2010 = models.BooleanField(default=False, db_column='recog_2010', verbose_name="Recon 2010")
    recog_2020_blanket = models.BooleanField(default=False, db_column='recog_2020_blanket', verbose_name="Recon 2020 Manta")
    recog_2020_plate = models.BooleanField(default=False, db_column='recog_2020_plate', verbose_name="Recon 2020 Plato")

    
    PADRINO_CHOICES = [
         ("Alemania", "Alemania"),     # 1
        ("Austria", "Austria"),       # 2
        ("España", "España"),         # 3
        ("Holanda", "Holanda"),       # 4
        ("Portugal", "Portugal"),     # 5
        ("Suiza", "Suiza"),           # 6
        ("USA", "USA"),               # 7
        ("Honduras", "Honduras"),     # 8
        ("Guatemala", "Guatemala"),   # 9
        ("Francia", "Francia"),       # 10
        ("Canada", "Canada"),         # 11
        ("Belgica", "Belgica"),       # 12
        ("Suecia", "Suecia"),         # 13
        ("Escocia", "Escocia"),       # 18
        ("Colombia", "Colombia"),     # 19
        ("Wales U.K.", "Wales U.K."), # 20
        ("Costa Rica C.A.", "Costa Rica C.A."), # 23
        ("Japon", "Japon"),           # 24
        ("Italia", "Italia"),         # 25
        ("n/d", "n/d"),               # 26
        ("U.A.E.", "U.A.E."),         # 27
        ("Mexico", "Mexico"),         # 28
        ("Irlanda", "Irlanda"),  
    ]

    padrino_ch_d = models.CharField(
        max_length=50,
      blank=True,
       null=True,
      choices=PADRINO_CHOICES,
      db_column='padrino_ch_d',
    verbose_name="Padrino CH/D",
    )

    class Meta:
        db_table = 'tbl_spn_sponsors'
        managed = False  

    def __str__(self):
        return f"{self.first_name_1} {self.last_name_1}"

# -------------------------- GODFATHER -------------------------- #
class Godfather(models.Model):
    id = models.AutoField(primary_key=True, db_column='spn_godfather_id')
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE, db_column='spn_sponsors_id', verbose_name="Sponsor", related_name="godfathers")

    number = models.IntegerField(null=True, blank=True, verbose_name="Número")
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Inicio")
    diploma = models.DateTimeField(null=True, blank=True, verbose_name="Diploma")
    money_code = models.CharField(max_length=50, null=True, blank=True, verbose_name="Código de Dinero")
    amount = models.FloatField(null=True, blank=True, verbose_name="Monto")
    desactivated = models.BooleanField(default=False, verbose_name="Desactivado")

    class Meta:
        db_table = 'tbl_spn_godfather'
        managed = False  

# -------------------------- CORRESPONDENCE -------------------------- #
class Correspondence(models.Model):
    id = models.AutoField(primary_key=True, db_column='spn_correspondence_id')
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE, db_column='spn_sponsors_id', verbose_name="Sponsor", related_name="correspondences")

    date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha")
    description = models.CharField(max_length=100, null=True, blank=True, verbose_name="Descripción")

    class Meta:
        db_table = 'tbl_spn_correspondence'
        managed = False  

# -------------------------- INCOME -------------------------- #
class Income(models.Model):
    id = models.AutoField(primary_key=True, db_column='spn_income_id')
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE, db_column='spn_sponsors_id', verbose_name="Sponsor")

    origin = models.CharField(max_length=50, null=True, blank=True, verbose_name="Origen")
    currency_code = models.CharField(max_length=50, verbose_name="Código de Moneda")
    amount = models.FloatField(verbose_name="Monto")
    date = models.DateTimeField(verbose_name="Fecha")
    receipt = models.CharField(max_length=20, null=True, blank=True, verbose_name="Recibo")
    
    # 🔹 Renombramos el campo problemático
    check_number = models.CharField(max_length=20, null=True, blank=True, db_column='check', verbose_name="Número de Cheque")

    text1 = models.CharField(max_length=100, null=True, blank=True, verbose_name="Texto 1")
    text2 = models.CharField(max_length=100, null=True, blank=True, verbose_name="Texto 2")
    receipt_number = models.BooleanField(default=False, verbose_name="Número de Recibo")
    payment_mail = models.BooleanField(default=False, verbose_name="Correo de Pago")

    class Meta:
        db_table = 'tbl_spn_income'
        managed = False  # 🔹 Evita que Django intente modificar la base de datos
# -------------------------- SPONSORED -------------------------- #

class Sponsored(models.Model):
    id = models.AutoField(primary_key=True, db_column='spn_sponsored_id')
    last_name_1 = models.CharField(max_length=100, db_column='last_name_1', verbose_name="Apellido 1", null=True, blank=True)
    last_name_2 = models.CharField(max_length=100, db_column='last_name_2', verbose_name="Apellido 2", null=True, blank=True)
    first_name_1 = models.CharField(max_length=100, db_column='first_name_1', verbose_name="Nombre 1", null=True, blank=True)
    first_name_2 = models.CharField(max_length=100, db_column='first_name_2', verbose_name="Nombre 2", null=True, blank=True)
    active = models.BooleanField(default=True, db_column='active', verbose_name="Activo")

    class Meta:
        db_table = 'tbl_spn_sponsored'
        managed = False

    def __str__(self):
        return f"{self.first_name_1} {self.last_name_1}"

# -------------------------- DESCR_GODFATHER -------------------------- #
class Descr_Godfather(models.Model):
    id = models.AutoField(primary_key=True, db_column='spn_descr_godfather_id')
    name = models.CharField(max_length=10, db_column='name', verbose_name="Código")
    description = models.CharField(max_length=100, db_column='description', verbose_name="Descripción")

    class Meta:
        db_table = 'tbl_spn_descr_godfather'
        managed = False

    def __str__(self):
        return self.description