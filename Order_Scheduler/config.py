# config.py
DELIVERY_ESTIMATE = {
    'normal': {'car': 3, 'motorbike': 2},  # delivery time in days for different modes of transport
    'traffic': {'car': 5, 'motorbike': 4}  # delivery time in days during heavy traffic
}

PREP_TIME = {
    'cookies': 0.5,  # time in hours required for preparing cookies
    'brownies': 0.8,  # time in hours required for preparing brownies
    'bread': 8,  # time in hours required for preparing bread (including rest time)
    # add more items and their respective preparation times as needed
}

bakery_timings = {
    'start_time': 9,  # bakery opens at 9am
    'end_time': 18,  # bakery closes at 6pm
    'pickup_start': 9,  # earliest pickup time is 9am
    'pickup_end': 17.5,  # latest pickup time is 5:30pm
    'first_delivery': 10,  # first delivery at 10am
    'last_delivery': 20  # last delivery by 8pm
}
