"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
#We don't have to write all the password-checking and JWT-generation logic ourselves.
from rest_framework_simplejwt.views import  (TokenObtainPairView, TokenRefreshView) 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # User.objects.filter(username=username).exists() 
    path('api/', include('api.urls')), 
    
    #/api/token/ 
    #↓ 
    #TokenObtainPairViews 
    # ↓ 
    #check username + password 
    # ↓ 
    #if correct 
    # ↓ 
    #generate JWT 
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    
    #Access tokens are intentionally short-lived. 
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    #Refresh token Used to get a new access token when the access token expires. 
]


'''JWT Authentication Flow:
LOGIN
  ↓
access token + refresh token
  ↓
use access token
  ↓
access token expires
  ↓
send refresh token
  ↓
get new access token'''

'''FLOW of writing django JWT
1. Install SimpleJWT
        ↓
2. settings.py
   Tell DRF to use JWT authentication
        ↓
3. core/urls.py
   Add JWT endpoints
        ↓
4. Test /api/token/
        ↓
5. JWT authentication is working'''