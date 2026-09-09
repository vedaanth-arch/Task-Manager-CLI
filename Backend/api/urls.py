from django.urls import path
from .views import task_list,task_detail

urlpatterns = [
    path('tasks/', task_list, name='task-list'),    
    path("task/<int:id>/",task_detail,name="task-detail"),

]
