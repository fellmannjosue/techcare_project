from django.urls import reverse
from django.utils.html import escapejs

class GlobalScriptMiddleware:
    """Append global JS variables and script to every HTML response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        content_type = response.get('Content-Type', '')
        if response.status_code == 200 and 'text/html' in content_type:
            username = request.user.username if request.user.is_authenticated else ''
            show_welcome = bool(request.session.pop('show_welcome', False))
            logout_url = reverse('logout') + '?inactive=1'

            script = (
                f"<script>var GLOBAL_USERNAME='{escapejs(username)}';"
                f"var SHOW_WELCOME={str(show_welcome).lower()};"
                f"var LOGOUT_URL='{escapejs(logout_url)}';</script>"
                f"<script src='/static/accounts/js/global.js' defer></script>"
            )

            content = response.content.decode('utf-8')
            if '</body>' in content:
                content = content.replace('</body>', script + '</body>')
                response.content = content
                response['Content-Length'] = len(content.encode('utf-8'))
        return response
