def total_products_price(products_prices, products_quantities):
    return sum([a * b for a, b in zip(products_prices, products_quantities)])
