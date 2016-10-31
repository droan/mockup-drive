from django.conf.urls import include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView


urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('core:home'))),
    url(r'^drive/', include('core.urls', namespace='core')),
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^admin/', admin.site.urls),
]
