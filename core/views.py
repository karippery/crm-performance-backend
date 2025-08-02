import time
from django.core.cache import cache
from django.forms import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from common.pagination import DefaultPagination
from core.filters import build_appuser_filters
from core.models import AppUser, CustomerRelationship
from core.serializers import AppUserSerializer
from rest_framework.filters import OrderingFilter
from django.db.models import Prefetch

class AppUserListView(ListAPIView):
    serializer_class = AppUserSerializer
    pagination_class = DefaultPagination
    filter_backends = [OrderingFilter]
    ordering_fields = "__all__"
    ordering = ["-created"]

    def get_queryset(self):

        relationship_prefetch = Prefetch(
            'relationships',
            queryset=CustomerRelationship.objects.select_related().order_by('-created')
        )

        base_qs = AppUser.objects.select_related("address") \
            .prefetch_related(relationship_prefetch)
        
        filtered_qs = self.apply_filters(base_qs)

        return filtered_qs.only(
            "id", "first_name", "last_name", "gender", "customer_id", 
            "phone_number", "created", "birthday", "last_updated",
            "address__street", "address__street_number", "address__city", 
            "address__country", "address__city_code"
        )
    
    def apply_filters(self, queryset):
        try:
            filters = build_appuser_filters(self.request.query_params)
            queryset = queryset.filter(filters)
            if any('__' in key for key in self.request.query_params):
                return queryset.distinct()
            return queryset
        except ValueError as e:
            raise ValidationError({'error': 'Invalid filter parameters', 'details': str(e)})
    
    def list(self, request, *args, **kwargs):
        total_start = time.time()
        cache_key = f"appusers::{request.get_full_path()}"
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            response = Response(cached_response)
            response.data['meta'] = {
                'query_time': 0,  # No DB query
                'response_time': time.time() - total_start,
                'cache_hit': True
            }
            return response
        
        start_time = time.time()
        response = super().list(request, *args, **kwargs)
        query_time = time.time() - start_time

        response.data['meta'] = {
            'query_time': query_time,
            'response_time': time.time() - total_start,
            'cache_hit': False
        }

        cache.set(cache_key, response.data, timeout=60 * 10)
        return response
