import logging

from ._guardpoint_cardholdertypes import CardholderTypesAPI
from ._guardpoint_scheduledmags import ScheduledMagsAPI
from ._guardpoint_customizedfields import CustomizedFieldsAPI
from ._guardpoint_personaldetails import PersonalDetailsAPI
from ._guardpoint_securitygroups import SecurityGroupsAPI
from .guardpoint_connection import GuardPointConnection, GuardPointAuthType
from ._guardpoint_cards import CardsAPI
from ._guardpoint_cardholders import CardholdersAPI
from .guardpoint_error import GuardPointError
from ._guardpoint_areas import AreasAPI
from .guardpoint_utils import url_parser

log = logging.getLogger(__name__)


class GuardPoint(GuardPointConnection, CardsAPI, CardholdersAPI, AreasAPI, SecurityGroupsAPI,
                 CustomizedFieldsAPI, PersonalDetailsAPI, ScheduledMagsAPI, CardholderTypesAPI):

    def __init__(self, **kwargs):
        # Set default values if not present
        host = kwargs.get('host', "localhost")
        port = kwargs.get('port', None)
        url_components = url_parser(host)
        if url_components['host'] == '':
            url_components['host'] = url_components['path']
            url_components['path'] = ''
        if port:
            url_components['port'] = port
        auth = kwargs.get('auth', GuardPointAuthType.BEARER_TOKEN)
        user = kwargs.get('username', "admin")
        pwd = kwargs.get('pwd', "admin")
        key = kwargs.get('key', "00000000-0000-0000-0000-000000000000")
        token = kwargs.get('token', None)
        super().__init__(url_components=url_components, auth=auth, user=user, pwd=pwd, key=key, token=token)



    # TODO: is this needed since count can be achieved with "$count=true&$top=0"
    def get_cardholder_count(self):
        url = self.baseurl + "/odata/GetCardholdersCount"
        code, json_body = self.gp_json_query("GET", url=url)

        if code != 200:
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    raise GuardPointError(json_body['error'])
            else:
                raise GuardPointError(str(code))

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'totalItems' not in json_body:
            raise GuardPointError("Badly formatted response.")

        return int(json_body['totalItems'])


