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

np.set_printoptions(threshold=sys.maxsize, linewidth=sys.maxsize) #將print()numpy array全部顯示

def show_label_list(request):
    labels = Labels.objects.all()
    npz_file = os.path.join(os.path.dirname(os.path.abspath("__file__")), f'media/labelme/example_folder/example_folder.npz')
    if os.path.isfile(npz_file):
        npz_file = f'/media/labelme/example_folder/example_folder.npz'
        return TemplateResponse(request, 'label_list.html', {'labels': labels, 'npz_file': npz_file})
    return TemplateResponse(request, 'label_list.html', {'labels': labels})

def get_labelme_json_file_path(request):
    if(request.method == "POST"):
        username = request.POST.get("username")
        json_file_path = request.POST.get("labelme_json_file_path") #D:/my_labelme_project/Annotations/example_folder/img2.json
        pattern = '^(\w:)?\/(\w+)\/(\w+)\/(\w+)' #用regex獲取檔案所在的資料夾路徑
        match = re.search(pattern, json_file_path)
        if(match): #如果成功regex
            json_folder_path = match.group() #group()會拿到full match，D:/my_labelme_project/Annotations/example_folder
        create_label_images_set(json_folder_path, json_file_path, username) #製作label data set
        return JsonResponse({'status': 'get labelme labelme json file path successfully'})

def lblsave_white_mask(filename, lbl): #單張mask存成白底使用這個function
    if osp.splitext(filename)[1] != '.png':
        filename += '.png'
    # Assume label ranses [-1, 254] for int32,
    # and [0, 255] for uint8 as VOC.
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

def create_label_images_set(json_folder_path, json_file_path, username):
        user_id = Users.objects.get(username = username).id
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        if os.path.isfile(json_file_path) and json_file_path.endswith('.json'): #如果檔案存在且是一個檔案且附檔名是.json
            #讀取labelme的json檔
            data = json.load(open(json_file_path))

			##############################
			#save_diretory
            save_file_folder_name = osp.basename(json_file_path).replace('.json', '') #baseneme就是獲取檔案名稱，並移除附檔名
            json_folder_name = json_folder_path.split('/')[-1]
            #存放所有json檔案的資料夾路徑
            jsons_folder_path = f'{settings.BASE_DIR}/media/labelme/{json_folder_name}' #D:\my_projects/media/labelme/example_folder
            #通過labelme處理訓練原圖後生成的json檔案
            json_folder_path = f'{settings.BASE_DIR}/media/labelme/{json_folder_name}/jsons' #D:\my_projects/media/labelme/example_folder/jsons
            #label_images_set資料夾路徑
            label_images_set_path = f'{settings.BASE_DIR}/media/labelme/{json_folder_name}/label_images_set' #D:\my_projects/media/labelme/example_folder/label_images_set
            #label.png存放所在的資料夾路徑
            file_folder_path = f'{settings.BASE_DIR}/media/labelme/{json_folder_name}/label_images_set/{save_file_folder_name}' #D:\my_projects/media/labelme/example_folder/label_images_set/img3

            if not osp.exists(jsons_folder_path):
                os.mkdir(jsons_folder_path)

            if not osp.exists(json_folder_path):
                os.mkdir(json_folder_path)

            if not osp.exists(label_images_set_path):
                os.mkdir(label_images_set_path)

            if not osp.exists(file_folder_path):
                os.mkdir(file_folder_path)

			#########################

            #把上面的json data儲存為json檔案存在 例如:media/labelme/example_folder/jsons/.json
            with open(f'{json_folder_path}/{osp.basename(json_file_path)}', 'w') as fp: #osp.basename(json_file_path)=檔案名稱.json
                json_object = json.dumps(data, indent = 4) #indent是拿來美化用的，data是上面讀取json檔案的資料
                fp.write(json_object)

			#########################

            if data['imageData']:
                imageData = data['imageData']
            else:
                imagePath = os.path.join(json_file_path, data['imagePath'])
                with open(imagePath, 'rb') as f:
                    imageData = f.read()
                    imageData = base64.b64encode(imageData).decode('utf-8')
            img = utils.img_b64_to_arr(imageData)
            label_name_to_value = {'_background_': 0} #其中'_background_': 0为背景信息，如无特殊需要不需改变，后面则为自定义标签。例如label_name_to_value={'_background_': 0, 'circle': 1, 'cross': 2, 'tick': 3,'thick':4}
            for shape in data['shapes']: #應該是這裡要要去分把一個label name 做成一張圖
                label_name = shape['label'] #拿到label name
                if label_name in label_name_to_value: #label_name_to_value是一個dict
                    label_value = label_name_to_value[label_name] # 把label name 加入進label_value
                else: # 如果lable name 沒有在value清單裡面的時候
                    label_value = len(label_name_to_value)
                    label_name_to_value[label_name] = label_value #{'label_name: 1也就是label_value}
            
            # label_values must be dense
            label_values, label_names = [], []
            # print("====label_name_to_value.items======", label_name_to_value.items()) #dict_items([('_background_', 0), ('test', 1), ('test2', 2)])
            for ln, lv in sorted(label_name_to_value.items(), key=lambda x: x[1]): #因為label_name_to_value這個dict無法被蝶代所以用items()讓他轉為可跌代，但會變成tuple(laabel_name1, laabel_name2, ..)
                label_values.append(lv) #lv就是Tuple的index編號: 0, 1, 2, 3, ...
                label_names.append(ln) #ln就是label name
            assert label_values == list(range(len(label_values)))
            
            #img.shape 的.shape會是一組tuple，像是(x維度，y個元素)
            lbl = utils.shapes_to_label(img.shape, data['shapes'], label_name_to_value) #lbl會是一個numpy array, shapes_to_label(img_shape, shapes, label_name_to_value, type='class')
            # print('===lbl====', lbl) #lbl包含了每個label的mask
			#[[0 0 0 ... 0 0 0]
            #[0 0 0 ... 0 0 0]
            #[0 0 0 ... 0 0 0]
            #...
            #[0 0 0 ... 0 0 0]
            #[0 0 0 ... 0 0 0]
            #[0 0 0 ... 0 0 0]]
            input_img_path = data['imagePath'] #從json資料中獲得Labelme專案中/Images/folder_path/原始圖片，的path
            img_name = osp.basename(input_img_path) #osp.basename是從input_img_path中取到整個img_name檔案名稱
            #開始從資料庫查詢是否有這張img的path紀錄
            has_input_img = Input_imgs.objects.filter(img_name = img_name)
            #開始處理label_mask
            #如果資料庫裡有這張data['imagePath']照片img_name名稱的話，就儲存label_mask檔案並將path存在資料庫
            if(has_input_img.count()):
                input_img_id = has_input_img[0].id #取得input_img的id
                input_img = Input_imgs.objects.get(id = input_img_id)
                #開始一張一張存_label_mask
                for i in range(1, len(label_name_to_value)): #跳過"_background_"從第二個開始
                    label_mask = (lbl==[i]).astype(np.uint8) #利用label_name_to_value去找出每一個對應的mask
                    #開始將一個一個label_mask的npy檔案，存在 例如:media/labelme/example_folder/label_images_set/img2/.npy
                    save(os.path.join(os.path.dirname(os.path.abspath("__file__")), f'media/labelme/{json_folder_name}/label_images_set/{save_file_folder_name}/{save_file_folder_name}_{label_names[i]}.npy'), label_mask)
                    #開始將一個一個label_mask的npy檔案，存在 例如:media/labelme/example_folder/.npy
                    save(os.path.join(os.path.dirname(os.path.abspath("__file__")), f'media/labelme/{json_folder_name}/{save_file_folder_name}_{label_names[i]}.npy'), label_mask)
                    #開始把這張照片的所有label_mask存在media資料夾中既有的npz檔案裡面
                    npz_file = os.path.join(os.path.dirname(os.path.abspath("__file__")), f'media/labelme/{json_folder_name}/{json_folder_name}.npz')
                    # 如果沒有npz檔案
                    if not os.path.isfile(npz_file):
                        data = dict() #因為npz是dic格式
                        data[f'{save_file_folder_name}_{label_names[i]}'] = label_mask #第一筆label_mask資料:data['圖片名稱_label名稱] = label_mask']
                        savez(npz_file, **data) #把第一筆資料創建成一個新的npz檔案
                    # 如果有npz檔案
                    elif os.path.isfile(npz_file):
                        data = dict(np.load(npz_file)) #解開npz
                        data[f'{save_file_folder_name}_{label_names[i]}'] = label_mask #修改dic加入新的label_mask
                        savez(os.path.join(os.path.dirname(os.path.abspath("__file__")), f'media/labelme/{json_folder_name}/{json_folder_name}.npz'), **data) #將data存成npz，並將dic key當作npz的key name
                    #開始一張一張將label_mask的PNG圖片存在media資料夾裡面
                    lblsave_white_mask(osp.join(file_folder_path, f'{save_file_folder_name}_label_{label_names[i]}.png'), label_mask) #產生label_mask圖片
                    #開始將label_mask的PNG及npy檔案path存在DB
                    has_label_record = input_img.labels.filter(input_img_id = input_img_id).filter(label_name = label_names[i]).count() #先驗證DB是否已有此label_name
                    #如果資料庫沒有這個label_name的話就開始存path
                    if(not has_label_record):
                        mask_path = f'labelme/{json_folder_name}/label_images_set/{save_file_folder_name}/{save_file_folder_name}_label_{label_names[i]}.png'
                        npy_path = f'labelme/{json_folder_name}/label_images_set/{save_file_folder_name}/{save_file_folder_name}_{label_names[i]}.npy'
                        create_label_mask = Labels(label_name = label_names[i], mask_path = mask_path, user_id = user_id, input_img_id = input_img_id, npy_path = npy_path)
                        create_label_mask.save()
            #如果資料庫沒有img_name的紀錄，就只儲存label_mask檔案到media資料夾
            else:
                logger.warn(
                '資料庫裏面沒有 [%s] 這張圖片名稱的紀錄' % img_name
                )
                #開始一張一張存label_mask檔案
                for i in range(1, len(label_name_to_value)): #跳過"_background_"從第二個開始
                    label_mask = (lbl==[i]).astype(np.uint8) #利用label_name_to_value去找出每一個對應的mask
                    #開始一張一張把label_mask存成npy格式，存在media資料夾裡面
                    save(os.path.join(os.path.dirname(os.path.abspath("__file__")), f'media/labelme/{json_folder_name}/label_images_set/{save_file_folder_name}/{save_file_folder_name}_{label_names[i]}.npy'), lbl==[i])
                    #開始把這張照片的所有label_mask存在media資料夾中既有的npz檔案裡面
                    npz_file = os.path.join(os.path.dirname(os.path.abspath("__file__")), f'media/labelme/{json_folder_name}/{json_folder_name}.npz')
                    # 如果沒有npz檔案
                    if not os.path.isfile(npz_file):
                        data = dict() #因為npz是dic格式
                        data[f'{save_file_folder_name}_{label_names[i]}'] = label_mask #第一筆label_mask資料:data['圖片名稱_label名稱] = label_mask']
                        savez(npz_file, **data) #把第一筆資料創建成一個新的npz檔案
                    # 如果有npz檔案
                    elif os.path.isfile(npz_file):
                        data = dict(np.load(npz_file)) #解開npz
                        data[f'{save_file_folder_name}_{label_names[i]}'] = label_mask #修改dic加入新的label_mask
                        savez(os.path.join(os.path.dirname(os.path.abspath("__file__")), f'media/labelme/{json_folder_name}/{json_folder_name}.npz'), **data) #將data存成npz，並將dic key當作npz的key name
                    #開始一張一張將label_mask的PNG圖片存在media資料夾裡面
                    lblsave_white_mask(osp.join(file_folder_path, f'{save_file_folder_name}_label_{label_names[i]}.png'), label_mask) #產生label_mask圖片

            captions = ['{}: {}'.format(lv, ln) #captions翻譯叫做字幕
                for ln, lv in label_name_to_value.items()]
            lbl_viz = utils.draw_label(lbl, img, captions) #好像是產生有字幕的label image
             
            PIL.Image.fromarray(img).save(f'{file_folder_path}/{save_file_folder_name}_img.png') #fromarray(img)裡面的參數為一個做好的圖片，然後存在一個路徑下，這裡是存image_img.png
            #PIL.Image.fromarray(lbl).save(osp.join(file_folder_path, 'label.png'))
            utils.lblsave(osp.join(file_folder_path, f'{save_file_folder_name}_labels.png'), lbl) #將mask照片存放在file_folder_path
            PIL.Image.fromarray(lbl_viz).save(f'{file_folder_path}/{save_file_folder_name}_labels_viz.png') #把有字幕的label image存成image_label_viz.png
 
            with open(osp.join(file_folder_path, 'label_names.txt'), 'w') as f: #從檔案最裡面的路徑file_folder_path去寫入到label_names.txt檔案裏面
                for lbl_name in label_names: 
                    f.write(lbl_name + '\n') #把label name寫進txt裡面
 
            warnings.warn('info.yaml is being replaced by label_names.txt')
            info = dict(label_names=label_names)
            with open(osp.join(file_folder_path, 'info.yaml'), 'w') as f:
                yaml.safe_dump(info, f, default_flow_style=False)

            print('Saved to: %s' % file_folder_path)

def labelme_url(request):
    return {'LABELME_URL': settings.LABELME_URL}