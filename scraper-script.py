from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# breakpoint()
# /bnesearch/Search.do?sort=estrellas_desc&showYearItems=&field=bnesearch&advanced=false&exact=on&textH=&completeText=&text=Destacadas.do&pageNumber=1&pageSize=30&language=
driver.get('https://www.bne.es/es')
sleep(3)
driver.find_element(By.XPATH, '//*[@id="popup-buttons"]/button[2]').click()
driver.find_element(By.XPATH, '//*[@id="block-bne-theme-mx1bne-menu"]').click()
driver.find_element(By.XPATH, '//*[@id="block-bne-theme-mx1bne"]/ul/li[1]/a').click()
sleep(3)
driver.find_element(By.XPATH, '//*[@id="block-bne-theme-contenidoprincipaldelapagina"]/article/div/div/div/nav/ul/li[2]/div/div/p[2]/span/a').click()
driver.switch_to.window(driver.window_handles[0])
driver.close()
driver.switch_to.window(driver.window_handles[0])
retries = 10
while retries:
    try:
        element = driver.find_element(By.XPATH, '//*[@id="sort"]')
        if element.is_displayed():
            element.click()
            driver.find_element(By.XPATH, '//*[@id="sort"]/option[9]').click()

            break
    except (NoSuchElementException,
            StaleElementReferenceException):
        if retries <= 0:
            raise
        else:
            driver.refresh()
    retries = retries - 1
    sleep(10)


driver.find_element(By.XPATH, '//*[@id="MaterialesFacetLink"]').click()

driver.find_element(By.XPATH, '//*[@id="subMaterialcategory1Check"]').click()

driver.find_element(By.XPATH, '//*[@id="subMaterialcategory4Check"]').click()

driver.find_element(By.XPATH, '//*[@id="DerechosFacetLink"]').click()

driver.find_element(By.XPATH, '//*[@id="DerechosFacet"]/ul/li/input').click()

driver.find_element(By.XPATH, '//*[@id="filtrarButton"]/input').click()

books = driver.find_elements(By.CSS_SELECTOR, "#lista div div.details h2 a")

for i in range(len(books)):
    book = books[i]
    href = book.get_attribute("href")

    driver.execute_script("window.open('%s', '_blank')" % href)

    driver.find_element(By.XPATH, '//*[@id="results"]/div[1]/div/div[1]/div[2]/a').click()

    driver.switch_to.window(driver.window_handles[0])

    books = driver.find_elements(By.CSS_SELECTOR, "#lista div div.details h2 a")

breakpoint()    