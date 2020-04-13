#!/usr/bin/env python

original_prices = [1.25, -9.45, 10.22, 3.78, -5.92, 1.16]
prices = [i if i > 0 else 0 for i in original_prices]
print(f"{prices}")

def get_price(price):
    if price > 0:
        return price

prices = [get_price(i) for i in original_prices]
print(f"{prices}")