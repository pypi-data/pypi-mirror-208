#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2023/4/14 17:00
# @Author  : Hubert Shelley
# @Project  : django_excel_importer
# @FileName: importer.py
# @Software: IntelliJ IDEA
"""
from django.db.models import Model
from openpyxl import load_workbook, Workbook
from rest_framework.generics import CreateAPIView

from importer.serializer import FileUploadSerializer


class Importer(CreateAPIView):
    """
    Django Excel 导入类
    基于Django模型字段进行数据校验
    并对每一条数据进行校验，校验通过后的数据进行批量导入
    校验错误的数据返回错误信息，不进行导入，以便用户修改后重新导入
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
    model_fields_index = None
    model: Model = None
    model_fields_dict = None
    model_fields_dict_index = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        file = data.get("file")
        excel: Workbook = load_workbook(file)
        return self.import_excel(excel)

    def import_excel(self, excel):
        """
        导入Excel
        :param excel:
        :return:
        """
        sheet = excel.active
        rows = sheet.rows
        header = [cell.value for cell in next(rows)]
        errors = []
        for row in rows:
            data = {}
            for index, cell in enumerate(row):
                data[header[index]] = cell.value
            data = self.clean_data(data)
            try:
                self.validate(data)
            except Exception as e:
                errors.append(self.handle_error(row, 0, "cell.value", type(e).__name__, str(e)))
        if errors:
            return self.handle_error_response(errors)
        return self.handle_success_response()

    def handle_model_fields_dict(self):
        """
        处理模型字段字典
        :return:
        """
        self.model_fields_dict = {}
        for field in self.model.field_names:
            self.model_fields_dict[field.verbose_name] = field.name
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

    def handle_success_response(self):
        """
        处理成功响应
        :return:
        """
        return []

    def handle_error_response(self, errors):
        """
        处理错误响应
        :param errors:
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

    def validate(self, data):
        """
        校验数据
        :param data:
        :return:
        """
        instance = self.model(**data)
        try:
            instance.full_clean()
        except Exception as e:
            raise e
