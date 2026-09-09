from rest_framework.decorators import api_view  
from rest_framework.response import Response
from .models import Task
from .Serializer import TaskSerializer
from rest_framework import status
@api_view(["GET","POST"])

def task_list(request):
    # GET request:
    # → Get existing tasks from the database
    # → Serialize the tasks
    # → Return the serialized data
    if request.method=="GET":
        tasks=Task.objects.all() #→ Get all existing tasks from the database.
        serializer=TaskSerializer(tasks,many=True) #→ Serialize the tasks. The many=True
        return Response(serializer.data)
    """POST
        ↓
    Request data → Serializer → Validate → Save → Response"""
    # POST request:
    # → Get data from request
    # → Give the data to TaskSerializer
    # → Validate the data
    # → Save the new task to the database
    # → Return the response


    if request.method=="POST":
        data=request.data #→ Get the data from the request body.
        serializer=TaskSerializer(data=data) #For POST, you're giving the serializer incoming data
        #validate
        if serializer.is_valid():
            serializer.save() #→ Save the new Task to the database.
            return Response(serializer.data,status=status.HTTP_201_CREATED) #→ Return the serialized data of the newly created Task with a 201 Created status code.
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST) #→ If the data is invalid, return the

@api_view(["GET","PUT","DELETE"])
def task_detail(request,id):
    # get the task using the id
    # ↓
    # serialize the task
    # ↓
    # return the response
    if request.method=="GET":
        try:
            task=Task.objects.get(id=id) #→ Get the Task object with the given id from the database.
            serializer=TaskSerializer(task) #→ Serialize the Task object.
            return Response(serializer.data) #→ Return the serialized data of the Task as a response.
        except Task.DoesNotExist:
            return Response({"error":"Task not found"},status=status.HTTP_404_NOT_FOUND) #→ If the Task with the given id does not exist, return a 404 Not Found response with an error message.


    if request.method=="PUT":
        task=Task.objects.get(id=id) #→ Get the Task object with the given id from the database.
        serializer=TaskSerializer(task,data=request.data) #→ Give the existing Task object and the new data to the serializer.
        if serializer.is_valid():
            serializer.save() #→ Save the new Task to the database.
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST) #→ If the data is invalid, return the

    if request.method=="DELETE":
        try:
            task=Task.objects.get(id=id)
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({"error":"Task not found"},status=status.HTTP_404_NOT_FOUND)        


# Create your views here


