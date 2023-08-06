#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2023/4/17 13:26
# @Author  : Hubert Shelley
# @Project  : django_excel_importer
# @FileName: serializer.py
# @Software: IntelliJ IDEA
"""
from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(label="导入文件(Excel)", required=True)
