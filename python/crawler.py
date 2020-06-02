import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
from seleniumwire import webdriver as wire_webdriver
import copy
import pickle
import multiprocessing
from models import *
import numpy as np
import concurrent.futures


def get_webdriver(headless=False, executable_path=r'./chromedriver.exe'):
    if headless:
        options = Options()
        options.add_argument("--headless")
        driver = wire_webdriver.Chrome(options=options)
    else:
        #driver = webdriver.Chrome('C:\\Users\\caioc\\Desktop\\scripts\\chromedriver') 
        driver = wire_webdriver.Chrome(executable_path=executable_path) 
    return driver


def get_headers():
    driver = get_webdriver(headless=False)
    url = "https://www.ifood.com.br"
    driver.get(url)
    time.sleep(3)
    btn = driver.find_element_by_xpath("//button[@label='Buscar']")
    btn.click()
    time.sleep(3)
    btn = driver.find_element_by_xpath("//button[@class='btn-address--full-size']")
    btn.click()
    time.sleep(6)
    a_link = driver.find_element_by_xpath("//a[@data-test-id='restaurant-item-link'][@role='link'][@tabindex='0'][@class='restaurant-card']")
    restaurant_url = a_link.get_attribute("href")
    a_link.click() 
    '''
    #clica na barra de pesquisa
    btn = driver.find_element_by_class_name("address-search-input__button")
    btn.click()

    #digita o endereço na barra de pesquisa
    input = driver.find_element_by_xpath("//div[@class='address-search-input address-search-input--sticky']/input[1]")

    #input = driver.find_element_by_class_name("address-search-input__field")
    input.clear()
    input.send_keys('avenida ulisses montarroytos, 5996, candeias')

    #clica no primeiro endereço que aparecer
    input = driver.find_element_by_xpath("//div[@class='btn-address btn-address--simple btn-address__container']")
    input.click()

    #confirma localização
    btn = driver.find_element_by_xpath("//button[@class='btn btn--default btn--size-m address-maps__submit']")
    btn.click()

    #adicionar ponto de referencia

    #salvar endereço
    '''
    time.sleep(10)
    rs = driver.requests
    restaurant_id = restaurant_url.split('/')[-1]

    for r in rs:
        if restaurant_id in r.path and 'menu' in r.path:
            print(r.path)
            final_request = r

    print(final_request.headers)
    
    headers = copy.deepcopy(final_request.headers)
    del headers['Referer']
    
    with open('pickle/headers.pickle', 'wb') as f:
        pickle.dump(headers, f, protocol=pickle.HIGHEST_PROTOCOL)

def get_merchants(lat, long, size, num_pages):
    page = 0
    merchants = {}
    while True:
        url = ("https://marketplace.ifood.com.br/v2/merchants"
                    f"?latitude={lat}"
                    f"&longitude={long}"
                    "&zip_code=undefined"
                    f"&page={page}"
                    "&channel=IFOOD"
                    f"&size={size}"
                    "&features=DELIVERY&sort=&categories=&payment_types=&delivery_fee_from=0&delivery_fee_to=25&delivery_time_from=0&delivery_time_to=240")
        r = requests.get(url).json()
        for m in r['merchants']:
            if m['available']:
                merchants[m['name']] = {'info':Merchant(m['id'], m['name'], m['slug'], m['userRating'], m['deliveryFee']['value'], m['distance'])}
        page += 1
        print('page = ', page)
        if r['size'] <= 0 or num_pages <= page:
            break
    return merchants

def get_merchant_menu(merchant_id, merchant_name, headers):
    url = f"https://wsloja.ifood.com.br/ifood-ws-v3/restaurants/{merchant_id}/menu"
    r = requests.get(url, headers=headers).json()
    itens = []
    menus = r['data']['menu']
    for m in menus:
        if m['enabled']:
            for item in m['itens']:
                if item['enabled']:
                    taxonomy = item.get('taxonomyName', None)
                    price = item.get('unitMinPrice',  item['unitPrice'])
                    description = item.get('description', None)
                    details = item.get('details', None)
                    itens.append(Item(description, price, taxonomy, merchant_id, merchant_name, details))
    
    return itens

class AsyncHelper:
    def __init__(self, headers):
        self.headers = headers

    def get_merchant_menu_async(self, merchant_list):
        menu_list = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for merchant, menu in zip(merchant_list, executor.map(self.get_menu, merchant_list)):
                menu_list.append(menu)
        
        return menu_list
    def get_menu(self, merchant):
        url = f"https://wsloja.ifood.com.br/ifood-ws-v3/restaurants/{merchant.id}/menu"
        r = requests.get(url, headers=self.headers).json()
        itens = []
        menus = r['data']['menu']
        for m in menus:
            if m['enabled']:
                for item in m['itens']:
                    if item['enabled']:
                        taxonomy = item.get('taxonomyName', None)
                        price = item.get('unitMinPrice',  item['unitPrice'])
                        description = item.get('description', None)
                        details = item.get('details', None)
                        itens.append(Item(description, price, taxonomy, merchant.id, merchant.name, details))
        
        return itens

'''
if __name__ == '__main__':
    #lat = '-8.200652'
    #long = '-34.922298'
    lat = -8.287812
    long = -35.977930
    size = 10


    with open('headers.pickle', 'rb') as f:
        headers = pickle.load(f)

    merchants = get_merchants(lat, long, 100, 3)
    print(len(merchants))
    num = 0
    for m in merchants:
        print(num)
        print(merchants[m]['info'].name)
        merchants[m]['itens'] = get_merchant_menu(merchants[m]['info'].id, merchants[m]['info'].name, headers)
        num += 1

    with open('merchants.pickle', 'wb') as f:
        pickle.dump(merchants, f, protocol=pickle.HIGHEST_PROTOCOL)

'''

def start_async(lat, long):
    try:
        with open('pickle/headers.pickle', 'rb') as f:
            headers = pickle.load(f)

        merchants = get_merchants(lat, long, 100, 3)
        merchant_list = []
        for m in merchants:
            merchant_list.append(merchants[m]['info'])
        
        print('num restaurants:', len(merchant_list))
        #convert list to a list of lists, each list will be passed to a process
        merchant_sublists = [list(i) for i in np.array_split(merchant_list, multiprocessing.cpu_count())]
        start = time.time()
        async_helper = AsyncHelper(headers)
        results = {}
        with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            for merchant_sublist, menu_sublist in zip(merchant_sublists, executor.map(async_helper.get_merchant_menu_async, merchant_sublists)):
                for i in range(len(merchant_sublist)):
                    results[merchant_sublist[i].name] = {'info':merchant_sublist[i], 'itens':menu_sublist[i]}
        
        print(f'Total time: {time.time() - start}')
        with open('pickle/merchants.pickle', 'wb') as f:
            pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)
    except:
        print('getting headers')
        get_headers()

if __name__ == '__main__':
    lat = '-8.200652'
    long = '-34.922298'
    start_async(lat, long)