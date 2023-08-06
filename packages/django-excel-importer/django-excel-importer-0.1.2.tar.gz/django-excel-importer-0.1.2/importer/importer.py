#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2023/4/14 17:00
# @Author  : Hubert Shelley
# @Project  : django_excel_importer
# @FileName: importer.py
# @Software: IntelliJ IDEA
"""
import abc
import re
import typing

from django.db.models import Model
from openpyxl import load_workbook, Workbook
from rest_framework.generics import CreateAPIView

from importer.exception import ImporterItemException, ImporterException
from importer.serializer import FileUploadSerializer


class Importer(CreateAPIView):
    """
    Django Excel 导入类
    基于Django模型字段进行数据校验
    并对每一条数据进行校验，校验通过后的数据进行批量导入
    校验错误的数据返回错误信息，不进行导入，以便用户修改后重新导入

    导入字段支持自主配置，支持自定义校验规则
    例如:
    valid_fields = {
        "department": {
            "startswith": {
                "field": "company",
                "error_type": "逻辑错误",
                "message": "部门必须以公司开头",
            },
        },
        "company_address": {
            "required": True
        },
    }

    错误信息进行格式化，方便用户查看
    错误格式：
    {
        "cursor": {
            "row": row,
            "column": column
        },
        "content": content,
        "error_type": error_type,
        "error": message
    }
    """
    serializer_class = FileUploadSerializer
    valid_fields = None
    model: Model = None
    model_fields_dict = None
    model_fields_dict_index = None
    # 标题行
    head_row = 1
    # 从第几行开始读取数据
    content_row = 2

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        file = data.get("file")
        excel: Workbook = load_workbook(file)
        return self.import_excel(excel)

    @abc.abstractmethod
    def handler_validated_instances(self, validated_instances: typing.Union[typing.List[Model], typing.List[None]]):
        """
        处理校验通过的实例
        :param validated_instances:
        :return:
        """
        pass

    def import_excel(self, excel):
        """
        导入Excel
        :param excel:
        :return:
        """
        sheet = excel.active
        rows = sheet.rows
        header = []
        errors = []
        validated_instances = []
        row_index = 1
        total = 0
        for row in rows:
            if row_index == self.head_row:
                header = [cell.value for cell in row]
                row_index += 1
                continue
            if row_index < self.content_row:
                row_index += 1
                continue
            total += 1
            data = {}
            for index, cell in enumerate(row):
                data[header[index]] = cell.value
            data = self.clean_data(data)
            try:
                instance = self.validate(data)
                validated_instances.append(instance)
            except ImporterException as e:
                for error in e.errors:
                    errors.append(
                        self.handle_error(
                            row[0].row,
                            self.model_fields_dict_index[error.key] if error.key else "",
                            data.get(error.key) if error.key else "",
                            **self.handle_exception(error)
                        )
                    )
        self.handler_validated_instances(validated_instances)
        if errors:
            return self.handle_error_response(errors, validated_instances, total)
        return self.handle_success_response(validated_instances, total)

    def handle_exception(self, exc: ImporterItemException) -> typing.Dict[str, str]:
        """
        处理异常
        :param exc:
        :return:
        """
        exec_mes = {
            "error_type": exc.error_type,
            "message": exc.message
        }
        return exec_mes

    def handle_model_fields_dict(self):
        """
        处理模型字段字典
        :return:
        """
        self.model_fields_dict = {}
        custom_head_dict = {
            k: v["head"] for k, v in self.valid_fields.items() if isinstance(v, dict) and v.get("head")
        }
        for field in self.model._meta.fields:
            if field.name in custom_head_dict.keys():
                self.model_fields_dict[custom_head_dict.pop(field.name)] = field.name
            else:
                self.model_fields_dict[field.verbose_name] = field.name
        for key in custom_head_dict.keys():
            if '.' in key:
                if custom_head_dict[key] in self.model_fields_dict.keys():
                    self.model_fields_dict[custom_head_dict[key]] = key
                    continue
                field_name = key.split('.')[0]
                if field_name in self.model_fields_dict.values():
                    for k, v in self.model_fields_dict.items():
                        if v == field_name:
                            if custom_head_dict[key] == k:
                                self.model_fields_dict[k] = key
                            else:
                                self.model_fields_dict[custom_head_dict[key]] = key
                            break
        self.model_fields_dict_index = {v: k for k, v in self.model_fields_dict.items()}

    def clean_data(self, data):
        """
        清洗数据
        :param data:
        :return:
        """
        if not self.model_fields_dict:
            self.handle_model_fields_dict()
        return_data = {}
        keys = self.model_fields_dict.keys()
        for key, value in data.items():
            if key in keys:
                return_data[self.model_fields_dict[key]] = value
        return return_data

    def handle_success_response(self, validated_instances: typing.Union[typing.List[Model], typing.List[None]],
                                total: int):
        """
        处理成功响应

        :param total: 导入数据总数
        :param validated_instances: 成功数据实体
        :return:
        """
        return []

    def handle_error_response(self, errors, validated_instances: typing.Union[typing.List[Model], typing.List[None]],
                              total: int):
        """
        处理错误响应

        :param total: 导入数据总数
        :param validated_instances: 成功数据实体
        :param errors: 错误消息
        :return:
        """
        return errors

    def handle_error(self, row, column, content, error_type, message):
        """
        错误信息
        :param row: 行
        :param column: 列
        :param content: 内容
        :param error_type: 错误类型
        :param message: 错误信息
        :return:
        """
        return {
            "cursor": {
                "row": row,
                "column": column
            },
            "content": content,
            "error_type": error_type,
            "error": message
        }

    def tidy_data(self, data: dict) -> dict:
        """
        整理数据
        :param data:
        :return:
        """

        def tidy_data(_data: dict, _keys: list, _value):
            if not _keys:
                return _value
            _key = _keys.pop(0)
            if _key not in _data.keys():
                _data[_key] = {}
            _data[_key] = tidy_data(_data[_key], _keys, _value)
            return _data

        tidied_data: dict = {}
        for key, value in data.items():
            if '.' not in key:
                tidied_data[key] = value
                continue
            keys = key.split('.')
            tidied_data[keys[0]] = tidy_data(tidied_data.get(keys[0], {}), keys[1:], value)
        return tidied_data

    def validate(self, data):
        """
        校验数据
        :param data:
        :return:
        """
        error = ImporterException()
        for key in self.valid_fields.keys():
            e = self.import_validate(key, data, self.valid_fields.get(key))
            if e:
                error.append(e)
        data = self.tidy_data(data)
        try:
            instance = self.model(**data)
            try:
                instance.full_clean()
            except Exception as e:
                error.append(e)
            if error.has_error():
                raise error
            return instance
        except Exception as e:
            error.append(e)
            raise error

    def import_validate(self, key: str, data: dict, valid_field: dict):
        """
        导入校验
        :param key:
        :param data:
        :param valid_field:
        :return:
        """
        if not valid_field:
            return None
        value = data.get(key)
        if valid_field:
            if valid_field.get("func"):
                try:
                    data[key] = valid_field.get("func")(value)
                except Exception as e:
                    return ImporterItemException(key=key, error_type="计算异常", message=str(e))
            if valid_field.get("required") and not value:
                return ImporterItemException(key=key, error_type="必填项", message="这是必填字段")
            if valid_field.get("max_length") and len(value) > valid_field.get("max_length"):
                return ImporterItemException(key=key, error_type="长度异常", message="超过最长长度")
            if valid_field.get("min_length") and len(value) < valid_field.get("min_length"):
                return ImporterItemException(key=key, error_type="长度异常", message="少于最段长度")
            if valid_field.get("max_value") and value > valid_field.get("max_value"):
                return ImporterItemException(key=key, error_type="数值异常",
                                             message=f"超过最大值{valid_field.get('max_value')}")
            if valid_field.get("min_value") and value < valid_field.get("min_value"):
                return ImporterItemException(key=key, error_type="数值异常",
                                             message=f"少于最小值{valid_field.get('min_value')}")
            if valid_field.get("choices") and value not in valid_field.get("choices"):
                return ImporterItemException(key=key, error_type="数值异常", message="不在选项中")
            if valid_field.get("regex") and not re.match(valid_field.get("regex"), value):
                return ImporterItemException(key=key, error_type="数值异常", message="不符合数值规则")
            if valid_field.get("unique") and self.model.objects.filter(**{key: value}).exists():
                return ImporterItemException(key=key, error_type="", message="")
            for _key, _value in valid_field.items():
                if not isinstance(_value, dict):
                    continue
                if _key in dir(value):
                    if isinstance(getattr(value, _key), typing.Callable):
                        if "value" in _value.keys():
                            if not getattr(value, _key)(_value.get("value")):
                                return ImporterItemException(key=key, error_type=_value.get("error_type", "未定义类型"),
                                                             message=_value.get("message", "未定义错误消息"))
                        if "field" in _value.keys():
                            if not getattr(value, _key)(data.get(_value.get("field"))):
                                return ImporterItemException(key=key, error_type=_value.get("error_type", "未定义类型"),
                                                             message=_value.get("message", "未定义错误消息"))
        return None
