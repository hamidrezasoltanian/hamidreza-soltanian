from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Prefetch
from django.utils import timezone
from datetime import datetime, timedelta
from .models import CalendarEvent, EventAttendance, Task, Reminder
from .serializers import (
    CalendarEventSerializer, EventAttendanceSerializer, TaskSerializer,
    ReminderSerializer, CreateEventSerializer, CreateTaskSerializer
)
from authentication.models import CustomUser
from common.models import Notification, Mention

class CalendarEventViewSet(viewsets.ModelViewSet):
    """مدیریت رویدادهای تقویم"""
    
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return CalendarEvent.objects.filter(
            Q(created_by=user) | Q(attendees__user=user)
        ).prefetch_related(
            'attendees__user', 'created_by'
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateEventSerializer
        return CalendarEventSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def calendar_view(self, request):
        """نمای تقویم"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        view_type = request.query_params.get('view', 'month')  # month, week, day
        
        if not start_date or not end_date:
            return Response({'error': 'start_date and end_date are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        events = self.get_queryset().filter(
            start_time__gte=start,
            end_time__lte=end
        ).order_by('start_time')
        
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_attendee(self, request, pk=None):
        """اضافه کردن شرکت‌کننده"""
        event = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # بررسی دسترسی
        if event.created_by != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        attendance, created = EventAttendance.objects.get_or_create(
            event=event,
            user=user,
            defaults={'status': 'not_responded'}
        )
        
        if created:
            # ارسال اعلان
            Notification.objects.create(
                user=user,
                notification_type='mention',
                title=f'به رویداد "{event.title}" دعوت شدید',
                message=f'{request.user.get_full_name()} شما را به رویداد دعوت کرد',
                content_object=event
            )
            
            return Response({'message': 'Attendee added successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Attendee already exists'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """پاسخ به دعوت رویداد"""
        event = self.get_object()
        status = request.data.get('status', 'attending')
        
        if status not in ['attending', 'maybe', 'declined']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        attendance, created = EventAttendance.objects.get_or_create(
            event=event,
            user=request.user,
            defaults={'status': status}
        )
        
        if not created:
            attendance.status = status
            attendance.responded_at = timezone.now()
            attendance.save()
        
        return Response({'message': 'Response recorded'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """رویدادهای آینده"""
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now() + timedelta(days=days)
        
        events = self.get_queryset().filter(
            start_time__gte=timezone.now(),
            start_time__lte=end_date
        ).order_by('start_time')
        
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """رویدادهای امروز"""
        today = timezone.now().date()
        start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        
        events = self.get_queryset().filter(
            start_time__gte=start_of_day,
            start_time__lte=end_of_day
        ).order_by('start_time')
        
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    """مدیریت وظایف"""
    
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        ).select_related('assigned_to', 'created_by').prefetch_related('tags')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTaskSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """وظایف من"""
        status_filter = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        due_date = request.query_params.get('due_date')
        
        tasks = self.get_queryset().filter(assigned_to=request.user)
        
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        if due_date:
            tasks = tasks.filter(due_date__date=due_date)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """وظایف سررسید گذشته"""
        tasks = self.get_queryset().filter(
            assigned_to=request.user,
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).order_by('due_date')
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """تکمیل وظیفه"""
        task = self.get_object()
        
        if task.assigned_to != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        # ارسال اعلان به سازنده
        Notification.objects.create(
            user=task.created_by,
            notification_type='task',
            title=f'وظیفه "{task.title}" تکمیل شد',
            message=f'{request.user.get_full_name()} وظیفه را تکمیل کرد',
            content_object=task
        )
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """واگذاری وظیفه"""
        task = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # بررسی دسترسی
        if task.created_by != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        task.assigned_to = user
        task.save()
        
        # ارسال اعلان
        Notification.objects.create(
            user=user,
            notification_type='task_assigned',
            title=f'وظیفه جدید محول شد',
            message=f'{request.user.get_full_name()} وظیفه "{task.title}" را به شما محول کرد',
            content_object=task
        )
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """داشبورد وظایف"""
        user = request.user
        
        # آمار کلی
        total_tasks = self.get_queryset().filter(assigned_to=user).count()
        completed_tasks = self.get_queryset().filter(assigned_to=user, status='completed').count()
        pending_tasks = self.get_queryset().filter(assigned_to=user, status='pending').count()
        in_progress_tasks = self.get_queryset().filter(assigned_to=user, status='in_progress').count()
        overdue_tasks = self.get_queryset().filter(
            assigned_to=user,
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        # وظایف امروز
        today = timezone.now().date()
        today_tasks = self.get_queryset().filter(
            assigned_to=user,
            due_date__date=today,
            status__in=['pending', 'in_progress']
        )
        
        # وظایف این هفته
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_tasks = self.get_queryset().filter(
            assigned_to=user,
            due_date__date__range=[week_start, week_end],
            status__in=['pending', 'in_progress']
        )
        
        return Response({
            'stats': {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': pending_tasks,
                'in_progress': in_progress_tasks,
                'overdue': overdue_tasks,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            'today_tasks': TaskSerializer(today_tasks, many=True).data,
            'week_tasks': TaskSerializer(week_tasks, many=True).data
        })

class ReminderViewSet(viewsets.ModelViewSet):
    """مدیریت یادآوری‌ها"""
    
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user).select_related('user', 'created_by')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """یادآوری‌های آینده"""
        hours = int(request.query_params.get('hours', 24))
        end_time = timezone.now() + timedelta(hours=hours)
        
        reminders = self.get_queryset().filter(
            remind_at__gte=timezone.now(),
            remind_at__lte=end_time,
            is_active=True
        ).order_by('remind_at')
        
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def snooze(self, request, pk=None):
        """تاخیر یادآوری"""
        reminder = self.get_object()
        minutes = int(request.data.get('minutes', 15))
        
        reminder.remind_at = timezone.now() + timedelta(minutes=minutes)
        reminder.save()
        
        serializer = self.get_serializer(reminder)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """رد یادآوری"""
        reminder = self.get_object()
        reminder.is_active = False
        reminder.save()
        
        return Response({'message': 'Reminder dismissed'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def due_soon(self, request):
        """یادآوری‌های نزدیک به موعد"""
        minutes = int(request.query_params.get('minutes', 60))
        end_time = timezone.now() + timedelta(minutes=minutes)
        
        reminders = self.get_queryset().filter(
            remind_at__gte=timezone.now(),
            remind_at__lte=end_time,
            is_active=True,
            is_sent=False
        ).order_by('remind_at')
        
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)

class EventAttendanceViewSet(viewsets.ModelViewSet):
    """مدیریت حضور در رویدادها"""
    
    serializer_class = EventAttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EventAttendance.objects.filter(user=self.request.user).select_related('event', 'user')
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """پاسخ به دعوت"""
        attendance = self.get_object()
        status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if status not in ['attending', 'maybe', 'declined']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        attendance.status = status
        attendance.responded_at = timezone.now()
        attendance.notes = notes
        attendance.save()
        
        # ارسال اعلان به سازنده رویداد
        Notification.objects.create(
            user=attendance.event.created_by,
            notification_type='mention',
            title=f'پاسخ به دعوت رویداد',
            message=f'{request.user.get_full_name()} پاسخ داد: {attendance.get_status_display()}',
            content_object=attendance.event
        )
        
        serializer = self.get_serializer(attendance)
        return Response(serializer.data)