from django.urls import path
from . import views

urlpatterns = [
    path('', views.errand_list, name='errand_list'),
    path('new/', views.errand_create, name='errand_create'),
    path('mine/', views.my_requests, name='my_requests'),
    path('<int:pk>/', views.errand_detail, name='errand_detail'),
    path('<int:pk>/edit/', views.errand_edit, name='errand_edit'),
    path('<int:pk>/delete/', views.errand_delete, name='errand_delete'),
]