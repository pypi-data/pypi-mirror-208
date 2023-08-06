
from rest_framework import serializers


class BaseInputReqSerializer(serializers.Serializer):
    input = serializers.JSONField(default=dict)


class BaseOutputRespSerializer(serializers.Serializer):
    output = serializers.JSONField()


class ErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()
    code = serializers.CharField()


class NotFoundSerializer(serializers.Serializer):
    detail = serializers.CharField()
    code = serializers.CharField()


class SuccessSerializer(serializers.Serializer):
    detail = serializers.CharField()
    code = serializers.CharField()
