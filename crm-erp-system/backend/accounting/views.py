from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Sum, Count
from django.utils import timezone
from .models import (
    FiscalYear, ChartOfAccounts, Journal, JournalEntry, 
    Ledger, TrialBalance, CostCenter, BankAccount
)
from .serializers import (
    FiscalYearSerializer, ChartOfAccountsSerializer, JournalSerializer,
    JournalEntrySerializer, LedgerSerializer, TrialBalanceSerializer,
    CostCenterSerializer, BankAccountSerializer
)


class FiscalYearViewSet(viewsets.ModelViewSet):
    queryset = FiscalYear.objects.all()
    serializer_class = FiscalYearSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """سال مالی فعال"""
        active_year = self.get_queryset().filter(is_active=True).first()
        if active_year:
            serializer = self.get_serializer(active_year)
            return Response(serializer.data)
        return Response({'message': 'هیچ سال مالی فعالی وجود ندارد'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """فعال کردن سال مالی"""
        fiscal_year = self.get_object()
        
        # غیرفعال کردن سایر سال‌های مالی
        FiscalYear.objects.filter(is_active=True).update(is_active=False)
        
        # فعال کردن سال مالی انتخاب شده
        fiscal_year.is_active = True
        fiscal_year.save()
        
        return Response({'message': 'سال مالی با موفقیت فعال شد'})


class ChartOfAccountsViewSet(viewsets.ModelViewSet):
    queryset = ChartOfAccounts.objects.all()
    serializer_class = ChartOfAccountsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'parent_account', 'is_active']
    search_fields = ['account_code', 'account_name', 'description']
    ordering_fields = ['account_code', 'account_name', 'created_at']
    ordering = ['account_code']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس سطح
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # فیلتر بر اساس والد
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent_account_id=parent_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """درخت حساب‌ها"""
        accounts = self.get_queryset().filter(parent_account__isnull=True)
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار حساب‌ها"""
        total_accounts = self.get_queryset().count()
        active_accounts = self.get_queryset().filter(is_active=True).count()
        
        type_stats = {}
        for account_type, _ in ChartOfAccounts.ACCOUNT_TYPES:
            type_stats[account_type] = self.get_queryset().filter(account_type=account_type).count()
        
        return Response({
            'total_accounts': total_accounts,
            'active_accounts': active_accounts,
            'type_stats': type_stats,
        })


class JournalViewSet(viewsets.ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'journal_type', 'fiscal_year']
    search_fields = ['journal_number', 'description']
    ordering_fields = ['journal_date', 'created_at']
    ordering = ['-journal_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(journal_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(journal_date__lte=date_to)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """تأیید دفتر روزنامه"""
        journal = self.get_object()
        
        if journal.status != 'draft':
            return Response({'error': 'فقط دفترهای روزنامه پیش‌نویس قابل تأیید هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # بررسی تعادل دفتر روزنامه
        total_debit = journal.entries.aggregate(total=Sum('debit_amount'))['total'] or 0
        total_credit = journal.entries.aggregate(total=Sum('credit_amount'))['total'] or 0
        
        if total_debit != total_credit:
            return Response({'error': 'دفتر روزنامه متعادل نیست'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        journal.status = 'approved'
        journal.approved_by = request.user
        journal.approved_at = timezone.now()
        journal.save()
        
        return Response({'message': 'دفتر روزنامه با موفقیت تأیید شد'})
    
    @action(detail=True, methods=['post'])
    def post(self, request, pk=None):
        """ثبت دفتر روزنامه"""
        journal = self.get_object()
        
        if journal.status != 'approved':
            return Response({'error': 'فقط دفترهای روزنامه تأیید شده قابل ثبت هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        journal.status = 'posted'
        journal.save()
        
        # ایجاد سند دفتر کل
        for entry in journal.entries.all():
            Ledger.objects.create(
                account=entry.account,
                journal_entry=entry,
                debit_amount=entry.debit_amount,
                credit_amount=entry.credit_amount,
                balance=entry.debit_amount - entry.credit_amount,
                created_by=request.user
            )
        
        return Response({'message': 'دفتر روزنامه با موفقیت ثبت شد'})


class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['journal', 'account']
    ordering_fields = ['entry_date', 'debit_amount', 'credit_amount']
    ordering = ['-entry_date']


class LedgerViewSet(viewsets.ModelViewSet):
    queryset = Ledger.objects.all()
    serializer_class = LedgerSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['account', 'journal_entry']
    ordering_fields = ['entry_date', 'debit_amount', 'credit_amount']
    ordering = ['-entry_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(entry_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(entry_date__lte=date_to)
        
        return queryset


class TrialBalanceViewSet(viewsets.ModelViewSet):
    queryset = TrialBalance.objects.all()
    serializer_class = TrialBalanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['fiscal_year', 'account']
    ordering_fields = ['account__account_code', 'debit_balance', 'credit_balance']
    ordering = ['account__account_code']
    
    @action(detail=False, methods=['get'])
    def generate(self, request):
        """تولید تراز آزمایشی"""
        fiscal_year_id = request.query_params.get('fiscal_year_id')
        if not fiscal_year_id:
            return Response({'error': 'سال مالی الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        # حذف تراز آزمایشی قبلی
        TrialBalance.objects.filter(fiscal_year_id=fiscal_year_id).delete()
        
        # تولید تراز آزمایشی جدید
        accounts = ChartOfAccounts.objects.filter(is_active=True)
        for account in accounts:
            ledger_entries = Ledger.objects.filter(account=account)
            debit_balance = ledger_entries.aggregate(total=Sum('debit_amount'))['total'] or 0
            credit_balance = ledger_entries.aggregate(total=Sum('credit_amount'))['total'] or 0
            
            TrialBalance.objects.create(
                fiscal_year_id=fiscal_year_id,
                account=account,
                debit_balance=debit_balance,
                credit_balance=credit_balance,
                created_by=request.user
            )
        
        return Response({'message': 'تراز آزمایشی با موفقیت تولید شد'})


class CostCenterViewSet(viewsets.ModelViewSet):
    queryset = CostCenter.objects.all()
    serializer_class = CostCenterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent_center', 'is_active']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس سطح
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # فیلتر بر اساس والد
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent_center_id=parent_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """درخت مراکز هزینه"""
        centers = self.get_queryset().filter(parent_center__isnull=True)
        serializer = self.get_serializer(centers, many=True)
        return Response(serializer.data)


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'currency', 'is_active']
    search_fields = ['account_number', 'account_name', 'bank_name']
    ordering_fields = ['account_name', 'created_at']
    ordering = ['account_name']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار حساب‌های بانکی"""
        total_accounts = self.get_queryset().count()
        active_accounts = self.get_queryset().filter(is_active=True).count()
        
        currency_stats = {}
        for currency, _ in BankAccount.CURRENCIES:
            currency_stats[currency] = self.get_queryset().filter(currency=currency).count()
        
        return Response({
            'total_accounts': total_accounts,
            'active_accounts': active_accounts,
            'currency_stats': currency_stats,
        })