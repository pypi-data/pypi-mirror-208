from pywebgo import utils
from typing import Callable
from selenium.webdriver.remote.webelement import WebElement

#     Specifications

#     'loc':        [Type: String] Locator of an element,
#     'value':      [Type: String] Value of the locator,
#     'action':     [Type: String] Action to be performed on the element,
#     'page':       [Type: Int] URL index of the element,
#     'rank':       [Type: Int] Position of execution of the element,
#     'action':     [Type: String/Function] Action or actions to be performed on the element,
#     'keys':       [Type: String] Keys to be sent if any,
#     'retrieve':   [Type: String/Function] Retrieve any data_keys from the element,
#     'window':     [Type: Int] Window on which the element is located,
#     'wait':       [Type: Float] Delay (in seconds) before the action is performed,
#     'custom':     [Type: Function] Custom function passed to overwrite webcontrol process for the element,
#     'copy':       [Type: Int] Index of the element to copy attributes from (only previous elements)


class ElementsHandler:

    def __init__(self):
        """
        Create private variables and initialize the handler.

        elements: Stores all the element dicts created.
        element_objects: Stores all the selenium element objects found.
        """
        self.elements = []
        self.element_objects = []

    def add_element_from_list(self, loc: str, value: str, page: int = 0, rank: int = None, action: str = None,
                              keys: str = None, retrieve: str = None, window: int = 0, wait: float = 0,
                              custom: Callable = None, copy: int = None):
        """
        Add an element to elements from a given list object.

        :param loc: locator
        :param value: locator value
        :param page: page index
        :param rank: rank index
        :param action: Action keyword
        :param keys: Keys to send
        :param retrieve: Data to retrieve
        :param window: window index
        :param wait: Wait before an action in seconds
        :param custom: Custom function to overwrite webcontrol
        :param copy: Inherit key:value pairs from an element
        """

        element = {
            'loc': loc,
            'value': value,
            'page': page,
            'rank': rank or len(self.elements),
            'action': action,
            'keys': keys,
            'retrieve': retrieve,
            'window': window,
            'wait': wait,
            'custom': custom,
            'copy': copy
        }
        self.elements.append(element)

    def add_element_from_dict(self, element: dict):
        """
        Add an element to elements.

        :param element: dict to append to elements
        """

        # Inherit src_element attributes if copy exists in element
        if 'copy' in element:
            src_element = self.elements[element['copy']]
            element = utils.copy_element(src_element, element)
            element.pop('rank')  # Do not inherit rank

        # Function to check if a key exists in element
        check_key = lambda key, default: element[key] if key in element else default

        # Create element dict from element
        element = {
            'loc': check_key('loc', None),  # Locator (str)
            'value': check_key('value', None),  # Locator value (str)
            'page': check_key('page', 0),  # Page index (int)
            'rank': check_key('rank', len(self.elements)),  # Rank index (int)
            'action': check_key('action', None),  # Action keyword (str, function)
            'keys': check_key('keys', None),  # Keys to send (str)
            'retrieve': check_key('retrieve', None),  # Data to retrieve (str, function)
            'window': check_key('window', 0),  # Window index (int)
            'wait': check_key('wait', 0),  # Wait before an action in seconds (float)
            'custom': check_key('custom', None),  # Custom function to overwrite webcontrol defaults (function)
            'copy': check_key('copy', None)  # Inherit attributes from a previous WebElement (function)
        }

        # Append the element object to elements
        self.elements.append(element)

    def add_element(self, element):

        # Check if current element is of type dict
        if isinstance(element, dict):
            self.add_element_from_dict(element)

        # Check if current element is of type list
        elif isinstance(element, list):
            self.add_element_from_list(*element)

    def create_elements(self, elements: list | dict):
        """
        Create and add elements from a list of lists or dictionaries.

        :param elements: list containing elements
        """
        for element in elements:
            self.add_element(element)

    def get_elements(self):
        """
        Returns the elements created in the current instance of the class.

        :return: ElementsHandler.elements
        """
        return self.elements

    def set_elements(self, elements):
        """
        Sets the elements in the current instance of the class.

        :param list elements:
        """
        self.elements = elements

    def sort_elements_by_rank(self):
        """
        Sorts all the elements with their rank and updates elements class variable.

        """
        self.elements = sorted(self.elements, key=lambda element: element['rank'])

    def store_web_element(self, web_element: WebElement):
        """
        Stores the given element_object object in element_objects class variable.

        :param web_element: selenium.webdriver.remote.webelement.WebElement
        """
        self.element_objects.append(web_element)
