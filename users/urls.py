from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'users/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^password/change/$',
        auth_views.password_change, {
            'template_name': 'users/password_change.html',
            'post_change_redirect': reverse_lazy('users:password_change_done'),
        },
        name='password_change'),
    url(r'^password/change/done/$',
        login_required(TemplateView.as_view(template_name='users/password_change_done.html')),
        name='password_change_done'),
]
