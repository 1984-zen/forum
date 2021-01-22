from django.shortcuts import render
import json
from django.http import JsonResponse

def get_labelme_json_file_path(request):
    if(request.method == "POST"):
        labelme_json_file_path = request.POST.get("labelme_json_file_path")
        print(labelme_json_file_path)
        return JsonResponse({'status': 'get labelme labelme json file path successfully'})
