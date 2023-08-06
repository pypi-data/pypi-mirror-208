'''
This module contains several self-contained functions for general purposes
'''

def disable_widget(widgets):
    for widget in widgets:
        if widget:
            widget.setEnabled(False)   

def enable_widget(widgets):
    for widget in widgets:
        if widget:
            widget.setEnabled(True)  

def convert_fraction_to_float(fraction):
    #code adapted from https://stackoverflow.com/questions/1806278/convert-fraction-to-float
    try:
        return float(fraction)
    except ValueError:
        num, denom = fraction.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac

def check_list_is_valid_formula(formula,valid_variable_names):
    flag = 1
    msg = ''
    for elem in formula:
        if type(elem) == str:
            if not ((elem in valid_variable_names) or (elem in ['+','-','*','/'])):
                flag = 0
                msg = "One of the elements ('" + elem + "') of the list is neither a valid data name (in the format dev#.DataName) nor a valid mathematical operation ('+', '-', '*', '/')"
                break
        elif isinstance(elem, list):
            msg, flag = CheckListIsValidFormula(elem,valid_variable_names)
        else:
            flag = 0
            msg = 'One of the elements of the list is neither a string nor a list'
            break
    return msg, flag

def evaluate_formula(formula,variables):
    #formula is a structured list
    #variabes is a dictionary of "NameVariable":ValueVariable
    value = 0
    op = '+'
    for elem in formula:
        if elem in ['+','-','*','/']:
            op = elem
        else: 
            if isinstance(elem, list):
                NewValue = evaluate_formula(elem,variables)
            else:
                NewValue =  variables[elem]
            value = operation(value,NewValue,op)
    return value

def operation(Value1,Value2,op):
    if op == '+':
        Value = Value1 + Value2
    if op == '*':
        Value = Value1 * Value2
    if op== '-':
        Value = Value1 - Value2
    if op == '/':
        try:
            Value = Value1 / Value2
        except ZeroDivisionError:
            Value = float('nan') 
    return Value