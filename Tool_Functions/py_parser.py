import ast
import os
from ast import FunctionDef, Return, Tuple, List
from pprint import pprint

'''
def string_handler(value):
    return str(value)


def int_handler(value):
    return int(value)


def float_handler(value):
    return float(value)


def bool_handler(value):
    return bool(value)


def csv_handler(value):
    pd_object = pd.read_csv(value)
    return pd_object


def json_handler(value):
    pd_object = pd.read_json(value)
    return pd_object


# map the inputs to the function blocks
options = {"string": string_handler,
           "int": int_handler,
           "float": float_handler,
           "bool": bool_handler,
           "csv": csv_handler,
           "json": json_handler
           }


class ObjectTypeDetermine(object):
    object_value = None
    object_type = None

    def __init__(self, object_value):
        self.object_value = object_value

    def __format__(self, object_type):
        self.object_type = object_type
        object_keyword = self.object_type.lower()

        return options[object_keyword](self.object_value)

'''


def form_absolute_path(tool_folder_name):
    # prefix = "/home/hao/Downloads/"
    prefix = "./"
    tool_folder_absolute_path = prefix + tool_folder_name

    return tool_folder_absolute_path


def read_script_into_string(filename):
    data = None

    with open(filename, 'r') as f:
        data = f.read()
    f.close()

    assert data is not None, "Open file failed.\n"

    return data


def print_function_arg_returned_names(filename):
    expr = read_script_into_string(filename)
    p = ast.parse(expr)

    # print parse tree
    pprint(ast.dump(p))

    function_list = []

    for node in p.body:

        function_attribute_dict = {}

        # find defined function in script
        if isinstance(node, FunctionDef):
            print("Function Name:")
            print(node.name)

            function_attribute_dict["function"] = node.name

            function_arguments_list = []
            for arg in node.args.args:
                print("Function Arguments:")
                print(arg.arg)

                function_arguments_list.append(arg.arg)

            function_attribute_dict["args"] = function_arguments_list
            # print()

            function_body = node.body

            function_returned_list = []
            print("Function Returned:")
            for body_node in function_body:
                if isinstance(body_node, Return):

                    returned_type = body_node.value

                    # if there are multiple returned parameters
                    if isinstance(returned_type, (Tuple, List)):
                        returned_vars_list = returned_type.elts
                        returned_vars_names_list = ["returned_" + str(i) for i in range(len(returned_vars_list))]
                        print(returned_vars_names_list)

                    # if there is one returned parameter
                    else:
                        returned_vars_names_list = ["returned_0"]
                        print(returned_vars_names_list)

                    function_returned_list = returned_vars_names_list

            function_attribute_dict["returned"] = function_returned_list

            function_list.append(function_attribute_dict)
            print()

    return function_list

    # if isinstance(returned_type, Name):
    #    returned_var = returned_type.id

    #    print(returned_var)
    #    function_returned_list.append(returned_var)

    # elif isinstance(returned_type, Str):

    #    returned_string = "'" + returned_type.s + "'"
    #    print(returned_string)

    #    function_returned_list.append(returned_string)

    # elif isinstance(returned_type, Call):
    # Call.func = Function Attribute
    #    returned_function_attribute = returned_type.func

    ## value.Name.id
    #    returned_function_attribute_name = returned_function_attribute.value.id
    #    returned_function_attribute_attr = returned_function_attribute.attr

    # Call.args = FUnction Args
    #    returned_function_args = returned_type.args

    # Call.keywords = FUnction Keywords
    #    returned_function_keywords = returned_type.keywords

    # start to concate returned function call body
    #    returned_function_call = ""
    #    returned_function_call += returned_function_attribute_name

    #    if returned_function_attribute_attr != "" and returned_function_attribute_attr is not None:
    #        returned_function_call += "."
    #        returned_function_call += returned_function_attribute_attr

    #   returned_function_args_and_keywords = ""

    #   if returned_function_args:
    #       pass

    #   if returned_function_keywords:
    #       pass

    #   returned_function_args_and_keywords = "(" + returned_function_args_and_keywords + ")"

    #   returned_function_call += returned_function_args_and_keywords

    #   print(returned_function_call)
    #   function_returned_list.append(returned_function_call)

    # else:
    #   print("Uncaught returned variable type")


def get_functions_in_main(tool_folder_name):
    module_list = []

    tool_folder_absolute_path = form_absolute_path(tool_folder_name)

    for root, dirs, files in os.walk(tool_folder_absolute_path, topdown=True):

        for filename in files:

            module_dictionary = {}

            filename_componenet_list = filename.split(".")

            name_prefix = filename_componenet_list[0]
            type_suffix = filename_componenet_list[1]

            # if name_prefix.lower() == "main" and type_suffix.lower() == "py":
            if type_suffix.lower() == "py":
                script_absolute_path = tool_folder_absolute_path + '/' + filename

                tool_functions_args_returns_list = print_function_arg_returned_names(script_absolute_path)

                module_dictionary["module_name"] = name_prefix
                module_dictionary["FARs"] = tool_functions_args_returns_list

                module_list.append(module_dictionary)

    return module_list
