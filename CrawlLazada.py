from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException,ElementNotInteractableException
from selenium.webdriver.common.by import By
import sys
from time import sleep
import numpy as np
import pandas as pd
import random
import time

# Cấu hình lại mã hóa đầu ra để hỗ trợ Unicode
sys.stdout.reconfigure(encoding='utf-8')
from selenium import webdriver


# # Open URL
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.get('https://www.lazada.vn/catalog/?spm=a2o4n.homepage.search.d_go&q=kh%C4%83n%20gi%E1%BA%A5y')

# ================================ GET link/title
elems = driver.find_elements(By.CSS_SELECTOR , ".RfADt [href]")
title = [elem.text for elem in elems]
links = [elem.get_attribute('href') for elem in elems]

# ================================ GET price
elems_price = driver.find_elements(By.CSS_SELECTOR , ".aBrP0")
len(elems_price)
price = [elem_price.text for elem_price in elems_price]

df1 = pd.DataFrame(list(zip(title, price, links)), columns = ['title', 'price','link_item'])
df1['index_']= np.arange(1, len(df1) + 1)

# ================================GET discount


elems_discountPercent = driver.find_elements(By.CSS_SELECTOR , ".WNoq3 .IcOsH")
discountPercent = [elem.text for elem in elems_discountPercent]

discount_idx, discount_percent_list = [], []
for i in range(1, len(title)+1):
    try:
        discount_percent = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[3]/div[1]/div/div[1]/div[2]/div[{}]/div/div/div[2]/div[4]/span".format(i))
        discount_percent_list.append(discount_percent.text)
        print(i)
        discount_idx.append(i)
    except NoSuchElementException:
        print("No Such Element Exception " + str(i))

df2 = pd.DataFrame(list(zip(discount_idx , discount_percent_list)), columns = ['discount_idx','discount_percent_list'])

df3 = df1.merge(df2, how='left', left_on='index_', right_on='discount_idx')
#print(df3)

# ================================ GET location/countReviews
elems_countReviews = driver.find_elements(By.CSS_SELECTOR , "._6uN7R")
countReviews = [elem.text for elem in elems_countReviews]

df3['countReviews'] = countReviews
file_name = f'Giay.csv'
df3.to_csv(file_name, index=False, encoding='utf-8-sig')
# ================================ GET more infor of each item  



# ============================GET INFOMATION OF ALL ITEMS
def getDetailItems(link):
    driver.get(link)
    count = 1
    driver.execute_script("window.scrollTo(0, 500)")
    sleep(random.randint(2,4))
    driver.execute_script("window.scrollTo(500, 1200)")
    sleep(random.randint(2,4))

    name_comment, content_comment, skuInfo_comment, like_count, star_count = [], [], [], [], []
    while True:
        try:
            
            print("Crawl Page " + str(count))
            try:
                ban = driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div[1]')
                if not ban.is_enabled():
                    print("Bị ban ròi nè")
                    sleep(60)
            except  NoSuchElementException:
                print("")
            driver.execute_script("window.scrollTo(1200, 1800)")
            sleep(random.randint(2,4))
            driver.execute_script("window.scrollTo(1800, 2500)") 
            sleep(random.randint(2,4))
            elems_star = driver.find_elements(By.CSS_SELECTOR, ".mod-reviews > .item > .top > .left")
            for elem in elems_star:
                stars = elem.find_elements(By.TAG_NAME, "img")
                stars_text = ""
                for star in stars:
                    img_src = star.get_attribute("src")
                    if 'https://laz-img-cdn.alicdn.com/tfs/TB19ZvEgfDH8KJjy1XcXXcpdXXa-64-64.png' in img_src:  
                        stars_text += '★'
                    elif 'https://laz-img-cdn.alicdn.com/tfs/TB18ZvEgfDH8KJjy1XcXXcpdXXa-64-64.png' in img_src:
                        stars_text += '☆'
                star_count.append(stars_text)

            elems_name = driver.find_elements(By.CSS_SELECTOR , ".middle")
            name_comment = [elem.text for elem in elems_name] + name_comment

            elems_content = driver.find_elements(By.CSS_SELECTOR , ".item > .item-content > .content")
            content_comment = [elem.text for elem in elems_content] + content_comment

            elems_skuInfo= driver.find_elements(By.CSS_SELECTOR , ".item-content .skuInfo")
            skuInfo_comment = [elem.text for elem in elems_skuInfo] + skuInfo_comment

            elems_likeCount = driver.find_elements(By.CSS_SELECTOR , ".item > .item-content > .bottom > .left > .left-content")
            like_count = [elem.text for elem in elems_likeCount] + like_count
            
            try:
                
                next_pagination_cmt = driver.find_element(By.XPATH, "/html/body/div[4]/div/div[10]/div[1]/div[2]/div/div/div/div[3]/div[2]/div/button[2]")
                if not next_pagination_cmt.is_enabled():
                    print("Nút 'next' không khả dụng. Dừng lại.")
                    break
                next_pagination_cmt.click()
                print("Đã click vào nút trang tiếp theo!")
                time.sleep(random.randint(1, 3))
                count += 1
            except NoSuchElementException:
                print("Không tìm thấy nút 'next'. Dừng lại.")
                break
        except ElementNotInteractableException:
            print("Element Not Interactable Exception!")
            break

    df4 = pd.DataFrame(list(zip(name_comment , content_comment, skuInfo_comment, like_count, star_count)), 
                       columns = ['name_comment', 'content_comment','skuInfo_comment', 'like_count', 'star'])

    df4.insert(0, "link_item", link)
    del name_comment, content_comment, skuInfo_comment, like_count, star_count
    return df4

df_list = []
for i, link in enumerate(links):
    try:
        df = getDetailItems(link)
        df_list.append(df)
        
        # Lưu DataFrame vào file CSV với tên dựa trên thứ tự
        file_name = f'comments_Giay_{i + 1}.csv'
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        print(f"Dữ liệu từ {link} đã được lưu vào file {file_name}")
    except IndexError as e:
        print(f"Lỗi: {e}. Vị trí: {i}.")
        break

driver.quit()
