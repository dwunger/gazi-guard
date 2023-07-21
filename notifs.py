from win10toast import ToastNotifier
from plyer import notification
import plyer.platforms.win.notification
import time
class RateLimitedNotifier:
    def __init__(self, min_interval=5):  # interval in seconds
        self.min_interval = min_interval
        self.last_notify_time = 0

    def notify(self, title, message):
        current_time = time.time()
        if current_time - self.last_notify_time > self.min_interval:
            self.last_notify_time = current_time
            # Do the notification here
            notification.notify(title=title, message=message)
            


def show_notification(title, message):
    toaster = ToastNotifier()
    toaster.show_toast(title, message, duration=2)