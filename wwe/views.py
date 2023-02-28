from django.shortcuts import render

# Create your views here.
def wwe(request):
    return render(request,"wwe.html")