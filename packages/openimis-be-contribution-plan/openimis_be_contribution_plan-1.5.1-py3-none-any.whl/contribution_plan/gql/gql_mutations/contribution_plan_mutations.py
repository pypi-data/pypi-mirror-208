from contribution_plan.apps import ContributionPlanConfig
from core.gql.gql_mutations import DeleteInputType
from contribution_plan.services import ContributionPlanService
from core.gql.gql_mutations.base_mutation import BaseMutation, BaseDeleteMutation, BaseReplaceMutation, \
    BaseHistoryModelCreateMutationMixin, BaseHistoryModelUpdateMutationMixin, \
    BaseHistoryModelDeleteMutationMixin, BaseHistoryModelReplaceMutationMixin
from contribution_plan.gql.gql_mutations import ContributionPlanInputType, ContributionPlanUpdateInputType, \
    ContributionPlanReplaceInputType
from contribution_plan.models import ContributionPlan
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied, ValidationError


class CreateContributionPlanMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_class = "ContributionPlanMutation"
    _mutation_module = "contribution_plan"
    _model = ContributionPlan

    class Input(ContributionPlanInputType):
        pass

    @classmethod
    def _validate_mutation(cls, user, **data):
        super()._validate_mutation(user, **data)
        if not user.has_perms(ContributionPlanConfig.gql_mutation_create_contributionplan_perms):
            raise PermissionDenied(_("unauthorized"))
        if ContributionPlanService.check_unique_code(data['code']):
            raise ValidationError(_("mutation.cp_code_duplicated"))


class UpdateContributionPlanMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_class = "ContributionPlanMutation"
    _mutation_module = "contribution_plan"
    _model = ContributionPlan

    class Input(ContributionPlanUpdateInputType):
        pass

    @classmethod
    def _validate_mutation(cls, user, **data):
        super()._validate_mutation(user, **data)
        if not user.has_perms(ContributionPlanConfig.gql_mutation_update_contributionplan_perms):
            raise PermissionDenied(_("unauthorized"))


class DeleteContributionPlanMutation(BaseHistoryModelDeleteMutationMixin, BaseDeleteMutation):
    _mutation_class = "ContributionPlanMutation"
    _mutation_module = "contribution_plan"
    _model = ContributionPlan

    class Input(DeleteInputType):
        pass

    @classmethod
    def _validate_mutation(cls, user, **data):
        super()._validate_mutation(user, **data)
        if not user.has_perms(ContributionPlanConfig.gql_mutation_delete_contributionplan_perms):
            raise PermissionDenied(_("unauthorized"))


class ReplaceContributionPlanMutation(BaseHistoryModelReplaceMutationMixin, BaseReplaceMutation):
    _mutation_class = "ContributionPlanMutation"
    _mutation_module = "contribution_plan"
    _model = ContributionPlan

    class Input(ContributionPlanReplaceInputType):
        pass

    @classmethod
    def _validate_mutation(cls, user, **data):
        super()._validate_mutation(user, **data)
        if not user.has_perms(ContributionPlanConfig.gql_mutation_replace_contributionplan_perms):
            raise PermissionDenied(_("unauthorized"))
