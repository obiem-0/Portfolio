from datetime import datetime, timedelta
import json

# Constants for bakery timings and modes of transport
class BakeryTimings:
    MAN_OP_START = 7  # 7am
    MAN_OP_END = 19   # 7pm
    OPENING_TIME = 9  # 9am
    CLOSING_TIME = 18 # 6pm
    PICKUP_START_TIME = 9 # 9am
    PICKUP_END_TIME = 17 * 60 + 30  # 5:30pm represented in minutes
    DELIVERY_START_TIME = 10  # 10am
    DELIVERY_END_TIME = 19  # 7pm
    OVEN_REST_TIME = 30 # 30 minutes
    
class ModesOfTransport:
    CAR = 1.5 # Example: 1.5 hours for delivery by car
    MOTORBIKE = 1 # Example: 1 hour for delivery by motorbike

class ItemSchedule:
    def __init__(self, item_id, start_time, finish_time, duration, steps):
        self.item_id = item_id
        self.start_time = start_time
        self.finish_time = finish_time
        self.duration = duration
        self.steps = steps

def load_data_from_json(file_path):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def find_recipe(item_id, recipes):
    for rec in recipes:
        if rec.get('product_id') == item_id:
            return rec
    return None


def calculate_delivery_windows(order, earliest_ready_time, latest_ready_time):
    # Calculate delivery and pickup time windows based on earliest and latest ready times
    delivery_time = datetime.strptime(order['request_delivery_date'], '%Y-%m-%d %H:%M:%S')
    transport_mode = order.get('transport_mode', 'car')
    transport_time = getattr(ModesOfTransport, transport_mode, 1)

    
    # ensures that earliest_delivery is not earlier than the bakery's opening time (BakeryTimings.OPENING_TIME) on the same day as the order's requested delivery date.
    earliest_delivery = max(earliest_ready_time, datetime(delivery_time.year, delivery_time.month, delivery_time.day, BakeryTimings.OPENING_TIME))
    
    # ensures that earliest_delivery is not earlier than the bakery's delivery start time (BakeryTimings.DELIVERY_START_TIME) on the same day as the order's requested delivery date.
    earliest_delivery = max(earliest_delivery, datetime(delivery_time.year, delivery_time.month, delivery_time.day, BakeryTimings.DELIVERY_START_TIME))
    
    # This line calculates the latest possible delivery time for an order, taking into account the closing time of the bakery and the time it takes for transportation.
    max_delivery_time = min(datetime(delivery_time.year, delivery_time.month, delivery_time.day, BakeryTimings.CLOSING_TIME) - timedelta(hours=transport_time), delivery_time)

    
    # Initialize latest_delivery before the loop
    # selects the earlier time between this maximum and the bakery's delivery end time, ensuring the delivery falls within these constraints.
    latest_delivery = min(max_delivery_time, datetime(delivery_time.year, delivery_time.month, delivery_time.day, BakeryTimings.DELIVERY_END_TIME))

    # Ensure that earliest_delivery is less than latest_delivery by at least the transport mode duration
    while earliest_delivery >= latest_delivery:
        earliest_delivery -= timedelta(minutes=1)

    earliest_pickup = max(earliest_delivery, datetime(delivery_time.year, delivery_time.month, delivery_time.day, BakeryTimings.PICKUP_START_TIME))
    pickup_end_time_minutes = BakeryTimings.PICKUP_END_TIME
    pickup_end_hour = pickup_end_time_minutes // 60
    pickup_end_minute = pickup_end_time_minutes % 60
    latest_pickup = min(latest_delivery, datetime(delivery_time.year, delivery_time.month, delivery_time.day, pickup_end_hour, pickup_end_minute))

    order['request_delivery_date'] = delivery_time.strftime('%Y-%m-%d %H:%M:%S')
    order['rdq'] = delivery_time.strftime('%d %b %Y, %H:%M')
    order['earliest_delivery'] = earliest_delivery.strftime('%d %b %Y, %H:%M')
    order['latest_delivery'] = latest_delivery.strftime('%d %b %Y, %H:%M')
    order['earliest_pickup'] = earliest_pickup.strftime('%d %b %Y, %H:%M')
    order['latest_pickup'] = latest_pickup.strftime('%d %b %Y, %H:%M')

def calculate_preparation_time(item, recipe):
    preparation_time = 0
    item_steps = []

    for step in recipe['steps']:
        step_duration = step['duration_minutes']
        step_duration_per_item = step_duration * item['quantity']
        item_steps.append({
            'step_name': step['description'],
            'step_duration': step_duration_per_item
        })
        preparation_time += step_duration_per_item

    return preparation_time, item_steps



def calculate_item_schedule(item, order_date, recipes):
    item_id = item['id']
    item_quantity = item['quantity']

    # Find the recipe to determine the manufacturing start and end dates
    recipe = find_recipe(item_id, recipes)
   
   

    if recipe:
        total_preparation_time, item_steps= calculate_preparation_time(item, recipe)
        item_duration = timedelta(minutes=total_preparation_time)

        # As a default, set the item start time as the order date. However, we'll need to add more logic here to take advantage of the items already scheduled.
        item_start_time = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')

        # Ensure items are ready 2 hours before the requested delivery time
        preparation_time_margin = timedelta(hours=2)

        # Calculate the earliest manufacturing start time considering bakery timings
        bakery_start_time = max(item_start_time, datetime(item_start_time.year, item_start_time.month, item_start_time.day, BakeryTimings.DELIVERY_START_TIME))
        bakery_end_time = datetime(item_start_time.year, item_start_time.month, item_start_time.day, BakeryTimings.MAN_OP_END)

        earliest_start_time = max(bakery_start_time, bakery_end_time - item_duration - preparation_time_margin)

        item_start_time = max(item_start_time, earliest_start_time)
        item_finish_time = item_start_time + item_duration

        total_preparation_time = max(total_preparation_time, item_duration.total_seconds() / 60)

        return ItemSchedule(item_id, item_start_time, item_finish_time, item_duration, item_steps)
    else:
        return None

 
def get_item_names(items, recipes):    
    for item in items:
        item['name'] = find_recipe(item['id'], recipes).get('product_name')
        
    return items
              
    

def calculate_order_schedule(orders, recipes):
    
    
    scheduled_orders = []

    for order in orders:
        item_schedules = []
        preparation_time_margin = timedelta(hours=2)

        # Initialize earliest_ready_time based on order_date
        earliest_ready_time = datetime.strptime(order['order_date'], '%Y-%m-%d %H:%M:%S')
        latest_ready_time = None
        
        order['items'] = get_item_names(order['items'], recipes)

        for item in order['items']:
            item_schedule = calculate_item_schedule(item, order['order_date'], recipes)
            

            if item_schedule:
                item_schedules.append(item_schedule)
                item_start_time, item_finish_time = item_schedule.start_time, item_schedule.finish_time

                # Update earliest_ready_time based on item_finish_time
                if item_finish_time > earliest_ready_time:
                    earliest_ready_time = item_finish_time

                if latest_ready_time is None or item_finish_time + preparation_time_margin > latest_ready_time:
                    latest_ready_time = item_finish_time + preparation_time_margin

        # Sort the item schedules based on finish times
        item_schedules.sort(key=lambda x: x.finish_time)

        calculate_delivery_windows(order, earliest_ready_time, latest_ready_time)

        item_start_times_str = {str(schedule.item_id): schedule.start_time.strftime('%d %b %Y, %H:%M') for schedule in item_schedules}
        item_finish_times_str = {str(schedule.item_id): schedule.finish_time.strftime('%d %b %Y, %H:%M') for schedule in item_schedules}

        try:
            order['earliest_ready_time'] = earliest_ready_time.strftime('%d %b %Y, %H:%M')
            order['latest_ready_time'] = latest_ready_time.strftime('%d %b %Y, %H:%M')
        except:
            order['earliest_ready_time'] = "N/A"
            order['latest_ready_time'] = "N/A"

        order['manufacturing_schedule'] = [{'item_id': str(schedule.item_id), 'steps': schedule.steps} for schedule in item_schedules]
        order['item_start_times'] = item_start_times_str
        order['item_finish_times'] = item_finish_times_str
        order['item_durations'] = {str(schedule.item_id): schedule.duration.total_seconds() for schedule in item_schedules}
        order['order_date'] =  datetime.strptime(order['order_date'], '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y, %H:%M')

        scheduled_orders.append(order)

    scheduled_orders = [order for order in scheduled_orders if 'earliest_ready_time' in order]
    scheduled_orders.sort(key=lambda x: x['earliest_ready_time'])
    
    
    json.dump(scheduled_orders, open('./schedule.json', 'w'))

    return scheduled_orders


     
if __name__ == "__main__":
  
        orders = load_data_from_json('./orders.json')['orders']
        recipes = load_data_from_json('./recipes.json')['recipes']

        scheduled_orders = calculate_order_schedule(orders, recipes)
        response_data = {'orders': scheduled_orders}
