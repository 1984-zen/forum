# -*- coding: utf-8 -*-

from django.db import models

class CustomManager(models.Manager):
    def preferred_order(self, *args, **kwargs):
        """Sort patterns by preferred order of Y then -- then N"""
        qs = self.get_queryset().filter(*args, **kwargs)
        qs = qs.annotate( custom_order=
            models.Case( 
                models.When(pref='Y', then=models.Value(0)),
                models.When(pref='--', then=models.Value(1)),
                models.When(pref='N', then=models.Value(2)),
                default=models.Value(3),
                output_field=models.IntegerField(), )
            ).order_by('custom_order', '-created_at'
        )
        return qs
    def make_category(self, *args, **kwargs):
        qs = self.get_queryset().filter(*args, **kwargs)
        qs = qs.annotate( category_color_code =
            models.Case( 
                models.When(category='null', then=models.Value('#FFFFFF')),
                models.When(category='medical', then=models.Value('#C4E1FF')),
                models.When(category='others', then=models.Value('#E8E8D0')),
                default=models.Value('#FFFFFF'),
                output_field=models.CharField(),)
            )
        return qs
    

    
    

# class MaleManager(models.Manager):
#     def get_query_set(self):
#         return super(MaleManager, self).get_query_set().filter(sex='M')
# class FemaleManager(models.Manager):
#     def get_query_set(self):
#         return super(FemaleManager, self).get_query_set().filter(sex='F')
# class Person(models.Model):
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
#     people = models.Manager()
#     men = MaleManager()
#     women = FemaleManager()