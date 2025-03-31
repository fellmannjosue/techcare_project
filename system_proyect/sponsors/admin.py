from django.contrib import admin
from .models import City, Country, Directed, Title, Sponsor, Godfather, Correspondence, Income

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'zip_code', 'country')  # 'zip_code' es el nombre correcto

@admin.register(Directed)
class DirectedAdmin(admin.ModelAdmin):
    list_display = ('id', 'description')
    search_fields = ('description',)

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'description')
    search_fields = ('description',)

@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name_1', 'last_name_1', 'email', 'city')
    search_fields = ('first_name_1', 'last_name_1', 'email')
    list_filter = ('city', 'sponsor', 'godfather')
    ordering = ('id',)

@admin.register(Godfather)
class GodfatherAdmin(admin.ModelAdmin):
    list_display = ('id', 'sponsor', 'start_date', 'amount', 'desactivated')
    search_fields = ('sponsor__first_name_1', 'sponsor__last_name_1')
    list_filter = ('desactivated',)
    ordering = ('id',)

@admin.register(Correspondence)
class CorrespondenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'sponsor', 'date', 'description')
    search_fields = ('sponsor__first_name_1', 'sponsor__last_name_1')
    ordering = ('id',)

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'sponsor', 'amount', 'currency_code', 'date')
    search_fields = ('sponsor__first_name_1', 'sponsor__last_name_1')
    list_filter = ('currency_code',)
    ordering = ('id',)
