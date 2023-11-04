from django.db import models
#extracted rules
class Rule(models.Model):
    rule_id = models.AutoField(primary_key=True)
    lhs = models.CharField(max_length=255)  # Assuming a maximum length of 255 characters for product names
    rhs = models.CharField(max_length=255)
    confidence = models.FloatField()