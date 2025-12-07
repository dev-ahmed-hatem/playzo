from rest_framework import serializers
from .models import Offer
from django.conf import settings


class OfferSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    display_image = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'description',
            'color',
            'image',
            'image_url',
            'display_image',
            'offer_type',
            'start_date',
            'end_date',
            'status',
            'is_featured',
            'is_exclusive',
            'is_active',
            'days_remaining',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
        ]

    def get_display_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image_url

    def get_days_remaining(self, obj):
        if obj.end_date:
            from datetime import datetime
            now = datetime.now(settings.CAIRO_TZ)
            remaining = obj.end_date - now
            return max(0, remaining.days)
        return None

    def validate(self, data):
        """Validate offer dates"""
        start_date = data.get('start_date', self.instance.start_date if self.instance else None)
        end_date = data.get('end_date', self.instance.end_date if self.instance else None)

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({
                "end_date": "End date must be after start date"
            })

        return data


class OfferWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            'title',
            'description',
            'color',
            'image',
            'image_url',
            'offer_type',
            'start_date',
            'end_date',
            'status',
            'is_featured',
            'is_exclusive',
        ]

    def create(self, validated_data):
        """Set the created_by field to current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)
