#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2023/4/18 10:15
# @Author  : Hubert Shelley
# @Project  : django_excel_importer
# @FileName: exception.py
# @Software: IntelliJ IDEA
"""
import typing

from django.core.exceptions import ValidationError


class ImporterItemException(Exception):
    """
    导入异常
    """

    def __init__(self, key="", error_type="", message=""):
        self.key = key
        self.error_type = error_type
        self.message = message


class ImporterException(Exception):
    """
    导入异常
    """

    def __init__(self):
        self.errors = []

    def append(self, error: typing.Union[ImporterItemException, Exception]):
        _error = []
        if isinstance(error, ValidationError):
            for key, value in error.error_dict.items():
                for message in value:
                    _error.append(
                        ImporterItemException(
                            key=key,
                            error_type="格式错误" if message.code != "null" else "必填项",
                            message="这是必填字段" if message.code == "null" else "",
                        )
                    )
        if isinstance(error, TypeError):
            _error.append(
                ImporterItemException(
                    key="",
                    error_type="数据错误",
                    message=error.__str__(),
                )
            )
        if isinstance(error, ImporterItemException):
            _error = [error]
        self.errors.extend(_error)

    def has_error(self):
        return len(self.errors) > 0
