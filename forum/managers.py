# -*- coding: utf-8 -*-

from django.db import models

class CustomOrderManager(models.Manager):
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