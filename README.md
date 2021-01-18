# 安裝環境
1. windows 10
2. Anaconda3
3. Python 3.8.3
4. pip 19.2.3
# Windows 環境下怎麼使用這個專案?
1. 下載專案 https://github.com/1984-zen/forum/archive/dev.zip
2. 打開anbaconda3 Powershell終端機
```
> 到你的MySQL新增一個新 database 
> cd 專案資料夾
> 複製一份 settings.py.example 並rename為 settings.py
> 用IDE編輯器打開settings.py修改DATABASES成為你的資料庫連線設定
# 安裝此專案的相依套件
> pip install -r requirements.txt
# 生成SECRET_KEY
> python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
# 複製這串SECRET_KEY
> 到IDE編輯器編輯settings.py的SECRET_KEY並貼上剛剛的KEY
# 資料庫遷移指令
> python ./manage.py makemigrations
```
### 注意1： 在使用 ./manage.py 之前需要確定你系统中的 python 命令是指向 python 3.6 及以上版本的。如果不是如此，請使用以下兩種方式中的一種：
- 修改 manage.py 第一行 #!/usr/bin/env python 為 #!/usr/bin/env python3
- 直接使用 python3 ./manage.py makemigrations 
### 注意2：如果資料migrate的過程發生問題:
- 試試看打開settings.py並編輯由USE_TZ = False改為True，結束migrate後再改回來
```
# 我們繼續資料庫遷移指令
> python ./manage.py migrate
> python ./manage.py runserver
```
### Optional 額外設定
```
EMAIL_BACKEND、EMAIL_HOST、EMAIL_PORT、EMAIL_HOST_USER、EMAIL_HOST_PASSWORD、EMAIL_USE_TLS、DEFAULT_FROM_EMAIL都是為了"忘記密碼"使用的，如果要使用必須要使用您的信箱設定，如果沒有要用就先刪掉他們
```

3. 開啟瀏覽器 訪問 127.0.0.1:8000/index
#
# 會員系統(Accounts system))
## 需求 & Story
- Story
    - 希望可以管理使用者
    - 此專案的重點在於「註冊」及 「登入」的功能（開發順位高）
    - 其餘需求是後面增加的（開發順位較低）
- 系統功能需求
    <details>
    <summary> 註冊部分需求 </summary>
    <pre><code>
    - 會員註冊需要 Username(名字)、Account(E-mail)、Password(密碼)、Re_Password(確認密碼) 四個欄位
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
# 論壇網站(Forum web site)
## 需求 & Story
- Story
    - 希望有可以互相分享檔案或文字資訊的的網頁平台
    - 純文字留言 + 上傳檔案 + 對文章做分類 + 對文章置頂
    - 此專案的重點在於「留言」及 「上傳檔案」的功能（開發順位高）
    - 其餘需求是後面增加的（開發順位較低）
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
# 線上測驗(Exams web site)
## 需求 & Story
- Story
    - 將尚未分類的資料透過Exams平台用人力去逐一標註
    - 創建測驗(單選題) + 上傳影片 + 上傳照片 + 可以紀錄帳號在同一測驗下的所有測驗結果 + 下載該次測驗結果excel檔案 + 非線性答題(根據回答跳至相關題目)
    - 此專案的重點在於「創建測驗」及 「上傳影片」及 「下載excel檔案」的功能（開發順位高）
    - 其餘需求是後面增加的（開發順位較低）
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