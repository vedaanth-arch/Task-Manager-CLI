from django.urls import path
from .views import task_list,task_detail
from .views import task_list, task_detail,register
urlpatterns = [
    path('tasks/', task_list, name='task-list'),    
    path("task/<int:id>/",task_detail,name="task-detail"),
    path("register/",register,name="register")
]
