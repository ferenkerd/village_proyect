from django.shortcuts import render

# Create your views here.
def custom_404(request, exception):
    return render(request, 'error_404.html')