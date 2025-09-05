from rest_framework import serializers
from .models import Product, ProductCategory, ProductImage, ProductAttribute, ProductAttributeValue


class ProductCategorySerializer(serializers.ModelSerializer):
    full_path = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductAttributeSerializer(serializers.ModelSerializer):
    choices_list = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductAttribute
        fields = '__all__'
    
    def get_choices_list(self, obj):
        return obj.get_choices_list()


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    value = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductAttributeValue
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    tags_list = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    attribute_values = ProductAttributeValueSerializer(many=True, read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer برای لیست محصولات (بدون جزئیات کامل)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_code', 'name', 'category', 'category_name',
            'sale_price', 'current_stock', 'status', 'is_low_stock', 
            'is_out_of_stock', 'created_at'
        ]