# core/context_processors.py

from datetime import datetime

def current_year(request):
    return {
        'year': datetime.now().year
    }
