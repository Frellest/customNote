from vosk import Model, KaldiRecognizer
import speech_recognition
import wave
import json
import os
import threading
import queue
import flet as ft
import time

# Глобальная очередь для команд
command_queue = queue.Queue()
is_listening = False
listening_thread = None

def say_hello(*args):
    print("Hello! Рад вас видеть!")
    return "Приветствую!"

def show_time(*args):
    current_time = time.strftime("%H:%M:%S")
    message = f"Текущее время: {current_time}"
    print(message)
    return message

def unknown_command(*args):
    message = "Не понимаю команду. Попробуйте еще раз!"
    print(message)
    return message

# Словарь команд с поддержкой многословных команд
commands = {
    "привет": say_hello,
    "здравствуй": say_hello,
    "hello": say_hello,
    "скажи время": show_time,
    "который час": show_time,
    "включи свет": lambda *args: "Включаю свет!",
    "выключи свет": lambda *args: "Выключаю свет!",
    "создай заметку": lambda *args: f"Создаю заметку: {' '.join(args[0]) if args[0] else 'без текста'}",
}

def find_matching_command(voice_input):
    """
    Поиск наиболее подходящей команды в распознанной фразе
    """
    voice_input = voice_input.lower().strip()
    
    # Сначала ищем точное совпадение с многословными командами
    for command in sorted(commands.keys(), key=len, reverse=True):
        if voice_input.startswith(command):
            # Возвращаем команду и оставшиеся слова как параметры
            remaining_text = voice_input[len(command):].strip()
            params = remaining_text.split() if remaining_text else []
            return command, params
    
    # Если точного совпадения нет, ищем по первому слову (для обратной совместимости)
    first_word = voice_input.split()[0] if voice_input.split() else ""
    for command in commands.keys():
        if command.startswith(first_word) or first_word in command:
            remaining_text = voice_input[len(first_word):].strip()
            params = remaining_text.split() if remaining_text else []
            return command, params
    
    return None, []

def record_and_recognize_audio():
    """
    Запись и распознавание аудио
    """
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()
    
    with microphone:
        recognized_data = ""

        # регулирование уровня окружающего шума
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your microphone is on, please?")
            return ""

        # использование online-распознавания через Google 
        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            pass

        # в случае проблем с доступом в Интернет происходит попытка 
        # использовать offline-распознавание через Vosk
        except speech_recognition.RequestError:
            print("Trying to use offline recognition...")
            recognized_data = use_offline_recognition()

        return recognized_data

def use_offline_recognition():
    """
    Переключение на оффлайн-распознавание речи
    :return: распознанная фраза
    """
    recognized_data = ""
    try:
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("models/vosk-model-small-ru-0.4"):
            print("Please download the model from:\n"
                  "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            return ""

        # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model("models/vosk-model-small-ru-0.4")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()

                # получение данных распознанного текста из JSON-строки
                # (чтобы можно было выдать по ней ответ)
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except:
        print("Sorry, speech service is unavailable. Try again later")

    return recognized_data

def execute_command_with_name(full_command: str, params: list):
    """
    Выполнение заданной пользователем команды с дополнительными аргументами
    """
    if full_command in commands:
        result = commands[full_command](params)
        return result
    else:
        return unknown_command()

def listening_worker():
    """
    Рабочий поток для прослушивания
    """
    global is_listening
    while is_listening:
        try:
            voice_input = record_and_recognize_audio()
            
            # Удаляем временный файл если он существует
            if os.path.exists("microphone-results.wav"):
                os.remove("microphone-results.wav")
            
            if voice_input and voice_input.strip():
                print(f"Распознано: {voice_input}")
                
                # Ищем подходящую команду в распознанной фразе
                command, params = find_matching_command(voice_input)
                
                if command:
                    # Помещаем команду в очередь
                    command_queue.put((command, params, voice_input))
                else:
                    # Если команда не найдена, помещаем всю фразу как неизвестную команду
                    command_queue.put(("unknown", [voice_input], voice_input))
                
        except Exception as e:
            print(f"Ошибка в потоке прослушивания: {e}")

def start_voice_listening():
    """
    Запуск прослушивания в отдельном потоке
    """
    global is_listening, listening_thread
    
    if is_listening:
        print("Прослушивание уже запущено")
        return
    
    is_listening = True
    listening_thread = threading.Thread(target=listening_worker)
    listening_thread.daemon = True
    listening_thread.start()
    print("Голосовое управление запущено...")

def stop_voice_listening():
    """
    Остановка прослушивания
    """
    global is_listening
    
    is_listening = False
    print("Голосовое управление остановлено")

def process_voice_commands():
    """
    Обработка накопленных голосовых команд
    Вызывать эту функцию периодически в основном потоке
    """
    processed_count = 0
    results = []
    while not command_queue.empty():
        try:
            command, params, original_phrase = command_queue.get_nowait()
            
            if command == "unknown":
                result = unknown_command(params)
            else:
                result = execute_command_with_name(command, params)
            
            results.append({
                "command": command,
                "original_phrase": original_phrase,
                "result": result,
                "timestamp": time.strftime("%H:%M:%S")
            })
            
            command_queue.task_done()
            processed_count += 1
            
        except queue.Empty:
            break
    
    return processed_count, results

# Flet UI компоненты
def main(page: ft.Page):
    page.title = "Голосовой ассистент"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Элементы UI
    status_text = ft.Text("Голосовое управление выключено", size=16)
    log_output = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=300)
    
    def update_status(message):
        status_text.value = message
        page.update()
    
    def add_log(message, color=None):
        log_entry = ft.Text(message, color=color) if color else ft.Text(message)
        log_output.controls.append(log_entry)
        if len(log_output.controls) > 20:  # Ограничиваем лог
            log_output.controls.pop(0)
        page.update()
    
    def start_listening(e):
        start_voice_listening()
        update_status("🎤 Голосовое управление активно...")
        add_log("Запущено голосовое управление", ft.colors.GREEN)
    
    def stop_listening(e):
        stop_voice_listening()
        update_status("Голосовое управление выключено")
        add_log("Остановлено голосовое управление", ft.colors.RED)
    
    # Создаем вкладки
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Главная",
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Голосовые команды", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Поддерживаемые команды:", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("• привет / здравствуй / hello"),
                        ft.Text("• скажи время / который час"),
                        ft.Text("• включи свет / выключи свет"),
                        ft.Text("• создай заметку [текст]"),
                        ft.Divider(),
                        status_text,
                    ]),
                    padding=20
                )
            ),
            ft.Tab(
                text="Лог команд",
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Лог голосовых команд", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=log_output,
                            border=ft.border.all(1),
                            padding=10,
                            border_radius=5,
                            height=250
                        )
                    ]),
                    padding=20
                )
            ),
        ],
        expand=1,
    )
    
    # Кнопки управления
    start_button = ft.ElevatedButton(
        "Начать запись",
        icon=ft.Icons.MIC,
        on_click=start_listening,
        bgcolor=ft.Colors.GREEN_200
    )
    
    stop_button = ft.ElevatedButton(
        "Остановить запись",
        icon=ft.Icons.STOP,
        on_click=stop_listening,
        bgcolor=ft.Colors.RED_200
    )
    
    # Расположение элементов
    page.add(
        ft.Column([
            ft.Row([start_button, stop_button]),
            ft.Divider(),
            tabs
        ], expand=True)
    )
    
    # Функция для периодической обработки команд
    def process_commands_periodically():
        while True:
            try:
                processed_count, results = process_voice_commands()
                if processed_count > 0:
                    for result in results:
                        # Добавляем запись в лог
                        log_message = f"[{result['timestamp']}] 💬 '{result['original_phrase']}' → {result['result']}"
                        page.run_task(lambda msg=log_message: add_log(msg, ft.colors.BLUE))
                
                time.sleep(0.5)  # Проверяем чаще для лучшей отзывчивости
            except Exception as e:
                print(f"Ошибка в таймере: {e}")
                time.sleep(1)
    
    # Запускаем обработку команд в отдельном потоке
    processing_thread = threading.Thread(target=process_commands_periodically, daemon=True)
    processing_thread.start()

if __name__ == "__main__":
    ft.app(target=main)