from django.conf.urls import url
from users.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^password/change/$', PasswordChangeView.as_view(), name='password_change'),
    url(r'^password/change/done/$', PasswordChangeDoneView.as_view(), name='password_change_done'),
]
