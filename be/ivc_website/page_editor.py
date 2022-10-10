import json
from django.conf import settings


def edit_home_page(home_content, text_to_edit, input_edit):
    # first key is the section (e.g. goals, explore, ...) and second key is the part of section (e.g. title)
    first_key, second_key = input_edit.split(".")
    home_content[first_key][second_key] = text_to_edit  # update the home content

    # save the update
    if settings.DEBUG:
        with open('ivc_website/static/ivc_website/home_content.json', "r", encoding="utf-8") as f:
            json.dump(home_content, f)
    else:
        try:
            with open(f'{settings.STATIC_ROOT}/ivc_website/home_content.json', "r", encoding="utf-8") as f:
                json.dump(home_content, f)
        except:  # in case if error occurred
            pass
