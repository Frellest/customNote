
from jnius import autoclass
import json
import time
from datetime import datetime

Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')
AlarmManager = autoclass('android.app.AlarmManager')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

class AlarmScheduler:
    def __init__(self):
        self.context = PythonActivity.mActivity
        self.alarm_manager = self.context.getSystemService(Context.ALARM_SERVICE)

    def schedule_remainder(self, remainder_id, message, timestamp_ms):
        """Уведомление на конкретное время"""

        try:
            """Собственно сам Intent, реализация, пулл значений"""
            intent = Intent(self.context, PythonActivity.getClass())
            intent.setAction("REMINDER_ACTION")
            intent.putExtra("remainder_id", str(remainder_id))
            intent.putExtra("message", str(message))

            """Билет системы"""
            pending_intent = PendingIntent.getActivity(
                self.context,
                remainder_id,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )

            """Точное время срабатывания"""
            self.alarm_manager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                timestamp_ms,
                pending_intent
            )

            print(f"✅ Напоминание {remainder_id} установлено на {datetime.fromtimestamp(timestamp_ms/1000)}")
            #для откладки
            return True

            

        except Exception as e:
            print(f"error {e}")
            return False