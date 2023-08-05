import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def validate_url(url):
    pattern = r'https?://www\.nike.com/.*'
    if not re.match(pattern, url):
        raise ValueError('Invalid URL: Must be a valid Nike.com URL.')


def request_page(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def get_nike_products(url):
    """
    This function takes a Nike.com URL and returns a dataframe.

    Args:
         url (:obj:`str`): String Nike.com url

    Returns:
        data: A panda Dataframe with various information regarding Nike products.
    """
    validate_url(url)
    soup = request_page(url)
    products_info = []
    products = soup.find_all('div', {'class': 'product-card__body'})
    for product in products:
        name = product.find('div', {'class': 'product-card__title'}).text.strip()
        price = product.find('div', {'class': 'product-price'}).text.strip()
        type = product.find('div', {'class': 'product-card__subtitle'}).text.strip()
        product_url = product.find('a').get('href')
        description = get_product_description(product_url)
        data = {
            'Product Name': name,
            'Price': price,
            'Type': type,
            'Description': description,
            'Product URL': product_url,
        }
        products_info.append(data)
    data = pd.DataFrame(products_info)
    return data


def sort_nike_products(products_info, sort_order='asc'):
    """
    This function sorts Nike dataframe based on price. Can be sorted in ascending or descending order.
    Args:
         products_info (:obj: `dataframe`): Nike products dataframe
         sort_order (:obj: `str`): Ascending or descending order

    Returns:
        data: A panda Dataframe in ascending or descending order.
    """
    if sort_order == 'asc':
        return products_info.sort_values(
            'Price', ascending=True, key=lambda val: val.str.replace('$', '').astype('float64'), ignore_index=True
        )
    elif sort_order == 'desc':
        return products_info.sort_values(
            'Price', ascending=False, key=lambda val: val.str.replace('$', '').astype('float64'), ignore_index=True
        )
    else:
        raise ValueError('Invalid sort order: Must be "asc" or "desc".')


def get_product_description(product_url):
    """
    This function returns a specific product's description.
    Args:
         product_url (:obj: `str`): Nike product's url

    Returns:
         description: A string description.
    """
    validate_url(product_url)
    soup = request_page(product_url)
    description = soup.find('div', {'class': 'description-preview body-2 css-1pbvugb'}).text.strip()
    return description


def filter_nike_products(products_info, price_range=None, product_type=None):
    """
    This function returns filtered nike product dataframe
    Args:
         products_info (:obj: `dataframe`): Nike products dataframe
         price_range (:obj: set): Price range
         product_type (:obj: str): Product type

    Returns:
         filtered_data: A filtered dataframe.
    """
    if price_range:
        min_price, max_price = price_range
        filtered_data = products_info.copy()
        filtered_data['Price'] = filtered_data['Price'].str.replace('$', '').astype(float)
        filtered_data = filtered_data.loc[(filtered_data['Price'] >= min_price) & (filtered_data['Price'] <= max_price)]
        filtered_data['Price'] = filtered_data['Price'].astype(str)
    else:
        filtered_data = products_info.copy()
        filtered_data['Price'] = filtered_data['Price'].str.replace('$', '').astype(float)
        filtered_data['Price'] = filtered_data['Price'].astype(str)

    if product_type:
        filtered_data = filtered_data.loc[filtered_data['Type'] == product_type]

    if filtered_data.empty:
        print("No products found for the specified criteria.")
    else:
        return filtered_data
