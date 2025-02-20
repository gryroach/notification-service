# thirdparty
from sqladmin import ModelView

# project
from models import PeriodicNotification, ScheduledNotification, Template


class TemplateAdmin(ModelView, model=Template):
    column_list = (
        Template.id,
        Template.name,
        Template.subject,
        Template.staff_id,
    )


class ScheduledNotificationAdmin(ModelView, model=ScheduledNotification):
    column_list = (
        ScheduledNotification.id,
        ScheduledNotification.event_type,
        ScheduledNotification.channel_type,
        ScheduledNotification.is_sent,
    )


class PeriodicNotificationAdmin(ModelView, model=PeriodicNotification):
    column_list = (
        PeriodicNotification.id,
        PeriodicNotification.event_type,
        PeriodicNotification.channel_type,
        PeriodicNotification.is_active,
        PeriodicNotification.next_run_time,
        PeriodicNotification.stop_date,
        PeriodicNotification.cron_schedule,
    )
