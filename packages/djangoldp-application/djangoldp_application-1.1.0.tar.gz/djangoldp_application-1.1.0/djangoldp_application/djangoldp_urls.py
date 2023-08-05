from django.urls import path
from .views import (
    ApplicationViewSet,
    ApplicationDetailViewSet,
    mark_as_doing,
    mark_as_done,
    mark_as_failed,
)

urlpatterns = [
    path(
        "ansible/inventory/",
        ApplicationViewSet.as_view({"get": "list"}),
        name="ansible_inventory",
    ),
    path(
        "ansible/<slug:slug>/",
        ApplicationDetailViewSet.as_view({"get": "retrieve"}, lookup_field="slug"),
        name="ansible_inventory_detail",
    ),
    path(
        "ansible/<slug:slug>/doing/",
        mark_as_doing,
        name="ansible_inventory_mark_doing",
    ),
    path(
        "ansible/<slug:slug>/done/",
        mark_as_done,
        name="ansible_inventory_mark_done",
    ),
    path(
        "ansible/<slug:slug>/failed/",
        mark_as_failed,
        name="ansible_inventory_mark_failed",
    ),
]
