from django.urls import path

from myshopify import views

urlpatterns = [
    path('login/', views.login, name="login"),
    path('finalize/', views.finalize, name='finalize'),
    path('authenticate/', views.authenticate, name='authenticate'),
]
