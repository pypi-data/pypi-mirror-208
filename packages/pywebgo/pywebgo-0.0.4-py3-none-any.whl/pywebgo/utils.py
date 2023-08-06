import re
from typing import Callable
from selenium.webdriver.common.by import By


def copy_element(src_element: dict, dest_element: dict) -> dict:
    """
    Inherit key:value pairs from src_element to dest_element without overwrite.

    :param src_element: Source dict to inherit from
    :param dest_element: Destination dict to inherit to
    :return: Merged copy of the src_element updated with dest_element.
    """
    src_copy = src_element.copy()
    src_copy.update(dest_element)
    return src_copy


def match_label(label: str, options: dict) -> str | Callable:
    """
    Find and return the value of label key in options.

    :param label: value to search for
    :param options: dict object to search through
    :return: value of the label key in options
    """
    cases = list(options.keys())
    for case in cases:
        if label == case:
            return options[case]


def make_options(cases: list, labels: list) -> dict:
    """
    Create key value pairs for the given lists

    :param cases: keys to put into the dict
    :param labels: values to put with keys
    :return: dict of options
    """
    return {cases[i]: labels[i] for i in range(len(cases))}


def get_strategy_options() -> dict:
    """
    Return strategy options.

    :return: strategy dictionary containing strategy identifiers
    """
    return {
        'id': By.ID,
        'name': By.NAME,
        'class': By.CLASS_NAME,
        'css': By.CSS_SELECTOR,
        'tag': By.TAG_NAME,
        'xpath': By.XPATH
    }


def get_successive_elements(elements: dict, index: int) -> tuple:
    """
    Return successive elements given at the index from elements list.

    :param elements: elements passed to the WebController
    :param index: index of the element to retrieve
    :return: current element and the successor element
    """
    return elements[index], elements[index + 1]


def get_element_identifiers(element: dict) -> dict:
    """
    Return element identifiers used to retrieve a web element object.

    :param element: element dict containing its identifiers
    :return: dict containing element identifiers
    """
    locator = element['value']
    strategy, index = strip_element_index(element)
    strategy = match_label(strategy, get_strategy_options())
    return {'strategy': strategy, 'locator': locator, 'index': index}


def strip_element_index(element: dict) -> tuple:
    """
    Return the locator of the element and its index.

    :param element: element dict containing its locator
    :return: locator of the element passed and its index (if exists)
    """
    regex_str = r'(?<=\[)(.*?)(?=])'
    index_search = re.search(regex_str, element['loc'])
    if index_search:
        index = index_search.group()
        strategy = element['loc'].replace(f'[{index}]', '')
        return strategy, index
    return element['loc'], None

