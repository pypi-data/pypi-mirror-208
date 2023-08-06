from NEMO.admin import AtLeastOneRequiredInlineFormSet
from NEMO.utilities import format_datetime
from django import forms
from django.contrib.admin import ModelAdmin, TabularInline, display, register, widgets
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from NEMO_billing.cap_discount.customization import CAPDiscountCustomization
from NEMO_billing.cap_discount.models import CAPDiscount, CAPDiscountAmount, CAPDiscountConfiguration, CAPDiscountTier
from NEMO_billing.invoices.models import BillableItemType
from NEMO_billing.utilities import disable_form_field


class IntMultipleChoiceField(forms.MultipleChoiceField):
    def prepare_value(self, value):
        if value is None:
            return value
        if type(value) is list:
            return [int(val) for val in value]
        return value.split(",")

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages["invalid_list"], code="invalid_list")
        return ",".join([str(val) for val in value])

    def validate(self, value):
        """Validate that the input is a list or tuple."""
        if self.required and not value:
            raise ValidationError(self.error_messages["required"], code="required")
        # Validate that each value in the value list is in self.choices.
        for val in value.split(","):
            if not self.valid_value(val):
                raise ValidationError(
                    self.error_messages["invalid_choice"],
                    code="invalid_choice",
                    params={"value": val},
                )


class CAPDiscountAmountInline(TabularInline):
    model = CAPDiscountAmount
    readonly_fields = ("new_charges",)
    extra = 1


class CAPDiscountTierAdminFormset(AtLeastOneRequiredInlineFormSet):
    pass


class CAPDiscountTierInline(TabularInline):
    model = CAPDiscountTier
    formset = CAPDiscountTierAdminFormset
    extra = 1
    min_num = 1

    def __init__(self, parent_model, admin_site):
        if parent_model == CAPDiscount:
            self.exclude = ["cap_discount_configuration"]
        else:
            self.exclude = ["cap_discount"]
        super().__init__(parent_model, admin_site)


class CAPDiscountConfigurationForm(forms.ModelForm):
    charge_types = IntMultipleChoiceField(
        choices=BillableItemType.choices(),
        required=True,
        widget=widgets.FilteredSelectMultiple(verbose_name="Types", is_stacked=False),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("instance"):
            for field_name in ["core_facility", "rate_category", "split_by_user"]:
                disable_form_field(self, field_name)
        self.fields["charge_types"].initial = CAPDiscountCustomization.get("cap_billing_default_billable_types")
        self.fields["reset_interval"].initial = CAPDiscountCustomization.get("cap_billing_default_interval")
        self.fields["reset_frequency"].initial = CAPDiscountCustomization.get("cap_billing_default_frequency")

    class Meta:
        model = CAPDiscountConfiguration
        fields = "__all__"


class CAPDiscountForm(forms.ModelForm):
    charge_types = IntMultipleChoiceField(
        choices=BillableItemType.choices(),
        required=True,
        widget=widgets.FilteredSelectMultiple(verbose_name="Types", is_stacked=False),
    )

    class Meta:
        model = CAPDiscount
        fields = "__all__"


@register(CAPDiscount)
class CAPDiscountAdmin(ModelAdmin):
    form = CAPDiscountForm
    inlines = [CAPDiscountTierInline, CAPDiscountAmountInline]
    list_display = (
        "id",
        "account",
        "core_facility",
        "rate_category",
        "user",
        "current_amount",
        "discount_display",
        "reset_frequency_display",
        "next_reset_display",
    )
    list_filter = ("configuration__core_facility", "configuration__rate_category", "account", "user")

    @display(ordering="configuration__core_facility", description="Core facility")
    def core_facility(self, cap_discount: CAPDiscount):
        return cap_discount.configuration.core_facility

    @display(ordering="configuration__rate_category", description="Rate category")
    def rate_category(self, cap_discount: CAPDiscount):
        return cap_discount.configuration.rate_category

    @display(description="Reset frequency")
    def reset_frequency_display(self, cap_discount: CAPDiscount):
        return cap_discount.get_recurrence_display() or "-"

    @display(ordering="capdiscounttier", description="Discount")
    def discount_display(self, cap_discount: CAPDiscount):
        return mark_safe("<br>".join(str(tier) for tier in cap_discount.capdiscounttier_set.all()))

    @display(description="Next reset")
    def next_reset_display(self, cap_discount: CAPDiscount):
        return format_datetime(cap_discount.next_reset(), "F Y") if cap_discount.next_reset() else "-"

    @display(description="Current amount")
    def current_amount(self, cap_discount: CAPDiscount):
        return cap_discount.latest_amount().end


@register(CAPDiscountConfiguration)
class CAPDiscountConfigurationAdmin(ModelAdmin):
    form = CAPDiscountConfigurationForm
    inlines = [CAPDiscountTierInline]
    list_display = (
        "id",
        "core_facility",
        "rate_category",
        "discount_display",
        "reset_frequency_display",
    )
    list_filter = ("core_facility", "rate_category")

    @display(description="Reset frequency")
    def reset_frequency_display(self, cap_discount: CAPDiscountConfiguration):
        return cap_discount.get_recurrence_interval_display() or "-"

    @display(ordering="capdiscounttier", description="Discount")
    def discount_display(self, cap_discount: CAPDiscount):
        return mark_safe("<br>".join(str(tier) for tier in cap_discount.capdiscounttier_set.all()))
