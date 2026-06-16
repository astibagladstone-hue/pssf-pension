from django.db import models

class ContributionSchedule(models.Model):
    STATUS=[('RECEIVED','Received'),('LOADED','Loaded'),('APPROVED','Approved'),('POSTED','Posted')]
    employer=models.CharField(max_length=200)
    period=models.CharField(max_length=20)
    expected_amount=models.DecimalField(max_digits=14, decimal_places=2)
    received_amount=models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status=models.CharField(max_length=20, choices=STATUS, default='RECEIVED')

    @property
    def variance(self):
        return self.expected_amount-self.received_amount

class RemittanceCase(models.Model):
    TYPE=[('UNDER','Under-remittance'),('OVER','Over-remittance'),('NONE','Non-remittance')]
    employer=models.CharField(max_length=200)
    period=models.CharField(max_length=20)
    case_type=models.CharField(max_length=20, choices=TYPE)
    amount=models.DecimalField(max_digits=14, decimal_places=2)
    resolved=models.BooleanField(default=False)
