from py_parser import get_functions_in_main
from pprint import pprint


def reformat_tool_name_for_template(refer_tool_name):
    return refer_tool_name


def reformat_module_name_for_template(refer_module_name):
    return refer_module_name


def reformat_function_name_for_template(refer_function_name):
    return refer_function_name


def reformat_function_arguments_for_template(refer_arguments_list):
    reformat_function_arguments = ""
    for i in range(len(refer_arguments_list)):
        reformat_function_arguments += refer_arguments_list[i]
        if i != len(refer_arguments_list) - 1:
            reformat_function_arguments += ","
    return reformat_function_arguments


def reformat_function_returned_for_template(refer_returned_list):
    reformat_function_returned = ""
    for i in range(len(refer_returned_list)):
        reformat_function_returned += refer_returned_list[i]
        if i != len(refer_returned_list) - 1:
            reformat_function_returned += ","
    return reformat_function_returned


def reformat_function_data_sources_for_template(refer_data_sources_list):
    reformat_function_data_sources = ""
    for i in range(len(refer_data_sources_list)):
        reformat_function_data_sources += refer_data_sources_list[i]
        if i != len(refer_data_sources_list) - 1:
            reformat_function_data_sources += ","
    return reformat_function_data_sources


def main(tool_name, data_soruces_list):
    template = "import pandas as pd\n" \
               "from {}.{} import {}\n" \
               "{} = {}({})\n"

    module_list = get_functions_in_main(tool_name)

    tool_name_in_template = reformat_tool_name_for_template(tool_name)

    pprint(module_list)

    for module in module_list:

        module_name = module['module_name']
        module_name_in_template = reformat_module_name_for_template(module_name)

        module_FARs = module['FARs']

        if not module_FARs:
            continue

        for function in module_FARs:
            function_name = function['function']
            function_name_in_template = reformat_function_name_for_template(function_name)

            function_arguments = function['args']
            function_arguments_in_template = reformat_function_arguments_for_template(function_arguments)

            function_data_sources = data_soruces_list
            function_data_sources_in_template = reformat_function_data_sources_for_template(function_data_sources)

            function_returned = function['returned']
            function_returned_in_template = reformat_function_returned_for_template(function_returned)

            fill = (
                template.format(tool_name_in_template,
                                module_name_in_template,
                                function_name_in_template,
                                function_returned_in_template,
                                function_name_in_template,
                                function_data_sources,
                                function_returned_in_template)
            )
            expression = exec(fill, globals(), locals())

            for returned in function_returned:
                print(locals().get(returned))
