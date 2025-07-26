# g_vars

_global = {
    "mailto": None,
    "value": None,
    "other": None
}

def set_var(name, value):
    _global[str(name)] = value

def get_var(name):
    return _global.get(name)

def all_vars():
    return dict(_global)  # devuelve una copia







