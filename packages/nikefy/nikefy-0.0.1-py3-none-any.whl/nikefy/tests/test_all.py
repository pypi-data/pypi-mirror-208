from nikefy import (
    request_page,
    validate_url,
    get_nike_products,
    sort_nike_products,
    get_product_description,
    filter_nike_products,
)
from unittest.mock import patch, mock_open, Mock, call
import unittest
from bs4 import BeautifulSoup
import pandas as pd


class TestNikefy(unittest.TestCase):
    def test_validate_url_valid(self):
        url = 'https://www.nike.com/'
        self.assertIsNone(validate_url(url))

    def test_validate_url_invalid(self):
        url = 'https://www.adidas.com/'
        with self.assertRaises(ValueError):
            validate_url(url)

    def test_sort_nike_products_asc(self):
        products_info = pd.DataFrame(
            {
                'Product Name': ['Nike Alphafly 2', 'Nike Vaporfly 3', 'Jordan Retro 6 G NRG'],
                'Price': ['$275', '$250', '$220'],
            }
        )
        expected_output = pd.DataFrame(
            {
                'Product Name': ['Jordan Retro 6 G NRG', 'Nike Vaporfly 3', 'Nike Alphafly 2'],
                'Price': ['$220', '$250', '$275'],
            }
        )
        self.assertTrue(expected_output.equals(sort_nike_products(products_info, 'asc')))

    def test_sort_nike_products_desc(self):
        products_info = pd.DataFrame(
            {
                'Product Name': ['Nike Air Max 270', 'Nike Air Max 95', "Nike Air Force 1 '07"],
                'Price': ['$160', '$175', '$110'],
            }
        )
        expected_output = pd.DataFrame(
            {
                'Product Name': ['Nike Air Max 95', 'Nike Air Max 270', "Nike Air Force 1 '07"],
                'Price': ['$175', '$160', '$110'],
            }
        )
        print((sort_nike_products(products_info, 'desc')))
        self.assertTrue(expected_output.equals(sort_nike_products(products_info, 'desc')))

    def test_sort_nike_products_invalid_order(self):
        products_info = pd.DataFrame(
            {
                'Product Name': ['Nike Air Max 270', 'Nike Air Max 95', "Nike Air Force 1 '07"],
                'Price': ['$160', '$175', '$110'],
            }
        )
        with self.assertRaises(ValueError):
            sort_nike_products(products_info, 'invalid')

    def test_get_product_description(self):
        with patch('nikefy.request_page') as mock_request_page:
            mock_request_page.return_value = BeautifulSoup(
                '<div class="description-preview body-2 '
                'css-1pbvugb"><p>With maximum cushioning to support every mile, the Invincible 3 gives you our '
                'highest level of comfort underfoot to help you stay on your feet today, tomorrow and beyond. '
                'Designed to help keep you on the run, it’s super supportive and bouncy, so that you can propel down '
                'your preferred path and come back for your next run feeling ready and reinvigorated.</p></div>',
                'html.parser',
            )
            description = get_product_description(
                'https://www.nike.com/t/invincible-3-mens-road-running-shoes-CLdFjq/DR2615-101'
            )
            self.assertEqual(
                description,
                'With maximum cushioning to support every mile, the Invincible 3 '
                'gives you our highest level of comfort underfoot to help you stay '
                'on your feet today, tomorrow and beyond. Designed to help keep you '
                'on the run, it’s super supportive and bouncy, so that you can propel '
                'down your preferred path and come back for your next run feeling ready '
                'and reinvigorated.'
                'Shown: White/Sail/Oatmeal/Obsidian'
                'Style: DR2615-101',
            )

    def test_get_nike_products_integration(self):
        url = 'https://www.nike.com/w/mens-shoes-nik1zy7ok'
        data = get_nike_products(url)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertGreater(len(data), 0)

    def test_filter_nike_products(self):
        data = {
            'Name': ['Nike Air Max 90', 'Nike Air Force 1', "Nike Blazer Mid '77"],
            'Type': ["Men's Shoes", "Women's Shoes", "Men's Shoes"],
            'Price': ['$130', '$120', '$90'],
        }
        products_info = pd.DataFrame(data)

        filtered_data = filter_nike_products(products_info, price_range=(100, 130), product_type="Men's Shoes")
        expected_data = pd.DataFrame({'Name': ['Nike Air Max 90'], 'Type': ["Men's Shoes"], 'Price': ['130.0']})

        self.assertTrue(expected_data.equals(filtered_data))


if __name__ == '__main__':
    unittest.main()
