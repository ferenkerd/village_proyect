from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib import messages
from django.urls import reverse

from django_recaptcha.client import submit
from django_recaptcha.fields import ReCaptchaField

from administrator.form import Customer_Sign_Up_Form, Data_User_Form, Log_In_Form
from administrator.models import Customer, Profile, User
from administrator.tokens import account_activation_token

from business.models import Services

from .form import Service_impression_Form, Service_architecture_Form
from .models import Services_Impression, Services_Arquitecture

from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    if request.method == 'GET':
        try:
            return render(request, "index.html")
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "index.html")

@login_required(login_url='log_in_customer')
def dashboard(request):
    if request.method == 'GET':
        try:
            return render(request, "dashboard_customer.html")
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "dashboard_customer.html")

@login_required(login_url='log_in_customer')
def services(request):
    if request.method == 'GET':
        try:
            services = Services.objects.all()
            return render(request, "services_customer.html", {
                'services': services
            })
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "services_customer.html")

@login_required(login_url='log_in_customer')
def add_orders(request, service_type, service_id):
    if request.method == 'GET':
        try:
            service = get_object_or_404(Services, pk=service_id, name=service_type)
            if service.name == 'Impresión':
                form = Service_impression_Form()
                return render(request, "add_orders_customer.html", {
                    'form_impri': form,
                    'services': service
                })
            if service.name == 'Arquitectura':
                form = Service_architecture_Form()
                return render(request, "add_orders_customer.html", {
                    'form_arqui': form,
                    'services': service
                })
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "add_orders_customer.html")
    elif request.method == 'POST':
        try:
            service = get_object_or_404(Services, pk=service_id, name=service_type)
            if service.name == 'Impresión':
                data = Service_impression_Form(request.POST)
                if data.is_valid:
                    form = data.save(commit=False)
                    form.user = request.user
                    form.name = service.name
                    form.business = service.user
                    form.save()
                    messages.success(request, "Se ha enviado la solicitud de impresión.")
                    return redirect('services_customer')
                else:
                    messages.error(request, "Ha ocurrido un error.")
                    return render(request, "add_orders_customer.html", {
                        'form': data,
                    })

            if service.name == 'Arquitectura':
                data = Service_architecture_Form(request.POST)
                if data.is_valid:
                    form = data.save(commit=False)
                    form.user = request.user
                    form.name = service.name
                    form.business = service.user
                    form.save()
                    messages.success(request, "Se ha enviado la solicitud de arquitectura.")
                    return redirect('services_customer')
                else:
                    messages.error(request, "Ha ocurrido un error.")
                    return render(request, "add_orders_customer.html", {
                        'form': data,
                    })
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "add_orders_customer.html", {
                'form': data,
            })

@login_required(login_url='log_in_customer')
def my_orders(request):
    if request.method == 'GET':
        try:
            orders = [Services_Impression.objects.filter(user=request.user), Services_Arquitecture.objects.filter(user=request.user)]
            return render(request, 'my_orders_customer.html', {
                'impresiones': orders[0][::-1],
                'arquitecturas': orders[1][::-1],
            })
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "my_orders_customer.html", {
                'impresiones': orders[0][::-1],
                'arquitecturas': orders[1][::-1]
            })

@login_required(login_url='log_in_customer')
def cancel_orders(request, service_type,order_id):
    if request.method == 'GET':
        try:
            if service_type == 'Impresión':
                impri = get_object_or_404(Services_Impression, pk=order_id)
                impri.status = 'Cancelado'
                impri.save()
                messages.success(request, f"Se ha cancelado la solicitud de impresión #{order_id}.")
                return redirect('my_orders_customer')
            
            if service_type == 'Arquitectura':
                arqui = get_object_or_404(Services_Arquitecture, pk=order_id)
                arqui.status = 'Cancelado'
                arqui.save()
                messages.success(request, f"Se ha cancelado la solicitud de arquitectura #{order_id}.")
                return redirect('my_orders_customer')
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, 'my_orders_customer.html')


def log_in(request):
    if request.method == "GET":
        try:
            return render(request, "log_in_customer.html", {
                'form': Log_In_Form
            })
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "log_in_customer.html", {
                'form': Log_In_Form
            })
    elif request.method == "POST":
        form =  Log_In_Form(request.POST)
        
        try: 
            if form.is_valid:
                username = request.POST["username"]
                password = request.POST["password"]
            else:
                messages.error(request, "Ha ocurrido un error.")
                return render(request, "log_in_customer.html", {
                    'form': Log_In_Form
                })
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "log_in_customer.html", {
                'form': Log_In_Form
            })


        try:
            customer = Customer.objects.get(username=username)
            if customer.role != 'CUSTOMER':
                messages.error(request, "No tiene permiso de customer.")
                return render(request, "log_in_customer.html", {
                    'form': Log_In_Form
                })
        except Customer.DoesNotExist:
            messages.error(request, "El usuario no existe.")
            return render(request, "log_in_customer.html", {
                'form': Log_In_Form
            })

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Usuario o contraseña incorrecta.")
            return render(request, "log_in_customer.html", {
                'form': Log_In_Form
            })
        else:
            ip_c = ReCaptchaField.get_remote_ip(request)
            recaptcha_response = submit(request.POST.get('g-recaptcha-response'), '6LdeIfkpAAAAAEL6BWrZ0ZZj92bn8JC8OhYam6P9', ip_c)
                
            if recaptcha_response.is_valid:
                login(request, user)
                messages.success(request, "Haz iniciado sesión.")
                return redirect("dashboard_business")                
            else:
                messages.error(request, "Verificación de CAPTCHA fallida.")
                return render(request, "log_in_business.html", {
                    "form": Log_In_Form(request.POST)
                })


def seleccionar_pedido(request, service_id):
    request.session['pedido_id'] = service_id
    return redirect('sign_up_customer')


def sign_up(request):
    if request.method == "GET":
        try:
            return render(request, "sign_up_customer.html", {
                'form': Customer_Sign_Up_Form
            })
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "sign_up_customer.html", {
                'form': Customer_Sign_Up_Form,
                'error': "a ocurrido un error",
            })
    elif request.method == "POST":
        try:
            form = Customer_Sign_Up_Form(request.POST)

            email = User.objects.filter(email=request.POST["email"]).exists()
            if email is True:
                messages.error(request, "Ya existe una cuenta con ese correo.")
                return render(request, "sign_up_business.html", {
                        'form': Customer_Sign_Up_Form
                    })

            if form.is_valid():
                user = form.save(commit=False)
                user.save()
                auth_token = account_activation_token.make_token(user=user)
                profile = Profile.objects.create(
                    user=user, auth_token=auth_token, is_verified=False)
                profile.save()
                login(request, user)
                domain = get_current_site(request).domain
                send_mail_after_registration(
                    user.username, user.email, profile.auth_token, domain)
                return redirect("verify_profile_customer")
                # service_id = request.session.get('service_id')
                # if service_id:
                #     return redirect('add_orders_customer', service_id=service_id)
            else:
                messages.error(request, "Ha ocurrido un error.")
                return render(request, "sign_up_customer.html", {
                    "form": form, 
                })        
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "sign_up_customer.html", {
                "form": form, 
            })  

@login_required(login_url='log_in_customer')
def log_out(request):
    if request.method == "GET":
        try:
            logout(request)
            messages.success(request, "Haz cerrado sesión.")
            return redirect("log_in_customer")        
        except:
             messages.error(request, "Ha ocurrido un error.")
             return redirect("dashboard_customer")

@login_required(login_url='log_in_customer')
def verify_account(request, auth_token):
    try:
        profile_obj = get_object_or_404(Profile, auth_token=auth_token, user= request.user)
        if profile_obj:
            if profile_obj.is_verified == True and profile_obj.data_full == False:
                return redirect("verify_profile_customer")
            elif profile_obj.is_verified == True and profile_obj.data_full == True:
                return redirect("verify_profile_customer")
            
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, "Email activada exitosamente.")
            return redirect("verify_profile_customer")
        else:
            messages.success(request, "No se a podido validar el email.")
            return redirect("verify_profile_customer")
    except:
        messages.success(request, "No se a podido validar el email.")
        return redirect("verify_profile_customer")

@login_required(login_url='log_in_customer')
def verify_profile(request):
    if request.method == "GET":
        try:
            profile = get_object_or_404(Profile, user=request.user)

            if profile.is_verified == False:
                messages.info(request, f"Revisa tu correo electronico {request.user.email}, y presiona el link de activación.") 
                return render(request, "verify_profile_customer.html", {
                    'email': False
                    })

            if profile.data_full == False:
                messages.info(request, "Completa el registro.") 
                return render(request, "verify_profile_customer.html", {
                    'data': False,
                    'form': Data_User_Form
                })

            if profile.is_verified == True and profile.data_full == True:
                messages.success(request, "Cuenta ya activa.")
                return render(request, "verify_profile_customer.html", {
                    'verifid': True,
                    'redireccionar': True,
                    })
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "verify_profile_customer.html", {
                'form': Data_User_Form
            })
    elif request.method == "POST":
        try:
            a = User.objects.get(pk=request.user.id)
            form = Data_User_Form(request.POST, instance=a)
            if form.is_valid():
                form.save()
                profile = get_object_or_404(Profile, user=request.user)
                profile.data_full = True
                profile.save()
                messages.success(request, "Se ha guardado los datos.")
                return redirect("verify_profile_customer")
            else:
                messages.error(request, "Ha ocurrido un error.")
                return render(request, "verify_profile_customer.html", {
                    "form": form
                })
        except:
            messages.error(request, "Ha ocurrido un error.")
            return render(request, "verify_profile_customer.html", {
                "form": form
            })

def send_mail_after_registration(username, to_email, token, domain, view_name='verify_account_customer'):
    subject = f'Tu cuenta de cliente necesita ser verificada {username}.'
    verify_url = domain + reverse(view_name, kwargs={'auth_token':token})
    print(verify_url)
    message = f'Hola {username}, presiona este link para verificar tu cuenta {verify_url}'
    email = EmailMessage(subject, message, to=[to_email])
    email.send()