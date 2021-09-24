from django import template
from memberships.models import Application, Contribution, Member, MemberChild, MemberContribution, CustomDocument

register = template.Library()

@register.inclusion_tag('memberships/tags/family_dashboard.html', takes_context=True)
def family_dashboard (context):
    children = MemberChild.objects.filter(member=context['member'])
    
    return {
        'member': context['member'],
        'children': children,
        'request': context['request'],
        
    }

@register.inclusion_tag('memberships/tags/contribution_dashboard.html', takes_context=True)
def contribution_dashboard (context):
    contribution = Contribution.objects.filter(is_active=True).first()
    if contribution:
        if 'member' in context:
            try:
                member_contribution = MemberContribution.objects.get(member=context['member'], contribution=contribution)
            except MemberContribution.DoesNotExist:
                member_contribution = None
    
    else:
        contribution = None

    # For tests
    # contribution = None
    # member_contribution = None

    return {
        'request': context['request'],
        'contribution': contribution,
        'member_contribution': member_contribution
    }

# Application stuff for Dashboard
@register.inclusion_tag('memberships/tags/application_dashboard.html', takes_context=True)
def application_dashboard (context):
    try:
        # member = Member.objects.get(pk=context['member'].id)

        application = Application.objects.filter(is_active=True).first()
        if application:
            application = application.prepare(context['member'])

    except Exception as e:
        # print (e)
        application = None

    return {
        'request': context['request'],
        'application': application
    }

# Application stuff for dedicated page
@register.inclusion_tag('memberships/tags/applications_account.html', takes_context=True)
def applications_account (context):
    try:
        member = Member.objects.get(pk=context['member'].id)

        _ = Application.objects.all()
        applications = []

        for application in _:
            applications.append(
                application.prepare(member)
            )    

    except Exception as e:
        print (e)
        applications = None

    return {
        'url': context['url'],
        'request': context['request'],
        'applications': applications
    }

@register.inclusion_tag('memberships/tags/documents_page.html', takes_context=True)
def documents_page (context):

    return {
        'request': context['request'],
        'documents': CustomDocument.objects.all()
    }