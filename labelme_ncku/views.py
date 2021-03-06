from django.shortcuts import render
import json
from django.http import JsonResponse
import os
import os.path as osp
import warnings
import PIL.Image
import yaml
from labelme import utils
import base64
import numpy as np
from numpy import save, load, savez
import re
from django.template.response import TemplateResponse
from labelme_ncku.models import Input_imgs, Labels
from accounts.models import Users
from django.conf import settings
import logging
import sys
from django.db.models import Count, Max
from django.db.models.expressions import F, Window
from django.db.models.functions.window import RowNumber
from django.db.models.functions import Rank, DenseRank
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Prefetch
from django.http import HttpResponse

# np.set_printoptions(threshold=sys.maxsize, linewidth=sys.maxsize) #測試numpy的時候才需要打開註解，會將print()numpy array全部顯示
#set logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_img(data):
    if data['imageData']:
        imageData = data['imageData']
    else:
        imagePath = data['imagePath']

        with open(imagePath, 'rb') as filepath:
            imageData = filepath.read()
            imageData = base64.b64encode(imageData).decode('utf-8')
    img = utils.img_b64_to_arr(imageData)
    return img

def save_json_data_to_file(jsons_folder_path, img_name, data):
    with open(f'{jsons_folder_path}/{img_name}.json', 'w') as filepath:
        json_object = json.dumps(data, indent = 4) #indent是拿來美化用的，data是上面讀取json檔案的資料
        filepath.write(json_object)

def update_dictionary(data, training_folder_path, dictionary_path):
    dictionary = json.load(open(dictionary_path))
    #檢查並擴充dictionary
    for shape in data['shapes']: #拿到json檔案裡面全部的labels資訊
        label_id = shape['label_id']
        label_name = shape['label']
        #檢查dictionary是否需要擴充
        if label_name not in dictionary.keys():
            #如果dictionary裡面沒有任何key values記錄
            if len(dictionary) == 0:
                dictionary_id = 1
            #如果有紀錄
            else:
                #抓取最大的value + 1
                dictionary_id = max(dictionary.values()) + 1
            #擴充dictionary
            dictionary[label_name] = dictionary_id #dictionary {'new_label_name: total + 1}
            #就更新到dictionary.json
            with open(f'{training_folder_path}/dictionary.json', 'w') as filepath:
                json_object = json.dumps(dictionary, indent = 4) #indent是拿來美化用的，data是上面讀取json檔案的資料
                filepath.write(json_object)
    return dictionary

def create_dictionary(training_folder_path, input_img_id):
    #從資料庫撈出dictionary_from_db[(label_name, dictionary_id)]
    dictionary_from_db = Labels.objects.filter(input_img_id = input_img_id).values("label_name").annotate(Count('id')).annotate(Max('dictionary_id')).annotate(rank = Window(expression=Rank(), order_by=F('id').asc())).values_list("label_name", "dictionary_id")
    dictionary = dict()
    #開始建立dictionary.json檔案內容
    for tup in dictionary_from_db:
        #tup(label_name, dictionary_id)
        dictionary[str(tup[0])] = int(tup[1])

    #把dictionary存成json檔案 例如:media/labelme/example_folder/dictionary.json
    with open(f'{training_folder_path}/dictionary.json', 'w') as filepath:
        json_object = json.dumps(dictionary, indent = 4) #indent是拿來美化用的，data是上面讀取json檔案的資料
        filepath.write(json_object)

def load_dictionary(training_folder_path, data, input_img_id):
    dictionary_path = f'{training_folder_path}/dictionary.json'
    #先檢查dictionary檔案是否存在
    if not osp.isfile(dictionary_path):
        #建立dictionary.json
        create_dictionary(training_folder_path, input_img_id)
    #最新的dictionary
    dictionary = update_dictionary(data, training_folder_path, dictionary_path)
    return dictionary

def create_label_name_to_value(data, dictionary, create_status, delete_status, lists):
    label_name_to_value = dict()
    for shape in data['shapes']: #拿到json檔案裡面全部的labels資訊
        label_id = shape['label_id']
        label_name = shape['label']
        #比對資料庫是否有這筆label_id(這張原圖中)
        if create_status:
            if label_id not in lists:
                #現在label_name_to_value是我們要的名單
                label_value = dictionary[label_name]
                label_name_to_value[label_name] = label_value
        #如果刪除到有重複的label_name時候
        if delete_status:
            if label_name in lists:
                #現在label_name_to_value是我們要的名單
                label_value = dictionary[label_name]
                label_name_to_value[label_name] = label_value
    return label_name_to_value

def get_shapes(data, label_name_to_value):
    shapes = []
    for shape in data['shapes']:
        label_name = shape['label']
        if label_name in label_name_to_value.keys():
            shapes.append(shape)
    return shapes

#將單張mask存成白圖黑底
def lblsave_white_mask(filename, lbl):
    if osp.splitext(filename)[1] != '.png':
        filename += '.png'
    if lbl.min() >= -1 and lbl.max() < 255:
        lbl_pil = PIL.Image.fromarray(lbl.astype(np.uint8), mode='P')
        colormap = np.ones((255, 3), dtype=float)
        colormap[0] = [0, 0, 0]
        lbl_pil.putpalette((colormap * 255).astype(np.uint8).flatten())
        lbl_pil.save(filename)
    else:
        #紀錄log
        logger.warn(
            '[%s] Cannot save the pixel-wise class label as PNG, '
            'so please use the npy file.' % filename
        )

def save_files(label_name_to_value, lbl, label_values, label_names, training_folder_name, img_name, label_collection_folder_path):
    for i in range(len(label_name_to_value)):
        #(lbl==[label_values[i]])會印出True/False，加上astype(np.uint8)會印出0/1
        label_numpy = (lbl==[label_values[i]]).astype(np.uint8) #lbl包含了很多個numpy array，"=="可以只找出對應dictionary的numpy array

        #布林遮罩，判斷numpy array裡面的label_numpy > 0的話就替換成對應的label_values值(label_values等同dictionary_id)
        label_numpy[label_numpy > 0] = label_values[i]

        npy_path = osp.join(settings.BASE_DIR, f'media/labelme/{training_folder_name}/npys/{img_name}_{label_names[i]}.npy')

        #儲存npy檔案，存在 例如:media/labelme/example_folder/npys/.npy
        save(npy_path, label_numpy)

        label_pic_path = osp.join(label_collection_folder_path, f'{img_name}_{label_names[i]}.png')

        #儲存label_pic圖片，存在 例如:media/labelme/example_folder/label_images_set/img1/.png
        lblsave_white_mask(label_pic_path, label_numpy) #產生label_pic

def update_training_txt(request, training_folder_name):
    training_folder_ids = Input_imgs.objects.filter(training_folder_name = training_folder_name).values_list("id", flat = True)
    training_txt = Labels.objects.filter(input_img_id__in = training_folder_ids).values_list("npy_path", "dictionary_id")
    training_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}'

    #從training_folder_path去寫入到training.txt檔案裏面
    with open(osp.join(training_folder_path, 'training.txt'), 'w') as filepath:
        for txt in training_txt:
            #txt[0] = npy_path
            #txt[1] = dictionary_id
            filepath.write(f'{txt[0].replace(f"labelme/{training_folder_name}/", "")} {txt[1]}' + '\n') #RegEx掉labelme/example_folder/之後把npys/.npy + dictionary_id寫進txt裡面
    return HttpResponse("成功產生training.txt<br><a href=\"/labelme\">回到首頁</a>")

def labelme_url(request):
    return {'LABELME_URL': settings.LABELME_URL}

def search(request, training_folder_name):
    find_keyword = request.GET.get('keyword')
    jump_page = request.GET.get('jump_page')

    if not find_keyword:
        return HttpResponseRedirect(reverse("show_patient_list", kwargs={"training_folder_name": training_folder_name}) + "?page=1")

    filtered_patient_list = Input_imgs.objects.filter(training_folder_name = training_folder_name).filter(Q(patient_folder_name__icontains=find_keyword)).values('patient_folder_name').annotate(Count('patient_folder_name')).filter(patient_folder_name__count__gte=1)

    if jump_page:
        return HttpResponseRedirect(reverse('search', kwargs={"training_folder_name": training_folder_name}) + "?page=" + jump_page + "&keyword=" + find_keyword)
    else:
        page = request.GET.get('page', 1)

    paginator = Paginator(filtered_patient_list, 20)

    try:
        labels_in_page = paginator.page(page)
    except PageNotAnInteger:
        labels_in_page = paginator.page(1)
    except EmptyPage:
        labels_in_page = paginator.page(paginator.num_pages)

    return TemplateResponse(request, 'show_patient_list.html', {'patient_list_in_page': labels_in_page, 'training_folder_name': training_folder_name})

def show_training_list(request):
    training_folder_list = Input_imgs.objects.values('training_folder_name').annotate(Count('id')).values_list('training_folder_name', flat = True)

    return TemplateResponse(request, 'show_training_list.html', {'training_folder_list': training_folder_list})


def show_patient_list(request, training_folder_name):
    training_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}'
    jump_page = request.GET.get('jump_page')
    back_to_patient_current_page = request.GET.get('back_to_patient_current_page')

    patient_list = Input_imgs.objects.filter(training_folder_name = training_folder_name).values('patient_folder_name').annotate(Count('patient_folder_name')).filter(patient_folder_name__count__gte=1)

    if jump_page:
        return HttpResponseRedirect(reverse('show_patient_list', kwargs={"training_folder_name": training_folder_name}) + "?page=" + jump_page)
    elif back_to_patient_current_page:
        page = request.GET.get('back_to_patient_current_page')
    else:
        page = request.GET.get('page', 1)

    paginator = Paginator(patient_list, 20)

    try:
        patient_list_in_page = paginator.page(page)
    except PageNotAnInteger:
        patient_list_in_page = paginator.page(1)
    except EmptyPage:
        patient_list_in_page = paginator.page(paginator.num_pages)

    return TemplateResponse(request, 'show_patient_list.html', {'patient_list_in_page': patient_list_in_page, 'training_folder_name': training_folder_name, 'training_folder_path': training_folder_path})

def show_patient_labels(request, training_folder_name, patient_folder_name):
    jump_page = request.GET.get('jump_page')
    #這個ids是避免template出現重複label_name用的，以'label_name', 'input_img_id'做分組並列出有大於等於1的結果，然後再取這些分組結果每組的最大id並攤平化 ids = <QuerySet [59, 60, 61, 63]>
    ids = Labels.objects.values('label_name', 'input_img_id').annotate(Count('label_name')).filter(label_name__count__gte=1).annotate(Max('id')).values_list('id__max', flat = True)

    #Input_img 去 LEFT JOIN Labels
    input_img_labels = Input_imgs.objects.filter(training_folder_name = training_folder_name, patient_folder_name = patient_folder_name).prefetch_related(Prefetch('labels', queryset=Labels.objects.filter(id__in = ids)))

    if jump_page:
        return HttpResponseRedirect(reverse('show_patient_labels', kwargs={"training_folder_name": training_folder_name, "patient_folder_name": patient_folder_name}) + "?page=" + jump_page)
    else:
        page = request.GET.get('page', 1)

    paginator = Paginator(input_img_labels, 20)

    try:
        labels_in_page = paginator.page(page)
    except PageNotAnInteger:
        labels_in_page = paginator.page(1)
    except EmptyPage:
        labels_in_page = paginator.page(paginator.num_pages)

    return TemplateResponse(request, 'show_label_list.html', {'input_img_labels': labels_in_page, 'training_folder_name': training_folder_name, 'patient_folder_name': patient_folder_name})

def create_label(request):
    if request.method == "POST":
        username = request.POST.get("username").replace('\n', "").replace('\r', "")
        #labelme_json_path = D:/my_labelme_project/Annotations/example_folder/example_subfolder/img2.json
        labelme_json_path = request.POST.get("labelme_json_path").replace('\r\n', "")

        #如果檔案存在且是一個檔案且附檔名是.json
        if osp.isfile(labelme_json_path) and labelme_json_path.endswith('.json'):
            #用剛剛的username查詢user_id
            user_id = Users.objects.get(username = username).id

            training_folder_name = request.POST.get("training_folder_name").split("/")[0].replace('\n', "").replace('\r', "") #example_folder

            #labelme_json_path D:/my_labelme_project/Annotations/example_folder/img2.json
            data = json.load(open(labelme_json_path))

            input_img_path = data['imagePath'] #此path為Labelme專案中/Images/example_folder/.jpg

            input_img_name = request.POST.get("input_img_name").replace('\n', "").replace('\r', "") #img1.jpg

            img_name = input_img_name.replace('.jpg', '') #img1

            #training model的根目錄路徑
            training_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}' #D:\my_projects/media/labelme/example_folder

            #通過labelme處理訓練後存放json檔的資料夾
            jsons_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/jsons' #D:\my_projects/media/labelme/example_folder/jsons

            #存放著各input_img的label.png的根目錄
            label_images_set_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/label_images_set' #D:\my_projects/media/labelme/example_folder/label_images_set

            #label.png存放所在的資料夾路徑
            label_collection_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/label_images_set/{img_name}' #D:\my_projects/media/labelme/example_folder/label_images_set/img3

            #存放所有npy檔案的資料夾路徑
            npys_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/npys'

            #查詢資料庫是否有這張input_img的紀錄
            try:
                input_img_id = Input_imgs.objects.get(img_name = input_img_name).id
            #沒有這張input_img的紀錄就直接結束
            except Input_imgs.DoesNotExist:
                #紀錄log
                logger.warn(
                    '[Create] Create label failed. Because this input_img: [%s] does not exsit in DB' % (input_img_name)
                )
                return JsonResponse({'status': f'create label failed. Because this input_img: [{input_img_name}] does not exsit in DB'})
            if not osp.exists(training_folder_path):
                os.mkdir(training_folder_path)

            if not osp.exists(jsons_folder_path):
                os.mkdir(jsons_folder_path)

            if not osp.exists(label_images_set_folder_path):
                os.mkdir(label_images_set_folder_path)

            if not osp.exists(label_collection_folder_path):
                os.mkdir(label_collection_folder_path)

            if not osp.exists(npys_folder_path):
                os.mkdir(npys_folder_path)

            #儲存成file.json在 例如:media/labelme/example_folder/jsons/.json
            save_json_data_to_file(jsons_folder_path, img_name, data)

            #從json檔讀取base64圖
            img = read_img(data)

            #載入並更新dictionary
            dictionary = load_dictionary(training_folder_path, data, input_img_id)

            label_ids_from_db = Labels.objects.filter(input_img_id = input_img_id).values_list("label_id", flat = True)

            #第一步先把資料庫沒有的label_id加到label_name_to_value名單
            label_name_to_value = create_label_name_to_value(data, dictionary, 1, 0, label_ids_from_db)

            #第二步把label_name_to_value從data的名單中將labels及points(注意:label_name可能會重複，但shape內容不同)加到shapes
            shapes = get_shapes(data, label_name_to_value)

            #開始處理numpy_array，lbl包含了每個label的numpy_array
            #img.shape 的.shape會是一組tuple，像是(x維度，y個元素)
            lbl = utils.shapes_to_label(img.shape, shapes, label_name_to_value) #shape_to_label(img_shape, shape, label_name_to_value, type='class')

            #將input_img原圖另存在 例如:media/labelme/example_folder/label_images_set/img_name/.npy
            PIL.Image.fromarray(img).save(f'{label_collection_folder_path}/{img_name}.png') #fromarray(img)裡面的參數為一個做好的圖片，然後存在一個路徑下，這裡是存image_img.png

            label_values, label_names = [], []

            for ln, lv in label_name_to_value.items():
                label_values.append(lv) #lv就是對應label的dictionary_id
                label_names.append(ln) #ln就是label name

            #開始一張一張存檔案(npy, label_pic)及寫入資料庫
            save_files(label_name_to_value, lbl, label_values, label_names, training_folder_name, img_name, label_collection_folder_path)

            #資料庫寫入這筆label
            for shape in data['shapes']:
                label_id = shape['label_id'].replace('\r', "")
                label_name = shape['label']
                #比對資料庫是否有這筆label_id(這張原圖中)
                if label_id not in label_ids_from_db:
                    label_pic_path = f'labelme/{training_folder_name}/label_images_set/{img_name}/{img_name}_{label_name}.png'
                    npy_path = f'labelme/{training_folder_name}/npys/{img_name}_{label_name}.npy'
                    create_label = Labels(label_name = label_name, label_pic_path = label_pic_path, npy_path = npy_path, user_id = user_id, input_img_id = input_img_id, label_id = label_id, dictionary_id = dictionary[label_name])
                    create_label.save()
                    #紀錄log
                    logger.info(
                        '[Create] create label successfully. Input_img_name: [%s] has been create label_name [%s] which label_id is [%s]' % (input_img_name, label_name, label_id)
                    )

            #重新抓取DB的"npy_path", "dictionary_id"資料並覆蓋到training.txt檔案
            # update_training_txt(training_folder_name, training_folder_path)

            # #紀錄log
            # logger.info(
            #     '[Create] Recorded to training.txt of [%s] training model successfully, file path: [%s/training.txt]' % (training_folder_name, training_folder_path)
            # )

            return JsonResponse({'status': f'create label successfully. input_img_name: [{input_img_name}] has been create Label_name: [{label_names}]'})

        #紀錄log
        logger.warn(
        '[Create] Create label failed. Because this labelme_json_path: [%s] does not exsit' % (labelme_json_path)
        )
        return JsonResponse({'status': f'create label failed. Because this labelme_json_path: [{labelme_json_path}] does not exsit'})

    return JsonResponse({})

def update_label(request):
    if request.method == "POST":
        username = request.POST.get("username").replace('\n', "").replace('\r', "")
        input_img_name = request.POST.get("input_img_name").replace('\n', "").replace('\r', "") #img1.jpg
        img_name = input_img_name.replace('.jpg', '') #img1
        edited_label_id = request.POST.get("edited_label_id").replace('\n', "").replace('\r', "") #要Edited label的id
        edited_label_name = request.POST.get("edited_label_name").replace('\n', "").replace('\r', "") #Edited label的name
        training_folder_name = request.POST.get("training_folder_name").split("/")[0].replace('\n', "").replace('\r', "") #example_folder
        #training model的根目錄路徑
        training_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}' #D:\my_projects/media/labelme/example_folder
        labelme_json_path = request.POST.get("labelme_json_path").replace('\r\n', "") #example_folder #D:\my_projects/media/labelme/example_folder/img1.json
        #通過labelme處理訓練後存放json檔的資料夾
        jsons_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/jsons' #D:\my_projects/media/labelme/example_folder/jsons
        #label.png存放所在的資料夾路徑
        label_collection_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/label_images_set/{img_name}' #D:\my_projects/media/labelme/example_folder/label_images_set/img3

        #查詢資料庫是否有這張input_img的紀錄
        try:
            input_img_id = Input_imgs.objects.get(img_name = input_img_name).id
        #沒有這張input_img的紀錄就直接結束
        except Input_imgs.DoesNotExist:
            #紀錄log
            logger.warn(
                '[Edit] Edit label failed. Because this input_img: [%s] does not exsit in DB' % (input_img_name)
            )
            return JsonResponse({'status': f'edit label failed. Because this input_img: [{input_img_name}] does not exsit in DB'})

        #如果資料庫裡有這個label_id的話，就Edit檔案及資料庫
        label = Labels.objects.filter(input_img_id = input_img_id).filter(label_id = edited_label_id)
        has_label_id = label.values("label_id").annotate(Count("label_id")).filter(label_id__count__gt = 0)

        #如果有這個label_id
        if has_label_id:
            #如果檔案存在且是一個檔案且附檔名是.json
            if osp.isfile(labelme_json_path) and labelme_json_path.endswith('.json'):
                #用剛剛的username查詢user_id
                user_id = Users.objects.get(username = username).id

                #labelme_json_path D:/my_labelme_project/Annotations/example_folder/img2.json
                data = json.load(open(labelme_json_path))
                #儲存成file.json在 例如:media/labelme/example_folder/jsons/.json
                save_json_data_to_file(jsons_folder_path, img_name, data)

                #從json檔讀取base64圖
                img = read_img(data)              

                #載入並更新dictionary
                dictionary = load_dictionary(training_folder_path, data, input_img_id)
                #開始驗證是否有修改label name的rename情況
                old_label_name = label.values_list('label_name', flat = True)[0]

                if old_label_name == edited_label_name:
                    #第一步先把要edit的label_id加到label_name_to_value名單
                    label_name_to_value = create_label_name_to_value(data, dictionary, 0, 1, [edited_label_name]) #第3個參數為create_status, 第4個參數為delete_status

                    #第二步把label_name_to_value從data的名單中將labels及points(注意:label_name可能會重複，但shape內容不同)加到shapes
                    shapes = get_shapes(data, label_name_to_value)

                    #開始處理numpy_array，lbl包含了每個label的numpy_array
                    #img.shape 的.shape會是一組tuple，像是(x維度，y個元素)
                    lbl = utils.shapes_to_label(img.shape, shapes, label_name_to_value) #shape_to_label(img_shape, shape, label_name_to_value, type='class')

                    label_values, label_names = [], []

                    for ln, lv in label_name_to_value.items():
                        label_values.append(lv) #lv就是對應label的dictionary_id
                        label_names.append(ln) #ln就是label name

                    #開始一張一張存檔案(npy, label_pic)及寫入資料庫
                    save_files(label_name_to_value, lbl, label_values, label_names, training_folder_name, img_name, label_collection_folder_path)

                #如果edited_label_name與原先不同，就要刪除舊npy及label_pic檔案，以及更新到資料庫及重新覆蓋training.txt
                elif old_label_name != edited_label_name:
                    #查找dictionary_id比對有無同樣叫這個edited_label_name
                    dictionary_id = dictionary[edited_label_name]

                    #刪除舊label_name的npy檔案
                    npy_path = label.values_list('npy_path', flat = True)[0]
                    if osp.isfile(f'{settings.BASE_DIR}/media/{npy_path}'):
                        #移除npy檔案 例如:labelme/example_folder/npys/.npy
                        os.remove(f'{settings.BASE_DIR}/media/{npy_path}')

                    #刪除舊label_name的label_pic圖片
                    label_pic_path = label.values_list('label_pic_path', flat = True)[0]
                    if osp.isfile(f'{settings.BASE_DIR}/media/{label_pic_path}'):
                        #移除npy檔案 例如:labelme/example_folder/label_images_set/img1/.png
                        os.remove(f'{settings.BASE_DIR}/media/{label_pic_path}')

                    npy_path = f'labelme/{training_folder_name}/npys/{img_name}_{edited_label_name}.npy'

                    label_pic_path = f'labelme/{training_folder_name}/label_images_set/{img_name}/{img_name}_{edited_label_name}.png'

                    #資料庫修改這筆label的label_name
                    label.update(label_name = edited_label_name, dictionary_id = dictionary_id, npy_path = npy_path, label_pic_path = label_pic_path)

                    #第一步先把要edit的label_id加到label_name_to_value名單
                    #因為原本的npy和label_pic有異動，所以要叫出所有叫這個old_label_name的檔案都重新產一次npy和label_pic
                    label_name_to_value = create_label_name_to_value(data, dictionary, 0, 1, [old_label_name, edited_label_name]) #第3個參數為create_status, 第4個參數為delete_status

                    #第二步把label_name_to_value從data的名單中將labels及points(注意:label_name可能會重複，但shape內容不同)加到shapes
                    shapes = get_shapes(data, label_name_to_value)

                    #開始處理numpy_array，lbl包含了每個label的numpy_array
                    #img.shape 的.shape會是一組tuple，像是(x維度，y個元素)
                    lbl = utils.shapes_to_label(img.shape, shapes, label_name_to_value) #shape_to_label(img_shape, shape, label_name_to_value, type='class')

                    label_values, label_names = [], []

                    for ln, lv in label_name_to_value.items():
                        label_values.append(lv) #lv就是對應label的dictionary_id
                        label_names.append(ln) #ln就是label name

                    #開始一張一張存檔案(npy, label_pic)及寫入資料庫
                    save_files(label_name_to_value, lbl, label_values, label_names, training_folder_name, img_name, label_collection_folder_path)

                    #紀錄log
                    logger.info(
                        '[Edit] rename label successfully. Input_img_name: [%s] has been renamed label_name [%s] to new name [%s] which label_id is [%s]' % (input_img_name, old_label_name, edited_label_name, edited_label_id)
                    )

                    #重新抓取DB的"npy_path", "dictionary_id"資料並覆蓋到training.txt檔案
                    # update_training_txt(training_folder_name, training_folder_path)

                    # #紀錄log
                    # logger.info(
                    # '[Edit] Recorded to training.txt of [%s] training model successfully, file path: [%s/training.txt]' % (training_folder_name, training_folder_path)
                    # )

                #紀錄log
                logger.info(
                    '[Edit] edited label successfully. Input_img_name: [%s] has been edit label_name [%s] npy file and label_pic which label_id is [%s]' % (input_img_name, edited_label_name, edited_label_id)
                )
                return JsonResponse({'status': f'edited label successfully. input_img_name: [{input_img_name}] has been updated Label_name: [{edited_label_name}]'})

            #紀錄log
            logger.warn(
            '[Edit] edit label failed. Because this [%s.json] file does not exsit in [%s]' % (img_name, labelme_json_path)
            )
            return JsonResponse({'status': f'edit label failed. Because this json file does not exsit in {labelme_json_path}'})

        #紀錄log
        logger.warn(
            '[Edit] edit label failed. Because this label_id: [%s] does not exsit in DB' % (edited_label_id)
        )
        return JsonResponse({'status': f'edit label failed. Because this label_id: [{edited_label_id}] does not exsit in DB'})

    return JsonResponse({})

def delete_label(request):
    if request.method == "POST":
        #該label的原圖檔案名稱
        input_img_name = request.POST.get("input_img_name").replace('\n', "").replace('\r', "") #img1.jpg
        deleted_label_id = request.POST.get("deleted_label_id").replace('\n', "").replace('\r', "") #要刪除label的id
        deleted_label_name = request.POST.get("deleted_label_name").replace('\n', "").replace('\r', "") #要刪除label的name
        training_folder_name = request.POST.get("training_folder_name").split("/")[0].replace('\n', "").replace('\r', "") #example_folder
        training_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}' #D:\my_projects/media/labelme/example_folder

        #查詢資料庫是否有這張input_img的紀錄
        try:
            #查詢原圖的id
            input_img_id = Input_imgs.objects.get(img_name = input_img_name).id
        #沒有這張input_img的紀錄就直接結束
        except Input_imgs.DoesNotExist:
            #紀錄log
            logger.warn(
                '[Delete Failed] Delete label failed. Because this input_img: [%s] does not exsit in DB' % (input_img_name)
            )
            return JsonResponse({'status': f'delete label failed. Because this input_img: [{input_img_name}] does not exsit in DB'})

        img_name = input_img_name.replace('.jpg', '') #去除副檔名

        #如果資料庫裡有這個label_id的話，就刪除檔案及資料庫
        label = Labels.objects.filter(input_img_id = input_img_id).filter(label_id = deleted_label_id)
        has_label_id = label.values("label_id").annotate(Count("label_id")).filter(label_id__count__gt = 0)

        #如果有這個label_id
        if has_label_id:
            #開始檢查是否有重複的label_name
            is_duplicate_label_name = Labels.objects.filter(input_img_id__in = label.values("input_img_id")).filter(label_name = deleted_label_name).values("label_name").annotate(Count("label_name")).filter(label_name__count__gt = 1)

            #如果沒有重複label_name就直接刪除npy檔, 刪除label_pic檔案, 刪除DB裡的資料
            if not is_duplicate_label_name:

                npy_path = label.values_list('npy_path', flat = True)[0]
                label_pic_path = label.values_list('label_pic_path', flat = True)[0]

                #刪除npy檔案
                if osp.isfile(f'{settings.BASE_DIR}/media/{npy_path}'):
                    #移除npy檔案 例如:labelme/example_folder/npys/.npy
                    os.remove(f'{settings.BASE_DIR}/media/{npy_path}')

                #刪除label_pic檔案
                if osp.isfile(f'{settings.BASE_DIR}/media/{label_pic_path}'):
                    os.remove(f'{settings.BASE_DIR}/media/{label_pic_path}')

                #刪除DB的資料
                label.delete()

                #紀錄log
                logger.info(
                    '[Delete] Delete label successfully. Input_img_name: [%s] has been deleted label_name [%s] which label_id is [%s]' % (input_img_name, deleted_label_name, deleted_label_id)
                )

                #重新抓取DB的"npy_path", "dictionary_id"資料並覆蓋到training.txt檔案
                # update_training_txt(training_folder_name, training_folder_path)

                # #紀錄log
                # logger.info(
                #     '[Delete] Recorded to training.txt of [%s] training model successfully, file path: [%s/training.txt]' % (training_folder_name, training_folder_path)
                # )

            #如果有重複label_name就更新npy檔案，更新label_pic，因為同一個名子都會被合併成一個檔案
            elif is_duplicate_label_name:

                #json_file_path是 D:/my_labelme_project/Annotations/example_folder/img2.json
                json_file_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/jsons/{img_name}.json'

                data = json.load(open(json_file_path))

                #更新json檔案，把目前要刪除的label_id的shape從data給移除掉
                for i, shape in enumerate(data['shapes']): #拿到json檔案裡面全部的labels資訊
                    label_id = shape['label_id']
                    label_name = shape['label']
                    #找到這個shape的index位置然移除該shape
                    if label_id in deleted_label_id:
                        #移除該shape
                        del data['shapes'][i]
                        break

                jsons_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/jsons' #D:\my_projects/media/labelme/example_folder/jsons

                #更新json檔案
                save_json_data_to_file(jsons_folder_path, img_name, data)

                #載入dictionary
                dictionary = load_dictionary(training_folder_path, data, input_img_id)

                #把json檔內有叫deleted_label_name的加到label_name_to_value名單
                label_name_to_value = create_label_name_to_value(data, dictionary, 0, 1, [deleted_label_name])

                #把label_name_to_value名單中的labels及points(注意:label_name可能會重複，但shape內容不同)加到shapes
                shapes = get_shapes(data, label_name_to_value)

                #從json檔讀取base64圖
                img = read_img(data)

                #開始處理numpy_array，lbl包含了每個label的numpy_array
                #img.shape 的.shape會是一組tuple，像是(x維度，y個元素)
                lbl = utils.shapes_to_label(img.shape, shapes, label_name_to_value) #shape_to_label(img_shape, shape, label_name_to_value, type='class')

                label_collection_folder_path = f'{training_folder_path}/label_images_set/{img_name}'

                label_values, label_names = [], []

                for ln, lv in label_name_to_value.items():
                    label_values.append(lv) #lv就是Tuple的index編號: 0, 1, 2, 3, ...
                    label_names.append(ln) #ln就是label name

                #開始一張一張存檔案(npy, label_pic)及寫入資料庫
                save_files(label_name_to_value, lbl, label_values, label_names, training_folder_name, img_name, label_collection_folder_path)

                #如果json檔沒有任何一個叫deleted_label_name，但資料庫有的話，就全部刪除資料庫裡有叫deleted_label_name的資料
                if not label_name_to_value:
                    labels = Labels.objects.filter(input_img_id = input_img_id).filter(label_name = deleted_label_name)
                    #刪除DB的資料
                    labels.delete()
                else:
                    #刪除DB的資料
                    label.delete()

                #紀錄log
                logger.info(
                    '[Delete] Delete label successfully. Input_img_name: [%s] has been deleted label_name [%s] which label_id is [%s]' % (input_img_name, deleted_label_name, deleted_label_id)
                )
            return JsonResponse({'status': f'delete label successfully. input_img_name: [{input_img_name}] has been delete Label_name: [{deleted_label_name}] which label_id: [{deleted_label_id}]'})
        #紀錄log
        logger.warn(
            '[Delete] Delete label failed. Because this label_id: [%s] does not exsit in DB' % (deleted_label_id)
        )
        return JsonResponse({'status': f'delete label failed. Because this label_id: [{deleted_label_id}] does not exsit in DB'})

    return JsonResponse({})