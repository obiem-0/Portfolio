from flask import Flask, render_template, jsonify 
import json

from scheduler import calculate_order_schedule, load_data_from_json


app = Flask(__name__)

# Route for serving HTML template
@app.route('/')
def index():
    orders = load_data_from_json('./orders.json')['orders']
    recipes = load_data_from_json('./recipes.json') ['recipes']
    products = load_data_from_json('./products.json') ['products']
    calculate_order_schedule(orders, recipes)
    return render_template('dashboard.html', orders=orders, products=products)


@app.route('/schedule')
def schedulepage():
    schedule = load_data_from_json('./schedule.json')
    return render_template('schedule.html', schedule=schedule)
    

# Route for serving JSON data
@app.route('/data', methods=['GET'])
def get_data():
    orders = load_data_from_json('orders.json')['orders']
    recipes = load_data_from_json('recipes.json') ['recipes']
    products = load_data_from_json('products.json') ['products']
    calculate_order_schedule(orders, recipes)
    return jsonify(orders=orders, products=products)  # Return JSON data using jsonify


if __name__ == '__main__':
    app.run(debug=True)
