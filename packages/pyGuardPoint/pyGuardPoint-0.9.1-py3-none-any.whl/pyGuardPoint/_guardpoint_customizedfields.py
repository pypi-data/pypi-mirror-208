import validators
from .guardpoint_error import GuardPointError

from .guardpoint_dataclasses import CardholderCustomizedField


class CustomizedFieldsAPI:

    def update_custom_fields(self, cardholder_uid: str, customFields: CardholderCustomizedField):
        if not validators.uuid(cardholder_uid):
            raise ValueError(f'Malformed Cardholder UID {cardholder_uid}')

        url = "/odata/API_CardholderCustomizedFields"
        url_query_params = f"({cardholder_uid})"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            # 'IgnoreNonEditable': ''
        }

        ch = customFields.dict(changed_only=True)

        code, json_body = self.gp_json_query("PATCH", headers=headers, url=(url + url_query_params), json_body=ch)

        if code != 204:  # HTTP NO_CONTENT
            if 'error' in json_body:
                raise GuardPointError(json_body['error'])
            elif 'message' in json_body:
                raise GuardPointError(json_body['message'])
            else:
                raise GuardPointError(str(code))

        return True
