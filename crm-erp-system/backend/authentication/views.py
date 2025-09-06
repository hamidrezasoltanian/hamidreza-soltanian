from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import CustomTokenObtainPairSerializer, UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """ثبت نام کاربر جدید"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
    if not username or not email or not password:
        return Response({
            'error': 'نام کاربری، ایمیل و رمز عبور الزامی است'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({
            'error': 'نام کاربری قبلاً استفاده شده است'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({
            'error': 'ایمیل قبلاً استفاده شده است'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    # ایجاد توکن
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'کاربر با موفقیت ایجاد شد',
        'user': UserSerializer(user).data,
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """ورود کاربر"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'نام کاربری و رمز عبور الزامی است'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({
            'error': 'نام کاربری یا رمز عبور اشتباه است'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'حساب کاربری غیرفعال است'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # ایجاد توکن
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'ورود موفقیت‌آمیز',
        'user': UserSerializer(user).data,
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    })


@api_view(['POST'])
def logout(request):
    """خروج کاربر"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': 'خروج موفقیت‌آمیز'
        })
    except Exception as e:
        return Response({
            'error': 'خطا در خروج'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_profile(request):
    """پروفایل کاربر"""
    return Response({
        'user': UserSerializer(request.user).data
    })


@api_view(['PUT'])
def update_profile(request):
    """بروزرسانی پروفایل کاربر"""
    user = request.user
    
    # بروزرسانی فیلدهای قابل تغییر
    if 'first_name' in request.data:
        user.first_name = request.data['first_name']
    if 'last_name' in request.data:
        user.last_name = request.data['last_name']
    if 'email' in request.data:
        user.email = request.data['email']
    
    user.save()
    
    return Response({
        'message': 'پروفایل با موفقیت بروزرسانی شد',
        'user': UserSerializer(user).data
    })


@api_view(['POST'])
def change_password(request):
    """تغییر رمز عبور"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response({
            'error': 'رمز عبور قدیمی و جدید الزامی است'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(old_password):
        return Response({
            'error': 'رمز عبور قدیمی اشتباه است'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(new_password) < 8:
        return Response({
            'error': 'رمز عبور جدید باید حداقل 8 کاراکتر باشد'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': 'رمز عبور با موفقیت تغییر کرد'
    })