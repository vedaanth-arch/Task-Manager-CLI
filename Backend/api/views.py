from rest_framework.decorators import api_view  
from rest_framework.response import Response
from .models import Task
from .Serializer import TaskSerializer
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def health(request):
    return JsonResponse({"status": "ok"})

@api_view(["GET","POST"])
@permission_classes([IsAuthenticated]) #→ Only allow authenticated users to access this view.
def task_list(request):
    # GET request:
    # → Get existing tasks from the database
    # → Serialize the tasks
    # → Return the serialized data
    if request.method=="GET":
        tasks=Task.objects.filter(owner=request.user)#→ Get all existing tasks from the database.
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
            serializer.save(owner=request.user) #→ Save the new Task to the database,"Save this task, and make the logged-in user its owner."
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
                ) #→ Return the serialized data of the newly created Task with a 201 Created status code.
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            ) #→ If the data is invalid, return the

@api_view(["GET","PATCH","DELETE"])
@permission_classes([IsAuthenticated]) #→ Only allow authenticated users to access this view.
def task_detail(request,id):
    try:
        task = Task.objects.get(
            id=id,
            owner=request.user
        )
    except Task.DoesNotExist:
        return Response(
            {"error": "Task not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    # get the task using the id
    # ↓
    # serialize the task
    # ↓
    # return the response
    if request.method=="GET":
        try:
            task=Task.objects.get(id=id,owner=request.user) #→ Get the Task object with the given id from the database,meant any authenticated user who knows the ID could potentially access that task.
            serializer=TaskSerializer(task) #→ Serialize the Task object.
            return Response(serializer.data) #→ Return the serialized data of the Task as a response.
        except Task.DoesNotExist:
            return Response({"error":"Task not found"},status=status.HTTP_404_NOT_FOUND) #→ If the Task with the given id does not exist, return a 404 Not Found response with an error message.

    if request.method == "PATCH":
        try:
            task = Task.objects.get(
                id=id,
            owner=request.user
        )
        except Task.DoesNotExist:
            return Response(
            {"error": "Task not found"},
            status=status.HTTP_404_NOT_FOUND
        )

        serializer = TaskSerializer(
        task,
        data=request.data,
        partial=True
    )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
    
    if request.method=="DELETE":
        try:
            task=Task.objects.get(id=id,owner=request.user) #→ Get the Task object with the given id from the database.
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({"error":"Task not found"},status=status.HTTP_404_NOT_FOUND)        

#Create a new Django user account through an API endpoint.
@api_view(["POST"])
@permission_classes([AllowAny]) #→ Allow any user (authenticated or not) to access this view.
def register(request):
        # POST request:
    # → Get data from request
    # → Get username, email, password
    # → Check whether username already exists
    # → Create User
    # → Return response
    if request.method=="POST":

        data=request.data
        username=data.get("username")
        email=data.get("email")
        password=data.get("password")
        if not username or not email or not password:
            return Response({"error":"Please provide username, email and password"},
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"error":"Username already exists"},
                            status=status.HTTP_400_BAD_REQUEST)
        user=User.objects.create_user(
        username=username,
        email=email,
        password=password
        )

        return Response({
            "message":"User Created Successfully"},
            status=status.HTTP_201_CREATED)

