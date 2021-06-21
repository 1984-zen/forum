# 本安裝介紹有分 Docker / Windows
# 如何在Docker安裝本專案
### 1. 下載
#### 1-1. [下載Django_專案](https://github.com/1984-zen/forum/archive/refs/heads/dev.zip)
```
cd到 { Django_專案 } 資料夾
```
### 2. 建立Django_專案IMAGE
```
$ docker build -t my-django .
```
### 3. Docker創建network
```
$ docker network create --subnet=172.18.0.0/16 mynetwork
```
### 4. 下載Mariadb 的 IMAGE檔案
```
$ docker pull mariadb:10.4.18
```
### 5. 啟動mariadbrunner容器
#### 5-1. 啟動mariadbrunner容器，同時設定資料庫的密碼
```
$ docker run --net mynetwork --ip 172.18.0.2 --name mariadbrunner -e MYSQL_ROOT_PASSWORD="{ your_database_password }" -d --restart unless-stopped mariadb:10.4.18
```
### 6. 建立資料庫
#### 6-1 到mariadbrunner容器
```
$ docker exec -it mariadbrunner bash
$ mysql -uroot -p
# create database { your_database_name };
```
### 7. 建立LabelMe_專案IMAGE
#### 7-1. [下載 LabelMe_專案](https://github.com/1984-zen/my_labelme_project.git)
```
cd到 { LabelMe_專案 } 資料夾
$ docker build -t my-labelme .
```
### 8. 啟動labelme容器
```
$ docker run -p 7000:80 -v /var/www/html/LabelMeAnnotationTool/Annotations --name labelme -d --net mynetwork --ip 172.18.0.3 --restart unless-stopped my-labelme
```
### 9. 啟動django容器
```
$ docker run -p 9000:8000 -v /var/www/html/LabelMeAnnotationTool/Annotations --volumes-from labelme -v C:/example_folder:/code/media/labelme/example_folder --name django -d --net mynetwork --ip 172.18.0.4 --restart unless-stopped my-django
```
### 10. 設定settings
### 10-1. 生成SECRET_KEY
```
$ python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
#### 10-2. 到django容器
```
$ docker exec -it django bash
$ /code# cd code/ncku_project
$ /code/ncku_project# cp settings.py.example settings.py
$ /code/ncku_project# vim settings.py

設定django的資料庫連線
'NAME': '{ your_database_name }'
'USER': 'root'
'PASSWORD': '{ your_database_password }'
'HOST': '172.18.0.2'
'PORT': '3306'

設定LABELME_URL = 'http://localhost:7000/LabelMeAnnotationTool/tool.html'
USE_TZ由False暫時改為True

貼上SECRET_KEY
SECRET_KEY = '{ your_secret_key }'

儲存並退出vim
```
#### 10-3. 資料庫migrate
```
$ /code# python manage.py migrate
$ /code/ncku_project# vim settings.py
USE_TZ改回False

儲存並退出vim
```

### 11. 建立範例資料
#### 11-1 到mariadbrunner容器
```
$ docker exec -it mariadbrunner bash
$ mysql -uroot -p
# use { your_database_name }
# insert into labelme_ncku_input_imgs (img_name, training_folder_name, patient_folder_name, created_at) values("img1.jpg", "example_folder", "test01", now());
# insert into labelme_ncku_input_imgs (img_name, training_folder_name, patient_folder_name, created_at) values("img2.jpg", "example_folder", "test01", now());
# insert into labelme_ncku_input_imgs (img_name, training_folder_name, patient_folder_name, created_at) values("img3.jpg", "example_folder", "test01", now());
```
# 完成

# 如何在Windows 10安裝本專案
#### win 10 安裝環境
1. windows 10 pro
2. Anaconda3
3. Python 3.8.3
4. pip 19.2.3
5. MariaDB 10.4.14
### 1. 下載
#### 1-1. [下載 LabelMe_專案](https://github.com/1984-zen/my_labelme_project.git)
- 安裝LabelMe_專案請參考[README](https://github.com/1984-zen/my_labelme_project)說明
#### 1-2. 下載專案 [下載Django專案](https://github.com/1984-zen/forum/archive/refs/heads/dev.zip)
```
cd到 { Django_專案 } 資料夾
複製 { Django_專案 資料夾 }\nckuh_project\settings.py.example 並將檔案重新命名為 settings.py
```
### 2. 建立資料庫
#### 2-1 到MySQL
```
$ mysql -uroot -p
# create database { your_database_name };
```
### 開始設定Django
### 3. 生成SECRET_KEY
```
$ python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
### 4. 設定資料庫連線
#### 4-1. 編輯settings.py
```
'NAME': '{ your_database_name }'
'USER': 'root'
'PASSWORD': '{ your_database_password }'
'HOST': '127.0.0.1'
'PORT': '3306'

設定LABELME_URL = 'http://127.0.0.1:7000/LabelMe/tool.html'
USE_TZ由False暫時改為True

貼上SECRET_KEY
SECRET_KEY = '{ your_secret_key }'
```
### 5. 資料庫migrate
```
cd到 { Django_專案 } 資料夾
$ python manage.py migrate

USE_TZ改回False
```
### 4. pip安裝相依套件
```
cd到 { Django_專案 } 資料夾
$ pip install -r requirements.txt
```
### 注意： 在使用 ./manage.py 之前需要確定你系统中的 python 命令是指向 python 3.6 及以上版本的。如果不是如此，請使用以下兩種方式中的一種：
1. 修改 { Django_專案 資料夾 }\manage.py 第一行
```
#!/usr/bin/env python 為 #!/usr/bin/env python3
```
2. 直接使用 python3
```
python3 ./manage.py migrate
```
### 5. 建立範例資料
#### 5-1 到MySQL
```
$ mysql -uroot -p
# use { your_database_name }
# insert into labelme_ncku_input_imgs (img_name, training_folder_name, patient_folder_name, created_at) values("img1.jpg", "example_folder", "test01", now());
# insert into labelme_ncku_input_imgs (img_name, training_folder_name, patient_folder_name, created_at) values("img2.jpg", "example_folder", "test01", now());
# insert into labelme_ncku_input_imgs (img_name, training_folder_name, patient_folder_name, created_at) values("img3.jpg", "example_folder", "test01", now());
```
#### 2. 啟動server
```
cd到 { Django_專案 } 資料夾
$ python ./manage.py runserver 9000
```
# 完成
```
開啟瀏覽器 訪問 127.0.0.1:9000/index
```
# 介紹
### 會員系統(Accounts system)
#### DEMO
![](https://github.com/1984-zen/forum/blob/master/media/register_demo.gif)
#### 需求
- 系統功能需求
    <details>
    <summary> 註冊部分需求 </summary>
    <pre><code>
    - 會員註冊需要 Username(名字)、Account(E-mail)、Password(密碼)、Re_Password(確認密碼) 四個欄位
    - 密碼儲存非明碼
    - 每個欄位經過驗證後送出，畫面會有訊息提示出錯不符合規則的欄位:
        - Account 不允許特殊符號、數字、英文字母以外的字元輸入
        - Password 不允許特殊符號、數字、英文字母以外的字元輸入 密碼長度4到10個字元 至少要有一個大寫或小寫的英文字母 至少要有一個0-9的數字
        - Password與Re_Password必須一致
    - 權限分為Guest、管理者(is_admin)及超級管理者(is_super_admin) 三個
        - 註冊成功後預設為管理者身分
        - 切換管理身分需要透過修改資料庫來達成
    </code></pre>   
    </details>
    <details>
    <summary> 登入部分需求 </summary>
    <pre><code>
    - 以 Email 和 密碼 做登入
    - 會提示登入成功或失敗的訊息
    </code></pre>   
    </details>
    <details>
    <summary> 找回密碼需求(自己額外做的) </summary>
    <pre><code>
    - 以Gmail信箱收到來自平台的驗證信後，點選重設密碼的連結後即可重新設定新密碼
    </code></pre>   
    </details>
    <details>
    <summary> 登出部分需求 </summary>
    <pre><code>
    - 登出後會刪除cookie後回到登入畫面
    </code></pre>   
    </details>
#
### 論壇網站(Forum web site)
#### DEMO
![](https://github.com/1984-zen/forum/blob/master/media/forum_web_site_demo.gif)
#### 需求
- 系統功能需求
    <details>
    <summary> 未登入的使用者 </summary>
    <pre><code>
    - 可以顯示user name為Guest
    - 可以觀看所有人的留言
    - 不可以新增、更新、刪除留言或檔案
    </code></pre>   
    </details>
    <details>
    <summary> 已登入的使用者 </summary>
    <pre><code>
    - 可以顯示user name為Guest
    - 可以觀看所有人的留言
    - 可以新增留言，但只能更新、刪除自己的留言或檔案
    </code></pre>   
    </details>
    <details>
    <summary> 留言部分需求 </summary>
    <pre><code>
    - 可以二階留言
    - 文章(一階段留言)可以置頂及分類
    </code></pre>   
    </details>
#
### 線上測驗(Exams web site)
#### DEMO
![](https://github.com/1984-zen/forum/blob/master/media/exams_web_site_demo.gif)
#### 需求
- 系統功能需求
    <details>
    <summary> 未登入的使用者 </summary>
    <pre><code>
    - 只能看到Exams的標題列表
    </code></pre>   
    </details>
    <details>
    <summary> 已登入的使用者(is_admin) </summary>
    <pre><code>
    - 可以進行測驗
    - 可以創建及更新、刪除部分測驗
    - 可以查看考生結果並下載excel
    </code></pre>   
    </details>
    <details>
    <summary> 已登入的使用者(is_super_admin) </summary>
    <pre><code>
    - 可以進行測驗
    - 可以創建及更新、刪除所有測驗
    - 可以查看考生結果並下載excel
    </code></pre>   
    </details>
    <details>
    <summary> 測驗部分需求 </summary>
    <pre><code>
    - 單選題
    - 進入測驗可以直接跳至上次回答完的下一題
    - 非線性答題(根據回答跳至相關題目)
    - 點選提交考卷後，即結束測驗
    - User已經回答過的選項會顯示已勾選，已送出的答案就不能再改
    - 測驗結果畫面可分為左半部為考生回答，右半部為選項的正確答案
    - 可以新增、修改即刪除測驗題目
    </code></pre>   
    </details>
### 標註網站(Label web site)
#### DEMO
![](https://github.com/1984-zen/forum/blob/master/media/labelme_web_site_demo.gif)
#### 需求
- 系統功能需求
    <details>
    <summary> 未登入的使用者 </summary>
    <pre><code>
    - 只能看到project名稱
    </code></pre>   
    </details>
    <details>
    <summary> 已登入的使用者 </summary>
    <pre><code>
    - 可以進入label清單及標註 (label)
    </code></pre>   
    </details>
