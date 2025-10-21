from jnius import autoclass

Context = autoclass("android.content.Context")
Intent = autoclass("android.content.Intent")
PendintIntent = autoclass("android.app.PendingIntent")
PythonActivity = autoclass("org.kivy.android.PythonActivity")

NotificationManager = autoclass("android.app.NotificationManager")
NotificationChannel = autoclass("android.app.NotificationChannel")
NotificationBuilder = autoclass("android.app.Notification$Builder")

android = autoclass('android.R')
#мб тут одинарные ковычки, но по-моему не имеет значения

class AndroidNotification:
    def __init__(self):
        self.context = PythonActivity.mActivity #определяем контекст для нашего конкретного приложения на питоне
        self.notification_manager = self.context.getSystemService(Context.NOTIFICATION_SERVICE) #создаем объект андройда уведомления

        self.setup_channel() #устанавливаем канал для уведомлений

    def setup_channel(self):
        channel_id = "voice_note" #id
        channel_name = "Голосовые заметки" #имя
        importance = NotificationManager.IMPORTANCE_HIGH #высокий приоритет

        channel = NotificationChannel(channel_id, channel_name, importance) #создаем сам объект канала, потом запуллим
        channel.setDescription("Напоминание Voice_Note") #описание канала задаем
        self.notification_manager.createNotificationChannel(channel) #запихиваем канал в систему

        self.channel_id = channel_id #записываем айдишник канала
    
    def send_notification(self, title, message):
        try:
            intent = Intent(self.context, PythonActivity.getClass())
            pending_intent = PendintIntent.getActivity(
                self.context, 0, intent,
                PendintIntent.FLAG_UPDATE_CURRENT | PendintIntent.FLAG_IMMUTABLE
            ) 
            #для обработки открытия приложения при клике на уведомление /////

            notification = (NotificationBuilder(self.context, self.channel_id)
                            .setContentTitle(title) #заголовок
                            .setContentText(message) #текст
                            .setSmallIcon(android.R.drawable.ic_media_play) #иконка
                            .setContentIntent(pending_intent) #действие по нажатии на кнопочку
                            .setAutoCancel(True)
                            .build())
            #забилдили, собрали уведомление из предоставленных нам данных
            #(получили объект класса
            #и пулим его системную
            #ветку уведомлений)

            self.notification_manager.notify(int(hash(title + message) % 10000), notification) # отправляем наше уведомление))
            return True #успешно


        except Exception as e:
            print(f"error {e}") #для откладки, инфа при ошибке
            return False
        
class AndroidVoiceRecorder:
    def __init__(self):
        self.is_recording = False #статус записи
    
    def start_recording(self):
        """заглушка пока что"""
        self.is_recording = True
        
        print("Запись началась!")
        #черещ android AudioRecorder
        #callback(b"audio_data_placeholder") 
    
    def stop_recording(self):
        self.is_recording = False
