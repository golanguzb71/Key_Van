import random


def find_key_by_value(redis_client, search_value):
    for key in redis_client.scan_iter():
        value = redis_client.get(key)
        if value == str(search_value):
            return key
    return None


def generate_code():
    return random.randint(10000, 99999)

