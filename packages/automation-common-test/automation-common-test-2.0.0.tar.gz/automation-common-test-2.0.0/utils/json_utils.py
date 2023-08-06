import json
import logging

data_path = None
dic_data = None
modify_data = dict()

# set the path of test data and update the dictionary
def set_data_path(file_path):
    global data_path
    data_path = file_path
    global dic_data
    dic_data = get_json_object(data_path)
    logging.info(f"Dic DFata{dic_data}")
    if type(modify_data) == dict and len(modify_data.items()):
        modify_main_dict_value_param()
def modify_parameter(param):
    global modify_data
    modify_data = param

        
# def get_json_object(file_path):
#     return open(file_path, 'rb')
def get_json_object(file_path):
    with open(file_path, 'r') as f:
        distros_dict = json.load(f)
    return distros_dict

def get_json_dict(file_path):
    logging.info(file_path)
    with open(file_path, 'r') as f:
        distros_dict = json.load(f)
    return distros_dict

def modify_main_dict_value_param():
    for modify_key, modify_value in modify_data.items():
        key_found = search_dict_key(dic_data, modify_key)
        if key_found:
            dic_data[modify_key] = modify_value


# Search a given key inside dictionary recursively
def search_dict_key(target_dict, search_key):
    for key, value in target_dict.items():
        if key == search_key and type(value) == dict:
            return target_dict[key]
        elif key == search_key:
            return True
        elif type(value) == dict:
            key_found = search_dict_key(target_dict[key], search_key)
            if key_found:
                return key_found
    return None

def parse_json_recursively(json_object, target_key):
    my_dict = {}
    if type(json_object) is dict and json_object:
        for key in list(json_object.keys()):
            if key == target_key:
                my_dict[key] = json_object[key]
            parse_json_recursively(json_object[key], target_key)
    elif type(json_object) is list and json_object:
        for item in json_object:
            parse_json_recursively(item, target_key)

    return my_dict


def fetch_data(target_key, nested_dictionary):
    if type(nested_dictionary) is list and nested_dictionary:
        for item in nested_dictionary:
            if type(item) is dict and item:
                for x in item:
                    if x == target_key:
                        print(item[x])
                        return item[x]
            else:
                return nested_dictionary[target_key]
    else:
        for key, dic_value in nested_dictionary.items():
            if type(dic_value) is dict and dic_value:
                if key == target_key:
                    return dic_value
            if type(dic_value) is dict and dic_value:
                for x in dic_value:
                    if x == target_key:
                        return dic_value[x]
            elif type(dic_value) is str and dic_value:
                for key_string, value_string in nested_dictionary.items():
                    if key_string == target_key:
                        return value_string
                return None
        return dic_value


def get_data(target_key, nested_dictionary=None):
    global dic_data
    if dic_data is None and nested_dictionary is None:
        dic_data = get_json_object(data_path)
    if nested_dictionary:
        test_data = fetch_data(target_key, nested_dictionary)
        return test_data
    if dic_data:
        test_data = fetch_data(target_key, dic_data)
        return test_data


def get_value(json_object, exp_key, similar=False):
    for key, data in json_object.items():
        if (key.lower() == exp_key.lower() or (exp_key.lower() in key.lower() and similar)) and type(
                data) == dict and data.get('value'):
            # Skip the value and return None if flag is true
            if data.get('skip_value'):
                return None
            return data.get('value')
        # Handling for Empty json objects in data file
        elif type(data) == dict and len(data):
            aux_value = get_value(data, exp_key)
            if aux_value is not None:
                return aux_value
    return None
