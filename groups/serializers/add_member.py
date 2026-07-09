from rest_framework import serializers


class AddGroupMemberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=16)
