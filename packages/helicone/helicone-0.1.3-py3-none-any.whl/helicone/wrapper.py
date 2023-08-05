import openai
from typing import Any, Dict, Optional
from utils import api_resources_classes


class HeliconeOpenAIWrapper:
    @staticmethod
    def add_helicone_headers(kwargs: Dict[str, Any], properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = kwargs.get("headers", {})
        headers["Helicone-Auth"] = f"Bearer {openai.api_key}"

        if properties:
            for key, value in properties.items():
                headers[f"Helicone-Property-{key}"] = value

        kwargs["headers"] = headers
        return kwargs


def create_wrapped_method(method):
    def wrapped_method(*args, **kwargs):
        properties = kwargs.pop("properties", None)
        kwargs = HeliconeOpenAIWrapper.add_helicone_headers(kwargs, properties)
        return method(*args, **kwargs)
    return wrapped_method


for api_resource_class, method_name in api_resources_classes:
    method = getattr(api_resource_class, method_name)
    setattr(api_resource_class, method_name, create_wrapped_method(method))
