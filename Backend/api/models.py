from django.db import models

class Task(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()
    done=models.BooleanField(default=False)
    owner=models.ForeignKey('auth.User',on_delete=models.CASCADE,related_name="tasks",null=True,blank=True)