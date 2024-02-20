from selenium import webdriver
from time import sleep
import os
from os.path import expanduser
from pathlib import Path
from datetime import datetime
import fitz
import fpdf
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options


global home
home = expanduser("~")

class PDF(fpdf.FPDF):
    def footer(self):
        if self.page_no() != 1:
            # Go to 1.5 cm from bottom
            self.set_y(-15)
            self.add_font("dejavu-sans", style="", fname="assets/DejaVuSans.ttf")
            self.set_font("dejavu-sans", size=12)
            # Print centered page number
            self.cell(0, 10, f"{self.page_no()}", 0, 0, 'C')

try:
    os.rename('%s/Downloads' % home, '%s/Downloads_backup' % home)
except:
    Path('%s/Downloads' % home).mkdir(parents=True, exist_ok=True)


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

retries = 10
while retries:
    try:
        driver.get('http://bdh.bne.es/bnesearch/Search.do?sort=estrellas_desc&showYearItems=&field=bnesearch&advanced=false&exact=on&textH=&completeText=&text=Destacadas.do&pageNumber=1&pageSize=30&language=')
        element = driver.find_element(By.XPATH, '//*[@id="sort"]')
        if element.is_displayed():
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
        pdfs = os.listdir('%s/Downloads' % home)

        while True:
            sleep(1)
            pdfs = os.listdir('%s/Downloads' % home)
            if pdfs[0].endswith('.crdownload'):
                print('wait dowload')
            else:
                print('downloaded')
                print(pdfs[0])

                return pdfs[0]
    except:
        sleep(2)
        return wait_download()
    

def download_books_per_page(driver: webdriver):
    books = driver.find_elements(By.CSS_SELECTOR, "#lista div div.details h2 a")

    book_id = 1

    for i in range(len(books)):
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

        try:
            title = driver.find_element(By.XPATH, '//*[@id="results"]/div[1]/div/div[2]/h1').text
        except:
            title = ''

        try:
            author = driver.find_element(By.XPATH, '//*[@id="results"]/div[1]/div/div[2]/h2').text
        except:
            author = ''

        driver.find_element(By.XPATH, '//*[@id="results"]/div[1]/div/div[1]/div[1]/a/img').click()
        
        driver.close()

        for tab in driver.window_handles:
            if tab != books_list_tab and tab != details_tab:
                download_tab = tab
                break

        driver.switch_to.window(download_tab)

        driver.find_element(By.XPATH, '//*[@id="viewer"]/div[1]/div[1]/div[2]/img').click()

        try:
            driver.find_element(By.XPATH, '//*[@id="pdfVolume"]').click()
        except:
            driver.find_element(By.XPATH, '//*[@id="viewer"]/div[1]/div[1]/div[3]/img').click()
            driver.find_element(By.XPATH, '//*[@id="pdfVolume"]').click()

        driver.find_element(By.XPATH, '//*[@id="downloadButton"]').click()

        pdf_name = wait_download()

        folder = '%s/pdfs_formated' % os.getcwd()
        Path(folder).mkdir(parents=True, exist_ok=True) 
        currentYear, currentMonth = datetime.now().year, datetime.now().month
        interior_pdf_fname = f"{currentYear}_{currentMonth}_{book_id}_paperback_interior.pdf"

        pdf_file = fitz.open('%s/Downloads/%s' % (home, pdf_name))
        book_text = b""
        for page in pdf_file:
            book_text += page.get_text().encode('utf-8')

        book_text = book_text.decode().replace('\n', '')

        pdf = PDF(format=(152.4, 228.6))
        pdf.add_font("dejavu-sans", style="", fname="assets/DejaVuSans.ttf")
        # TITLE
        pdf.add_page()
        pdf.set_font("dejavu-sans", size=12)

        lines_num = len(pdf.multi_cell(w=0, align='C', padding=(0, 8), text=f"{title}\n\n{author}", dry_run=True, output="LINES"))
        if lines_num >= 3:
            padding_top = (228.6 - 24 * (lines_num - 1)) / 2
        else:
            padding_top = (228.6 - 24 * (lines_num)) / 2
        pdf.multi_cell(w=0, align='C', padding=(padding_top, 8, 0), text=f"{title}\n\n{author}")
        # TEXT
        pdf.add_page()
        pdf.set_font("dejavu-sans", size=12)
        pdf.multi_cell(w=0, h=4.6, align='J', padding=8, text=book_text)
        #
        pages = pdf.page_no()

        if pages >= 24 and pages <= 828:
            pdf.output(f"{folder}/{interior_pdf_fname}")
            

        os.remove('%s/Downloads/%s' % (home, pdf_name))

        book_id += 1

        driver.close()

        driver.switch_to.window(books_list_tab)

        books = driver.find_elements(By.CSS_SELECTOR, "#lista div div.details h2 a")
        if book_id == 100:
            break

    return book_id

download_books_per_page(driver)

driver.find_element(By.XPATH, '//*[@id="navsup"]/span[5]/a/img').click()

download_books_per_page(driver)

driver.find_element(By.XPATH, '//*[@id="navsup"]/span[10]/a/img').click()

navsup_element = driver.find_element(By.XPATH, '//*[@id="navsup"]/span[11]/a/img')

try:
    while navsup_element.is_displayed():
        download_books_per_page(driver)
        navsup_element.click()
        navsup_element = driver.find_element(By.XPATH, '//*[@id="navsup"]/span[11]/a/img')
except Exception as e:
    print(str(e))
    
