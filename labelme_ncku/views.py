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
from django.db.models.functions import Rank

np.set_printoptions(threshold=sys.maxsize, linewidth=sys.maxsize) #將print()numpy array全部顯示
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

def save_json_data_to_file(jsons_folder_path, input_img_name, data):
    with open(f'{jsons_folder_path}/{input_img_name}.json', 'w') as filepath:
        json_object = json.dumps(data, indent = 4) #indent是拿來美化用的，data是上面讀取json檔案的資料
        filepath.write(json_object)

def update_dictionary(data, dictionary, training_folder_path):
    #檢查並擴充dictionary
    for shape in data['shapes']: #拿到json檔案裡面全部的labels資訊
        label_id = shape['label_id']
        label_name = shape['label']
        #檢查dictionary是否需要擴充
        if label_name not in dictionary:
            dictionary_id = len(dictionary)
            #擴充dictionary
            dictionary[label_name] = dictionary_id #dictionary {'new_label_name: total + 1}
            #就更新到dictionary.json
            with open(f'{training_folder_path}/dictionary.json', 'w') as filepath:
                json_object = json.dumps(dictionary, indent = 4) #indent是拿來美化用的，data是上面讀取json檔案的資料
                filepath.write(json_object)

def create_dictionary(training_folder_path):
    #從資料庫撈出label_name及Rank排名的QuerySet[{'label_name': 'ddd', 'rank': 1},...]，Rank會當作是dictionary_id
    dictionary_from_db = Labels.objects.values("label_name").annotate(Count('id')).annotate(rank = Window(expression=Rank(), order_by=F('id').asc())).values("label_name", "rank")
    dictionary = dict()
    #開始建立dictionary.json檔案內容
    for obj in dictionary_from_db:
        #obj = {'label_name': 'ddd', 'rank': 1}
        dictionary[str(obj['label_name'])] = obj['rank']

    #把dictionary存成json檔案 例如:media/labelme/example_folder/dictionary.json
    with open(f'{training_folder_path}/dictionary.json', 'w') as filepath:
        json_object = json.dumps(dictionary, indent = 4) #indent是拿來美化用的，data是上面讀取json檔案的資料
        filepath.write(json_object)

def load_dictionary(training_folder_path):
    dictionary_path = f'{training_folder_path}/dictionary.json'
    if not osp.isfile(dictionary_path):
        create_dictionary(training_folder_path)
    dictionary = json.load(open(dictionary_path))
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
        if label_name in label_name_to_value:
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
        logger.warn(
            '[%s] Cannot save the pixel-wise class label as PNG, '
            'so please use the npy file.' % filename
        )

def save_files(label_name_to_value, lbl, label_values, label_names, training_folder_name, input_img_name, label_collection_folder_path):
    for i in range(len(label_name_to_value)):
        #(lbl==[label_values[i]])會印出True/False，加上astype(np.uint8)會印出0/1
        label_numpy = (lbl==[label_values[i]]).astype(np.uint8) #lbl包含了很多個numpy array，"=="可以只找出對應dictionary的numpy array

        #布林遮罩，判斷numpy array裡面的label_numpy > 0的話就替換成對應的label_values值(label_values等同dictionary_id)
        label_numpy[label_numpy > 0] = label_values[i]

        npy_path = osp.join(settings.BASE_DIR, f'media/labelme/{training_folder_name}/npys/{input_img_name}_{label_names[i]}.npy')

        #儲存npy檔案，存在 例如:media/labelme/example_folder/npys/.npy
        save(npy_path, label_numpy)

        label_pic_path = osp.join(label_collection_folder_path, f'{input_img_name}_{label_names[i]}.png')

        #儲存label_pic圖片，存在 例如:media/labelme/example_folder/label_images_set/img1/.png
        lblsave_white_mask(label_pic_path, label_numpy) #產生label_numpy圖片

        #儲存合併在npz檔案裡面 例如:media/labelme/example_folder/.npz
        npz_path = osp.join(settings.BASE_DIR, f'media/labelme/{training_folder_name}/{training_folder_name}.npz')

        # 如果沒有npz檔案，就要先建立檔案
        if not osp.isfile(npz_path):
            npz_data = dict() #因為npz是dic格式
        # 如果有npz檔案
        elif osp.isfile(npz_path):
            npz_data = dict(np.load(npz_path)) #解開npz

        npz_data[f'{input_img_name}_{label_names[i]}'] = label_numpy

        #第一筆會建創成一個新的npz檔案，之後是更新這npz檔案
        savez(npz_path, **npz_data)

def labelme_url(request):
    return {'LABELME_URL': settings.LABELME_URL}

def show_label_list(request):
    # 用'label_name', 'input_img_id'做分組並列出有大於等於1的結果，然後再取這些分組結果每組的最大id並攤平化 ids = <QuerySet [59, 60, 61, 63]>
    ids = Labels.objects.values('label_name', 'input_img_id').annotate(Count('label_name')).filter(label_name__count__gte=1).annotate(Max('id')).values_list('id__max', flat = True)

    # labels會印出object結構的QuerySet
    labels = Labels.objects.filter(id__in = ids)

    npz_path = osp.join(settings.BASE_DIR, f'media/labelme/example_folder/example_folder.npz')

    if osp.isfile(npz_path):
        npz_path = f'/media/labelme/example_folder/example_folder.npz'
        return TemplateResponse(request, 'label_list.html', {'labels': labels, 'npz_path': npz_path})
    return TemplateResponse(request, 'label_list.html', {'labels': labels})

def create_label(request):
    if request.method == "POST":
        username = request.POST.get("username")
        #labelme_json_path = D:/my_labelme_project/Annotations/example_folder/img2.json
        labelme_json_path = request.POST.get("labelme_json_file_path")

        #如果檔案存在且是一個檔案且附檔名是.json
        if osp.isfile(labelme_json_path) and labelme_json_path.endswith('.json'):
            #用剛剛的username查詢user_id
            user_id = Users.objects.get(username = username).id

            pattern = '^(\w:)?\/(\w+)\/(\w+)\/(\w+)'
            match = re.search(pattern, labelme_json_path)
            if match:
                #group()會拿到full match，D:/my_labelme_project/Annotations/example_folder
                #training_folder_name = example_folder
                training_folder_name = match.group().split('/')[-1]

            #labelme_json_path D:/my_labelme_project/Annotations/example_folder/img2.json
            data = json.load(open(labelme_json_path))

            #save_diretory
            input_img_name = osp.basename(labelme_json_path).replace('.json', '') #baseneme就是獲取檔案名稱，並移除附檔名

            #存放所有json檔案的資料夾路徑
            training_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}' #D:\my_projects/media/labelme/example_folder

            #通過labelme處理訓練原圖後生成的json檔案
            jsons_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/jsons' #D:\my_projects/media/labelme/example_folder/jsons

            #label_images_set資料夾路徑
            label_images_set_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/label_images_set' #D:\my_projects/media/labelme/example_folder/label_images_set

            #label.png存放所在的資料夾路徑
            label_collection_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/label_images_set/{input_img_name}' #D:\my_projects/media/labelme/example_folder/label_images_set/img3

            if not osp.exists(training_folder_path):
                os.mkdir(training_folder_path)

            if not osp.exists(jsons_folder_path):
                os.mkdir(jsons_folder_path)

            if not osp.exists(label_images_set_path):
                os.mkdir(label_images_set_path)

            if not osp.exists(label_collection_folder_path):
                os.mkdir(label_collection_folder_path)

            #儲存成file.json在 例如:media/labelme/example_folder/jsons/.json
            save_json_data_to_file(jsons_folder_path, input_img_name, data)

            img = read_img(data)

            #查詢input_img_id
            if data['imagePath']:
                input_img_path = data['imagePath'] #此path為Labelme專案中/Images/example_folder/.jpg
                img_name = osp.basename(input_img_path) #img_name.jpg
                #查詢是否有這筆input_img_name
                has_input_img = Input_imgs.objects.filter(img_name = img_name)
                #如果有紀錄的話
                if has_input_img.count():
                    #原圖input_img的id
                    input_img_id = has_input_img.values_list("id", flat = True)[0]

            #載入dictionary
            dictionary = load_dictionary(training_folder_path)

            #更新dictionary
            update_dictionary(data, dictionary, training_folder_path)

            label_ids_from_db = Labels.objects.filter(input_img_id = input_img_id).values_list("label_id", flat = True)

            #第一步先把資料庫沒有的label_id加到label_name_to_value名單
            label_name_to_value = create_label_name_to_value(data, dictionary, 1, 0, label_ids_from_db)

            #第二步把label_name_to_value名單中的labels及points(注意:label_name可能會重複，但shape內容不同)加到shapes
            shapes = get_shapes(data, label_name_to_value)

            #開始處理numpy_array，lbl包含了每個label的numpy_array
            #img.shape 的.shape會是一組tuple，像是(x維度，y個元素)
            lbl = utils.shapes_to_label(img.shape, shapes, label_name_to_value) #shape_to_label(img_shape, shape, label_name_to_value, type='class')

            #將input_img原圖另存在 例如:media/labelme/example_folder/label_images_set/input_img_name/.npy
            PIL.Image.fromarray(img).save(f'{label_collection_folder_path}/{input_img_name}.png') #fromarray(img)裡面的參數為一個做好的圖片，然後存在一個路徑下，這裡是存image_img.png

            label_values, label_names = [], []

            for ln, lv in label_name_to_value.items():
                label_values.append(lv) #lv就是Tuple的index編號: 0, 1, 2, 3, ...
                label_names.append(ln) #ln就是label name

            #開始一張一張存檔案(npy, npz, label_pic)及寫入資料庫
            save_files(label_name_to_value, lbl, label_values, label_names, training_folder_name, input_img_name, label_collection_folder_path)

            #資料庫寫入這筆label
            for shape in data['shapes']:
                label_id = shape['label_id']
                label_name = shape['label']
                #比對資料庫是否有這筆label_id(這張原圖中)
                if label_id not in label_ids_from_db:
                    label_pic_path = f'labelme/{training_folder_name}/label_images_set/{input_img_name}/{input_img_name}_{label_name}.png'
                    npy_path = f'labelme/{training_folder_name}/npys/{input_img_name}_{label_name}.npy'
                    create_label = Labels(label_name = label_name, label_pic_path = label_pic_path, npy_path = npy_path, user_id = user_id, input_img_id = input_img_id, label_id = label_id, dictionary_id = dictionary[label_name])
                    create_label.save()
                    #紀錄log
                    logger.info(
                    '[Create] LabelMe input_img_name: [%s] has been create label_name [%s] which label_id is [%s]' % (input_img_name, label_name, label_id)
                    )

            label_paths = Labels.objects.values_list("npy_path", "dictionary_id")

            #從training_folder_path去寫入到training.txt檔案裏面
            with open(osp.join(training_folder_path, 'training.txt'), 'w') as filepath:
                for label in label_paths:
                    #RegEx掉labelme/example_folder/之後把npys/black_10x10_zen5.npy + dictionary_id寫進txt裡面
                    filepath.write(f'{label[0].replace("labelme/example_folder/", "")} {label[1]}' + '\n')

            print('Saved training.txt to: %s' % training_folder_path)
            return JsonResponse({'status': 'create label successfully'})

def delete_label(request):
    if request.method == "POST":
        #該label的原圖檔案名稱
        input_img_name = request.POST.get("input_img_name") #img1.jpg
        deleted_label_id = request.POST.get("deleted_label_id") #要刪除label的id
        deleted_label_name = request.POST.get("deleted_label_name") #要刪除label的name
        training_folder_name = request.POST.get("training_folder_name") #example_folder

        #開始查詢是否有這個label_id
        input_img_id = Input_imgs.objects.get(img_name = input_img_name).id
        input_img_name = input_img_name.replace('.jpg', '') #去除副檔名

        #如果資料庫裡有這張input_img名稱的話，就刪除檔案及資料庫的該path
        label = Labels.objects.filter(input_img_id = input_img_id).filter(label_id = deleted_label_id)
        has_label_id = label.values("label_id").annotate(Count("label_id")).filter(label_id__count__gt = 0)

        #如果有這個label_id
        if has_label_id:
            #開始檢查是否有重複的label_name
            is_duplicate_label_name = Labels.objects.filter(input_img_id__in = label.values("input_img_id")).filter(label_name = deleted_label_name).values("label_name").annotate(Count("label_name")).filter(label_name__count__gt = 1)

            #如果沒有重複label_name就直接刪除npy檔, 從npz裡面移除, 刪除label_pic檔案, 刪除DB裡的資料
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

                #從npz移除該label_numpy
                npz_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/{training_folder_name}.npz'
                if osp.isfile(npz_path):
                    npz_data = dict(np.load(npz_path))
                    del npz_data[f'{input_img_name}_{deleted_label_name}']

                #刪除DB的資料
                label.delete()

            #如果有重複label_name就更新npy檔案，更新label_pic，更新npz，因為同一個名子都會被合併成一個檔案
            elif is_duplicate_label_name:

                #json_file_path是 D:/my_labelme_project/Annotations/example_folder/img2.json
                json_file_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}/jsons/{input_img_name}.json'

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
                save_json_data_to_file(jsons_folder_path, input_img_name, data)

                training_folder_path = f'{settings.BASE_DIR}/media/labelme/{training_folder_name}' #D:\my_projects/media/labelme/example_folder

                #載入dictionary
                dictionary = load_dictionary(training_folder_path)

                #把json檔內有叫deleted_label_name的加到label_name_to_value名單
                label_name_to_value = create_label_name_to_value(data, dictionary, 0, 1, [deleted_label_name])

                #把label_name_to_value名單中的labels及points(注意:label_name可能會重複，但shape內容不同)加到shapes
                shapes = get_shapes(data, label_name_to_value)

                #從json檔讀取base64圖
                img = read_img(data)

                #開始處理numpy_array，lbl包含了每個label的numpy_array
                #img.shape 的.shape會是一組tuple，像是(x維度，y個元素)
                lbl = utils.shapes_to_label(img.shape, shapes, label_name_to_value) #shape_to_label(img_shape, shape, label_name_to_value, type='class')

                label_collection_folder_path = f'{training_folder_path}/label_images_set/{input_img_name}'

                label_values, label_names = [], []

                for ln, lv in label_name_to_value.items():
                    label_values.append(lv) #lv就是Tuple的index編號: 0, 1, 2, 3, ...
                    label_names.append(ln) #ln就是label name

                #開始一張一張存檔案(npy, npz, label_pic)及寫入資料庫
                save_files(label_name_to_value, lbl, label_values, label_names, training_folder_name, input_img_name, label_collection_folder_path)

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
        '[Delete] LabelMe input_img_name: [%s] has been deleted label_name [%s] which label_id is [%s]' % (input_img_name, deleted_label_name, deleted_label_id)
        )
        return JsonResponse({'data': 'successfully'})