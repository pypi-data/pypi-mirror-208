"""IoT Core API endpoints implemented into Python methods.

Typical usage example:

```
from iotcoreapi import iotcoreapi

API_Host = '[base-url]'
API_Port = 56000
NexusToken = 'xxxxxxxxxxxxxxxxx'
version = 'v3'
logger = [logging.Logger object. Can be None or ignored]

iot_api = IoTCoreAPI(API_Host, API_Port, NexusToken, version, logger)

# Read all tags from API catalogue
tags = iot_api.catalogue_tags()
```
"""

from iotcoreapi.iotcoreapi import IoTCoreAPI
