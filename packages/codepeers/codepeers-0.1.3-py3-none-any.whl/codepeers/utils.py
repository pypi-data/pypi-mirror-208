def extract_dict_keys(d, *keys):
    return {k: d[k] for k in keys if k in d}
