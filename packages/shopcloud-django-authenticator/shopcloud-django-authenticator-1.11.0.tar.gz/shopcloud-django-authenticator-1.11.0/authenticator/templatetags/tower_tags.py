from django import template
from django.template import Context, Template

register = template.Library()


@register.simple_tag
def tower_login(request, pk):
    url = f"https://tower.talk-point.de/authenticator/login-redirect/{pk}/"
    next = request.GET.get('next')
    if next is not None:
        url = f"{url}?next={next}"
    html = f"""<div class="submit-row"><hr/><br/><a href="{url}" rel="noopener nofollow">Login mit Tower</a></div>"""
    return Template(html).render(Context())
