from django.shortcuts import render
from django.http import HttpResponse
import json

import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time

def domestic_judicial(name):

    # --------------------- 參數設定 --------------------

    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # py
    # BASE_DIR = os.path.abspath('') # ipynb
    PATH = os.path.join(BASE_DIR, "chromedriver.exe")

    options = webdriver.ChromeOptions()
    options.add_argument('headless') # 無視窗顯示
    options.add_argument('incognito')
    driver = webdriver.Chrome(executable_path = PATH, options=options)    

    search_name = name

    url = 'http://domestic.judicial.gov.tw/abbs/wkw/WHD9HN01.jsp'
    driver.maximize_window()
    driver.get(url)

    date_list = []
    id_list = []
    title_list = []
    law_list = []
    content_list = []
    recorder_list = []

    def create_df(content):
        try:
            event_date = content[content.index("發文日期：")+5: content.index("發文字號：")]
            date_list.append(event_date)
        except:
            event_date = content[content.index("發文日期")+5: content.index("發文字號")]
            date_list.append(event_date)

        try:
            event_id = content[content.index("發文字號：")+5: content.index("附件：")]
            id_list.append(event_id)
        except:
            event_id = content[content.index("發文字號")+5: content.index("附件")]
            id_list.append(event_id)

        try:
            event_title = content[content.index("主旨：")+3: content.index("依據：")]
            title_list.append(event_title)
        except:
            event_title = content[content.index("主旨")+3: content.index("依據")]
            title_list.append(event_title)

        try:
            event_law = content[content.index("依據：")+3: content.index("公告事項：")]
            law_list.append(event_law)
        except:
            event_law = content[content.index("依據")+3: content.index("公告事項")]
            law_list.append(event_law)

        try:
            event_content = content[content.index("公告事項：")+5: content.index("書記官：")]
            content_list.append(event_content)
        except:
            event_content = content[content.index("公告事項")+5: content.index("書記官")]
            content_list.append(event_content)

        try:
            event_recorder = content[content.index("書記官：")+4: content.index("書記官：")+7]
            recorder_list.append(event_recorder)
        except:
            event_recorder = content[content.index("書記官")+4: content.index("書記官")+7]
            recorder_list.append(event_recorder)

    # --------------------- page1 --------------------

    # https://www.geeksforgeeks.org/how-to-access-popup-login-window-in-selenium-using-python/

    search = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/form/table/tbody/tr[2]/td/div/div[1]/center/table/tbody/tr[3]/td[2]/input"))
    )

    main_page = driver.current_window_handle

    search.clear()
    search.send_keys(search_name)

    driver.find_element_by_xpath("/html/body/form/table/tbody/tr[2]/td/div/div[1]/center/table/tbody/tr[1]/td[2]/font/input").click()


    # --------------------- page2 & alert (pop-up windows)--------------------

    # https://www.selenium.dev/documentation/en/webdriver/browser_manipulation/

    wait_rows = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/form/table[2]/tbody/tr[4]/td[2]/font/table/tbody/tr"))
    )

    rows = len(driver.find_elements_by_xpath("/html/body/form/table[2]/tbody/tr[4]/td[2]/font/table/tbody/tr"))


    for i in range(5, rows+1):

        driver.find_element_by_xpath(f"/html/body/form/table[2]/tbody/tr[4]/td[2]/font/table/tbody/tr[{i}]/td[7]/div/center/img").click()
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.number_of_windows_to_be(2))

        for handle in driver.window_handles:
            if handle != main_page:
                login_page = handle

        wait.until(EC.new_window_is_opened)
        
        driver.switch_to.window(login_page)

        content = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/form/table/tbody/tr[4]/td[2]/table[2]/tbody/tr/td/div/pre"))
        )   
        #content = driver.find_element_by_xpath("/html/body/form/table/tbody/tr[4]/td[2]/table[2]/tbody/tr/td/div/pre")    
        create_df(content.text)
        driver.close()
        driver.switch_to.window(main_page)


    data = {
        'date': date_list,
        'id_num': id_list,
        'title': title_list,
        'law': law_list,
        'content': content_list,
        'recorder': recorder_list
    }


    df = pd.DataFrame(data)

    driver.close()

    json_records = df.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)

    return data

def law_judicial(name):

    # --------------------- 參數設定 --------------------

    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # py
    # BASE_DIR = os.path.abspath('') # ipynb
    PATH = os.path.join(BASE_DIR, "chromedriver.exe")

    options = webdriver.ChromeOptions()
    options.add_argument('headless') # 無視窗顯示
    options.add_argument('incognito')
    driver = webdriver.Chrome(executable_path = PATH, options=options)    

    search_name = name

    url = 'https://law.judicial.gov.tw/FJUD/Default_AD.aspx'
    driver.maximize_window()
    driver.get(url)


    # --------------------- 抓取Table --------------------

    # https://www.geeksforgeeks.org/scrape-table-from-website-using-python-selenium/

    id_list = []
    href_list = []
    date_list = []
    title_list = []
    content_list = []

    search = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/form/div[5]/div/div/div[2]/div[2]/table/tbody/tr[6]/td/input"))
    )
    search.clear()
    search.send_keys(search_name)


    driver.find_element_by_xpath("/html/body/form/div[5]/div/div/div[2]/div[2]/div/input").click()



    # ------------------ 內頁表格 ----------------

    wait = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "iframe-data"))
    )

    # time.sleep(2)
    driver.switch_to.frame('iframe-data')

    num = 0 
    try:
        num = driver.find_element_by_xpath("/html/body/form/div[3]/div/div[3]/div[1]/span[1]").text

        num1 = num.index('共 ')
        num2 = num.index(' 筆')
        num = num[num1+2: num2]
        print(f"num: {num}")
    except:
        num = 200

    page = int(num)//20 + 1

    for p in range(page):

        temp = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/form/div[3]/div/table/tbody/tr"))
        )

        rows = len(driver.find_elements_by_xpath("/html/body/form/div[3]/div/table/tbody/tr"))

        for i in range(2, rows, 2):
            id_val = driver.find_element_by_xpath(f"/html/body/form/div[3]/div/table/tbody/tr[{i}]/td[2]/a")
            id_list.append(id_val.text)
            href_list.append(id_val.get_attribute('href'))
            date_val = driver.find_element_by_xpath(f"/html/body/form/div[3]/div/table/tbody/tr[{i}]/td[3]")
            date_list.append(date_val.text)
            title = driver.find_element_by_xpath(f"/html/body/form/div[3]/div/table/tbody/tr[{i}]/td[4]")
            title_list.append(title.text)

        for i in range(3, rows+1, 2):
            content = driver.find_element_by_xpath(f"/html/body/form/div[3]/div/table/tbody/tr[{i}]/td/span")
            content_list.append(content.text)

        if p==(page-1):        
            break
        
        driver.find_element_by_link_text("下一頁").click()

    data = {
        'title': title_list,
        'date': date_list,
        'content': content_list,
        'id': id_list,
        'url': href_list
    }

    df = pd.DataFrame(data)

    driver.close()

    df['date'] = df['date'].str.replace('.', '-', regex=False)

    for i in range(len(df)):
        date_index = df.at[i, 'date'].index('-')
        temp = int(df.at[i, 'date'][0:date_index]) + 1911
        df.at[i, 'date'] = str(temp) + df.at[i, 'date'][date_index:]

    from datetime import datetime
    import matplotlib.dates as mdates

    # %Y %m %d %H %M %S (年、月、日、時、分、秒)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df['date'] = df['date'].astype('str')

    # convert into json
    json_records = df.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)
 
    return data

def business_registration(name):

    # --------------------- 參數設定 --------------------

    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #py
    # BASE_DIR = os.path.abspath('') #ipynb
    PATH = os.path.join(BASE_DIR, "chromedriver.exe")

    options = webdriver.ChromeOptions()
    options.add_argument('headless')  
    options.add_argument('incognito')
    driver = webdriver.Chrome(executable_path = PATH, options=options)    

    # 搜尋網址
    url = 'https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do'

    # 搜尋名稱
    search_name = name

    # 登記現況: 僅顯示核准設立:True / 全部顯示:False
    search_status = True

    driver.maximize_window()
    driver.get(url)

    
    
    # --------------------- 搜尋 --------------------

    search = driver.find_element_by_xpath('//*[@id="qryCond"]')
    search.clear()
    search.send_keys(search_name)


    # 名稱或工商登記 Radio Button
    driver.find_element_by_xpath('//*[@id="infoDefault"]').click()

    # 公司 Check Box
    type1 = driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[1]')
    if not type1.get_attribute('checked'):
        type1.click()
        
    # 分公司 Check Box
    type2 = driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[3]')
    if not type2.get_attribute('checked'):
        type2.click()
        
    # 商業 Check Box
    type3 = driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[5]')
    if not type3.get_attribute('checked'):
        type3.click()
        
    # 工廠 Check Box
    type4 = driver.find_element_by_xpath('//*[@id="queryListForm"]/div[1]/div[1]/div/div[4]/div[2]/div/div/div/input[7]')
    if not type4.get_attribute('checked'):
        type4.click()

    if search_status:
        # 登記現況: 僅顯示核准設立  Radio Button
        driver.find_element_by_xpath('//*[@id="isAliveY"]').click()
    else:
        # 登記現況: 全部顯示  Radio Button
        driver.find_element_by_xpath('//*[@id="isAliveA"]').click()

    # Submit
    driver.find_element_by_xpath('//*[@id="qryBtn"]').click()


    # --------------------- 抓取Table --------------------

    # https://www.geeksforgeeks.org/scrape-table-from-website-using-python-selenium/

    data_type_list = []
    registration_authority_list = []
    id_list = []
    title_list = []
    status_list = []

    # 舊表格呈現
    data_view = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.LINK_TEXT, "舊版表格格式"))
    )

    data_view.click()

    # get page number
    page_number_str = driver.find_element_by_xpath("/html/body/div[2]/form[1]/div[3]/div/div/div/div/div[4]/div[1]").text
    t1 = page_number_str.index("分")
    t2 = page_number_str.index("頁")
    page_number = int(page_number_str[t1+1:t2])


    for i in range(page_number):
        
        if (i>0):
            page = driver.find_element_by_link_text(str(i+1))
            page.click()

        temp_wait = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/form[1]/div[3]/div/div/div/div/div[3]/table/tbody/tr"))
        )

        rows = len(driver.find_elements_by_xpath("/html/body/div[2]/form[1]/div[3]/div/div/div/div/div[3]/table/tbody/tr"))

        # Printing the data of the table
        for r in range(rows):
            data_type = driver.find_element_by_xpath(f"/html/body/div[2]/form[1]/div[3]/div/div/div/div/div[3]/table/tbody/tr[{r+1}]/td[1]")
            registration_authority = driver.find_element_by_xpath(f"/html/body/div[2]/form[1]/div[3]/div/div/div/div/div[3]/table/tbody/tr[{r+1}]/td[2]")
            id = driver.find_element_by_xpath(f"/html/body/div[2]/form[1]/div[3]/div/div/div/div/div[3]/table/tbody/tr[{r+1}]/td[3]")
            name = driver.find_element_by_xpath(f"/html/body/div[2]/form[1]/div[3]/div/div/div/div/div[3]/table/tbody/tr[{r+1}]/td[4]/a")
            status = driver.find_element_by_xpath(f"/html/body/div[2]/form[1]/div[3]/div/div/div/div/div[3]/table/tbody/tr[{r+1}]/td[5]")
            
            data_type_list.append(data_type.text)
            registration_authority_list.append(registration_authority.text)
            id_list.append(id.text)
            title_list.append(name.text)
            status_list.append(status.text)

    data = {
        'title': title_list,
        'id_num': id_list,
        'data_type': data_type_list,
        'registration_authority': registration_authority_list,
        'status': status_list
    }

    df = pd.DataFrame(data)

    driver.close()

    json_records = df.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)

    return data







def home(request):
    return render(request, 'home.html')


def table(request):
    if 'your_name' in request.GET and request.GET['your_name'] != '':  
        
        # --------------------- 參數設定 --------------------

        BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # py
        # BASE_DIR = os.path.abspath('') # ipynb
        PATH = os.path.join(BASE_DIR, "chromedriver.exe")

        options = webdriver.ChromeOptions()
        options.add_argument('headless') # 無視窗顯示
        options.add_argument('incognito')
        driver = webdriver.Chrome(executable_path = PATH, options=options)    

        name  = request.GET.get('your_name')
        search_name = name
        # search_name = '邱大榮'

        url = 'https://law.judicial.gov.tw/FJUD/Default_AD.aspx'
        driver.maximize_window()
        driver.get(url)


        # --------------------- 抓取Table --------------------

        # https://www.geeksforgeeks.org/scrape-table-from-website-using-python-selenium/

        id_list = []
        href_list = []
        date_list = []
        title_list = []
        content_list = []

        search = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/form/div[5]/div/div/div[2]/div[2]/table/tbody/tr[6]/td/input"))
        )
        search.clear()
        search.send_keys(search_name)


        driver.find_element_by_xpath("/html/body/form/div[5]/div/div/div[2]/div[2]/div/input").click()



        # ------------------ 內頁表格 ----------------

        wait = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "iframe-data"))
        )

        # time.sleep(2)
        driver.switch_to.frame('iframe-data')

        num = driver.find_element_by_xpath("/html/body/form/div[3]/div/div[3]/div[1]/span[1]").text
        num1 = num.index('共 ')
        num2 = num.index(' 筆')
        num = num[num1+2: num2]
        print(f"num: {num}")

        page = int(num)//20 + 1

        for p in range(page):

            temp = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/form/div[3]/div/table/tbody/tr"))
            )

            rows = len(driver.find_elements_by_xpath("/html/body/form/div[3]/div/table/tbody/tr"))

            for i in range(2, rows, 2):
                id_val = driver.find_element_by_xpath(f"/html/body/form/div[3]/div/table/tbody/tr[{i}]/td[2]/a")
                id_list.append(id_val.text)
                href_list.append(id_val.get_attribute('href'))
                date_val = driver.find_element_by_xpath(f"/html/body/form/div[3]/div/table/tbody/tr[{i}]/td[3]")
                date_list.append(date_val.text)
                title = driver.find_element_by_xpath(f"/html/body/form/div[3]/div/table/tbody/tr[{i}]/td[4]")
                title_list.append(title.text)

            for i in range(3, rows+1, 2):
                content = driver.find_element_by_xpath(f"/html/body/form/div[3]/div/table/tbody/tr[{i}]/td/span")
                content_list.append(content.text)

            if p==(page-1):        
                break
            
            driver.find_element_by_link_text("下一頁").click()

        data = {
            'title': title_list,
            'date': date_list,
            'content': content_list,
            'id': id_list,
            'url': href_list
        }

        df = pd.DataFrame(data)

        driver.close()

        df['date'] = df['date'].str.replace('.', '-', regex=False)

        for i in range(len(df)):
            date_index = df.at[i, 'date'].index('-')
            temp = int(df.at[i, 'date'][0:date_index]) + 1911
            df.at[i, 'date'] = str(temp) + df.at[i, 'date'][date_index:]

        from datetime import datetime
        import matplotlib.dates as mdates

        # %Y %m %d %H %M %S (年、月、日、時、分、秒)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df['date'] = df['date'].astype('str')

        # convert into json
        json_records = df.reset_index().to_json(orient ='records')
        data = []
        data = json.loads(json_records)
        context = {'d': data}
    
        return render(request, 'table.html', context)

    else:
        return render(request, 'search.html')

def search_info(request):
    if 'your_name' in request.GET and request.GET['your_name'] != '':  

        name  = request.GET.get('your_name')
        t = business_registration(name)
    
        context = {'d': t}
        
        return render(request, 'table_search_info.html', context)

    else:
        return render(request, 'search_search_info.html')

def law_personal(request):
    if 'your_name' in request.GET and request.GET['your_name'] != '':  

        name  = request.GET.get('your_name')

        t1 = domestic_judicial(name)
        t2 = law_judicial(name)
    
        context = {'d1': t1, 'd2': t2}
        
        return render(request, 'table_law_personal.html', context)

    else:
        return render(request, 'search_law_personal.html')

def law_company(request):

    if 'your_name' in request.GET and request.GET['your_name'] != '':  

        name  = request.GET.get('your_name')

        print(name)

        t = law_judicial(name)
    
        context = {'d': t}
        
        return render(request, 'table_law_company.html', context)

    else:
        return render(request, 'search_law_company.html')




