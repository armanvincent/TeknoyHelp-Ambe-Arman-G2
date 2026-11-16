from django.urls import path
from . import views, workflow_views

urlpatterns = [
    path('', views.errand_list, name='errand_list'),
    path('new/', views.errand_create, name='errand_create'),
    path('mine/', views.my_requests, name='my_requests'),
    path('tasks/', workflow_views.my_tasks, name='my_tasks'),
    path('manage/', workflow_views.manage_errands, name='manage_errands'),
    path('<int:pk>/', views.errand_detail, name='errand_detail'),
    path('<int:pk>/edit/', views.errand_edit, name='errand_edit'),
    path('<int:pk>/delete/', views.errand_delete, name='errand_delete'),
    path('<int:pk>/accept/', workflow_views.errand_accept, name='errand_accept'),
    path('<int:pk>/withdraw/', workflow_views.errand_withdraw, name='errand_withdraw'),
    path('<int:pk>/complete/', workflow_views.errand_complete, name='errand_complete'),
    path('<int:pk>/confirm/', workflow_views.errand_confirm, name='errand_confirm'),
    path('<int:pk>/admin-delete/', workflow_views.admin_errand_delete, name='admin_errand_delete'),
]