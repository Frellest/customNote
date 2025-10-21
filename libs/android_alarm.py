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
        
class RemainderStorage:
    #хранилище JSON
    def __init__(self):
        self.filename = "remainders.json"

    def save_remainder(self, remainder_data):
        #сохранение напоминания в файл
        remainders = self.load_all()
        remainders.append(remainder_data)

        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(remainders, f, ensure_ascii=False, indent = 2)
        
    def load_all(self):
        #загружаем все в массив
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: #если файла нету - список пуст
            return []
    
    def delete_remainder(self, remainder_data):
        remainders = self.load_all()

        remainders = [r for r in remainders if r['id'] != remainder_id]

        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(remainders, f, ensure_ascii=False, indent = 2)
