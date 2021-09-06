from django import template
from memberships.models import Contribution, MemberContribution

register = template.Library()

@register.inclusion_tag('memberships/tags/contribution_dashboard.html', takes_context=True)
def contribution_dashboard (context):
    # contribution = Contribution.objects.filter(is_active=True).first()
    # if contribution:
    #     if 'member' in context:
    #         try:
    #             member_contribution = MemberContribution.objects.get(member=context['member'], contribution=contribution)
    #         except MemberContribution.DoesNotExist:
    #             member_contribution = None
    
    # else:
    #     contribution = None
    contribution = None
    member_contribution = None

    return {
        'request': context['request'],
        'contribution': contribution,
        'member_contribution': member_contribution
    }