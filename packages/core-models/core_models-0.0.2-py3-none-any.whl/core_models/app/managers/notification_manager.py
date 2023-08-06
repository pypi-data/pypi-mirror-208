from typing import Optional

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from onesignal_sdk.client import Client
from onesignal_sdk.error import OneSignalHTTPError

from core_models import settings
from core_models.utils import log_exception, MailAttachment


class NotificationManager:
    client = Client(app_id=settings.ONE_SIGNAL_APP_ID,
                    rest_api_key=settings.ONE_SIGNAL_REST_API_KEY,
                    user_auth_key=settings.ONE_SIGNAL_USER_AUTH_KEY)

    def send_mail(
            self, subject='', template_dir='', to=None,
            bcc=None, from_email=None, context_dict=None,
            file: Optional[MailAttachment] = None,
            request=None
    ):
        body_html = render_to_string(f'{template_dir}/mail.html', context_dict or {}, request=request)
        body_txt = render_to_string(f'{template_dir}/mail.txt', context_dict or {}, request=request)

        msg = EmailMultiAlternatives(
            subject=subject, body=body_txt, to=to or [],
            bcc=bcc or [], from_email=from_email
        )
        msg.attach_alternative(body_html, "text/html")
        if file is not None:
            msg.attach(
                filename=file.name,
                content=file.content,
                mimetype=file.mime
            )
        sent = msg.send(fail_silently=True)
        print(f"Mail sent: {sent}")
        return sent

    def send_push(self, notification):
        """
        For sending push notification to all user devices
        by passing either uid or user object
        :param notification:
        :return:
        """
        try:
            include_player_ids = notification.created_by.notification_tokens
            if bool(include_player_ids):
                notification_body = {
                    'contents': {'en': notification.text},
                    'data': {
                        "id": notification.id,
                        "object_id": notification.object_id,
                        "notice_type": notification.notice_type,
                        "seen": notification.seen,
                    },
                    'include_player_ids': include_player_ids
                }

                # Make a request to OneSignal and parse response
                response = self.client.send_notification(notification_body)
                print("---------PushNotificationManager-------------")
                print(response.body)  # JSON parsed response
                print("---------/PushNotificationManager/-------------")

        except OneSignalHTTPError as e:  # An exception is raised if
            # response.status_code != 2xx
            log_exception("PushNotificationManager", e)
        except Exception as e:
            log_exception("PushNotificationManager", e)
