"""
Custom management command to seed test data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random
from datetime import datetime, timedelta
from dashboard.models import *

fake = Faker()

class Command(BaseCommand):
    help = 'Seed database with test data'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Created admin user')
        
        schemes = []
        scheme_names = ['PSSF General', 'PSSF Teachers', 'PSSF Health', 'PSSF Civil Service']
        for name in scheme_names:
            scheme = Scheme.objects.create(
                name=name,
                code=f"SCHEME{len(schemes)+1:03d}",
                sponsor_name=fake.company(),
                date_established=fake.date_between(start_date='-10y', end_date='-1y'),
                status=random.choice(['ACTIVE', 'ACTIVE', 'ACTIVE', 'INACTIVE'])
            )
            schemes.append(scheme)
            self.stdout.write(f'Created scheme: {scheme.name}')
        
        statuses = ['ACTIVE', 'ACTIVE', 'ACTIVE', 'INACTIVE', 'RETIRED']
        for i in range(50):
            member = Member.objects.create(
                member_number=f"MEM{str(i+1).zfill(5)}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_between(start_date='-65y', end_date='-18y'),
                national_id=fake.unique.ssn(),
                scheme=random.choice(schemes),
                join_date=fake.date_between(start_date='-10y', end_date='-30d'),
                status=random.choice(statuses),
                employer=fake.company(),
                email=fake.email(),
                phone=fake.phone_number(),
                salary=random.randint(30000, 200000)
            )
            self.stdout.write(f'Created member: {member.member_number}')
        
        for i in range(30):
            receipt = ContributionReceipt.objects.create(
                receipt_no=f"REC{str(i+1).zfill(5)}",
                receipt_type=random.choice(['NORMAL', 'NORMAL', 'NORMAL', 'EXCHEQUER']),
                receipt_date=fake.date_between(start_date='-1y', end_date='today'),
                description=fake.sentence(),
                receipt_amount=random.randint(100000, 5000000),
                allocated_amount=random.randint(100000, 4000000),
                scheme=random.choice(schemes),
                status=random.choice(['POSTED', 'POSTED', 'ALLOCATED'])
            )
            self.stdout.write(f'Created receipt: {receipt.receipt_no}')
        
        for i in range(20):
            ticket = Ticket.objects.create(
                ticket_number=f"TICK{str(i+1).zfill(5)}",
                subject=fake.sentence(),
                description=fake.paragraph(),
                member=Member.objects.order_by('?').first(),
                status=random.choice(['NEW', 'OPEN', 'IN_PROGRESS', 'CLOSED']),
                priority=random.choice(['LOW', 'NORMAL', 'HIGH', 'CRITICAL']),
                due_date=fake.date_between(start_date='-30d', end_date='+30d'),
                is_overdue=random.choice([True, False])
            )
            self.stdout.write(f'Created ticket: {ticket.ticket_number}')
        
        for account_type in ['INVESTMENT', 'OPERATING', 'RESERVE']:
            account = TrustFundAccount.objects.create(
                account_name=f"{account_type} Account",
                account_type=account_type,
                bank_name=fake.company(),
                account_number=fake.unique.iban(),
                current_balance=random.randint(1000000, 50000000),
                as_at_date=datetime.now().date()
            )
            self.stdout.write(f'Created trust account: {account.account_name}')
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
