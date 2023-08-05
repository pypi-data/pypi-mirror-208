import os
import json
from lxml import html



def parse_form(data, **fields):
    """
    Parses and HTML form and returns data required to submit it.
    """
    page = html.fromstring(data)
    form = page.xpath("//form")[0]
    url = form.xpath("./@action")[0]
    post_data = {**fields}
    for field in form.xpath("./input"):
        post_data[field.xpath("./@name")[0]] = field.xpath("./@value")[0]
    return {"url": url, "post_data": post_data}


def loginrequired(func):
    """
    Decorator that ensures the user is authenticated.
    """
    def wrapper(self, *args, **kwargs):
        if self.token is None:
            raise Exception("Login required but not yet performed")
        return func(self, *args, **kwargs)
    return wrapper

def save_json(json_data, json_filename: str = 'info.json'):
    if not os.path.isdir('json'):
        os.mkdir('json')
    
    with open(f"json{os.sep}{json_filename}", 'w', encoding='UTF-8') as outfile:
        json.dump(json_data, outfile)
    return True
