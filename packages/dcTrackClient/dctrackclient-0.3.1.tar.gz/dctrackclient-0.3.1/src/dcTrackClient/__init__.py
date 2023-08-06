import requests


class Client:
    def __init__(self, baseUrl: str, username: str = '', password: str = '', apiToken: str = ''):
        """Provide either a username and password, or an API token to access the dcTrack database with Python."""
        self.__BASE_URL = baseUrl
        self.__USERNAME = username
        self.__PASSWORD = password
        self.__APITOKEN = apiToken

    def __request(self, method: str, endpoint: str, body: dict = None):
        if self.__USERNAME and self.__PASSWORD:
            return requests.request(method,  self.__BASE_URL + '/' + endpoint, json=body, auth=(self.__USERNAME, self.__PASSWORD)).json()
        elif self.__APITOKEN:
            return requests.request(method, self.__BASE_URL + '/' + endpoint, json=body, headers={'Authorization': 'Token ' + self.__APITOKEN}).json()
        else:
            raise Exception('Undefined username/password or token.')

    def getItem(self, id: int):
        """Get item details using the item ID."""
        return self.__request('GET', '/api/v2/dcimoperations/items/' + str(id) + '/?')

    def createItem(self, returnDetails: bool, payload: dict):
        """Create a new item. When returnDetails is set to true, the API call will return the full json payload. If set to false, the call returns only the "id" and "tiName"."""
        return self.__request('POST', '/api/v2/dcimoperations/items/?returnDetails=' + str(returnDetails) + '&', payload)

    def updateItem(self, id: int, returnDetails: bool, payload: dict):
        """Update an existing item. When returnDetails is set to true, the API call will return the full json payload. If set to false, the call returns only the "id" and "tiName"."""
        return self.__request('PUT', '/api/v2/dcimoperations/items/' + str(id) + '/?returnDetails=' + str(returnDetails) + '&', payload)

    def deleteItem(self, id: int):
        """Delete an item using the item ID."""
        return self.__request('DELETE', '/api/v2/dcimoperations/items/' + str(id) + '/?')

    def searchItems(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for items using criteria JSON object. Search criteria can be any of the fields applicable to items, including custom fields. Specify the fields to be included in the response. This API supports pagination. Returns a list of items with the specified information."""
        return self.__request('POST', '/api/v2/quicksearch/items/?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def cabinetItems(self, CabinetId: int):
        """Returns a list of Items contained in a Cabinet using the ItemID of the Cabinet. The returned list includes all of the Cabinet's Items including Passive Items."""
        return self.__request('GET', '/api/v2/items/cabinetItems/' + str(CabinetId) + '/?')

    def manageItemsBulk(self, payload: dict):
        """Add/Update/Delete Items."""
        return self.__request('POST', '/api/v2/dcimoperations/items/bulk/?', payload)

    def getMakes(self):
        """Returns a list of makes with basic information."""
        return self.__request('GET', '/api/v2/makes/?')

    def createMake(self, payload: dict):
        """Add a new Make. Returns JSON entity containing Make information that was passed in from the Request payload."""
        return self.__request('POST', '/api/v2/makes/?', payload)

    def updateMake(self, makeId: int, payload: dict):
        """Modify a Make. Returns JSON entity containing Make information that was passed in from the Request payload."""
        return self.__request('PUT', '/api/v2/makes/' + str(makeId) + '/?', payload)

    def deleteMake(self, makeId: int):
        """Delete a Make."""
        return self.__request('DELETE', '/api/v2/makes/' + str(makeId) + '/?')

    def searchMakes(self, makeName: str):
        """Search for a make using the make name. Returns a list of makes with basic information."""
        return self.__request('GET', '/api/v2/dcimoperations/search/makes/' + str(makeName) + '/?')

    def getModel(self, modelId: int, usedCounts: int):
        """Get Model fields for the specified Model ID. usedCounts is an optional parameter that determines if the count of Items for the specified model is returned in the response. If set to "true" the counts will be included in the response, if omitted or set to "false" the item count will not be included in the response."""
        return self.__request('GET', '/api/v2/models/' + str(modelId) + '/?usedCounts=' + str(usedCounts) + '&')

    def createModel(self, returnDetails: bool, proceedOnWarning: bool, payload: dict):
        """Add a new Model. Returns JSON entity containing Make information that was passed in from the Request payload. "proceedOnWarning" relates to the warning messages that are thrown in dcTrack when you try to delete custom fields that are in use. The "proceedOnWarning" value can equal either "true" or "false." If "proceedOnWarning" equals "true," business warnings will be ignored. If "proceedOnWarning" equals "false," business warnings will not be ignored. Fields that are not in the payload will remain unchanged."""
        return self.__request('POST', '/api/v2/models/?returnDetails=' + str(returnDetails) + '&proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def deleteModel(self, id: int):
        """Delete a Model using the Model ID."""
        return self.__request('DELETE', '/api/v2/models/' + str(id) + '/?')

    def searchModels(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for models by user supplied search criteria. Returns a list of models with the "selectedColumns" returned in the payload. Search by Alias is not supported."""
        return self.__request('POST', '/api/v2/quicksearch/models/?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def deleteModelImage(self, id: int, orientation: str):
        """Delete a Mode Image using the Model ID and the Image Orientation, where id is the Model Id and orientation is either front or back"""
        return self.__request('DELETE', '/api/v2/models/images/' + str(id) + '/' + str(orientation) + '/?')

    def getConnector(self, connectorId: int, usedCount: bool):
        """Get a Connector record by ID. Returns a Connector with all information including Compatible Connectors. The usedCount parameter is optional. If usedCount is true, the response will include the number of times the connector is in use by Models and Items. If false, no counts are returned. If omitted the default is false."""
        return self.__request('GET', '/api/v2/settings/connectors/' + str(connectorId) + '/?usedCount=' + str(usedCount) + '&')

    def createConnector(self, payload: dict):
        """Add a new Connector. Returns JSON entity containing Connector information that was passed in from the Request payload."""
        return self.__request('POST', '/api/v2/settings/connectors/?', payload)

    def updateConnector(self, connectorId: int, payload: dict):
        """Update an existing Connector. Returns JSON entity containing Connector information that was passed in from the Request payload."""
        return self.__request('PUT', '/api/v2/settings/connectors/' + str(connectorId) + '/?', payload)

    def deleteConnector(self, payload: dict):
        """Delete one or more Connector records."""
        return self.__request('POST', '/api/v2/settings/connectors/delete/?', payload)

    def searchConnectors(self, pageNumber: int, pageSize: int, usedCount: bool, payload: dict):
        """Retrieve a List of Connectors. Returns JSON entity containing Connector information that was passed in from the Request payload. Please note, Compatible Connectors are not returned by this API, but can be returned when querying a single Connector using the /api/v2/settings/connectors/{connectorId} API."""
        return self.__request('POST', '/api/v2/settings/connectors/quicksearch/?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&usedCount=' + str(usedCount) + '&', payload)

    def deleteConnectorImage(self, connectorId: int):
        """Delete a Connector Image using the Connector ID."""
        return self.__request('DELETE', '/api/v2/settings/connectors/' + str(connectorId) + '/images/?')
