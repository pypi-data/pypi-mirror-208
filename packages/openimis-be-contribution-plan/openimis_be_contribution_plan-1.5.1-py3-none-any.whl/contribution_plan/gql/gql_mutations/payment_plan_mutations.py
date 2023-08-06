from core.gql.gql_mutations import DeleteInputType
from core.gql.gql_mutations.base_mutation import BaseMutation, BaseDeleteMutation, BaseReplaceMutation, \
    BaseHistoryModelCreateMutationMixin, BaseHistoryModelUpdateMutationMixin, \
    BaseHistoryModelDeleteMutationMixin, BaseHistoryModelReplaceMutationMixin
from contribution_plan.services import PaymentPlan as PaymentPlanService
from contribution_plan.gql.gql_mutations import PaymentPlanInputType, PaymentPlanUpdateInputType, \
    PaymentPlanReplaceInputType
from contribution_plan.apps import ContributionPlanConfig
from contribution_plan.models import PaymentPlan
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CreatePaymentPlanMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_class = "PaymentPlanMutation"
    _mutation_module = "contribution_plan"
    _model = PaymentPlan

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                ContributionPlanConfig.gql_mutation_create_paymentplan_perms):
            raise ValidationError(_("mutation.authentication_required"))
        if PaymentPlanService.check_unique_code(data['code']):
            raise ValidationError(_("mutation.payment_plan_code_duplicated"))

    class Input(PaymentPlanInputType):
        pass


class UpdatePaymentPlanMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_class = "PaymentPlanMutation"
    _mutation_module = "contribution_plan"
    _model = PaymentPlan

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                ContributionPlanConfig.gql_mutation_update_paymentplan_perms):
            raise ValidationError(_("mutation.authentication_required"))
        if PaymentPlanService.check_unique_code(data['code']):
            raise ValidationError(_("mutation.payment_plan_code_duplicated"))

    class Input(PaymentPlanUpdateInputType):
        pass


class DeletePaymentPlanMutation(BaseHistoryModelDeleteMutationMixin, BaseDeleteMutation):
    _mutation_class = "PaymentPlanMutation"
    _mutation_module = "contribution_plan"
    _model = PaymentPlan

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                ContributionPlanConfig.gql_mutation_delete_paymentplan_perms):
            raise ValidationError(_("mutation.authentication_required"))

    class Input(DeleteInputType):
        pass


class ReplacePaymentPlanMutation(BaseHistoryModelReplaceMutationMixin, BaseReplaceMutation):
    _mutation_class = "PaymentPlanMutation"
    _mutation_module = "contribution_plan"
    _model = PaymentPlan

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                ContributionPlanConfig.gql_mutation_replace_paymentplan_perms):
            raise ValidationError(_("mutation.authentication_required"))

    class Input(PaymentPlanReplaceInputType):
        pass
