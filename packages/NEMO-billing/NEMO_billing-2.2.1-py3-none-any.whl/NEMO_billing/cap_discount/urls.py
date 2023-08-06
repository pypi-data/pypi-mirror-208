from django.urls import path

from NEMO_billing.cap_discount import views

urlpatterns = [
    path("usage_cap_discounts/", views.usage_cap_discounts, name="usage_cap_discounts"),
    path("usage_cap_discounts_user/<int:user_id>/", views.usage_cap_discounts_user, name="usage_cap_discounts_user"),
    path(
        "usage_cap_discounts_account/<int:account_id>/",
        views.usage_cap_discounts_account,
        name="usage_cap_discounts_account",
    ),
]
