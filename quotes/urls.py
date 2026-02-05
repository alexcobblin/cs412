from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.quote, name='quote'),
    path('quote/', views.quote, name='quote'),
    path('show_all/', views.show_all, name='show_all'),
    path('about/', views.about, name='about'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)