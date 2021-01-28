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
            label_name_to_value = {'_background_': 0} #其中'_background_': 0为背景信息，如无特殊需要不需改变，后面则为自定义标签。例如label_name_to_value={'_background_': 0, 'circle': 1, 'cross': 2, 'tick': 3,'thick':4}
            for shape in data['shapes']: #應該是這裡要要去分把一個label name 做成一張圖
                label_name = shape['label'] #拿到label name
                if label_name in label_name_to_value: #label_name_to_value是一個dict
                    label_value = label_name_to_value[label_name] # 把label name 加入進label_value
                else: # 如果lable name 沒有在value清單裡面的時候
                    label_value = len(label_name_to_value)
                    label_name_to_value[label_name] = label_value #{'label_name: 1也就是label_value}
            
            # label_values must be dense
            label_values, label_names = [], [] #label_values是什麼?
            print("====label_name_to_value.items======", label_name_to_value.items()) #dict_items([('_background_', 0), ('test', 1), ('test2', 2)])
            for ln, lv in sorted(label_name_to_value.items(), key=lambda x: x[1]): #因為label_name_to_value這個dict無法被蝶代所以用items()讓他轉為可跌代，但會變成tuple(laabel_name1, laabel_name2, ..)
                label_values.append(lv) #lv就是Tuple的index編號: 0, 1, 2, 3, ...
                label_names.append(ln) #ln就是label name
            assert label_values == list(range(len(label_values)))
            
            #img.shape 的.shape會是一組tuple，像是(x維度，y個元素)
            lbl = utils.shapes_to_label(img.shape, data['shapes'], label_name_to_value) #lbl會是一個numpy array, shapes_to_label(img_shape, shapes, label_name_to_value, type='class')
            print('===lbl====', lbl.size) #size = 4915200
            # print('===lbl====', lbl) #lbl包含了每個label的mask
			#[[0 0 0 ... 0 0 0]
            #[0 0 0 ... 0 0 0]
            #[0 0 0 ... 0 0 0]
            #...
            #[0 0 0 ... 0 0 0]
            #[0 0 0 ... 0 0 0]
            #[0 0 0 ... 0 0 0]]
            for i in range(1, len(label_name_to_value)):
                mask_from_lbl = (lbl==[i]).astype(np.uint8) #利用label_name_to_value去找出每一個對應的mask
                lblsave_white_mask(osp.join(out_dir2, save_file_name + f'_label_{label_names[i]}.png'), mask_from_lbl)
            captions = ['{}: {}'.format(lv, ln) #captions翻譯叫做字幕
                for ln, lv in label_name_to_value.items()]
            lbl_viz = utils.draw_label(lbl, img, captions) #好像是產生有字幕的label image
             
            PIL.Image.fromarray(img).save(out_dir2+'\\'+save_file_name+'_img.png') #fromarray(img)裡面的參數為一個做好的圖片，然後存在一個路徑下，這裡是存image_img.png
            #PIL.Image.fromarray(lbl).save(osp.join(out_dir2, 'label.png'))
            utils.lblsave(osp.join(out_dir2, save_file_name+'_labels.png'), lbl) #utils.lblsave(路徑, lbl) 是什麼意思?
            PIL.Image.fromarray(lbl_viz).save(out_dir2+'\\'+save_file_name+
            '_label_viz.png') #把有字幕的label image存成image_label_viz.png
 
            with open(osp.join(out_dir2, 'label_names.txt'), 'w') as f: #從檔案最裡面的路徑out_dir2去寫入到label_names.txt檔案裏面
                for lbl_name in label_names: 
                    f.write(lbl_name + '\n') #把label name寫進txt裡面
 
            warnings.warn('info.yaml is being replaced by label_names.txt')
            info = dict(label_names=label_names)
            with open(osp.join(out_dir2, 'info.yaml'), 'w') as f:
                yaml.safe_dump(info, f, default_flow_style=False)
				
				
			#save png to another directory
            #另外建立一個mask_png資料夾存mask.png檔案
            if not osp.exists(json_file + '\\' + 'mask_png'):
                os.mkdir(json_file + '\\' + 'mask_png')
            mask_save2png_path = json_file + '\\' + 'mask_png'

            utils.lblsave(osp.join(mask_save2png_path, save_file_name+'_label.png'), lbl)
 
            print('Saved to: %s' % out_dir2)