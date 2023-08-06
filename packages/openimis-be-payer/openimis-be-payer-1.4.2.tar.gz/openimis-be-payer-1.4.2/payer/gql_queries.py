import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from django import forms
from django.utils.translation import gettext_lazy

from invoice.apps import InvoiceConfig
from .apps import PayerConfig
from .models import Payer
from core import ExtendedConnection
from product.schema import ProductGQLType
import django_filters
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied


class IntegerFilter(django_filters.NumberFilter):
    field_class = forms.IntegerField


class PayerFilter(django_filters.FilterSet):
    location = IntegerFilter(
        lookup_expr=["exact"],
        method="filter_location",
        label=gettext_lazy("Filter payers with or below a given location ID"),
    )

    def filter_location(self, queryset, name, value):
        return queryset.filter(Q(location__id=value) | Q(location__parent__id=value))

    class Meta:
        model = Payer
        fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "name": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "phone": ["exact", "icontains"],
            "type": ["exact"],
        }


class FundingGQLType(graphene.ObjectType):
    pay_date = graphene.Date()
    amount = graphene.Decimal()
    receipt = graphene.String()
    uuid = graphene.UUID()
    product = graphene.Field(ProductGQLType)

    def resolve_pay_date(self, info, **kwargs):
        if not info.context.user.has_perms(PayerConfig.gql_query_payers_perms):
            raise PermissionDenied(_("unauthorized"))
        return self.pay_date

    def resolve_amount(self, info, **kwargs):
        if not info.context.user.has_perms(PayerConfig.gql_query_payers_perms):
            raise PermissionDenied(_("unauthorized"))
        return self.amount

    def resolve_receipt(self, info, **kwargs):
        if not info.context.user.has_perms(PayerConfig.gql_query_payers_perms):
            raise PermissionDenied(_("unauthorized"))
        return self.receipt

    def resolve_uuid(self, info, **kwargs):
        if not info.context.user.has_perms(PayerConfig.gql_query_payers_perms):
            raise PermissionDenied(_("unauthorized"))
        return self.uuid

    def resolve_product(self, info, **kwargs):
        if not info.context.user.has_perms(PayerConfig.gql_query_payers_perms):
            raise PermissionDenied(_("unauthorized"))
        return self.policy.product


class FundingConnection(graphene.Connection):
    class Meta:
        node = FundingGQLType

    total_count = graphene.Int()

    def resolve_total_count(self, info, **kwargs):
        if not info.context.user.has_perms(PayerConfig.gql_query_payers_perms):
            raise PermissionDenied(_("unauthorized"))
        return len(self.iterable)


class PayerGQLType(DjangoObjectType):

    fundings = graphene.relay.ConnectionField(FundingConnection)

    def resolve_fundings(self, info, **kwargs):
        if not info.context.user.has_perms(PayerConfig.gql_query_payers_perms):
            raise PermissionDenied(_("unauthorized"))
        return (
            self.premiums.filter(validity_to__isnull=True).order_by("-pay_date").all()
        )

    class Meta:
        model = Payer
        interfaces = (graphene.relay.Node,)
        filterset_class = PayerFilter
        connection_class = ExtendedConnection

        exclude_fields = ("premiums",)
