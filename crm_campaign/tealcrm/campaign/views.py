from __future__ import print_function
import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
limit = 50
offset = 0

try:
    api_response = api_instance.get_smtp_templates(limit=limit, offset=offset)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SMTPApi->get_smtp_templates: %s\n" % e)