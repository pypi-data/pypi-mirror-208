# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-08 17:08:41
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Rey's translate methods.
"""


from reytool.rrequest import request


def translate_baidu(text: str) -> str:
    """
    Use `fanyi.baidu.com` translated text.

    Parameters
    ----------
    text : Text to be translated.

    Retuens
    -------
    Translated text.
    """

    # Set parameters.
    url = r"https://fanyi.baidu.com/sug"
    data = {
        "kw": text
    }

    # Requests.
    response = request(url, data)
    response_data = response.json()["data"]

    # Handle result.
    if not len(response_data):
        return
    translate_data = response_data[0]["v"]
    translate_text = translate_data.split(";")[0].split(". ")[-1]

    return translate_text


def translate(text: str) -> str:
    """
    `translate` text.

    Parameters
    ----------
    text : Text to be translated.

    Retuens
    -------
    Translated text.
    """

    # Set parameters.
    translate_func = [
        translate_baidu
    ]

    # Translate.
    for func in translate_func:
        translate_text = func(text)
        if translate_text != None:
            return translate_text