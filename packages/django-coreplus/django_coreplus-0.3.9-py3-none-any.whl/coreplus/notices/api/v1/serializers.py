from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags import humanize

from notifications.models import Notification
from rest_framework import serializers
from push_notifications.api.rest_framework import (
    UniqueRegistrationSerializerMixin,
    DeviceSerializerMixin,
)
from ...models import FirebaseDevice


class ContentTypeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ContentType
        fields = "__all__"

    def get_name(self, obj) -> str:
        return f"{obj.app_label}.{obj.model}"


class NotificationSerializer(serializers.ModelSerializer):
    actor_content_type = ContentTypeSerializer()
    target_content_type = ContentTypeSerializer()
    action_object_content_type = ContentTypeSerializer()
    data = serializers.DictField()
    target_object_id = serializers.IntegerField()
    actor_object_id = serializers.IntegerField()
    action_object_object_id = serializers.IntegerField()
    humanize_time = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Notification
        fields = "__all__"

    def validate(self, attrs):
        # TODO: Add validation for data
        return super().validate(attrs)

    def get_humanize_time(self, obj):
        return humanize.naturaltime(obj.timestamp)


class FirebaseDeviceSerializer(
    UniqueRegistrationSerializerMixin, serializers.ModelSerializer
):
    class Meta(DeviceSerializerMixin.Meta):
        model = FirebaseDevice
        fields = (
            "id",
            "name",
            "registration_id",
            "device_id",
            "active",
            "date_created",
            "cloud_message_type",
            "application_id",
        )
        extra_kwargs = {"id": {"read_only": False, "required": False}}
