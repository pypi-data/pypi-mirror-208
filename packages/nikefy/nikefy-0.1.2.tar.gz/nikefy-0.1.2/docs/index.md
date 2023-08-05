# Welcome to Nikefy's documentation!

## Overview
Python library that amasses metadata from Nike.com website.
Nikefy will allow users to quickly access metadata from Nike.com website such as products and prices data.
* Create a database that easily queries shoes
* Easily find sold out products
* Find out most popular products via ratings

## Install

```
pip install nikefy
```

# Usage
```python
import nikefy as nf

url = 'https://www.nike.com/w/mens-shoes-nik1zy7ok'
nf.get_nike_products(url)
nike_products = nf.get_nike_products(url)
sorted_nike_products = sort_nike_products(nike_products, sort_order='asc')
filtered_nike_products = filter_nike_products(nike_products, price_range=(100, 150), product_type="Men's Shoes")
```

`get_nike_products()` gets Men's shoes from Nike.com website and returns a dataframe

`sort_nike_products()` sorts Men's shoes based on price

`filter_nike_products()` filters Men's shoes based on price range and type

# Example
Running the following code
```python
import nikefy as nf

url = 'https://www.nike.com/w/mens-shoes-nik1zy7ok'
nike_products = nf.get_nike_products(url)
print(nike_products)
```
Outputs something like this to the console
```
                             Product Name Price  ...                                        Description                                        Product URL
0                         Nike Pegasus 40  $130  ...  A springy ride for every run, the Peg’s famili...  https://www.nike.com/t/pegasus-40-mens-road-ru...
1                     Nike Dunk Low Retro  $110  ...  Created for the hardwood but taken to the stre...  https://www.nike.com/t/dunk-low-retro-mens-sho...
2                        Air Jordan 1 Low  $110  ...  Inspired by the original that debuted in 1985,...  https://www.nike.com/t/air-jordan-1-low-mens-s...
3                        Air Jordan 1 Mid  $125  ...  Inspired by the original AJ1, this mid-top edi...  https://www.nike.com/t/air-jordan-1-mid-mens-s...
4                      Nike Free Metcon 5  $120  ...  When your workouts wade into the nitty gritty,...  https://www.nike.com/t/free-metcon-5-mens-trai...
5                          Cosmic Unity 3  $170  ...  Better for your game, designed with sustainabi...  https://www.nike.com/t/cosmic-unity-3-basketba...
```

## Demo
![](https://raw.githubusercontent.com/cgr2134/nikefy/main/docs/img/demo.gif)

```eval_rst
.. note::
    Use Nikefy to further simplify the shopping experience.
```