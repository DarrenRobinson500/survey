import django_filters
from .models import Answer

class AnswerFilter(django_filters.FilterSet):
    person = django_filters.CharFilter(lookup_expr='icontains')  # Search by company name
    period = django_filters.CharFilter(lookup_expr='exact')  # Exact match for periods

    class Meta:
        model = Answer
        fields = ['person', 'period']
