import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from django.db.models import Q, Count, Sum, Avg
from customers.models import Customer
from products.models import Product
from invoices.models import Invoice
from analytics.models import AnalyticsEvent
import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """AI-powered recommendation engine"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.customer_clusters = None
        self.product_clusters = None
    
    def get_customer_recommendations(self, customer_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get product recommendations for a customer"""
        try:
            customer = Customer.objects.get(id=customer_id)
            
            # Get customer's purchase history
            customer_invoices = Invoice.objects.filter(
                customer=customer,
                status='paid'
            ).prefetch_related('items__product')
            
            # Get purchased product IDs
            purchased_products = set()
            for invoice in customer_invoices:
                for item in invoice.items.all():
                    purchased_products.add(item.product.id)
            
            # Get similar customers based on purchase patterns
            similar_customers = self._find_similar_customers(customer_id)
            
            # Get products from similar customers
            similar_customer_products = self._get_products_from_customers(similar_customers)
            
            # Filter out already purchased products
            recommended_products = similar_customer_products - purchased_products
            
            # Get product details and scores
            recommendations = []
            for product_id in list(recommended_products)[:limit]:
                try:
                    product = Product.objects.get(id=product_id)
                    score = self._calculate_product_score(product, customer)
                    
                    recommendations.append({
                        'product': {
                            'id': product.id,
                            'name': product.name,
                            'description': product.description,
                            'price': float(product.price),
                            'category': product.category.name if product.category else None,
                            'image': product.image.url if product.image else None
                        },
                        'score': score,
                        'reason': self._get_recommendation_reason(product, customer)
                    })
                except Product.DoesNotExist:
                    continue
            
            # Sort by score
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return recommendations
            
        except Customer.DoesNotExist:
            logger.error(f"Customer {customer_id} not found")
            return []
        except Exception as e:
            logger.error(f"Error getting customer recommendations: {str(e)}")
            return []
    
    def get_product_recommendations(self, product_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get similar products based on a given product"""
        try:
            product = Product.objects.get(id=product_id)
            
            # Get products in the same category
            category_products = Product.objects.filter(
                category=product.category,
                status='active'
            ).exclude(id=product_id)
            
            # Calculate similarity scores
            recommendations = []
            for similar_product in category_products:
                score = self._calculate_product_similarity(product, similar_product)
                
                recommendations.append({
                    'product': {
                        'id': similar_product.id,
                        'name': similar_product.name,
                        'description': similar_product.description,
                        'price': float(similar_product.price),
                        'category': similar_product.category.name if similar_product.category else None,
                        'image': similar_product.image.url if similar_product.image else None
                    },
                    'score': score,
                    'reason': f"Similar to {product.name}"
                })
            
            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
            
        except Product.DoesNotExist:
            logger.error(f"Product {product_id} not found")
            return []
        except Exception as e:
            logger.error(f"Error getting product recommendations: {str(e)}")
            return []
    
    def get_trending_products(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending products based on recent activity"""
        try:
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            start_date = timezone.now() - timedelta(days=days)
            
            # Get products with recent activity
            trending_products = Product.objects.filter(
                status='active',
                created_at__gte=start_date
            ).annotate(
                view_count=Count('analytics_events', filter=Q(
                    analytics_events__event_type='product_viewed',
                    analytics_events__timestamp__gte=start_date
                )),
                purchase_count=Count('invoice_items__invoice', filter=Q(
                    invoice_items__invoice__status='paid',
                    invoice_items__invoice__created_at__gte=start_date
                )),
                total_revenue=Sum('invoice_items__total_price', filter=Q(
                    invoice_items__invoice__status='paid',
                    invoice_items__invoice__created_at__gte=start_date
                ))
            ).order_by('-view_count', '-purchase_count')
            
            recommendations = []
            for product in trending_products[:limit]:
                score = self._calculate_trending_score(product)
                
                recommendations.append({
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'description': product.description,
                        'price': float(product.price),
                        'category': product.category.name if product.category else None,
                        'image': product.image.url if product.image else None
                    },
                    'score': score,
                    'metrics': {
                        'view_count': product.view_count,
                        'purchase_count': product.purchase_count,
                        'total_revenue': float(product.total_revenue or 0)
                    },
                    'reason': 'Trending product'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting trending products: {str(e)}")
            return []
    
    def get_customer_segments(self) -> List[Dict[str, Any]]:
        """Get customer segments using clustering"""
        try:
            # Get customer data for clustering
            customers = Customer.objects.filter(status='active').prefetch_related('invoice_set')
            
            customer_data = []
            customer_ids = []
            
            for customer in customers:
                # Calculate customer metrics
                total_spent = sum(invoice.total_amount for invoice in customer.invoice_set.filter(status='paid'))
                invoice_count = customer.invoice_set.filter(status='paid').count()
                avg_invoice_value = total_spent / invoice_count if invoice_count > 0 else 0
                
                customer_data.append([
                    total_spent,
                    invoice_count,
                    avg_invoice_value,
                    1 if customer.customer_type == 'legal' else 0
                ])
                customer_ids.append(customer.id)
            
            if len(customer_data) < 2:
                return []
            
            # Perform clustering
            X = np.array(customer_data)
            n_clusters = min(5, len(customer_data) // 2)
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X)
            
            # Group customers by cluster
            segments = {}
            for i, cluster_id in enumerate(clusters):
                if cluster_id not in segments:
                    segments[cluster_id] = {
                        'customers': [],
                        'metrics': {
                            'total_spent': 0,
                            'invoice_count': 0,
                            'avg_invoice_value': 0,
                            'legal_customers': 0
                        }
                    }
                
                segments[cluster_id]['customers'].append(customer_ids[i])
                segments[cluster_id]['metrics']['total_spent'] += customer_data[i][0]
                segments[cluster_id]['metrics']['invoice_count'] += customer_data[i][1]
                segments[cluster_id]['metrics']['avg_invoice_value'] += customer_data[i][2]
                segments[cluster_id]['metrics']['legal_customers'] += customer_data[i][3]
            
            # Calculate averages and add segment names
            result = []
            for cluster_id, segment in segments.items():
                customer_count = len(segment['customers'])
                segment['metrics']['total_spent'] /= customer_count
                segment['metrics']['invoice_count'] /= customer_count
                segment['metrics']['avg_invoice_value'] /= customer_count
                segment['metrics']['legal_customers'] = int(segment['metrics']['legal_customers'])
                
                # Assign segment name based on characteristics
                if segment['metrics']['total_spent'] > 1000000:
                    segment_name = 'VIP Customers'
                elif segment['metrics']['total_spent'] > 500000:
                    segment_name = 'High Value Customers'
                elif segment['metrics']['total_spent'] > 100000:
                    segment_name = 'Medium Value Customers'
                else:
                    segment_name = 'Low Value Customers'
                
                result.append({
                    'id': cluster_id,
                    'name': segment_name,
                    'customer_count': customer_count,
                    'metrics': segment['metrics'],
                    'customers': segment['customers'][:10]  # Limit for performance
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting customer segments: {str(e)}")
            return []
    
    def _find_similar_customers(self, customer_id: int, limit: int = 10) -> List[int]:
        """Find customers with similar purchase patterns"""
        try:
            customer = Customer.objects.get(id=customer_id)
            
            # Get customer's purchased products
            customer_products = set()
            for invoice in customer.invoice_set.filter(status='paid'):
                for item in invoice.items.all():
                    customer_products.add(item.product.id)
            
            if not customer_products:
                return []
            
            # Find other customers who bought similar products
            similar_customers = Customer.objects.filter(
                invoice__items__product__in=customer_products,
                status='active'
            ).exclude(id=customer_id).annotate(
                common_products=Count('invoice__items__product', filter=Q(
                    invoice__items__product__in=customer_products,
                    invoice__status='paid'
                ))
            ).order_by('-common_products')[:limit]
            
            return [c.id for c in similar_customers]
            
        except Exception as e:
            logger.error(f"Error finding similar customers: {str(e)}")
            return []
    
    def _get_products_from_customers(self, customer_ids: List[int]) -> set:
        """Get products purchased by given customers"""
        try:
            products = set()
            for invoice in Invoice.objects.filter(
                customer_id__in=customer_ids,
                status='paid'
            ).prefetch_related('items__product'):
                for item in invoice.items.all():
                    products.add(item.product.id)
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting products from customers: {str(e)}")
            return set()
    
    def _calculate_product_score(self, product: Product, customer: Customer) -> float:
        """Calculate recommendation score for a product"""
        try:
            score = 0.0
            
            # Base score from product popularity
            view_count = AnalyticsEvent.objects.filter(
                event_type='product_viewed',
                content_object=product
            ).count()
            score += min(view_count * 0.1, 1.0)
            
            # Score from category preference
            if customer.customer_type == 'legal' and product.category and 'business' in product.category.name.lower():
                score += 0.3
            
            # Score from price range preference
            customer_avg_spent = customer.invoice_set.filter(status='paid').aggregate(
                avg=Avg('total_amount')
            )['avg'] or 0
            
            if customer_avg_spent > 0:
                price_ratio = product.price / customer_avg_spent
                if 0.5 <= price_ratio <= 2.0:  # Within reasonable range
                    score += 0.2
            
            # Score from recent trends
            from datetime import timedelta
            from django.utils import timezone
            
            recent_views = AnalyticsEvent.objects.filter(
                event_type='product_viewed',
                content_object=product,
                timestamp__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            if recent_views > 0:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating product score: {str(e)}")
            return 0.0
    
    def _calculate_product_similarity(self, product1: Product, product2: Product) -> float:
        """Calculate similarity between two products"""
        try:
            # Text similarity based on name and description
            text1 = f"{product1.name} {product1.description or ''}"
            text2 = f"{product2.name} {product2.description or ''}"
            
            if not text1.strip() or not text2.strip():
                return 0.0
            
            # Use TF-IDF for text similarity
            corpus = [text1, text2]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Category similarity
            category_similarity = 0.0
            if product1.category and product2.category:
                if product1.category == product2.category:
                    category_similarity = 1.0
                elif product1.category.parent == product2.category.parent:
                    category_similarity = 0.5
            
            # Price similarity
            price_similarity = 0.0
            if product1.price > 0 and product2.price > 0:
                price_ratio = min(product1.price, product2.price) / max(product1.price, product2.price)
                price_similarity = price_ratio
            
            # Weighted combination
            final_score = (
                similarity * 0.4 +
                category_similarity * 0.3 +
                price_similarity * 0.3
            )
            
            return min(final_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating product similarity: {str(e)}")
            return 0.0
    
    def _calculate_trending_score(self, product: Product) -> float:
        """Calculate trending score for a product"""
        try:
            score = 0.0
            
            # View count weight
            view_count = getattr(product, 'view_count', 0)
            score += min(view_count * 0.1, 0.4)
            
            # Purchase count weight
            purchase_count = getattr(product, 'purchase_count', 0)
            score += min(purchase_count * 0.2, 0.4)
            
            # Revenue weight
            total_revenue = getattr(product, 'total_revenue', 0) or 0
            if total_revenue > 0:
                score += min(total_revenue / 1000000, 0.2)  # Normalize by 1M
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating trending score: {str(e)}")
            return 0.0
    
    def _get_recommendation_reason(self, product: Product, customer: Customer) -> str:
        """Get human-readable reason for recommendation"""
        reasons = []
        
        # Category-based reason
        if product.category:
            if customer.customer_type == 'legal' and 'business' in product.category.name.lower():
                reasons.append("محصول مناسب برای کسب و کار")
            else:
                reasons.append(f"محصول از دسته‌بندی {product.category.name}")
        
        # Price-based reason
        customer_avg_spent = customer.invoice_set.filter(status='paid').aggregate(
            avg=Avg('total_amount')
        )['avg'] or 0
        
        if customer_avg_spent > 0:
            price_ratio = product.price / customer_avg_spent
            if price_ratio < 0.5:
                reasons.append("قیمت مناسب")
            elif price_ratio > 2.0:
                reasons.append("محصول پریمیوم")
        
        # Popularity reason
        view_count = AnalyticsEvent.objects.filter(
            event_type='product_viewed',
            content_object=product
        ).count()
        
        if view_count > 10:
            reasons.append("محصول محبوب")
        
        return "، ".join(reasons) if reasons else "توصیه شده برای شما"