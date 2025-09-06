from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FiscalYearViewSet, ChartOfAccountsViewSet, JournalViewSet,
    JournalEntryViewSet, LedgerViewSet, TrialBalanceViewSet,
    CostCenterViewSet, BankAccountViewSet
)

router = DefaultRouter()
router.register(r'fiscal-years', FiscalYearViewSet)
router.register(r'chart-of-accounts', ChartOfAccountsViewSet)
router.register(r'journals', JournalViewSet)
router.register(r'journal-entries', JournalEntryViewSet)
router.register(r'ledgers', LedgerViewSet)
router.register(r'trial-balances', TrialBalanceViewSet)
router.register(r'cost-centers', CostCenterViewSet)
router.register(r'bank-accounts', BankAccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
]