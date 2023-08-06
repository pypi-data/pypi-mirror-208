from django.contrib import admin, messages

# from django.http.response import HttpResponseRedirect
# from django.shortcuts import get_object_or_404
# from django.urls import re_path
from push_notifications.admin import DeviceAdmin
from django.utils.translation import gettext_lazy as _

from .models import Broadcast, FirebaseDevice


@admin.register(FirebaseDevice)
class FirebaseDeviceAdmin(DeviceAdmin):
    list_display = (
        "__str__",
        "device_id",
        "user",
        "active",
        "date_created",
        "cloud_message_type",
    )
    list_filter = ("active", "cloud_message_type")


@admin.register(Broadcast)
class BroadcastModelAdmin(admin.ModelAdmin):
    menu_order = 9
    model = Broadcast
    menu_label = _("Broadcasts")
    list_display = ["title", "message", "sent_counter", "last_sent_at"]
    list_filter = ["last_sent_at"]
    actions = ["send"]

    @admin.action(description=_("Send selected Broadcast message"))
    def send(self, request, queryset):
        try:
            for obj in queryset:
                obj.send(actor=request.user)
            self.message_user(
                request,
                level=messages.SUCCESS,
                message=_("Notification #{} sent.").format(obj.id),
            )
        except Exception as err:
            self.message_user(request, level=messages.ERROR, message=err)
