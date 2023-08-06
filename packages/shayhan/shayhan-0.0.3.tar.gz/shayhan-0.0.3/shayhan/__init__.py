from prettytable import PrettyTable


def peek(variable_objects, limit=5, variable_names=None):
    """ This is function to print the type, shape, and value of a variable

    Args:
        variable_objects (any type): any type of variable
        limit (int, optional): The length of a variable. Defaults to 5.
    """
    variableTable = PrettyTable(["Variable","Type", "Shape", "Value"])
    if not isinstance(variable_objects, (list)):
        variable_objects = [variable_objects]
    variable_names= variable_names.split(',')
    
    i=0
    for variable_object in variable_objects:
#         variable_name = f"{variable_object=}".split("=")[0]
        short_data_type =f'{type(variable_object)}'.split("<class '")[1].split('.')[0]
        full_data_type = f'{type(variable_object)}'.split("<class '")[1].split("'")[0]
        variable_name = i if variable_names==None else variable_names[i]

        if isinstance(variable_object, (float, int, str,)):
            variableTable.add_row([variable_name, full_data_type, "1", variable_object], divider=True)        
        elif isinstance(variable_object, (list, dict, tuple, set)):
            variableTable.add_row([variable_name, full_data_type, len(variable_object), variable_object[:limit]], divider=True) 
        elif short_data_type == 'numpy': #type(value)==numpy.ndarray:
            import numpy
            variableTable.add_row([variable_name, full_data_type, variable_object.shape, variable_object[:limit] if variable_object.ndim==1 else variable_object[:limit,:limit]], divider=True)
        elif short_data_type == 'torch': 
            import torch
            variableTable.add_row([variable_name, full_data_type, variable_object.shape, variable_object[:limit] if variable_object.ndim==1 else variable_object[:limit,:limit]], divider=True)
        elif short_data_type == 'tensorflow': #type(value)==numpy.ndarray:
            import tensorflow
            variableTable.add_row([variable_name, full_data_type, variable_object.shape, variable_object[:limit,:limit].todense()], divider=True)
        elif short_data_type == 'scipy': #type(value)==numpy.ndarray:
            import scipy
            variableTable.add_row([variable_name, full_data_type, variable_object.shape, "-"], divider=True)
        else:
            variableTable.add_row([variable_name, type(variable_object), "-", "-"], divider=True)
        i=i+1
    print(variableTable)
    
def peek_no_division(variable_objects, limit=5):
    """ This is function to print the type, shape, and value of a variable

    Args:
        variable_objects (any type): any type of variable
        limit (int, optional): The length of a variable. Defaults to 5.
    """
    variableTable = PrettyTable(["Variable","Type", "Shape", "Value"])
    if not isinstance(variable_objects, (list)):
        variable_objects = [variable_objects]
    variable_names= variable_names.split(',')
    
    i=0
    for variable_object in variable_objects:
#         variable_name = f"{variable_object=}".split("=")[0]
        short_data_type =f'{type(variable_object)}'.split("<class '")[1].split('.')[0]
        full_data_type = f'{type(variable_object)}'.split("<class '")[1].split("'")[0]
        variable_name = i if variable_names==None else variable_names[i]

        if isinstance(variable_object, (float, int, str,)):
            variableTable.add_row([variable_name, full_data_type, "1", variable_object])        
        elif isinstance(variable_object, (list, dict, tuple, set)):
            variableTable.add_row([variable_name, full_data_type, len(variable_object), variable_object[:limit]]) 
        elif short_data_type == 'numpy': 
            import numpy
            variableTable.add_row([variable_name, full_data_type, variable_object.shape, variable_object[:limit] if variable_object.ndim==1 else variable_object[:limit,:limit]])
        elif short_data_type == 'torch': 
            import torch
            variableTable.add_row([variable_name, full_data_type, variable_object.shape, variable_object[:limit] if variable_object.ndim==1 else variable_object[:limit,:limit]])
        elif short_data_type == 'tensorflow': 
            import tensorflow
            variableTable.add_row([variable_name, full_data_type, variable_object.shape, variable_object[:limit,:limit].todense()])
        elif short_data_type == 'scipy': 
            import scipy
            variableTable.add_row([variable_name, full_data_type, variable_object.shape, "-"])
        else:
            variableTable.add_row([variable_name, type(variable_object), "-", "-"])
        i=i+1
    print(variableTable)