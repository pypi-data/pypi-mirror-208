class DataHandler:

    def __init__(self):
        self.database = []

    def add_data(self, elem_index, data_type, data):
        """

        :param elem_index:
        :param data_type:
        :param data:
        """
        data_dict = {
            "element": elem_index,
            "type": data_type,
            "data-keys": data
        }
        self.database.append(data_dict)

    def get_element_data(self, element_index):
        """

        :param element_index:
        :return:
        """
        return self.database[element_index]['data_keys']

    def retrieve_data(self):
        """

        :return:
        """
        return self.database
