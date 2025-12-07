from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Offer
from .serializers import OfferSerializer, OfferWriteSerializer
from django.conf import settings
from datetime import datetime


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing offers (view-only for regular users)
    """
    queryset = Offer.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'start_date', 'end_date']
    ordering = ['-is_featured', '-created_at']  # Default ordering

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OfferWriteSerializer
        return OfferSerializer

    def get_permissions(self):
        """
        Set permissions based on action.
        - List/retrieve: Allow any authenticated user
        - Create/update/delete: Admin only
        """
        if self.action in ['list', 'retrieve', 'active', 'featured', 'for_home', 'upcoming']:
            return [permissions.AllowAny()]  # Changed to AllowAny for viewing
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        """
        Filter queryset based on user permissions and request parameters.
        """
        queryset = super().get_queryset()

        # Get query parameters
        status_param = self.request.query_params.get('status', None)
        offer_type = self.request.query_params.get('type', None)
        is_featured = self.request.query_params.get('is_featured', None)
        is_exclusive = self.request.query_params.get('is_exclusive', None)
        is_active = self.request.query_params.get('is_active', None)

        # For non-admin users, only show active/upcoming offers
        if not self.request.user.is_staff:
            now = datetime.now(settings.CAIRO_TZ)
            queryset = queryset.filter(
                Q(status=Offer.Status.ACTIVE) | Q(status=Offer.Status.UPCOMING),
                end_date__gte=now
            ).order_by('-is_featured', '-created_at')
        else:
            # Admin users can filter by status
            if status_param:
                queryset = queryset.filter(status=status_param)

        # Filter by offer type
        if offer_type:
            queryset = queryset.filter(offer_type=offer_type)

        # Filter by featured status
        if is_featured is not None:
            is_featured_bool = is_featured.lower() == 'true'
            queryset = queryset.filter(is_featured=is_featured_bool)

        # Filter by exclusive status
        if is_exclusive is not None:
            is_exclusive_bool = is_exclusive.lower() == 'true'
            queryset = queryset.filter(is_exclusive=is_exclusive_bool)

        # Filter by active status (based on dates)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            now = datetime.now(settings.CAIRO_TZ)

            if is_active_bool:
                queryset = queryset.filter(
                    status=Offer.Status.ACTIVE,
                    start_date__lte=now,
                    end_date__gte=now
                )
            else:
                queryset = queryset.filter(
                    Q(status=Offer.Status.EXPIRED) |
                    Q(status=Offer.Status.DRAFT) |
                    Q(end_date__lt=now)
                )

        return queryset

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def active(self, request):
        """
        Get all currently active offers.
        This endpoint is public (AllowAny).
        """
        now = datetime.now(settings.CAIRO_TZ)

        active_offers = Offer.objects.filter(
            status=Offer.Status.ACTIVE,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-is_featured', '-created_at')

        # Apply additional filters from query params
        offer_type = request.query_params.get('type', None)
        if offer_type:
            active_offers = active_offers.filter(offer_type=offer_type)

        is_featured = request.query_params.get('is_featured', None)
        if is_featured is not None:
            is_featured_bool = is_featured.lower() == 'true'
            active_offers = active_offers.filter(is_featured=is_featured_bool)

        serializer = self.get_serializer(active_offers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """
        Get featured active offers.
        This endpoint is public (AllowAny).
        """
        now = datetime.now(settings.CAIRO_TZ)

        featured_offers = Offer.objects.filter(
            is_featured=True,
            status=Offer.Status.ACTIVE,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-created_at')

        # Filter by offer type if provided
        offer_type = request.query_params.get('type', None)
        if offer_type:
            featured_offers = featured_offers.filter(offer_type=offer_type)

        serializer = self.get_serializer(featured_offers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def for_home(self, request):
        """
        Get offers for home page display.
        Returns featured offers first, then other active offers.
        This endpoint is public (AllowAny).
        """
        now = datetime.now(settings.CAIRO_TZ)

        # Get featured offers
        featured_offers = Offer.objects.filter(
            is_featured=True,
            status=Offer.Status.ACTIVE,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-created_at')

        # Get other active offers (non-featured)
        other_offers = Offer.objects.filter(
            is_featured=False,
            status=Offer.Status.ACTIVE,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-created_at')

        # Get upcoming offers
        upcoming_offers = Offer.objects.filter(
            status=Offer.Status.UPCOMING,
            start_date__gt=now
        ).order_by('start_date')

        # Apply type filter if provided
        offer_type = request.query_params.get('type', None)
        if offer_type:
            featured_offers = featured_offers.filter(offer_type=offer_type)
            other_offers = other_offers.filter(offer_type=offer_type)
            upcoming_offers = upcoming_offers.filter(offer_type=offer_type)

        featured_serializer = self.get_serializer(featured_offers, many=True)
        other_serializer = self.get_serializer(other_offers, many=True)
        upcoming_serializer = self.get_serializer(upcoming_offers, many=True)

        return Response({
            'featured': featured_serializer.data,
            'active': other_serializer.data,
            'upcoming': upcoming_serializer.data,
            'count': {
                'featured': featured_offers.count(),
                'active': other_offers.count(),
                'upcoming': upcoming_offers.count(),
            }
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def upcoming(self, request):
        """
        Get upcoming offers (not yet started).
        This endpoint is public (AllowAny).
        """
        now = datetime.now(settings.CAIRO_TZ)

        upcoming_offers = Offer.objects.filter(
            status=Offer.Status.UPCOMING,
            start_date__gt=now
        ).order_by('start_date')

        # Apply filters from query params
        offer_type = request.query_params.get('type', None)
        if offer_type:
            upcoming_offers = upcoming_offers.filter(offer_type=offer_type)

        is_featured = request.query_params.get('is_featured', None)
        if is_featured is not None:
            is_featured_bool = is_featured.lower() == 'true'
            upcoming_offers = upcoming_offers.filter(is_featured=is_featured_bool)

        serializer = self.get_serializer(upcoming_offers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def expired(self, request):
        """
        Get expired offers (admin only).
        """
        now = datetime.now(settings.CAIRO_TZ)

        expired_offers = Offer.objects.filter(
            Q(status=Offer.Status.EXPIRED) |
            Q(end_date__lt=now)
        ).order_by('-end_date')

        # Apply filters from query params
        offer_type = request.query_params.get('type', None)
        if offer_type:
            expired_offers = expired_offers.filter(offer_type=offer_type)

        serializer = self.get_serializer(expired_offers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """
        Activate an offer (admin only).
        """
        offer = self.get_object()

        if offer.status == Offer.Status.ACTIVE:
            return Response(
                {"error": "Offer is already active"},
                status=status.HTTP_400_BAD_REQUEST
            )

        offer.status = Offer.Status.ACTIVE
        offer.save()

        serializer = self.get_serializer(offer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """
        Deactivate an offer (admin only).
        """
        offer = self.get_object()

        if offer.status != Offer.Status.ACTIVE:
            return Response(
                {"error": "Offer is not active"},
                status=status.HTTP_400_BAD_REQUEST
            )

        offer.status = Offer.Status.EXPIRED
        offer.save()

        serializer = self.get_serializer(offer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def toggle_featured(self, request, pk=None):
        """
        Toggle featured status of an offer (admin only).
        """
        offer = self.get_object()
        offer.is_featured = not offer.is_featured
        offer.save()

        serializer = self.get_serializer(offer)
        return Response({
            "message": f"Offer {'featured' if offer.is_featured else 'unfeatured'} successfully",
            "offer": serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def toggle_exclusive(self, request, pk=None):
        """
        Toggle exclusive status of an offer (admin only).
        """
        offer = self.get_object()
        offer.is_exclusive = not offer.is_exclusive
        offer.save()

        serializer = self.get_serializer(offer)
        return Response({
            "message": f"Offer {'marked as exclusive' if offer.is_exclusive else 'marked as non-exclusive'} successfully",
            "offer": serializer.data
        })
