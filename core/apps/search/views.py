from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle

from apps.products.models import Product

class ProductAutoCompleteView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'autocomplete'
    
    def get(self, request):
        query = request.query_params.get('q', '')

        if len(query) < 3:
            return Response({"error":"Query must be at least 3 characters"},status=status.HTTP_400_BAD_REQUEST)
        
        limit = 10
        results = []

        prefix_mateches = list(
            Product.objects.filter(
                title__istartswith = query
            ).values_list('title',flat=True)[:limit]
        )
        
        results.extend(prefix_mateches)

        if len(results) < limit:
            remaining = limit - len(results)
            general_matches = list(
                Product.objects.filter(
                    title__icontains=query
                ).exclude(
                    title__istartswith = query
                ).values_list('title', flat=True)[:remaining]
            )
            results.extend(general_matches)
        
        return Response(results,status=status.HTTP_200_OK)