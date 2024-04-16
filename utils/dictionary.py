
def remove_empty_values(dict) -> dict:
    keys_to_remove=[]

    for key, value in dict.items():
        if not value:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        dict.pop(key)
    return dict
