import datetime
import requests
import pandas as pd
import numpy as np
import itertools
from dateutil.relativedelta import relativedelta
from typing import Any, Union
from tqdm import tqdm


# pd.set_option('display.max_columns', None)
class API(object):
    """
    API manages connection and collection of Sustainalytics.

    Public Attributes
    -----------------
    client_id : str
        a special ID provided by sustainalytics to client for authentication and authorization
    client_secretkey : str
        a special key provided by sustainalytics to client for authentication and authorization
    access_headers : dict
        a dictionary managing the api tokens
    fieldIds : list
        a list of identifiers i.e. ISINs, CUSIPs, SEDOLs, Entity Ids(Sustainalytics).
    universe_of_access : dataframe/json
        a collection of EntityIds and universe the client can access.
    productIDs : list
        a list of productIds the client can access

    full_definition : dataframe/json
        a collection of the field definitions and more so product, package and cluster information

    Private Attributes
    ------------------
    __universe_entity_ids : list
        a list of entityIds the client can access

    Public Methods
    -----------------
    get_access_headers()
        returns the access and authorization token to the api.

    get_fieldIDs()
        :returns a list of fieldIds

    get_fieldsInfo(dtype=json)
        :returns a collection containing the fields information accessible to clients
    get_fieldDefinitions(dtype=json)
        :returns a collection of field definitions
    get_productIDs()
        :returns a list of product IDs
    get_productsInfo(dtype=json)
        :returns a collection of products information
    get_packageIDs()
        :returns a list of package IDs
    get_packageInfo(dtype=json)
        :returns a collection of package information
    get_fieldClusterIDs()
        :returns a list of field cluster IDs
    get_fieldClusterInfo(dtype=json)
        :returns a collection of field cluster information

    get_fieldMappings(dtype=json)
        :returns a collections of fieldId mappings to their descriptive information

    get_fieldMappingDefinitions(dtype=json)
        :returns a collection of the field mappings definitions.
    get_universe_access(dtype=json)
        :returns a collection of entity ids and universe access of an account
    get_universe_entityIDs(dtype=json)
        :returns a list of entityIds the client can access
    get_fullFieldDefinitions(dtype=json)
        :returns a collection of fieldDefinitions
    get_pdfReportService(dtype=json):
        :returns manages the pdf report generation.
    get_pdfReportInfo(dtype=json)
        :returns a collection of pdf information
    get_pdfReportUrl(identifier=None,reportId=None,dtype=json)
        :returns URL pdf link for an entityId and a reportId

    get_data(dtype=json)
        :returns a collections of sustainalytics data to the client.
    
    Private Methods
    --------------
    __process_fieldsdata(field):
        :returns a processed list of fieldIds
    --
    """

    def __init__(self, client_id, client_secretkey):
        """
        Initialize connection with the API with client id and client_secretkey
        :param client_id:
        :param client_secretkey:
        """
        self.client_id = client_id
        self.client_secretkey = client_secretkey
        self.access_headers = self.get_access_headers()
        self.fieldIds = None
        self.universe_of_access = None
        # self.productIDs = self.get_productIDs()
        # print(self.universe_of_access)
        # print(self.universe_of_access)
        self.__universe_entity_ids = None
        # full definition
        # self.full_definition = self.get_fullFieldDefinitions(dtype='dataframe')

    def get_access_headers(self):
        """
        Get token from the system
        :return: access token
        """
        try:
            access_token_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            }

            access_token_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secretkey
            }

            access_token = requests.post('https://api.sustainalytics.com/auth/token', headers=access_token_headers,
                                         data=access_token_data,
                                         ).json()['access_token']

            access_headers = {
                'Accept': 'text/json',
                'Authorization': str('Bearer ' + access_token)}
            return access_headers
        except:
            raise ConnectionError(
                'API Access Error: Please ensure the client_id and secret_key are valid else reach-out to your account manager for support')

    def get_fieldIds(self):
        """
        Returns a list of field ids activated for the the client
        :return: a list
        """

        temp_data = self.get_fieldDefinitions(dtype='dataframe')

        if len(temp_data) > 0:
            return temp_data['fieldId'].tolist()
        else:
            return []

    def get_fieldsInfo(self, dtype='json', fieldIds=None):
        """
        Returns a fieldidInfo activated for the the client
        :return: a list
        """
        if fieldIds is not None:
            temp_data = self.get_fieldDefinitions(dtype='dataframe')
            temp_data = temp_data[temp_data['fieldId'].isin(fieldIds)].copy()
            # print(temp_data)
        else:
            temp_data = self.get_fieldDefinitions(dtype='dataframe')
        # print(temp_data.info())
        if len(temp_data) > 0:
            if dtype == 'json':
                return pd.Series(temp_data['fieldName'].values, index=temp_data['fieldId']).to_dict()
            else:
                return temp_data[['fieldId', 'fieldName']]
        else:
            return {}

    def get_fieldDefinitions(self, dtype='json'):
        """
        Returns the field definitions either as a dataframe or json
        :param dtype: dataframe or json
        :return: requested Data formats
        """

        try:

            if dtype == 'json':
                temp_data = requests.get('https://api.sustainalytics.com/v2/FieldDefinitions',
                                         headers=self.access_headers, timeout=60).json()
            else:
                temp_data = pd.DataFrame(requests.get('https://api.sustainalytics.com/v2/FieldDefinitions',
                                                      headers=self.access_headers, timeout=60).json())

        except:
            self.access_headers = self.get_access_headers()
            if dtype == 'json':

                temp_data = requests.get('https://api.sustainalytics.com/v2/FieldDefinitions',
                                         headers=self.access_headers, timeout=60).json()
            else:
                temp_data = pd.DataFrame(requests.get('https://api.sustainalytics.com/v2/FieldDefinitions',
                                                      headers=self.access_headers, timeout=60).json())
        return temp_data

    def get_productIds(self):
        """
        Returns a list of product ids activated for the the client
        :param dtype: dataframe or json
        :return: requested Data formats
        """

        temp_data = self.get_fieldMappings(dtype='dataframe')

        if len(temp_data) > 0:
            return temp_data['productId'].tolist()
        else:
            return []

    def get_productsInfo(self, dtype='json'):
        """
        Returns products info for the clients
        :param dtype: dataframe or json
        :return: requested Data formats
        """

        temp_data = self.get_fieldMappings(dtype='dataframe')

        if len(temp_data) > 0:
            if dtype == 'json':
                return pd.Series(temp_data['productName'].values, index=temp_data['productId']).to_dict()
            else:
                return temp_data[['productId', 'productName']]
        else:
            return {}

    def get_packageIds(self):
        """
        Returns a list of package ids activated for the the client
        :param dtype: dataframe or json
        :return: requested Data formats
        """

        temp_data = self.get_fieldMappings(dtype='dataframe')
        temp_data = pd.DataFrame(list(itertools.chain.from_iterable(temp_data['packages'].tolist())))

        if len(temp_data) > 0:
            return temp_data['packageId'].tolist()
        else:
            return []

    def get_packageInfo(self, dtype='json'):
        """
        Returns products info for the clients
        :param dtype: dataframe or json
        :return: requested Data formats
        """

        temp_data = self.get_fieldMappings(dtype='dataframe')
        temp_data = pd.DataFrame(list(itertools.chain.from_iterable(temp_data['packages'].tolist())))

        if len(temp_data) > 0:
            if dtype == 'json':
                return pd.Series(temp_data['packageName'].values, index=temp_data['packageId']).to_dict()
            else:
                return temp_data[['packageId', 'packageName']]
        else:
            return {}

    def get_fieldClusterIds(self):
        """
        Returns a list of fieldcluster ids activated for the the client
        :param dtype: dataframe or json
        :return: requested Data formats
        """

        temp_data = self.get_fieldMappings(dtype='dataframe')
        temp_data = pd.DataFrame(list(itertools.chain.from_iterable(temp_data['packages'].tolist())))
        temp_data = pd.DataFrame(list(itertools.chain.from_iterable(temp_data['clusters'].tolist())))

        if len(temp_data) > 0:
            return temp_data['fieldClusterId'].tolist()
        else:
            return []

    def get_fieldClusterInfo(self, dtype='json'):
        """
        Returns fieldcluster info for the clients
        :param dtype: dataframe or json
        :return: requested Data formats
        """

        temp_data = self.get_fieldMappings(dtype='dataframe')
        temp_data = pd.DataFrame(list(itertools.chain.from_iterable(temp_data['packages'].tolist())))
        temp_data = pd.DataFrame(list(itertools.chain.from_iterable(temp_data['clusters'].tolist())))

        if len(temp_data) > 0:
            if dtype == 'json':
                return pd.Series(temp_data['fieldClusterName'].values, index=temp_data['fieldClusterId']).to_dict()
            else:
                return temp_data[['fieldClusterId', 'fieldClusterName']]
        else:
            return {}

    def get_fieldMappings(self, dtype='json'):
        """
        Returns the field definitions either as a dataframe or json
        :param dtype: dataframe or json
        :return: requested Data formats
        """

        try:

            if dtype == 'json':
                temp_data = requests.get('https://api.sustainalytics.com/v2/FieldMappings',
                                         headers=self.access_headers, timeout=60).json()
            else:
                temp_data = pd.json_normalize(requests.get('https://api.sustainalytics.com/v2/FieldMappings',
                                                           headers=self.access_headers, timeout=60).json())
                # primary_meta_cols = temp_data.columns.tolist().remove('packages')
                # temp_data = pd.json_normalize(temp_data, record_path='packages', meta=primary_meta_cols)

        except:
            self.access_headers = self.get_access_headers()
            if dtype == 'json':

                temp_data = requests.get('https://api.sustainalytics.com/v2/FieldMappings',
                                         headers=self.access_headers, timeout=60).json()

            else:
                temp_data = pd.json_normalize(
                    requests.get('https://api.sustainalytics.com/v2/FieldMappings', headers=self.access_headers,
                                 timeout=60).json())

                # JSON DENORMALIZATION
                # primary_meta_cols = temp_data.columns.tolist().remove('packages')
                # temp_data2 = pd.json_normalize(temp_data,record_path='packages',meta=primary_meta_cols)
        return temp_data

    def get_fieldMappingDefinitions(self, dtype='json'):
        """
        Returns the field definitions either as a dataframe or json
        :param dtype: dataframe or json
        :return: requested Data formats
        """

        try:

            if dtype == 'json':
                temp_data = requests.get('https://api.sustainalytics.com/v2/FieldMappingDefinitions',
                                         headers=self.access_headers, timeout=60).json()
            else:
                temp_data = pd.DataFrame(requests.get('https://api.sustainalytics.com/v2/FieldMappingDefinitions',
                                                      headers=self.access_headers, timeout=60).json())

        except:
            self.access_headers = self.get_access_headers()
            if dtype == 'json':

                temp_data = requests.get('https://api.sustainalytics.com/v2/FieldMappingDefinitions',
                                         headers=self.access_headers, timeout=60).json()
            else:
                temp_data = pd.DataFrame(requests.get('https://api.sustainalytics.com/v2/FieldMappingDefinitions',
                                                      headers=self.access_headers, timeout=60).json())
        return temp_data

    def get_universe_access(self, dtype='json'):
        """
        Get all the companyids in the universes
        :param dtype: return type dataframe or json
        :return: json or dataframe
        """
        try:

            if dtype == 'json':
                temp_data = requests.get('https://api.sustainalytics.com/v2/UniverseOfAccess',
                                         headers=self.access_headers, timeout=60).json()
            else:
                temp_data = pd.DataFrame(requests.get('https://api.sustainalytics.com/v2/UniverseOfAccess',
                                                      headers=self.access_headers, timeout=60).json())

        except:
            self.access_headers = self.get_access_headers()
            if dtype == 'json':

                temp_data = requests.get('https://api.sustainalytics.com/v2/UniverseOfAccess',
                                         headers=self.access_headers, timeout=60).json()
            else:
                temp_data = pd.DataFrame(requests.get('https://api.sustainalytics.com/v2/UniverseOfAccess',
                                                      headers=self.access_headers, timeout=60).json())

        return temp_data

    def get_universe_entityIds(self, keep_duplicates=False):
        """
        Returns a list of entityids in the Universe of Access for the client
        :return: list of entity ids
        """
        self.universe_of_access = self.get_universe_access(dtype='dataframe')
        self.__universe_entity_ids = list(itertools.chain.from_iterable(self.universe_of_access['entityIds'].tolist()))
        if keep_duplicates is True:
            return self.__universe_entity_ids
        else:
            return list(set(self.__universe_entity_ids))

    def __process_fieldsdata(self, field):
        """
        Return a processed dataframe
        :return: new_dataframe
        """
        if not bool(field) or field is np.nan:
            self.fieldIds = self.get_fieldIds()
            fieldstr = [str(i) for i in self.fieldIds]
            self.fieldIds_default = dict.fromkeys(fieldstr, np.nan)
            return self.fieldIds_default
        else:
            return field

    def __process_definitions(self, value, src_df, match_length, src_id_name):
        """
        Process the definition file
        :param value: definition id
        :param src_df: dataframe file to lookup
        :param match_length: 2, 4 ,6
        :param src_id_name: name of definition id
        :return: id, idname
        """
        value_str = str(value)[:match_length]
        # print(src_df.columns)
        temp_df = src_df[src_df[src_id_name] == int(value_str)].copy()
        if len(temp_df) >= 1:
            return temp_df.iat[0, 0], temp_df.iat[0, 1]
        else:
            return None, None

    def get_fullFieldDefinitions(self, dtype='json'):
        """
        Return all definitions
        :return: full dataframe of the definition mapping
        """
        field_info = self.get_fieldsInfo(dtype='dataframe')
        field_cluster = self.get_fieldClusterInfo(dtype='dataframe')
        packages = self.get_packageInfo(dtype='dataframe')
        products = self.get_productsInfo(dtype='dataframe')
        # Go up the ladder
        field_info['productId'], field_info['productName'] = zip(
            *field_info.apply(lambda x: self.__process_definitions(x['fieldId'], products, 2, 'productId'), axis=1))
        field_info['packageId'], field_info['packageName'] = zip(
            *field_info.apply(lambda x: self.__process_definitions(x['fieldId'], packages, 4, 'packageId'), axis=1))
        field_info['fieldClusterId'], field_info['fieldClusterName'] = zip(
            *field_info.apply(lambda x: self.__process_definitions(x['fieldId'], field_cluster, 6, 'fieldClusterId'),
                              axis=1))
        if dtype == 'json':
            return field_info.to_json(orient='records')
        else:
            return field_info

    def get_pdfReportService(self, productId: int = None, dtype: str = 'json'):
        """
        Get the PDF reports
        :return: info
        """
        if productId is None:
            raise ValueError('Please specify productId')
        if isinstance(productId, int) == False:
            raise ValueError('productId must be integer and have only one value per call')

        try:

            if dtype == 'json':
                temp_data = requests.get('https://api.sustainalytics.com/v2/ReportService',
                                         headers=self.access_headers, params=(('ProductId', productId),),
                                         timeout=60).json()
            else:
                temp_data = pd.DataFrame(requests.get('https://api.sustainalytics.com/v2/ReportService',
                                                      headers=self.access_headers, params=(('ProductId', productId),),
                                                      timeout=60).json())
                if temp_data.shape[0] == 0:
                    return {'Message': 'No available reports to show'}

        except:
            self.access_headers = self.get_access_headers()
            if dtype == 'json':

                temp_data = requests.get('https://api.sustainalytics.com/v2/ReportService',
                                         headers=self.access_headers, params=(('ProductId', productId),),
                                         timeout=60).json()
            else:
                temp_data = pd.DataFrame(requests.get('https://api.sustainalytics.com/v2/ReportService',
                                                      headers=self.access_headers, params=(('ProductId', productId),),
                                                      timeout=60).json())
                if temp_data.shape[0] == 0:
                    return {'Message': 'No available reports to show'}
        return temp_data

    def get_pdfReportUrl(self, identifier=None, reportId=None, dtype='json'):
        """
        Returns the URL of the PDF report
        :param identifier: Sustainalytics Entity identifier
        :param reportId: report ID
        :return: json
        """
        temp_data = pd.DataFrame()
        request_url = 'https://api.sustainalytics.com/v2/ReportService/url/'
        if identifier is not None and reportId is not None:
            request_url = request_url + str(identifier).strip(' \t\n') + "/" + str(reportId).strip(' \t\n')
            try:

                if dtype == 'json':
                    temp_data = requests.get(request_url,
                                             headers=self.access_headers, timeout=60).json()
                else:
                    temp_data = pd.DataFrame(requests.get(request_url,
                                                          headers=self.access_headers, timeout=60).json())

            except:
                self.access_headers = self.get_access_headers()
                if dtype == 'json':

                    temp_data = requests.get(request_url,
                                             headers=self.access_headers, timeout=60).json()
                else:
                    temp_data = pd.DataFrame(requests.get(request_url,
                                                          headers=self.access_headers, timeout=60).json())

            return temp_data
        else:
            return temp_data

    def get_pdfReportInfo(self, productId: int = None, dtype: str = 'json'):
        """
        Returns a json of report IDs accessible to client
        :return: json or dataframe
        """
        temp_data = self.get_pdfReportService(productId=productId, dtype='dataframe')
        if isinstance(temp_data, pd.DataFrame) and len(temp_data) > 0:
            temp_data = pd.DataFrame(list(itertools.chain.from_iterable(temp_data['reports'].tolist())))
            if dtype == 'json':
                return pd.Series(temp_data['reportType'].values, index=temp_data['reportId']).to_dict()
            else:
                return temp_data[['reportId', 'reportType']].drop_duplicates()
        else:
            return {'Message': 'Client has no pdf report access'}

    def __process_parameter_for_request(self, parameter_name: str, parameter_values: list = None,
                                        all_parameters_values: tuple = None) -> tuple:
        """ Prepares a parameter to be added to the tuple with all the parameter values for the endpoint request.

        Args:
            parameter_name: Name of the parameter.
            parameter_values: Values given to the parameter.
            all_parameters_values: Tuple containing all the parameter data.

        Returns:
            The tuple with all parameter values with new parameter added to it.
        """
        if (parameter_values is not None) and (isinstance(parameter_values, list)) and (len(parameter_values) > 0):
            parameter_str = ','.join([str(elem) for elem in parameter_values])
            all_parameters_values = all_parameters_values + ((str(parameter_name), parameter_str),)
            return all_parameters_values
        elif (parameter_values is not None) and (
                isinstance(parameter_values, str) or isinstance(parameter_values, int)):
            all_parameters_values = all_parameters_values + ((str(parameter_name), parameter_values),)
            return all_parameters_values
        else:
            return all_parameters_values

    def __get_endpoint_data(self, params: tuple, extracted_data: Union[list, pd.DataFrame], dtype: str,
                            endpoint: str) -> Union[list, pd.DataFrame]:
        """ Makes a GET request to the specified endpoint and returns it in the specified format.

        Args:
            params: Parameters for the request.
            extracted_data: Place where to store the data.
            dtype: json or dataframe.
            endpoint: endpoint to call.

        Returns:
            A json or a dataframe with the extracted data.
        """
        requests_url = requests.get(f"https://api.sustainalytics.com/v2/{endpoint}",
                                    headers=self.access_headers, params=params, timeout=180).json()
        if dtype == 'json':
            temp_data = requests_url
            extracted_data = extracted_data + temp_data
            return extracted_data
        else:
            temp_data = pd.DataFrame(requests_url)
            extracted_data = pd.concat([extracted_data, temp_data], ignore_index=True)
            return extracted_data

    def __make_request_to_endpoint(self, all_parameter_values: tuple, extracted_data: Union[list, pd.DataFrame],
                                   endpoint: str, dtype: str) -> Union[list, pd.DataFrame]:
        """ Makes a request to a given V2 endpoint.

        Args:
            all_parameter_values: tuple containing all parameter data.
            extracted_data: place where to store the data from the request.
            endpoint: endpoint to make request to.
            dtype: json or dataframe.

        Returns:
            A json or a dataframe with the extracted data.
        """
        try:
            extracted_data = self.__get_endpoint_data(all_parameter_values, extracted_data, dtype, endpoint)
            return extracted_data
        except:
            self.access_headers = self.get_access_headers()
            extracted_data = self.__get_endpoint_data(all_parameter_values, extracted_data, dtype, endpoint)
            return extracted_data

    def __set_parameters(self, startdate: str = None, productId: int = None, packageIds: list = None,
                         fieldClusterIds: list = None, fieldIds: list = None, identifiers: list = None) -> tuple:
        """ Gathers all the data from the parameters in order to combine them into a tuple.

        Args:
            startdate: Date filter for last changes query.
            productId: The product ID.
            packageIds: A list of package ids.
            fieldClusterIds: A list of field cluster ids.
            fieldIds: A list of field ids.
            identifiers: A list of security or company identifiers.

        Returns:
            A tuple with all the params ready to be passed for a request.
        """
        params = ()
        params = self.__process_parameter_for_request("StartDate", startdate, params)
        params = self.__process_parameter_for_request("productId", productId, params)
        params = self.__process_parameter_for_request("PackageIds", packageIds, params)
        params = self.__process_parameter_for_request("fieldClusterIds", fieldClusterIds, params)
        params = self.__process_parameter_for_request("fieldIds", fieldIds, params)
        params = self.__process_parameter_for_request("identifiers", identifiers, params)
        return params

    def __json_or_dataframe(self, dtype: str) -> Union[list, pd.DataFrame]:
        """ Creates a list or a dataframe based on the input.

        Args:
            dtype: json or dataframe.

        Returns:
            A empty list or an empty dataframe.
        """
        if dtype == 'json':
            return []
        else:
            return pd.DataFrame()

    def __create_identifier_groups(self, identifiers: list, chunk_size: int) -> list:
        """ Creates identifier groups of 10 when the number of elements in the identifiers list is >10.

        Args:
            identifiers: A list of security or company identifiers.
            chunk_size: The chunk size. 10 is the maximum value.

        Returns:
            A list of lists with the identifiers.
        """
        return [identifiers[i:i + chunk_size] for i in range(0, len(identifiers), chunk_size)]

    def __process_identifier_groups(self, identifiers: list) -> str:
        """ Transforms the lists of identifiers into str values, strips them and puts a comma after each of them.

        Args:
            identifiers: The list of identifiers.

        Returns:
            The values from the list of identifiers as a string.
        """
        return ','.join([str(elem).strip() for elem in identifiers])

    def __check_date_format(self, date: str) -> None:
        """ Checks whether the given date is in 'yyyy-mm-dd' format.

        Args:
            date: The date to check the format of.

        Raises:
            ValueError: if the date is in any other format.
        """
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except:
            raise ValueError(f"Incorrect date format, should be 'yyyy-mm-dd': {date}.")

    def __check_less_than_3_months_ago(self, date: str) -> None:
        """ Checks whether the given date is more than 3 months ago, and raises an error if it is.

        Args:
            date: The date to check, in 'yyyy-mm-dd' format.

        Raises:
            ValueError: if the date is more than 3 months ago from current date.
        """
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        today = datetime.date.today()
        three_months_ago = today + relativedelta(months=-3)
        if date < three_months_ago:
            raise ValueError('The date entered is more than 3 months ago.')

    def __check_type(self, arg_name: str, actual_values, expected_type) -> None:
        """ Checks values to see if their actual type matches the expected one.

        Args:
            actual_values: The values to check the type of.
            expected_type: Expected type of the values.

        Raises:
            TypeError: if the expected type is different from the current type.
        """
        if not isinstance(actual_values, expected_type):
            raise TypeError(
                f"Expected {expected_type.__name__} for {arg_name}, but got {type(actual_values).__name__} instead.")

    def __check_possible_existence_type(self, arg_name: str, actual_values: Any, expected_type: Any) -> None:
        """ Checks whether there are any actual values. If there are their actual type will be compared to the expected
        type.

        Args:
            actual_values: The values to check the type of.
            expected_type: Expected type of the values.

        Raises:
            TypeError: if the expected type is different from the current type.
        """
        if actual_values is not None:
            if not isinstance(actual_values, expected_type):
                raise TypeError(
                    f"Expected {expected_type.__name__} for {arg_name}, but got {type(actual_values).__name__} instead.")

    def __check_greater_than(self, arg_name: str, actual_value: int, comparison_value: int) -> None:
        """ Checks whether the values of an argument are bigger than a provided value.

        Args:
            actual_value: The value given in the function call.
            comparison_value: The value to compare with.

        Raises:
            ValueError: if the actual value is smaller than the expected one.
        """
        if not actual_value > comparison_value:
            raise ValueError(f"{actual_value} must be bigger than {comparison_value} for {arg_name}.")

    def __check_less_than(self, arg_name: str, actual_value: int, comparison_value: int) -> None:
        """ Checks whether the values of an argument are smaller than a provided value.

        Args:
            actual_value: The value given in the function call.
            comparison_value: The value to compare with.

        Raises:
            ValueError: if the actual value is bigger than the expected one.
        """
        if not actual_value < comparison_value:
            raise ValueError(f"{actual_value} must be smaller than {comparison_value} for {arg_name}.")

    def __check_is_value_valid(self, arg_name: str, actual_value: str, valid_values: list) -> None:
        """ Checks whether the actual value is in the list of valid values.

        Args:
            actual_value: The value given in the function call.
            valid_values: The possible values.

        Raises:
            ValueError: If the actual value is not present in the valid values list.
        """
        if actual_value not in valid_values:
            raise ValueError(
                f"{actual_value} is not a valid value for {arg_name}. Valid values are: {', '.join(valid_values)}.")

    def __check_list_not_empty(self, arg_name: str, actual_values: list) -> None:
        """ Checks whether a list is empty. Throws a ValueError it is.

        Args:
            arg_name: Name of the argument.
            actual_values: The list to check if it's empty or not.

        Raises:
            ValueError: if list is empty.
        """
        if not actual_values:
            raise ValueError(f"The list of {arg_name} must contain at least 1 value.")

    def __get_LastChangesSince_validations(self, startdate: str, productId: int, identifiers: list, packageIds: list,
                                           fieldClusterIds: list, fieldIds: list, dtype: str, chunk_size: int) -> None:
        """ Validation checks for the get_LastChangesSince function.

        Args:
            startdate: Date filter for last changes query. Can retrieve data only for last 3 months from current date.
            productId: The product ID. Only one value allowed.
            identifiers: A list of security or company identifiers.
            packageIds: A list of package ids.
            fieldClusterIds: A list of field cluster ids.
            fieldIds: A list of field ids.
            dtype: json or dataframe.
            chunk_size: The chunk size if using identifiers. 10 is the maximum value.
        """
        self.__check_type("startdate", startdate, str)
        self.__check_date_format(startdate)
        self.__check_less_than_3_months_ago(startdate)
        self.__check_type("productId", productId, int)
        self.__check_greater_than("chunk_size", chunk_size, 0)
        self.__check_less_than("chunk_size", chunk_size, 11)
        self.__check_possible_existence_type("identifiers", identifiers, list)
        self.__check_possible_existence_type("packageIds", packageIds, list)
        self.__check_possible_existence_type("fieldClusterIds", fieldClusterIds, list)
        self.__check_possible_existence_type("fieldIds", fieldIds, list)
        self.__check_possible_existence_type("chunk_size", chunk_size, int)
        self.__check_is_value_valid("dtype", dtype, ['json', 'dataframe'])

    def get_LastChangesSince(self, startdate: str, productId: int, identifiers: list = None, packageIds: list = None,
                             fieldClusterIds: list = None, fieldIds: list = None, dtype: str = 'json',
                             chunk_size: int = 10) -> Union[list, pd.DataFrame]:
        """ Make an API request to the LastChangesSince v2 endpoint with the given parameters and return the response.

        Args:
            startdate: Date filter for last changes query. Can retrieve data only for last 3 months from current date.
            productId: The product ID. Only one value allowed.
            identifiers: A list of security or company identifiers.
            packageIds: A list of package ids.
            fieldClusterIds: A list of field cluster ids.
            fieldIds: A list of field ids.
            dtype: json or dataframe.
            chunk_size: The chunk size if using identifiers. 10 is the maximum value. If the number of identifiers is
            bigger than the chunk size, then the number of API calls to the endpoint would be equal to the number of
            identifiers/chunk size.

        Returns:
            A json or a dataframe representing the response from the v2 endpoint LastChangesSince of the API.
        """

        self.__get_LastChangesSince_validations(startdate, productId, identifiers, packageIds, fieldClusterIds,
                                                fieldIds, dtype, chunk_size)

        extracted_data = self.__json_or_dataframe(dtype)

        if (identifiers is not None) and len(identifiers) > 10:
            identifier_groups = self.__create_identifier_groups(identifiers, chunk_size)
            for i, id_group_list in enumerate(identifier_groups):
                # grouped_identifiers = self.__process_identifier_groups(id_group_list)
                params = self.__set_parameters(startdate, productId, packageIds, fieldClusterIds, fieldIds,
                                               id_group_list)

                extracted_data = self.__make_request_to_endpoint(params, extracted_data, "LastChangesSince", dtype)
        else:
            params = self.__set_parameters(startdate, productId, packageIds, fieldClusterIds, fieldIds, identifiers)
            extracted_data = self.__make_request_to_endpoint(params, extracted_data, "LastChangesSince", dtype)
        return extracted_data

    def __get_data_validations(self, identifiers: list, productId: int, packageIds: list, fieldClusterIds: list,
                               fieldIds: list, dtype: str, chunk_size: int, timestamps: bool,
                               use_progressbar: bool) -> None:
        """ Validation checks for the get_data function.

        Args:
            identifiers: A list of security or company identifiers separated by comma.
            productId: The product ID.
            packageIds: A list of package ids separated by comma.
            fieldClusterIds: A list of field cluster ids separated by comma.
            fieldIds: A list of field ids separated by comma.
            dtype: json or dataframe.
            chunk_size: The chunk size.
            timestamps: A boolean value indicating whether to return data with timestamps or not.
            use_progressbar: A boolean value indicating whether to show a progress bar or not during the function call.
        """
        self.__check_type("productId", productId, int)
        self.__check_type("identifiers", identifiers, list)
        self.__check_list_not_empty("identifiers", identifiers)
        self.__check_greater_than("chunk_size", chunk_size, 0)
        self.__check_less_than("chunk_size", chunk_size, 11)
        self.__check_type("timestamps", timestamps, bool)
        self.__check_type("use_progressbar", use_progressbar, bool)
        self.__check_is_value_valid("dtype", dtype, ['json', 'dataframe'])
        self.__check_possible_existence_type("packageIds", packageIds, list)
        self.__check_possible_existence_type("fieldClusterIds", fieldClusterIds, list)
        self.__check_possible_existence_type("fieldIds", fieldIds, list)
        self.__check_possible_existence_type("chunk_size", chunk_size, int)

    def get_data(self, identifiers: list, productId: int, packageIds: list = None, fieldClusterIds: list = None,
                 fieldIds: list = None, dtype: str = 'json', chunk_size: int = 10, timestamps: bool = False,
                 use_progressbar: bool = True) -> Union[list, pd.DataFrame]:
        """Get bulk data via sustainalytics API

        Args:
            identifiers: A list of security or company identifiers separated by comma.
            productId: The product ID.
            packageIds: A list of package ids separated by comma.
            fieldClusterIds: A list of field cluster ids separated by comma.
            fieldIds: A list of field ids separated by comma.
            dtype: json or dataframe.
            chunk_size: The chunk size. 10 is the maximum value. If the number of identifiers is
            bigger than the chunk size, then the number of API calls to the endpoint would be equal to the number of
            identifiers/chunk size.
            timestamps: A boolean value indicating whether to return data with timestamps or not.
            use_progressbar: A boolean value indicating whether to show a progress bar or not during the function call.

        Returns:
            json or Dataframe
        """

        self.__get_data_validations(identifiers, productId, packageIds, fieldClusterIds, fieldIds, dtype, chunk_size,
                                    timestamps, use_progressbar)

        data_pull = self.__json_or_dataframe(dtype)

        if len(identifiers) > 10:
            identifiers = self.__create_identifier_groups(identifiers, chunk_size)
        else:
            identifiers = [identifiers]

        with tqdm(total=len(identifiers), disable=not use_progressbar) as pbar:
            for i, id_group_list in enumerate(identifiers):
                # grouped_identifiers = self.__process_identifier_groups(id_group_list)
                params = self.__set_parameters(productId=productId, packageIds=packageIds,
                                               fieldClusterIds=fieldClusterIds,
                                               fieldIds=fieldIds, identifiers=id_group_list)
                if timestamps:
                    data_pull = self.__make_request_to_endpoint(params, data_pull, "DataServiceWTimestamps", dtype)
                else:
                    data_pull = self.__make_request_to_endpoint(params, data_pull, "DataService", dtype)
                pbar.update(1)
        return data_pull
