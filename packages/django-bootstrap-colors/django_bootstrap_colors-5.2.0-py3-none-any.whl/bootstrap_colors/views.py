from django.conf import settings
from django.views.generic import TemplateView


class BootstrapColorsView(TemplateView):
    template_name = 'bootstrap_colors.css'
    content_type = 'text/css'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['BOOTSTRAP_THEME_COLORS'] = settings.BOOTSTRAP_THEME_COLORS
        return context
