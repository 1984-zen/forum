from django.shortcuts import render
import json
from django.http import JsonResponse

def get_labelme_json_file(request):
    data = request.body.decode('utf-8') 
    labelme_json_file = json.loads(data)
    print(labelme_json_file['shapes'])
    return JsonResponse({'status': 'get labelme json formate successfully'})
