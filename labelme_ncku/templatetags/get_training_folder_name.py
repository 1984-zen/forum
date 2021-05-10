from django import template

register = template.Library()

@register.filter
def get_training_folder_name(value):
    training_folder_name_index = value.split("/").index('training_folder_name')

    training_folder_name = value.split("/")[training_folder_name_index + 1]

    return training_folder_name