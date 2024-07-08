from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    return render(request, 'sliders/index.html')

def update_result(request):
    slider1 = request.GET.get('slider1', 0)
    slider2 = request.GET.get('slider2', 0)
    slider3 = request.GET.get('slider3', 0)
    
    result = int(slider1) + int(slider2) + int(slider3)
    return JsonResponse({'result': result, 'slider1': slider1, 'slider2': slider2, 'slider3': slider3})
