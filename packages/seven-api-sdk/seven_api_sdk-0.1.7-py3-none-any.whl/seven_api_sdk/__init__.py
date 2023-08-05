from dataclasses import dataclass, field
import json
from pprint import pprint
from typing import Union
import requests
import boto3

__version__ = '0.1.6'


@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class _ApiEndPointBase:
    """A base dataclass for API calls towards SEVEN"""

    password: str = field(init=True)
    username: str = field(init=True)
    client_id: str = field(init=True)
    client_name: str = field(init=True)
    parameter:   Union[str, None] = field(init=True, default=None)
    token: str = field(init=False)
    api_url: str = field(init=False)

    def __post_init__(self):
        self._check_parameters()
        self._init_auth()
        self._set_url()
    
    def _check_parameters(self):
        """Validates the passed parameters. The method has to be implemented on the child classes"""
        raise NotImplementedError("This method '_check_parameters()' has to be implemented inside the child classes")

    def _set_url(self):
        raise NotImplementedError("This method '_set_url()' has to be implemented inside the child classes")

    def _init_auth(self):
        """Validates the user credentials and returns a bearer token"""

        cidp = boto3.client('cognito-idp', region_name="eu-central-1")

        response = cidp.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={'USERNAME': self.username, 'PASSWORD': self.password},
                ClientId=self.client_id)
        print("----- Log in response -----")
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200 and \
                response["AuthenticationResult"]["TokenType"] == "Bearer":

            # AWS official docs on using tokens with user pools:
            # https://amzn.to/2HbmJG6
            # If authentication was successful we got three tokens
            self.token = "Bearer " + response['AuthenticationResult']['AccessToken']
            self.id_token = response['AuthenticationResult']['IdToken']
            self.refresh_token = response['AuthenticationResult']['RefreshToken']
            print("Successful authentication")
        else:
            print("AUTHENTICATION FAILED \n")
            pprint(response)

            self.token = ""
        print("---------------------------")

    def call_api(self) -> dict:
        """Calls the API and returns a python dictionary with the 
        response code and the data on the second place."""

        #if the authentication failed we do not make the call
        if self.token == "":
            return {}

        headers = {'Authorization': self.token}

        if self.parameter is None:
            r = requests.get(self.api_url, headers=headers, timeout=20)
        else:
            payload = {"reqParam": self.parameter}
            r = requests.get(self.api_url, headers=headers, params=payload, timeout=20)
           
        response = {"status_code": r.status_code}
        r.close()
        if response["status_code"] != 200:
            print("Something went wrong with the call")
            return response
        else:
            print("Successful call")
            response["content"] = json.loads(r.text)

            return response


class StoreFields(_ApiEndPointBase):
    """A class to retrieve store fields. Accepts no parameters."""

    def _set_url(self) -> None:
        self.api_url: str = f"https://api.prjct7.app/{self.client_name}/store/store_fields"
    
    def _check_parameters(self) -> None:
        if self.parameter is not None:
            raise ValueError("Received a parameter. This endpoint accepts no Parameters")


class StoreData(_ApiEndPointBase):
    """A class to retrieve store data. If called without a parameter it returns all the stores.
    If you specify a storeID, it returns the data only for that store."""

    def _set_url(self) -> None:
        self.api_url: str = f"https://api.prjct7.app/{self.client_name}/store/store_data"
    
    def _check_parameters(self) -> None:
        if self.parameter is None:
            pass  # that is valid, we return all stores
        elif self.parameter != 'all' and not str(self.parameter).isdigit():
            raise ValueError(f"Received an unexpected parameter: {self.parameter}. "
                             f"Expected 'None' to all store data, or a store ID to return a single store.")


class ProcessFields(_ApiEndPointBase):
    """A class to retrieve process fields. Accepts no parameters. """

    def _set_url(self) -> None:
        self.api_url: str = f"https://api.prjct7.app/{self.client_name}/process/process_fields"
    
    def _check_parameters(self) -> None:
        if self.parameter is not None:
            raise ValueError("Received a parameter. This endpoint accepts no Parameters")


class ProcessData(_ApiEndPointBase):
    """A class to retrieve process data.
    You MUST provide a parameters that describes what kind of data  in which grouping you want to receive.

    Valid parameters:
    
    proc_by_storeID: Returns all process data grouped by StoreID

    proc_by_procID: Return all process data grouped by ProcessID

    proc_by_proc_type: Returns all process data grouped by ProcessType

    proc_metadata: Returns process metadata

    raw_data: Returns the raw file retrieved from SLT"""

    def _set_url(self) -> None:
        self.api_url: str = f"https://api.prjct7.app/{self.client_name}/process/process_data"
    
    def _check_parameters(self) -> None:
        valid_params = ["proc_by_storeID", "proc_by_procID", "proc_by_proc_type", "proc_metadata", "raw_data"]
        if self.parameter is None:
            raise ValueError(f"Received no parameter argument. You must specify the resource you try to retrieve. "
                             f"Valid parameters are: {valid_params}")
        if self.parameter not in valid_params:
            raise ValueError(f"Received an unexpected parameter: '{self.parameter}' "
                             f" Expected parameters are: {valid_params}")


class Costs(_ApiEndPointBase):
    """A class to retrieve process data.
    You MUST provide a parameters that describes what kind of data  in which grouping you want to receive.
    Valid parameters:

   vendors_by_id: returns all the vendors organized by their ID

   cost_sub_categories: returns all cost sub categories

   cost_by_proc_instance: returns all cost organized by process instance ID

   raw_data: returns the raw source data from SLT"""

    def _set_url(self) -> None:
        self.api_url: str = f"https://api.prjct7.app/{self.client_name}/costs"
    
    def _check_parameters(self) -> None:
        valid_params = ["vendors_by_id", "cost_sub_categories", "cost_by_proc_instance", "raw_data"]
        if self.parameter is None:
            raise ValueError(f"Received no parameter argument. You must specify the resource you try to retrieve. "
                             f"Valid parameters are: {valid_params}")
        if self.parameter not in valid_params:
            raise ValueError(f"Received an unexpected parameter: '{self.parameter}'  "
                             f"Expected parameters are: {valid_params}")


class Reports(_ApiEndPointBase):
    """A class to retrieve reports. You MUST provide a parameters that describes what kind of data
    in which grouping you want to receive.
    The parameter is the name of the report.
    This is not defined in the sdk as report names differ from tenant to tenant.
    In case you did not receive the necessary report names, please contact your administrator"""

    def _set_url(self) -> None:
        self.api_url: str = f"https://api.prjct7.app/{self.client_name}/reports"
    
    def _check_parameters(self) -> None:
        if self.parameter is None:
            raise ValueError("Received None as a parameter. You must specify which report you want to receive!")
