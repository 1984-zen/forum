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
import re

def get_labelme_json_file_path(request):
    if(request.method == "POST"):
        labelme_json_file_path = request.POST.get("labelme_json_file_path") #D:/my_labelme_project/Annotations/example_folder/img2.json
        pattern = '^(\w:)?\/(\w+)\/(\w+)\/(\w+)' #用regex獲取檔案所在的資料夾路徑
        match = re.search(pattern, labelme_json_file_path) #D:/my_labelme_project/Annotations/example_folder/
        if(match): #如果成功regex
            folder_path = match.group() #group()拿到full match
            create_label_images_set(folder_path) #製作label data set
            return JsonResponse({'status': 'get labelme labelme json file path successfully'})

def create_label_images_set(folder_path):
    json_file = folder_path.replace('/','\\') #D:\my_labelme_project\Annotations\example_folder
 
    count = os.listdir(json_file) #列出這個資料夾下的所有東西(包含資料夾及檔案) ['file_name.json', 'labelme_json', 'mask_png', 'test0106.json']
    for i in range(0, len(count)):
        path = os.path.join(json_file, count[i])
        if os.path.isfile(path) and path.endswith('.json'): #如果是一個檔案且附檔名是.json
            data = json.load(open(path))

			##############################
			#save_diretory
            out_dir1 = osp.basename(path).replace('.json', '') #baseneme就是獲取檔案名稱，並移除附檔名
            save_file_name = out_dir1
            out_dir1 = osp.join(osp.dirname(path), out_dir1)

            if not osp.exists(json_file + '\\' + 'label_images_set'):
                os.mkdir(json_file + '\\' + 'label_images_set')
            label_images_set = json_file + '\\' + 'label_images_set'

            out_dir2 = label_images_set + '\\' + save_file_name #以檔案名稱為資料夾名稱_json
            if not osp.exists(out_dir2):
                os.mkdir(out_dir2)

			#########################

            if data['imageData']:
                imageData = data['imageData']
            else:
                imagePath = os.path.join(os.path.dirname(path), data['imagePath'])
                with open(imagePath, 'rb') as f:
                    imageData = f.read()
                    imageData = base64.b64encode(imageData).decode('utf-8')
            img = utils.img_b64_to_arr(imageData)
            label_name_to_value = {'_background_': 0}
            for shape in data['shapes']:
                label_name = shape['label']
                if label_name in label_name_to_value:
                    label_value = label_name_to_value[label_name]
                else:
                    label_value = len(label_name_to_value)
                    label_name_to_value[label_name] = label_value
            
            # label_values must be dense
            label_values, label_names = [], []
            for ln, lv in sorted(label_name_to_value.items(), key=lambda x: x[1]):
                label_values.append(lv)
                label_names.append(ln)
            assert label_values == list(range(len(label_values)))
            
            lbl = utils.shapes_to_label(img.shape, data['shapes'], label_name_to_value)
            
			
			
            captions = ['{}: {}'.format(lv, ln)
                for ln, lv in label_name_to_value.items()]
            lbl_viz = utils.draw_label(lbl, img, captions)
             
            PIL.Image.fromarray(img).save(out_dir2+'\\'+save_file_name+'_img.png')
            #PIL.Image.fromarray(lbl).save(osp.join(out_dir2, 'label.png'))
            utils.lblsave(osp.join(out_dir2, save_file_name+'_label.png'), lbl)
            PIL.Image.fromarray(lbl_viz).save(out_dir2+'\\'+save_file_name+
            '_label_viz.png')
 
            with open(osp.join(out_dir2, 'label_names.txt'), 'w') as f:
                for lbl_name in label_names:
                    f.write(lbl_name + '\n')
 
            warnings.warn('info.yaml is being replaced by label_names.txt')
            info = dict(label_names=label_names)
            with open(osp.join(out_dir2, 'info.yaml'), 'w') as f:
                yaml.safe_dump(info, f, default_flow_style=False)
				
				
			#save png to another directory
            if not osp.exists(json_file + '\\' + 'mask_png'):
                os.mkdir(json_file + '\\' + 'mask_png')
            mask_save2png_path = json_file + '\\' + 'mask_png'

            utils.lblsave(osp.join(mask_save2png_path, save_file_name+'_label.png'), lbl)
 
            print('Saved to: %s' % out_dir2)