from NEMO.decorators import accounting_or_user_office_or_manager_required
from NEMO.models import Account, User
from NEMO.views.usage import date_parameters_dictionary
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from NEMO_billing.cap_discount.models import CAPDiscount


@login_required
def usage_cap_discounts(request, user=None):
    if not user:
        user = request.user
    base_dictionary, start, end, kind, identifier = date_parameters_dictionary(request)
    base_dictionary["cap_discounts"] = CAPDiscount.objects.filter(user=user)
    return render(request, "cap_discount/usage_cap_discounts.html", base_dictionary)


@accounting_or_user_office_or_manager_required
@login_required
def usage_cap_discounts_user(request, user_id):
    return usage_cap_discounts(request, get_object_or_404(User, pk=user_id))


@accounting_or_user_office_or_manager_required
def usage_cap_discounts_account(request, account_id):
    base_dictionary, start, end, kind, identifier = date_parameters_dictionary(request)
    base_dictionary["cap_discounts"] = CAPDiscount.objects.filter(account=get_object_or_404(Account, pk=account_id))
    return render(request, "cap_discount/usage_cap_discounts.html", base_dictionary)
