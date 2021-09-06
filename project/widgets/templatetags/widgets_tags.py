from django import template
from widgets.models import Place

register = template.Library()

def _place_menu (context):
    return {
        'place': Place.objects.first(),
        'request': context['request'],
    }

@register.inclusion_tag('widgets/place_menu_widget.html', takes_context=True)
def place_menu (context):
    return _place_menu (context)

@register.inclusion_tag('widgets/place_menu_res_widget.html', takes_context=True)
def place_menu_res (context):
    return _place_menu (context)

@register.inclusion_tag('widgets/place_contact_widget.html', takes_context=True)
def place_contact (context):
    return _place_menu (context)  

@register.inclusion_tag('widgets/place_maps_widget.html', takes_context=True)
def place_maps (context):
    return _place_menu (context)  

@register.inclusion_tag('widgets/place_widget.html', takes_context=True)
def place (context):
    if 'foo' in context:
        print (context['foo'])

    return {
        'request': context['request'],
        'foo': context['foo']
    }