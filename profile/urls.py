from django.urls import path
from django.contrib.auth import views as auth_views
from .views import profile_view, edit_profile

app_name = 'profile'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='profile/login.html',
        next_page='shop:product_list'
        ), name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(next_page='profile:login'), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile')
]
