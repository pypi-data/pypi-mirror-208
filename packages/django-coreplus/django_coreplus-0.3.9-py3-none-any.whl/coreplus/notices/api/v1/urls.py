from push_notifications.api.rest_framework import (
    APNSDeviceAuthorizedViewSet,
    GCMDeviceAuthorizedViewSet,
    WebPushDeviceAuthorizedViewSet,
)
from rest_framework.routers import DefaultRouter

from coreplus.notices.api.v1.viewsets import NotificationViewSet, FirebaseDeviceViewSet

router = DefaultRouter()
router.register("apnsdevices", APNSDeviceAuthorizedViewSet, "apnsdevice")
router.register("gcmdevices", GCMDeviceAuthorizedViewSet, "gcmdevice")
router.register("webpushdevices", WebPushDeviceAuthorizedViewSet, "webpushdevice")
router.register("fcmdevices", FirebaseDeviceViewSet, "firebasedevice")
router.register("notification", NotificationViewSet, "notification")

urlpatterns = [] + router.urls
