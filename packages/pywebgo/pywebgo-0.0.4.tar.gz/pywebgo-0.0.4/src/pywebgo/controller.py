import re
import time
from pywebgo import utils
from .data import DataHandler
from .elements import ElementsHandler
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains


class WebController(webdriver.Chrome):
    """
    Implements search, action execution and data retrieval successively for given element dictionaries.

    Inherits from *selenium.webdriver.Chrome*

    Attributes:
    - :class:`list` urls --> non-linked web pages to traverse through
    - :class:`bool` teardown --> closes the browser after execution if true
    - :class:`float` wait --> time delay for executing each action
    - :class:`ElementsHandler` elem_handler --> instance of ElementsHandler class to manage elements
    - :class:`DataHandler` data_handler --> instance of DataHandler class to manage data associated with the elements
    """

    def __init__(self, urls: list, teardown: bool = True, wait: float = 0, options: list = None):
        """
        Initialize a new instance of the WebController class.

        :param urls: non-linked web pages to traverse through
        :param teardown: closes the browser after execution if true
        :param wait: time delay for executing each action
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
        if options:
            for option in options:
                chrome_options.add_argument(option)

        super(WebController, self).__init__(chrome_options=chrome_options)

        # ---- Private Variables ----- #
        self.urls = urls
        self.wait = wait
        self.teardown = teardown
        self.elem_handler = ElementsHandler()
        self.data_handler = DataHandler()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context related to this object.

        :param exc_type: exception type if any
        :param exc_val: exception value if any
        :param exc_tb: exception traceback if any
        """
        if self.teardown:
            self.quit()

    def append_urls(self, urls: list) -> None:
        """
        Append the given list of urls to WebController.urls.

        :param urls: urls to traverse through
        """
        self.urls += urls

    def create_elements(self, elements: list | dict) -> None:
        """
        Create and store elements in ElementsHandler from the given list of dictionaries/lists.

        :param elements: elements dict/list to create elements list from
        """
        self.elem_handler.create_elements(elements)

    def execute_actions(self, web_element: WebElement, element: dict) -> None:
        """
        Execute all the actions associated with the given element.

        :param web_element: selenium WebElement object for the element passed
        :param element: contains all the relevant information related to the element
        """
        # Exit if action does not exist
        if not element['action']:
            return

        # Only run wait_for_all_actions if an action has no wait
        if not self.wait_for_action(element):
            self.wait_for_all_actions()

        # Call the action if it is a function
        if callable(element['action']):
            element['action'](self, element)
            return

        # Get the next action and recurse the function
        next_action_match = re.search(r'(?<= )(.*)', element['action'])
        if next_action_match:
            element_copy = element.copy()
            element_copy['action'] = next_action_match.group()
            self.execute_actions(web_element, element_copy)

        # Get the current action and execute it
        this_action_match = re.search(r'^\S+', element['action'])
        if this_action_match:
            this_action = this_action_match.group()
            if this_action == 'send-keys':
                web_element.send_keys(element['keys'])
                return
            if this_action == 'select':
                Select(web_element).select_by_visible_text(element['keys'])
            self.perform_action_chains(this_action, web_element)

    def execute_operations(self, timeout: float = 20) -> None:
        """
        Execute all the operations associated with the current WebController object.

        :param timeout: time before throwing exception if the element is not found
        """
        # Load the first url
        start_url = self.urls[0]
        self.load_page(start_url)
        for element in self.elem_handler.elements:
            index = self.elem_handler.elements.index(element)
            # Switch window if the element is located in a different window
            self.switch_window(element)
            # Call the custom function if it exists
            if callable(element['custom']):
                element['custom'](self, element)
                continue
            web_element = self.get_element(element, timeout)
            self.elem_handler.store_web_element(web_element)
            self.retrieve_data(web_element, element)
            self.execute_actions(web_element, element)
            self.load_next_page(index)

    def get_active_element(self, timeout):
        """
        Switch to and return the active web element object.

        :param timeout: time before throwing exception if the element is not found
        :return: active web element
        """
        active_element = self.switch_to.active_element
        self.wait_for_element_visibility(active_element, timeout)
        return active_element

    def get_element(self, element: dict, timeout: float) -> WebElement:
        """
        Get the WebElement from the given element dict using the 'loc' and 'value' keys

        :param timeout: time before throwing exception if the element is not found
        :param element: a dictionary containing WebElement specifications
        :return: a WebElement corresponding to the given element dict
        """

        # If locator is active, get the active element
        if element['loc'] == 'active':
            return self.get_active_element(timeout)

        # Get element identifiers
        identifiers = utils.get_element_identifiers(element)
        strategy, locator, index = identifiers.values()
        self.wait_for_element_load(element, timeout)
        if index:
            return self.find_elements(strategy, locator)[int(index)]
        return self.find_element(strategy, locator)

    def get_page_html(self, url: str = None) -> str:
        """
        Retrieve and return the HTML of the current page or from a given url.

        :param url: URL of a web page
        :return: requested HTML of a web page
        """
        if url:
            self.load_page(url)
        return self.page_source

    def load_page(self, url: str) -> None:
        """
        Load the web page from the given URL.

        :param url: URL of the web page to be loaded
        """
        self.get(url)

    def load_next_page(self, curr_elem_index: int) -> None:
        """
        Load the web page at the next URL in the url list.

        :param curr_elem_index: index of the current element
        """
        last_elem_index = len(self.elem_handler.elements) - 1
        if curr_elem_index != last_elem_index:
            curr_elem, next_elem = utils.get_successive_elements(self.elem_handler.elements, curr_elem_index)
            if curr_elem['page'] != next_elem['page']:
                self.load_page(self.urls[next_elem['page']])

    def perform_action_chains(self, action_label: str, web_element: WebElement) -> None:
        """
        Perform actions on the given element using the action_label string.

        :param action_label: action/actions to perform
        :param web_element: element to perform action on
        """
        action_chains = ActionChains(self)
        action_options = {
            'click': action_chains.click,
            'dbl-click': action_chains.double_click,
            'click-hold': action_chains.click_and_hold,
            'release': action_chains.release,
            'hover': action_chains.move_to_element
        }
        action = utils.match_label(action_label, action_options)
        action(web_element).perform()

    def retrieve_data(self, web_element: WebElement, element: dict) -> None:
        """
        Retrieve the requested data_keys from the WebElement object specified in the element

        :param web_element: element object
        :param element: dictionary containing element specifications
        """
        if not element['retrieve']:
            return

        if callable(element['retrieve']):
            element['retrieve'](self, element)
            return

        retrieve = element['retrieve']
        retrieve_options = {
            'text': web_element.text,
            'tag': web_element.tag_name,
            'aria-role': web_element.aria_role,
            'id': web_element.id,
            'location': web_element.location,
            'accessible-name': web_element.accessible_name
        }
        element_data = utils.match_label(retrieve, retrieve_options)
        attribute = re.search('^attr', element['retrieve'])

        if attribute:
            self.get_element_attribute(element, web_element)

        if element_data:
            index = self.elem_handler.elements.index(element)
            self.data_handler.add_data(index, element['retrieve'], element_data)

    @staticmethod
    def get_element_attribute(element: dict, web_element: WebElement) -> str:
        """
        Return the requested attribute value for a given element.

        :param element: a dictionary containing WebElement specifications
        :param web_element: element object
        :return: requested attribute value of a given element
        """
        regex_str = r'(?<=\[)(.*?)(?=])'
        attr_val = re.search(regex_str, element['retrieve']).group()
        return web_element.get_attribute(attr_val)

    def switch_window(self, element: dict) -> None:
        """
        Switch the window if the current element is located on a different window.

        :param element: a dictionary containing WebElement specifications
        """
        window_index = element['window']
        dest_window = self.window_handles[window_index]
        self.switch_to.window(dest_window)

    @staticmethod
    def wait_for_action(element: dict) -> bool:
        """
        Wait (in seconds) before executing a particular action.

        :param element: dictionary containing element specifications
        :return: true if the action is delayed
        """
        if element['wait']:
            time.sleep(element['wait'])
            return True

    def wait_for_all_actions(self) -> None:
        """
        Wait (in seconds) for a certain period for all actions.
        """
        if self.wait:
            time.sleep(self.wait)

    def wait_for_element_load(self, element: dict, timeout: float) -> None:
        """
        Implicitly wait for an element to load.

        :param element: dictionary containing element specifications
        :param timeout: time before throwing exception if the element is not found
        """
        wait = WebDriverWait(self, timeout)
        identifiers = utils.get_element_identifiers(element)
        (strategy, locator) = (identifiers['strategy'], identifiers['locator'])
        wait.until(expected_conditions.presence_of_element_located((strategy, locator)))

    def wait_for_element_visibility(self, element: dict | WebElement, timeout: float) -> None:
        """
        Implicitly wait for an element to become visible.

        :param element: dictionary containing element specifications
        :param timeout: time before throwing exception if the element is not found
        """
        wait = WebDriverWait(self, timeout)
        if isinstance(element, WebElement):
            wait.until(expected_conditions.visibility_of(element))
        else:
            identifiers = utils.get_element_identifiers(element)
            (strategy, locator) = (identifiers['strategy'], identifiers['locator'])
            wait.until(expected_conditions.visibility_of_element_located((strategy, locator)))

    def element_exists(self, element, wait=0) -> bool:
        """
        Check if an element exists.

        :param element: dictionary containing element specifications
        :param wait:
        :return:
        """
        try:
            identifiers = utils.get_element_identifiers(element)
            (strategy, locator) = (identifiers['strategy'], identifiers['locator'])
            time.sleep(wait)
            self.find_element(strategy, locator)
        except NoSuchElementException:
            return False
        return True

    def run_controller(self, elements: list, timeout: float = 20) -> None:
        """
        Runs the controller to initiate the execution of the operations.

        :param timeout:
        :param elements: elements to interact with
        """
        self.create_elements(elements)
        self.elem_handler.sort_elements_by_rank()
        self.execute_operations(timeout=timeout)
