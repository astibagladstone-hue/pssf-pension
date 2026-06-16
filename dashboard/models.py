"""
PSSF Dashboard Models
Improved with proper indexes, constraints, and abstract base classes
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]

class Scheme(BaseModel):
    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    sponsor_name = models.CharField(max_length=255, db_index=True)
    date_established = models.DateField()
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('SUSPENDED', 'Suspended')], default='ACTIVE', db_index=True)
    description = models.TextField(blank=True)
    
    class Meta:
        indexes = [models.Index(fields=['code', 'status'])]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Member(BaseModel):
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('RETIRED', 'Retired'), ('DECEASED', 'Deceased'), ('WITHDRAWN', 'Withdrawn')]
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    
    member_number = models.CharField(max_length=50, unique=True, db_index=True)
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(db_index=True)
    national_id = models.CharField(max_length=50, unique=True, db_index=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='members', db_index=True)
    join_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    employer = models.CharField(max_length=255, blank=True, db_index=True)
    email = models.EmailField(blank=True, db_index=True)
    phone = models.CharField(max_length=30, blank=True)
    salary = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    next_of_kin_name = models.CharField(max_length=255, blank=True)
    next_of_kin_phone = models.CharField(max_length=30, blank=True)
    next_of_kin_relationship = models.CharField(max_length=100, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['scheme', 'status']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['join_date', 'status']),
        ]
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.member_number} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

class ContributionReceipt(BaseModel):
    TYPE_CHOICES = [('NORMAL', 'Normal'), ('EXCHEQUER', 'Exchequer')]
    STATUS_CHOICES = [('DRAFT', 'Draft'), ('POSTED', 'Posted'), ('ALLOCATED', 'Allocated'), ('REJECTED', 'Rejected')]
    
    receipt_no = models.CharField(max_length=50, unique=True, db_index=True)
    receipt_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='NORMAL', db_index=True)
    receipt_date = models.DateField(db_index=True)
    description = models.CharField(max_length=500)
    receipt_amount = models.DecimalField(max_digits=16, decimal_places=2, validators=[MinValueValidator(0)])
    allocated_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    unallocated_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='receipts', db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', db_index=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_reference = models.CharField(max_length=100, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['receipt_date', 'scheme']),
            models.Index(fields=['status', 'receipt_type']),
        ]
        ordering = ['-receipt_date']
    
    def __str__(self):
        return f"{self.receipt_no} - {self.receipt_amount}"
    
    def save(self, *args, **kwargs):
        self.unallocated_amount = self.receipt_amount - self.allocated_amount
        if self.unallocated_amount < 0:
            self.unallocated_amount = 0
        super().save(*args, **kwargs)

class MemberContribution(BaseModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='contributions', db_index=True)
    receipt = models.ForeignKey(ContributionReceipt, on_delete=models.CASCADE, related_name='line_items', null=True, blank=True, db_index=True)
    period_month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], db_index=True)
    period_year = models.IntegerField(db_index=True)
    employee_contribution = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    employer_contribution = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_contribution = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        indexes = [
            models.Index(fields=['period_year', 'period_month']),
            models.Index(fields=['member', 'period_year', 'period_month']),
        ]
        unique_together = [['member', 'period_year', 'period_month']]
        ordering = ['-period_year', '-period_month']
    
    def save(self, *args, **kwargs):
        self.total_contribution = self.employee_contribution + self.employer_contribution
        super().save(*args, **kwargs)

class Ticket(BaseModel):
    PRIORITY_CHOICES = [('LOW', 'Low'), ('NORMAL', 'Normal'), ('HIGH', 'High'), ('CRITICAL', 'Critical')]
    STATUS_CHOICES = [('NEW', 'New'), ('OPEN', 'Open'), ('IN_PROGRESS', 'In Progress'), ('ESCALATED', 'Escalated'), ('CLOSED', 'Closed'), ('ARCHIVED', 'Archived')]
    SOURCE_CHOICES = [('EMAIL', 'Email'), ('PHONE', 'Phone'), ('PORTAL', 'Portal'), ('WALK_IN', 'Walk-in'), ('OTHER', 'Other')]
    
    ticket_number = models.CharField(max_length=30, unique=True, db_index=True)
    subject = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets', db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW', db_index=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL', db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='EMAIL')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets', db_index=True)
    due_date = models.DateField(null=True, blank=True, db_index=True)
    is_overdue = models.BooleanField(default=False, db_index=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(blank=True)
    escalation_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_escalated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date', 'is_overdue']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"
    
    def save(self, *args, **kwargs):
        if self.due_date and timezone.now().date() > self.due_date and self.status not in ('CLOSED', 'ARCHIVED'):
            self.is_overdue = True
        super().save(*args, **kwargs)
    
    @property
    def days_open(self):
        if self.status in ('CLOSED', 'ARCHIVED') and self.resolved_date:
            return (self.resolved_date - self.created_at).days
        return (timezone.now() - self.created_at).days

class Correspondence(BaseModel):
    DIRECTION_CHOICES = [('INBOUND', 'Inbound'), ('OUTBOUND', 'Outbound')]
    
    correspondence_number = models.CharField(max_length=50, unique=True, db_index=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='correspondences', db_index=True)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default='INBOUND')
    sent_date = models.DateTimeField(db_index=True)
    sender = models.CharField(max_length=100, db_index=True)
    recipient = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_booked = models.BooleanField(default=False, db_index=True)
    booked_date = models.DateTimeField(null=True, blank=True)
    attachment_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        indexes = [
            models.Index(fields=['ticket', 'is_booked']),
            models.Index(fields=['sent_date', 'direction']),
        ]
        ordering = ['sent_date']


# Extended pension administration modules

class WithdrawalApplication(BaseModel):
    STATUS=[('PENDING','Pending'),('APPROVED','Approved'),('REJECTED','Rejected'),('PAID','Paid')]
    member=models.ForeignKey(Member,on_delete=models.CASCADE,related_name='withdrawals')
    amount=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    status=models.CharField(max_length=20,choices=STATUS,default='PENDING')
    application_date=models.DateField(auto_now_add=True)

class ClaimApplication(BaseModel):
    STATUS=[('SUBMITTED','Submitted'),('APPROVED','Approved'),('REJECTED','Rejected'),('PAID','Paid')]
    member=models.ForeignKey(Member,on_delete=models.CASCADE,related_name='claims')
    claim_type=models.CharField(max_length=50)
    amount=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    status=models.CharField(max_length=20,choices=STATUS,default='SUBMITTED')
    application_date=models.DateField(auto_now_add=True)

class TrustFundAccount(BaseModel):
    name=models.CharField(max_length=255)
    account_number=models.CharField(max_length=100,unique=True)
    balance=models.DecimalField(max_digits=18,decimal_places=2,default=0)

class TrustFundTransaction(BaseModel):
    account=models.ForeignKey(TrustFundAccount,on_delete=models.CASCADE)
    transaction_type=models.CharField(max_length=50)
    amount=models.DecimalField(max_digits=18,decimal_places=2,default=0)
    transaction_date=models.DateField()

class IncomeDrawdownPlan(BaseModel):
    member=models.ForeignKey(Member,on_delete=models.CASCADE)
    start_date=models.DateField()
    monthly_amount=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    status=models.CharField(max_length=20,default='ACTIVE')

class DrawdownPayment(BaseModel):
    plan=models.ForeignKey(IncomeDrawdownPlan,on_delete=models.CASCADE)
    payment_date=models.DateField()
    amount=models.DecimalField(max_digits=14,decimal_places=2,default=0)

class Pensioner(BaseModel):
    member=models.OneToOneField(Member,on_delete=models.CASCADE)
    pension_number=models.CharField(max_length=50,unique=True)
    monthly_pension=models.DecimalField(max_digits=14,decimal_places=2,default=0)

class PensionPayrollRun(BaseModel):
    payroll_month=models.DateField()
    total_amount=models.DecimalField(max_digits=18,decimal_places=2,default=0)
    status=models.CharField(max_length=20,default='DRAFT')

class MemberInterest(BaseModel):
    member=models.ForeignKey(Member,on_delete=models.CASCADE)
    year=models.IntegerField()
    interest_amount=models.DecimalField(max_digits=14,decimal_places=2,default=0)
