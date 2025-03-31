from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def user_menu(request):
    return render(request, 'menu/user_menu.html')
