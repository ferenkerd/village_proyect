from django.shortcuts import redirect, get_object_or_404, HttpResponseRedirect
from django.urls import resolve
from django.urls import reverse
from administrator.models import User, Profile
from django.contrib.auth import logout
from django.contrib import messages

class VerifiedMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = get_object_or_404(Profile, user=request.user)
            user = get_object_or_404(User, id=request.user.id)

            if request.path == f"/business/verify_account/{profile.auth_token}":
                return self.get_response(request)
            
            if request.path == f"/customer/verify_account/{profile.auth_token}":
                return self.get_response(request)
            
            if request.path == "/customer/log_out":  # Agregamos esta condicional
                logout(request)  # Cerramos la sesión del usuario
                return redirect("log_in_customer")  # Redirigimos a la página de inicio
            
            if request.path == "/business/log_out":  # Agregamos esta condicional
                logout(request)  # Cerramos la sesión del usuario
                return redirect("log_in_business")  # Redirigimos a la página de inici
        
            
            if request.path != "/business/verify_profile/" and user.role == "BUSINESS":
                if not profile.is_verified:
                    print("Falta Email")
                    return redirect('verify_profile_business')

                if not profile.data_full:
                    print("Falta Data")
                    return redirect('verify_profile_business')




            if request.path != "/customer/verify_profile/"  and user.role == "CUSTOMER":
                if not profile.is_verified:
                    print("Falta Email")
                    return redirect('verify_profile_customer')

                if not profile.data_full:
                    print("Falta Data")
                    return redirect('verify_profile_customer')
        
        return self.get_response(request)

class  RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)
            
            if user.role == "CUSTOMER" and request.path.startswith('/business/'):
                messages.error(request, 'No tienes permiso para acceder a esta página.')
                return redirect(reverse('dashboard_customer'))
            
            elif user.role == "BUSINESS" and request.path.startswith('/customer/'):
                messages.error(request, 'No tienes permiso para acceder a esta página.')
                return redirect(reverse('dashboard_business'))
                
        return self.get_response(request)