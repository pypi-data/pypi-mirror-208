from typing import Dict, Any, Union, List
import warnings


# Generate using ChatGPT https://chat.openai.com/
def filter_dict(d: Dict[str, Any], keys_to_exclude: Union[str, List[str]], required_key: str = None) -> Union[Dict[str, Any], None]:
    """
    Returns a new dictionary that contains all the key-value pairs from `d`, except for those whose keys are in `keys_to_exclude`.

    If `required_key` is provided and it exists in `d`, the function will return a new dictionary that contains all the key-value pairs from `d`, except for those whose keys are in `keys_to_exclude`. If `required_key` is not provided or it does not exist in `d`, the function will return None.

    Args:
    - d: A dictionary whose keys are strings and whose values can be of any type.
    - keys_to_exclude: A string or list of strings representing the keys to be excluded from the output dictionary.
    - required_key: An optional string representing a key that must exist in `d` for the function to return a dictionary. If `required_key` is not provided or it does not exist in `d`, the function will return None.

    Returns:
    - A new dictionary that contains all the key-value pairs from `d`, except for those whose keys are in `keys_to_exclude`, or None if `required_key` is not provided or it does not exist in `d`.
    """
    if isinstance(keys_to_exclude, str):
        keys_to_exclude = [keys_to_exclude]
    if required_key is not None and required_key not in d:
        return None
    return {k: v for k, v in d.items() if k not in keys_to_exclude}


class OrkgResponse(object):

    @property
    def succeeded(self) -> bool:
        return str(self.status_code)[0] == '2'

    def __init__(self, response, status_code: str, content: Union[list, dict], url: str, paged: bool):
        if response is None and status_code is None and content is None and url is None:
            raise ValueError("either response should be provided or content with status code")
        if not paged:
            warnings.warn("You are running an out-of-date ORKG backend! GET (i.e., listing) calls now provide pagination information", DeprecationWarning)
        if (response is not None and str(response.status_code)[0] != '2') or (status_code is not None and content is not None and status_code[0] != '2'):
            self.status_code = response.status_code if response is not None else status_code
            self.content = response.content if response is not None else content
            self.page_info = None
            return
        if response is not None:
            self.status_code = response.status_code
            self.content = response.json() if len(response.content) > 0 else response.content
            self.page_info = None
            if paged and isinstance(self.content, dict):
                self.page_info = filter_dict(self.content, 'content', 'pageable')
                self.content = self.content['content'] if 'content' in self.content else self.content
            self.url = response.url
        if status_code is not None and content is not None:
            self.status_code = status_code
            self.content = content
            self.page_info = None
            if paged and isinstance(self.content, dict) and 'content' in content:
                self.page_info = filter_dict(self.content, 'content', 'pageable')
                self.content = self.content['content']
            self.url = url

    def __repr__(self):
        return "%s %s" % ("(Success)" if self.succeeded else "(Fail)", self.content)

    def __str__(self):
        return self.content


class OrkgUnpaginatedResponse(object):

    @property
    def all_succeeded(self) -> bool:
        return all([response.succeeded for response in self.responses])

    def __init__(self, responses: List[OrkgResponse]):
        self.responses = responses
        self.content: List[dict] = []

        for response in self.responses:
            self.content.extend(response.content)
