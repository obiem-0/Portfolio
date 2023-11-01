# utils.py
from datetime import timedelta

def calculate_delivery_time(order_date, delivery_estimate):
    return order_date + timedelta(days=delivery_estimate)

def calculate_preparation_time(order_count, prep_time):
    return order_count * prep_time

def calculate_order_duration(order_items, recipes):
    if recipes is None:
        print("Recipes data is None!")
        return 0
    
    total_duration = 0
    for item in order_items:
        for recipe in recipes:
            if recipe['product_id'] == item['id']:
                for step in recipe['steps']:
                    total_duration += step['duration_minutes'] * item['quantity']
    return total_duration
