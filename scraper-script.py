from selenium import webdriver
from time import sleep
import os
from pathlib import Path
import fitz
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
try:
    os.rename('/home/%s/Downloads' % os.getenv('USERNAME'), '/home/%s/Downloads_backup' % os.getenv('USERNAME'))
except:
    Path('/home/%s/Downloads' % os.getenv('USERNAME')).mkdir(parents=True, exist_ok=True)
chrome_options = Options()
chrome_options.enable_downloads = True
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--verbose')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "./downloads/",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
})

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

driver.switch_to.window(driver.window_handles[0])

retries = 10
while retries:
    try:
        driver.get('http://bdh.bne.es/bnesearch/Search.do?sort=estrellas_desc&showYearItems=&field=bnesearch&advanced=false&exact=on&textH=&completeText=&text=Destacadas.do&pageNumber=1&pageSize=30&language=')
        element = driver.find_element(By.XPATH, '//*[@id="sort"]')
        if element.is_displayed():
            # element.click()
            # driver.find_element(By.XPATH, '//*[@id="sort"]/option[9]').click()

            break
    except (NoSuchElementException, StaleElementReferenceException):
        if retries <= 0:
            raise
        else:
            driver.refresh()
    retries = retries - 1
    sleep(4)

driver.find_element(By.XPATH, '//*[@id="MaterialesFacetLink"]').click()
driver.find_element(By.XPATH, '//*[@id="subMaterialcategory1Check"]').click()
driver.find_element(By.XPATH, '//*[@id="subMaterialcategory4Check"]').click()
driver.find_element(By.XPATH, '//*[@id="DerechosFacetLink"]').click()
driver.find_element(By.XPATH, '//*[@id="DerechosFacet"]/ul/li/input').click()
driver.find_element(By.XPATH, '//*[@id="filtrarButton"]/input').click()

books_list_tab = driver.current_window_handle

def wait_download():
    try:
        pdfs = os.listdir('/home/%s/Downloads' % os.getenv('USERNAME'))

        while True:
            sleep(1)
            pdfs = os.listdir('/home/%s/Downloads' % os.getenv('USERNAME'))
            if pdfs[0].endswith('.crdownload'):
                print('wait dowload')
            else:
                print('downloaded')
                print(pdfs[0])

                return pdfs[0]
    except:
        sleep(2)
        return wait_download()
    
    #knigi menshe 24 ili bolshe 828 ne sohranyaem

def download_books_per_page(driver: webdriver):
    books = driver.find_elements(By.CSS_SELECTOR, "#lista div div.details h2 a")

    for i in range(10):
        book = books[i]
        href = book.get_attribute("href")

        driver.execute_script("window.open('%s', '_blank')" % href)

        details_tab = None
        download_tab = None

        for tab in driver.window_handles:
            if tab != books_list_tab:
                details_tab = tab
                break
        
        driver.switch_to.window(details_tab)

        # print(driver.find_element(By.XPATH, '//*[@id="results"]/div[1]/div/div[2]/h1').text)

        # print(driver.find_element(By.XPATH, '//*[@id="results"]/div[1]/div/div[2]/h2').text)

        driver.find_element(By.XPATH, '//*[@id="results"]/div[1]/div/div[1]/div[1]/a/img').click()
        
        driver.close()

        for tab in driver.window_handles:
            if tab != books_list_tab and tab != details_tab:
                download_tab = tab
                break

        driver.switch_to.window(download_tab)

        # driver.find_element(By.XPATH, '//*[@id="viewer"]/div[1]/div[1]/div[2]/img').click()
        driver.find_element(By.XPATH, '//*[@id="viewer"]/div[1]/div[1]/div[3]/img').click()
        driver.find_element(By.XPATH, '//*[@id="pdfVolume"]').click()
        driver.find_element(By.XPATH, '//*[@id="downloadButton"]').click()

        pdf_name = wait_download()

        pdf_file = fitz.open('/home/%s/Downloads/%s' % (os.getenv('USERNAME'), pdf_name))
        book_text = b""
        for page in pdf_file:
            book_text += page.get_text().encode('utf-8')

        os.remove('/home/%s/Downloads/%s' % (os.getenv('USERNAME'), pdf_name))

        driver.close()

        driver.switch_to.window(books_list_tab)

        books = driver.find_elements(By.CSS_SELECTOR, "#lista div div.details h2 a")


download_books_per_page(driver)

# driver.find_element(By.XPATH, '//*[@id="navsup"]/span[5]/a/img').click()

#download_books_per_page(driver)

# driver.find_element(By.XPATH, '//*[@id="navsup"]/span[10]/a/img').click()

# navsup_element = driver.find_element(By.XPATH, '//*[@id="navsup"]/span[11]/a/img')

# try:
#     while navsup_element.is_displayed():
#         #download_books_per_page(driver)
#         navsup_element.click()
#         navsup_element = driver.find_element(By.XPATH, '//*[@id="navsup"]/span[11]/a/img')
# except:
#     breakpoint()

breakpoint()