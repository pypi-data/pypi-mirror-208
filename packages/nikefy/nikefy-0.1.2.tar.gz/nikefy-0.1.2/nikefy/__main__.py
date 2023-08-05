from .nikefy import get_nike_products, sort_nike_products, filter_nike_products

if __name__ == "__main__":
    url = 'https://www.nike.com/w/mens-shoes-nik1zy7ok'
    nike_products = get_nike_products(url)
    print(nike_products)
    sorted_nike_products = sort_nike_products(nike_products, sort_order='asc')
    print(sorted_nike_products)
    filtered_nike_products = filter_nike_products(nike_products, price_range=(100, 150), product_type="Men's Shoes")
    print(filtered_nike_products)
