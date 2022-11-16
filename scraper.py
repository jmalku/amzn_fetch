import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
from faker import Faker

result = []

def get_soup_retry(url):
    fake = Faker()
    uag_random = fake.user_agent()

    header = {
        'User-Agent': uag_random,
        'Accept-Language': 'en-US,en;q=0.9'
    }
    isCaptcha = True
    while isCaptcha:
        page = requests.get(url, headers=header)
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, 'lxml')
        if 'captcha' in str(soup):
            uag_random = fake.user_agent()
            print(f'\rBot has been detected... retrying ... use new identity: {uag_random} ', end='', flush=True)
            continue
        else:
            print('Bot bypassed')
            return soup


def get_detail(url):
    soup = get_soup_retry(url)
    try:
        title = soup.find('span', attrs={'id': 'productTitle'}).text.strip()  # to get the text, and strip is used to remove all the leading and trailing spaces from a string.
    except AttributeError:
        title = ''
    try:
        discount_percent = soup.find('td', attrs={'class': 'a-span12 a-color-price a-size-base'}).find('span', attrs={
            'class': 'a-color-price'}).text.split('(')[1].replace(')', '')
    except AttributeError:
        discount_percent = ''

    if discount_percent:
        try:
            original_price = soup.find('span', attrs={'class': 'a-price a-text-price a-size-base'}).find('span', attrs={
                'class': 'a-offscreen'}).text.strip()
        except AttributeError:
            original_price = ''
        discount_save = soup.find('td', attrs={'class': 'a-span12 a-color-price a-size-base'}).find('span', attrs={
            'class': 'a-color-price'}).find('span', attrs={'class': 'a-offscreen'}).text.strip()
    else:
        original_price = ''
        discount_save = ''
        pass

    try:
        current_price = soup.find('span', attrs={'class': 'a-price a-text-price a-size-medium apexPriceToPay'}).find(
            'span', attrs={'class': 'a-offscreen'}).text.strip()
    except AttributeError:
        current_price = ''
    try:
        review_count = soup.find('span', attrs={'id': 'acrCustomerReviewText'}).text.strip()
    except AttributeError:
        review_count = ''
    try:
        feature_bullet = soup.find('div', attrs={'id': 'feature-bullets'}).find('ul', attrs={
            'class': 'a-unordered-list a-vertical a-spacing-mini'}).find_all('li')
        sv_feature = []
        for li in feature_bullet:
            text = li.find('span', attrs={'class': 'a-list-item'})
            features = str(text.string).strip()
            if 'None' in features:
                pass
            else:
                sv_feature.append(features)
    except AttributeError:
        sv_feature = ''
    data = soup.select(
        "#imageBlock_feature_div > script:nth-child(2)")  # using selector, right click > copy > copy selector
    try:
        script_text = data[0].text  # remove html tag
        # use regex to pull out the relevant json string
        json_str = re.search('{(.+)}', script_text)[0].replace("\'", '"').replace("null",
                                                                                  '"null"')  # replace single quote ' to double quote "
        json_obj = json.loads(json_str)
        images_url = []
        for i in json_obj['initial']:
            images_hires = i['hiRes']
            images_large = i['large']
            if images_hires is None:
                images_url.append(images_large)
            else:
                images_url.append(images_hires)
    except IndexError:
        images_url = ''

    try:
        available_stock = soup.find('div', attrs={'id': 'availability'}).find('span').text.strip()
    except AttributeError:
        available_stock = ''
    try:
        asin = soup.find(id='averageCustomerReviews').get('data-asin')
    except AttributeError:
        asin = url.split('/dp/')[1].replace('/', '')
    try:
        description = soup.find('div', attrs={'id': 'productDescription'}).text.replace('\n', '').strip()
    except AttributeError:
        description = ''
    try:
        rating = soup.find('span', attrs={'data-hook': 'rating-out-of-text'}).text.strip()
    except AttributeError:
        rating = ''

    goal = {
        'asin': asin,
        'title': title,
        'price': current_price,
        'rating': rating,
        'review': review_count,
        'stock': available_stock,
        'feature': sv_feature,
        'description': description,
        'discount_percent': discount_percent,
        'original_price': original_price,
        'discount_save': discount_save,
        'images_url': images_url
    }
    print(goal)

    result.append(goal)
    return result


def search_keyword(keyword):
    count_page = 0
    count_asin = 0
    while True:
        count_page += 1
        url = f'https://www.amazon.com/s?k={keyword}&page={count_page}'
        print(f'Getting page: {count_page} | {url}')
        soup = get_soup_retry(url)
        try:
            result = soup.find('div', attrs={'class': 's-main-slot s-result-list s-search-results sg-row'}).find_all('div', attrs={'data-component-type': 's-search-result'})
        except AttributeError:
            continue
        for ids in result:
            count_asin += 1
            asin = ids['data-asin']
            url_product = f'https://www.amazon.com/dp/{asin}'
            print(f'{count_asin}. {url_product}')
            list_result = get_detail(url_product)
            df = pd.DataFrame(list_result)
            keyword = str(keyword).replace('+', '_')
            # df.to_csv(f'result_amzn_{keyword}.csv', index=False)
            df.to_excel(f'result_amzn_{keyword}.xlsx', index=False)
            # if count_asin % 50 == 0:
            #     sleep = random.randint(3, 9)
            #     print(f'calm down {sleep} seconds')
            #     time.sleep(sleep)

        last_page = soup.find('li', {'class': 'a-disabled a-last'})
        if not last_page:
            pass
        else:
            break
