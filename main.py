import os
<<<<<<< HEAD
import jnius_config


# Настройка для Amazon Corretto
java_home = r'C:\Program Files\Amazon Corretto\jdk17.0.16_8'
os.environ['JAVA_HOME'] = java_home
os.environ['PATH'] = os.path.join(java_home, 'bin') + os.pathsep + os.environ['PATH']

# Настройка JVM
jvm_path = os.path.join(java_home, 'bin', 'server', 'jvm.dll')
jnius_config.set_options(f'-Djava.library.path={os.path.dirname(jvm_path)}')

import flet as ft
import flet_permission_handler as fph
import sqlite3
import datetime
import calendar
from jnius import autoclass
import traceback
import threading
import time
import json
from vosk import Model, KaldiRecognizer
from libs.android_native import AndroidNotification, AndroidVoiceRecorder
from libs.android_alarm import RemainderStorage, AlarmScheduler


class VoiceAssistant:
    def __init__(self):
        # 🏗️ Инициализация компонентов
        self.notification = AndroidNotification()
        self.recorder = AndroidVoiceRecorder() 
        self.alarm_scheduler = AlarmScheduler()
        self.reminder_storage = RemainderStorage()
        
        # 🎯 Счетчик для ID напоминаний
        self.reminder_id_counter = int(time.time())
        
        # 📋 Словарь команд
        self.commands = {
            "привет": self.cmd_hello,
            "тест": self.cmd_test,
            "уведомление": self.cmd_notification,
            "напомни": self.cmd_reminder,
        }
    
    # 🎙️ КОМАНДЫ ПОМОЩНИКА
    
    def cmd_hello(self, params):
        """Команда: привет"""
        return "Привет! Я голосовой помощник. Скажите 'напомни сделать уроки в 17:15'"
    
    def cmd_test(self, params):
        """Команда: тест"""
        return "✅ Приложение работает! Можно тестировать напоминания."
    
    def cmd_notification(self, params):
        """Команда: уведомление [текст]"""
        text = " ".join(params) if params else "Тестовое уведомление"
        self.notification.send_notification("Помощник", text)
        return f"📨 Уведомление отправлено: {text}"
    
    def cmd_reminder(self, params):
        """Команда: напомни [что] в [время]"""
        if not params:
            return "❌ Укажите что напомнить. Например: 'напомни позвонить маме в 18:30'"
        
        text = " ".join(params)
        
        # ⏰ Парсим время (упрощенно)
        reminder_time, reminder_text = self.parse_reminder_time(text)
        if not reminder_time:
            return "❌ Не понял время. Скажите например: 'напомни сделать уроки в 17:15'"
        
        # 🆔 Создаем уникальный ID
        reminder_id = self.reminder_id_counter
        self.reminder_id_counter += 1
        
        # 💾 Сохраняем напоминание
        reminder_data = {
            "id": reminder_id,
            "text": reminder_text,
            "timestamp": int(reminder_time.timestamp() * 1000),  # мс
            "created": time.time()
        }
        
        self.reminder_storage.save_reminder(reminder_data)
        
        # ⏰ Планируем в системе
        success = self.alarm_scheduler.schedule_reminder(
            reminder_id,
            reminder_text,
            reminder_data["timestamp"]
        )
        
        if success:
            time_str = reminder_time.strftime("%d.%m.%Y в %H:%M")
            return f"✅ Напоминание: '{reminder_text}' на {time_str}"
        else:
            return "❌ Ошибка установки напоминания"
    
    def parse_reminder_time(self, text):
        """Упрощенный парсинг времени из текста"""
        try:
            words = text.split()
            
            # 🔍 Ищем время в формате ЧЧ:ММ
            time_str = None
            for word in words:
                if ':' in word and len(word) <= 5:
                    time_str = word
                    break
            
            if not time_str:
                return None, None
            
            # ✂️ Убираем время из текста напоминания
            reminder_text = text.replace(time_str, '').replace('в', '').strip()
            
            # 🕐 Парсим время
            now = datetime.now()
            hours, minutes = map(int, time_str.split(':'))
            
            reminder_time = datetime(
                now.year, now.month, now.day,
                hours, minutes, 0
            )
            
            # 📅 Если время уже прошло - ставим на завтра
            if reminder_time < now:
                reminder_time = reminder_time.replace(day=now.day + 1)
            
            return reminder_time, reminder_text
            
        except Exception as e:
            print(f"❌ Ошибка парсинга времени: {e}")
            return None, None
    
    def recognize_speech(self, audio_data):
        """Заглушка для распознавания речи"""
        # 🔄 Здесь будет Vosk распознавание
        return "тест уведомление"  # 📝 Заглушка для теста

class Date(ft.BottomSheet):
    def __init__(self, write_func, page, change_auto_do):
        self.on_date_selected = None
        self.data = 2
        self.write_funct = write_func
        self.change_auto_do = change_auto_do
        self.page = page
        self.current_date = datetime.datetime.now()
        self.selected_date = None
        self.month_names = [
                    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
                ]   
        self.week_days = ["Пн", "Вт", "Cр", "Чт", "Пт", "Сб", " Вс"]

        self.month_text = ft.Text(size=18, font_family="SFProDisplay-Bold", color=ft.Colors.INVERSE_SURFACE)
        self.calendar_grid = ft.GridView(
            expand=False,
            runs_count=7,
            spacing=5,
            run_spacing=10,
            max_extent=40,
            adaptive=False
        )
        content = self._build_ui()
        super().__init__(
            content=content,
            open=False,
            bgcolor=ft.Colors.SURFACE,
            
        )
        self._update_calendar_display()
    def _build_ui(self):
        return ft.Container(
            content=ft.Column(controls=[
                # Навигация и заголовок
                ft.Row([
                    ft.IconButton(
                        ft.Icons.CHEVRON_LEFT,
                        on_click=self._prev_month,
                        icon_size=20
                    ),
                    ft.Container(
                        content=self.month_text,
                        alignment=ft.alignment.center
                    ),
                    ft.IconButton(
                        ft.Icons.CHEVRON_RIGHT, 
                        on_click=self._next_month,
                        icon_size=20
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                #дни недели
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            day, 
                            size=14, 
                            font_family="SFProDisplay-Medium"
                        ),
                        width=40,
                        alignment=ft.alignment.center
                    ) for day in self.week_days
                ]),
                
                # Календарь
                ft.Container(
                    content=self.calendar_grid,
                    height = 220,
                    width= 350,
                    padding=5,
                    alignment=ft.alignment.center,
                    clip_behavior=ft.ClipBehavior.NONE
                )
            ], spacing=0, tight=True),
            padding=ft.padding.only(bottom=10)
    )
    def show(self):
        self.open = True
        if self.page:
            self.update()
    def hide(self):
        self.open = False
        if self.page:
            self.update()
    
    def _update_calendar_display(self):
            """Обновляет отображение календаря"""
            self.month_text.value = f"{self.month_names[self.current_date.month - 1]} {self.current_date.year}"
            
            # Очищаем grid
            self.calendar_grid.controls.clear()
            
            # Получаем календарь для текущего месяца
            cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
            
            
            # Добавляем дни в календарь
            for week in cal:
                for day in week:
                    if day == 0:
                        # Пустой день
                        self.calendar_grid.controls.append(
                            ft.Container(width=40, height=40)
                        )
                    else:
                        day_date = datetime.date(self.current_date.year, self.current_date.month, day)
                        is_selected = self.selected_date == day_date
                        is_today = day_date == datetime.date.today()
                        
                        day_container = ft.Container(
                            content=ft.Text(
                                str(day),
                                color=ft.Colors.INVERSE_SURFACE if is_selected else (
                                    ft.Colors.ORANGE if is_today else ft.Colors.INVERSE_SURFACE
                                ),
                                font_family="SFProDisplay-Medium" if is_today else "SFProDisplay-Bold"
                            ),
                            bgcolor=ft.Colors.ORANGE if is_selected else (
                                ft.Colors.ORANGE_100 if is_today else ft.Colors.SURFACE
                            ),
                            alignment=ft.alignment.center,
                            border_radius=20,
                            width=40,
                            height=40,
                            on_click=lambda e, d=day_date: self._select_date(d)
                        )
                        
                        self.calendar_grid.controls.append(day_container)

            if self.page:
                self.update()
            
    def _select_date(self, date):
        """Выбирает дату"""
        self.selected_date = date
        self._update_calendar_display()
        
        if self.on_date_selected:
            self.on_date_selected(date)

        self.write_funct(self.data, self.selected_date.isoformat())
        self.change_auto_do(self.data)
    
    def _prev_month(self, e):
        """Переход к предыдущему месяцу"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12, day=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1, day=1)
        self._update_calendar_display()
    
    def _next_month(self, e):
        """Переход к следующему месяцу"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1, day=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1, day=1)
        self._update_calendar_display()
    
    def get_selected_date(self):
        """Возвращает выбранную дату"""
        return self.selected_date

class Date_Time_Menu(ft.BottomSheet):
    def __init__(self, write_func, page, time_pic):
        self.on_date_selected = None
        self.write_funct = write_func
        self.time_picker = time_pic
        self.data = 2
        self.page = page
        self.user_time = "22:00"
        self.current_date = datetime.datetime.now()
        self.selected_date = None
        self.month_names = [
                    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
                ]   
        self.week_days = ["Пн", "Вт", "Cр", "Чт", "Пт", "Сб", " Вс"]

        self.month_text = ft.Text(size=18, font_family="SFProDisplay-Bold", color=ft.Colors.INVERSE_SURFACE)
        self.calendar_grid = ft.GridView(
            expand=False,
            runs_count=7,
            spacing=5,
            run_spacing=10,
            max_extent=40,
            adaptive=False
        )
        self.time = ft.Text(
                        self.user_time, 
                        size=16, 
                        color=ft.Colors.ORANGE,
                        font_family="SFProDisplay-Bold"
                    )
        content = self._build_ui()
        super().__init__(
            content=content,
            open=False,
            bgcolor=ft.Colors.SURFACE,
            
        )
        self._update_calendar_display()
    def _build_ui(self):
        return ft.Container(
            content=ft.Column(controls=[
                # Навигация и заголовок
                ft.Row([
                    ft.IconButton(
                        ft.Icons.CHEVRON_LEFT,
                        on_click=self._prev_month,
                        icon_size=20
                    ),
                    ft.Container(
                        content=self.month_text,
                        alignment=ft.alignment.center
                    ),
                    ft.IconButton(
                        ft.Icons.CHEVRON_RIGHT, 
                        on_click=self._next_month,
                        icon_size=20
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                #дни недели
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            day, 
                            size=14, 
                            font_family="SFProDisplay-Medium"
                        ),
                        width=40,
                        alignment=ft.alignment.center
                    ) for day in self.week_days
                ]),
                
                # Календарь
                ft.Container(
                    content=self.calendar_grid,
                    height = 220,
                    width= 350,
                    padding=5,
                    alignment=ft.alignment.center,
                    clip_behavior=ft.ClipBehavior.NONE
                ),

                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                value="Выберите время",
                                size=16,
                                font_family="SFProDisplay-Bold",
                                color=ft.Colors.INVERSE_SURFACE,
                            ),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        self.time,
                                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.INVERSE_SURFACE)
                                    ], spacing=5
                                ),
                                on_click=self.open_timer_picker
                            )
                        ], alignment= ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(left=10, right=5, bottom=5, top=5)
                )
            ], spacing=0, tight=True),
            padding=ft.padding.only(bottom=10)
    )
    def show(self):
        self.open = True
        if self.page:
            self.update()
    def hide(self):
        self.open = False
        if self.page:
            self.update()
    def open_timer_picker(self, e):
        self.time_picker.open = True
        self.page.update()
    
    def _update_calendar_display(self):
            """Обновляет отображение календаря"""
            self.month_text.value = f"{self.month_names[self.current_date.month - 1]} {self.current_date.year}"
            
            # Очищаем grid
            self.calendar_grid.controls.clear()
            
            # Получаем календарь для текущего месяца
            cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
            
            
            # Добавляем дни в календарь
            for week in cal:
                for day in week:
                    if day == 0:
                        # Пустой день
                        self.calendar_grid.controls.append(
                            ft.Container(width=40, height=40)
                        )
                    else:
                        day_date = datetime.date(self.current_date.year, self.current_date.month, day)
                        is_selected = self.selected_date == day_date
                        is_today = day_date == datetime.date.today()
                        
                        day_container = ft.Container(
                            content=ft.Text(
                                str(day),
                                color=ft.Colors.INVERSE_SURFACE if is_selected else (
                                    ft.Colors.ORANGE if is_today else ft.Colors.INVERSE_SURFACE
                                ),
                                font_family="SFProDisplay-Medium" if is_today else "SFProDisplay-Bold"
                            ),
                            bgcolor=ft.Colors.ORANGE if is_selected else (
                                ft.Colors.ORANGE_100 if is_today else ft.Colors.SURFACE
                            ),
                            alignment=ft.alignment.center,
                            border_radius=20,
                            width=40,
                            height=40,
                            on_click=lambda e, d=day_date: self._select_date(d)
                        )
                        
                        self.calendar_grid.controls.append(day_container)

            if self.page:
                self.update()
            
    def _select_date(self, date):
        """Выбирает дату"""
        self.selected_date = date
        self._update_calendar_display()
        
        if self.on_date_selected:
            self.on_date_selected(date)

        self.write_funct(self.data, self.selected_date.isoformat())
    
    def _prev_month(self, e):
        """Переход к предыдущему месяцу"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12, day=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1, day=1)
        self._update_calendar_display()
    
    def _next_month(self, e):
        """Переход к следующему месяцу"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1, day=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1, day=1)
        self._update_calendar_display()
    
    def get_selected_date(self):
        """Возвращает выбранную дату"""
        return self.selected_date

    def set_date(self, date):
        """Устанавливает конкретную дату"""
        if isinstance(date, datetime.datetime):
            self.current_date = date
            self.selected_date = date.date()
        elif isinstance(date, datetime.date):
            self.current_date = datetime.datetime.combine(date, datetime.time())
            self.selected_date = date
        self._update_calendar_display()
        

        if self.page:
            self.update()

class TextEditing(ft.TextField):
    def __init__(self, id) -> None:
        super().__init__()
        self.textfield = ft.TextField(multiline= True,
                                      autofocus= True,
                                      border=ft.InputBorder.NONE,
                                      min_lines=40,
                                      text_style=ft.TextStyle(font_family="SFProDisplay-Medium"),
                                      on_change=self.save_text,
                                      content_padding=10,
                                      cursor_color="orange",
                                      hint_text="Напишите что-нибудь...",
                                      expand= True)
        self.namefield = ft.TextField(border=ft.InputBorder.NONE,
                                      min_lines=1,
                                      max_lines=1,
                                      max_length=28,
                                      text_size=20,
                                      text_style=ft.TextStyle(font_family="SFProDisplay-Bold"),
                                      on_change=self.save_name,
                                      content_padding=10,
                                      hint_text="Название",
                                      cursor_color="orange")
        
        self.current_name = "save.txt"
        self.id = id
        self.data = get_info(self.id)
    def save_text(self, e: ft.ControlEvent):
        update_text(self.id, self.textfield.value)
    
    def save_name(self, e:ft.ControlEvent):
        update_Name(self.id, self.namefield.value)

    def read_text(self):
        self.textfield.value = self.data[2]
    
    def read_name(self):
        self.namefield.value = self.data[1]
    
    def build(self):
        self.read_text()
        self.read_name()
        return ft.Column(controls=[self.namefield, self.textfield], spacing=-10)

def database_txt():
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT Not NULL,
    status BOOLEAN NOT NULL DEFAULT FALSE,
    priorety BOOLEAN NOT NULL DEFAULT FALSE,
    date TEXT DEFAULT None,
    time TEXT DEFAULT None,
    created TEXT NOT NULL,
    date_do TEXT DEFAULT None,
    repeat TEXT DEFAULT None
    )
    ''')

    connection.commit()
    connection.close()

    connection = sqlite3.connect('txtFiles.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Txt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT Not NULL,
    text TEXT Not NULL,
    priorety BOOLEAN NOT NULL DEFAULT FALSE
    )
    ''')
    
    connection.commit()
    connection.close()

def new_note_to_database(name, text, priorety):
    connection = sqlite3.connect('txtFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'INSERT INTO Txt (name, text, priorety) VALUES (?, ?, ?)', (name, text, priorety))

    cursor.execute(f'SELECT id FROM Txt WHERE name = ? AND text = ?', (name, text))
    result = cursor.fetchone()
    print(result)
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
    return result[0]
def new_task_to_database(text, status, priorety, created):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'INSERT INTO Task (text, status, priorety, created) VALUES (?, ?, ?, ?)', (text, status, priorety, created))

    cursor.execute(f'SELECT id FROM Task WHERE text = ?', (text, ))
    result = cursor.fetchone()
    print(result)
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
    return result[0]

def update_text(id, text):
    connection = sqlite3.connect('txtFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'UPDATE Txt SET text = ? WHERE id = ?', (text, id))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
def update_task(id, text):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'UPDATE Task SET text = ? WHERE id = ?', (text, id))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()

def update_task_do_status(id, status):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'UPDATE Task SET status = ? WHERE id = ?', (status, id))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
def update_task_priorety(id, priorety):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'UPDATE Task SET priorety = ? WHERE id = ?', (priorety, id))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
def update_note_priorety(id, priorety):
    connection = sqlite3.connect('txtFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'UPDATE Txt SET priorety = ? WHERE id = ?', (priorety, id))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
def update_Name(id, name):
    connection = sqlite3.connect('txtFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'UPDATE Txt SET name = ? WHERE id = ?', (name, id))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
def update_date(id, date):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'UPDATE Task SET date = ? WHERE id = ?', (date, id))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
def set_auto_do(id, date_do):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    print(date_do, id)
    
    cursor.execute(f'UPDATE Task SET date_do = ? WHERE id = ?', (date_do, id))
    
    print("do it_mather fucker", date_do)

    connection.commit()
    connection.close()
def delete_auto_do(id):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    cursor.execute(f'UPDATE Task SET date_do = ? WHERE id = ?', ('None', id))

    connection.commit()
    connection.close()
def update_time(id, time):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'UPDATE Task SET time = ? WHERE id = ?', (time, id))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
def delete_date_and_time(id):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'UPDATE Task SET date = ? WHERE id = ?', (None, id))
    cursor.execute(f'UPDATE Task SET time = ? WHERE id = ?', (None, id))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
def set_repeat_status(id, status):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()
    
    cursor.execute(f'UPDATE Task SET repeat = ? WHERE id = ?', (status, id))

    connection.commit()
    connection.close()
def delete_repeat_status(id):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    cursor.execute(f'UPDATE Task SET repeat = ? WHERE id = ?', (None, id))

    connection.commit()
    connection.close()

def get_info(id):
    connection = sqlite3.connect('txtFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'SELECT * FROM Txt WHERE id = ?', (id,))
    result = cursor.fetchone()
    
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
    return result
def get_info_task(id):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'SELECT * FROM Task WHERE id = ?', (id,))
    result = cursor.fetchone()
    
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
    return result

def get_all_id():
    connection = sqlite3.connect('txtFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute("SELECT id FROM Txt")
    ids = [row[0] for row in cursor.fetchall()]
    
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
    return ids
def get_all_id_task():
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute("SELECT id FROM Task")
    ids = [row[0] for row in cursor.fetchall()]
    
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
    return ids

def delete_note(id):
    connection = sqlite3.connect('txtFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'DELETE FROM Txt WHERE id = ?', (id, ))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
def delete_task(id):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    # Создаем таблицу Txt
    cursor.execute(f'DELETE FROM Task WHERE id = ?', (id, ))
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()
def get_list_to_auto_do(today):
    connection = sqlite3.connect('TaskFiles.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT COUNT(*) FROM Task WHERE date_do = ?', (today[0:10], ))
    count = cursor.fetchone()[0]

    print(count, today[0:10])
    
    for i in range(count):
        cursor.execute(f'DELETE FROM Task WHERE date_do = ?', (today[0:10], ))

    connection.commit()
    connection.close()

def main(page:ft.Page):

    database_txt()
    today = datetime.datetime.now().isoformat()
    get_list_to_auto_do(today)

    sys_theme = page.platform_brightness
    print(sys_theme)

    if sys_theme == ft.Brightness.DARK:
        page.theme_mode = "dark"
        elements_base_color = ft.Colors.GREY_900
    else:
        page.theme_mode = "light"
        elements_base_color = ft.Colors.GREY_300
    
    page.window.height = 640 # Временное решение, чтобы понимать как приложение выглядит в вертикальном формате
    page.window.width = 360


    repeat_values = {
        "DAILY": ft.Text(value="Ежедневно", font_family="SFProDisplay-Bold", size=14, color= ft.Colors.ORANGE),
        "EVERY_WEEK": ft.Text(value="Через неделю", font_family="SFProDisplay-Bold", size=14, color= ft.Colors.ORANGE)
    }


    ph = fph.PermissionHandler()
    page.overlay.append(ph)

    page.fonts = {
        "SFProDisplay-Bold": "assets/fonts/SFProDisplay-Bold.ttf",
        "SFProDisplay-Medium": "assets/fonts/SFProDisplay-Medium.ttf"
    }
    page.bgcolor = ft.Colors.SURFACE 
    page.scroll = True

    def check_message_permision():
        permission = ph.check_permission(fph.PermissionType.NOTIFICATION)
        print(f"permission is {permission}")
        if permission == fph.PermissionStatus.GRANTED:
            print(f"permission is {permission}")
        else:
            request_message_permission()

    def request_message_permission():
        permission = ph.request_permission(fph.PermissionType.NOTIFICATION)
        print(f"permiss: {permission}")
    
    def send_notification(title, text):
        try:
            #получаем главное activity окружения
            activity_host_class = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
            assert activity_host_class
            activity_host = autoclass(activity_host_class)
            activity = activity_host.mActivity

            #получаем доступ к android notification manager
            context = autoclass("android.content.Context")
            notification_manager = autoclass("android.app.NotificationManager")
            notification_channel = autoclass("android.app.NotificationChannel")
            notification_builder = autoclass("android.app.NotificationChannel")
            notification = autoclass("android.app.Notification$Builder")

            #запускаем уведомления
            notification_service = activity.getSystemService(context.NOTIFICATION_SERVICE)

            #каналы уведомлений 
            channel_id = "my_notification_channel"
            channel_name = "Flet notifi channel"
            importance = notification_manager.IMPORTANCE_DEFAULT

            channel = notification_channel(channel_id, channel_name, importance)
            notification_service.createNotificationChannel(channel)
            
            #билдим
            builder = notification_builder(activity, channel_id)
            builder.setContentTitle(title)
            builder.setContentText(text)
            builder.setSmallIcon(activity.getApplicationInfo().icon)
            builder.setAutoCancel(True)

            #отправляем
            notification_id = 1
            notification = builder.build()
            notification_service.notify(notification_id, notification)

            #проверка работоспособности для пк
            print("send the message")
        except Exception as ex:
            print("error")
             
             
    def Notes_Column_upd(page, column):
        if page.theme_mode == "dark":
            clr = "white",
            container_color = ft.Colors.GREY_900
        else:
            clr = "black",
            container_color = ft.Colors.GREY_300
        
        column.controls.clear()
        notes_priorety_column.controls.clear()
        
        all_id = get_all_id()
        for id in all_id:
            data_note = get_info(id)
            name = data_note[1]
            txt = data_note[2]
            priorety = data_note[3]
            sym_size = 15

            if txt == "" and name == "":
                delete_note(id)
                continue
            if priorety == 1:
                    priorety = True
            else:
                priorety = False

            sym = 35
            
            star = ft.IconButton(icon=ft.Icons.STAR_BORDER, selected_icon=ft.Icons.STAR, selected=priorety, on_click=lambda e, idd = id: change_priorety_note(e, idd), icon_size=18)

            text = ft.Container(
                content= ft.Row(
                    controls=
                    [
                        ft.Column(
                                controls=[
                                    ft.Text(value= name, size=sym_size, font_family="SFProDisplay-Bold", max_lines=1, color=clr),
                                    ft.Text(value= txt, font_family="SFProDisplay-Medium", max_lines=1, color=clr)
                                ],
                                spacing=0,
                                expand=True
                            ),
                        star
                    ]
                ),
                margin= ft.margin.only(left=20),
                alignment=ft.alignment.bottom_left,
                
            )

            MiniNotes = ft.GestureDetector(
                content=ft.Container(
                        bgcolor=container_color,
                        height = page.height / 14,
                        border_radius=5,
                        content= text,
                        alignment=ft.alignment.center_left,
                        margin= ft.margin.symmetric(horizontal=5),
                        on_click=open_note,
                        data = id,
                        expand=True
                    ),
                on_long_press_start=lambda e, idd = id: open_menu_bar(e, idd)
            )
            print(id)
            if priorety:
                notes_priorety_column.controls.append(MiniNotes)
            else:
                column.controls.append(MiniNotes)
            page.update()

    def open_menu_bar(e, id):
        delete_button_note.data = id
        menu_bar.open = True
        print("did it")
        page.update()
    
    def change_theme(e):
            if page.theme_mode == "dark":
                page.theme_mode = "light"
                app_bars["main_task"].bgcolor = ft.Colors.SURFACE 
                bottom_add_task_btn.bgcolor = ft.Colors.GREY_300
                bg_task_color = ft.Colors.GREY_300
            else:
                page.theme_mode = "dark"
                app_bars["main_task"].bgcolor = ft.Colors.SURFACE 
                bottom_add_task_btn.bgcolor = ft.Colors.GREY_900
                bg_task_color = ft.Colors.GREY_900
            print("change_theme do it")
            Notes_Column_upd(page, notes_column)
            page.update()

    def set_main_screen(e):
        page.clean()
        
        Notes_Column_upd(page, notes_column)

        change_bottom_bar("main_notes")
        change_app_bar("main_notes")
        
        page.add(main_screen)

    def change_bottom_bar(state):
        page.bottom_appbar = app_bars[state]
    def change_app_bar(state):
        page.appbar = top_app_bars[state]
        
    def create_note(e):
        page.clean()

        id = new_note_to_database("", "", False)
        text_editor = TextEditing(id)

        change_bottom_bar("do_notes")
        change_app_bar("do_notes")

        page.add(opened_note_page_element(text_editor=text_editor))
    
    def open_note(e):
        page.clean()

        id = e.control.data
        text_editor = TextEditing(id)
        
        change_bottom_bar("do_notes")
        change_app_bar("do_notes")
        
        page.add(opened_note_page_element(text_editor=text_editor))
    
    def opened_note_page_element(text_editor):
        opened_note = text_editor.build()
        return opened_note
    
    def add_all_tasks():
            ids = get_all_id_task()

            task_column.controls.clear()
            task_priorety_column.controls.clear()

            
            for id in ids:
                info = get_info_task(id)
                text = info[1]
                priorety = info[3]

                if (text == ""):
                    delete_task(id)
                    continue
                if priorety == 1:
                    priorety = True
                else:
                    priorety = False
                if info[2] == 1:
                    did_it = True
                else: 
                    did_it = False

                print(did_it)

                block_cont = ft.Container(
                    content= ft.Row(
                        controls=[
                            ft.Checkbox(
                                value = did_it,
                                shape=ft.RoundedRectangleBorder(radius=10),
                                on_change=lambda e, task_id=id, status=did_it: update_task_do_status(task_id, not status)
                            ),
                            ft.Text(value=text, font_family="SFProDisplay-Medium", max_lines=3, expand=True, no_wrap=False),
                            ft.IconButton(icon=ft.Icons.STAR_BORDER, selected_icon=ft.Icons.STAR, selected=priorety, on_click=lambda e, idd = id: change_priorety_task(e, idd), icon_size=18)
                        ], 
                    ),
                    margin=ft.margin.symmetric(horizontal=10),
                )
                block = get_theme_container_task(block_cont)
                block.data = id
                
                if priorety:
                    task_priorety_column.controls.append(block)
                else:
                    task_column.controls.append(block)
                
                page.update()
    
    def get_theme_container_task(block_cont):
        if page.theme_mode == "light":
            block = ft.Container(
                    content= block_cont,
                    height=page.height/14,
                    bgcolor= ft.Colors.GREY_300,
                    border_radius=5,
                    on_click= set_task_settings,
                    data=1
                )
        else:
            block = ft.Container(
                    content= block_cont,
                    height=page.height/14,
                    bgcolor= ft.Colors.GREY_900,
                    border_radius=5,
                    on_click= set_task_settings,
                    data=1
                )
        return block

    
    def new_task(e):
        create_task_menu.open = True
        today = datetime.date.today()
        task_space_to_enter_name.data = new_task_to_database(task_space_to_enter_name.value, status=False, priorety=False, created=today.isoformat())

        page.update()
    
    def change_name_task_on_dismissed(e):
        id = task_space_to_enter_name.data
        update_task(id, task_space_to_enter_name.value) 
        task_space_to_enter_name.value = ""
        add_all_tasks()

    def get_theme_mode():
        if page.theme_mode == "dark":
            return "black"
        else:
            return "white"
    
    task_column = ft.Column(spacing=3)
    task_priorety_column = ft.Column(spacing=3)

    task_space_to_enter_name = ft.TextField(hint_text="Добавить задачу", hint_style=ft.TextStyle(font_family="SFProDisplay-Bold"), border=ft.InputBorder.NONE, data=1, text_style=ft.TextStyle(font_family="SFProDisplay-Medium"), expand=True, max_lines=3, max_length=50, autofocus=True)

    def open_notifications_menu(e):
        create_notifications_menu.open = True
        check_message_permision()
        page.update()
    def open_do_it_menu(e):
        create_do_it_menu.open = True
        page.update()
    
    def open_calendar_picker(e):
        date_picker.show()
        page.update()
    def open_date_do_it_picker(e):
        do_it_date_picker.show()
        page.update()

    def close_all_menu(e= None):
        date_picker.open = False
        create_notifications_menu.open = False
        do_it_date_picker.open = False
        create_do_it_menu.open = False
        create_repeat.open = False
        print("all menu are close")
        page.update()
    
    def change_time_picker(e):
        id = date_picker.data
        
        update_time(id, e.control.value.isoformat())
        page.controls.clear()
        close_all_menu()
        set_task_settings(None, idd=id)

    def change_auto_do(id):
        set_task_settings(None, id)
        close_all_menu()

    create_task_menu = ft.BottomSheet(
        content= ft.Container(
                    content=ft.Column(
                        controls=
                        [
                            ft.Row(
                                controls= 
                                [
                                    ft.Icon(ft.Icons.CIRCLE_OUTLINED, size=25),
                                    task_space_to_enter_name
                                ], spacing=20
                            ),
                            ft.Row(
                                controls=
                                [
                                    ft.IconButton(ft.Icons.NOTIFICATIONS, icon_size=20, icon_color=ft.Colors.GREY),
                                    ft.IconButton(ft.Icons.CALENDAR_MONTH, icon_size=20, icon_color=ft.Colors.GREY),
                                    ft.IconButton(ft.Icons.RECYCLING_OUTLINED, icon_size=20, icon_color=ft.Colors.GREY)
                                    
                                ], spacing=30
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10
                    ),
                height = 120,
                alignment= ft.alignment.center,
                margin=ft.margin.symmetric(horizontal=20)
        ),
        use_safe_area=True,
        shape=ft.RoundedRectangleBorder(10),
        open=False,
        maintain_bottom_view_insets_padding = True,
        on_dismiss=change_name_task_on_dismissed
    )
    
    time_picker = ft.TimePicker(
            confirm_text="Confirm",
            error_invalid_text="Time out of range",
            help_text="Pick your time slot",
            data=1,
            on_change=change_time_picker, 
            on_dismiss=close_all_menu
        )
    date_picker = Date_Time_Menu(update_date, page, time_pic=time_picker)
    do_it_date_picker = Date(set_auto_do, page, change_auto_do)
    create_repeat = ft.BottomSheet(
        content= ft.Container(
                    content=ft.Column(
                        controls=
                        [
                            ft.Text("Повтор", font_family="SFProDisplay-Bold"),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.TODAY),
                                        ft.Text("Ежедневно", font_family="SFProDisplay-Bold")
                                    ]
                                ),
                                on_click= lambda e, status= "DAILY" :set_new_repeat_status(e, status=status),
                            ),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.VIEW_WEEK),
                                        ft.Text("Еженедельно", font_family="SFProDisplay-Bold")
                                    ]
                                ),
                                on_click= lambda e, status= "EVERY_WEEK" :set_new_repeat_status(e, status=status)
                            )

                        ], alignment=ft.MainAxisAlignment.CENTER,spacing=20
                    ),
                height = 150,
                alignment= ft.alignment.center,
                margin=ft.margin.symmetric(horizontal=20),
                data=1
        ),
        use_safe_area=True,
        shape=ft.RoundedRectangleBorder(10),
        open=False,
        maintain_bottom_view_insets_padding = True
    )

    create_notifications_menu = ft.BottomSheet(
        on_dismiss=close_all_menu,
        content= ft.Container(
                    content=ft.Column(
                        controls=
                        [
                            ft.Text("Напоминание", font_family="SFProDisplay-Bold"),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=
                                            [
                                                ft.Icon(ft.Icons.CALENDAR_MONTH),
                                                ft.Text("Выбрать дату", font_family="SFProDisplay-Bold")
                                            ]
                                        ),
                                        ft.Icon(ft.Icons.ARROW_RIGHT)
                                    ]
                                ),
                                on_click=open_calendar_picker
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20
                    ),
                height = 120,
                alignment= ft.alignment.center,
                margin=ft.margin.symmetric(horizontal=20)
        ),
        use_safe_area=True,
        shape=ft.RoundedRectangleBorder(10),
        open=False,
        maintain_bottom_view_insets_padding = True
    )
    create_do_it_menu = ft.BottomSheet(
        on_dismiss=close_all_menu,
        content= ft.Container(
                    content=ft.Column(
                        controls=
                        [
                            ft.Text("Срок", font_family="SFProDisplay-Bold"),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=
                                            [
                                                ft.Icon(ft.Icons.CALENDAR_MONTH),
                                                ft.Text("Выбрать дату", font_family="SFProDisplay-Bold")
                                            ]
                                        ),
                                        ft.Icon(ft.Icons.ARROW_RIGHT)
                                    ]
                                ),
                                on_click=open_date_do_it_picker
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20
                    ),
                height = 120,
                alignment= ft.alignment.center,
                margin=ft.margin.symmetric(horizontal=20)
        ),
        use_safe_area=True,
        shape=ft.RoundedRectangleBorder(10),
        open=False,
        maintain_bottom_view_insets_padding = True
    )
    
    bottom_add_task_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ADD),
                ft.Text(value="Добавить задачу", font_family="SFProDisplay-Bold", color= ft.Colors.ORANGE)
            ]
        ),
        height=page.height/14,
        width = page.width - 40,
        bgcolor= elements_base_color,
        border_radius=5,
        padding=10,
        on_click=new_task
    )

    main_task = ft.Column(
                controls=
                [
                    task_priorety_column,
                    task_column
                ], spacing=3
            )

    def set_todo_page(e):
        page.clean()
        change_bottom_bar("main_task")
        change_app_bar("main_task")
        add_all_tasks()

        page.add(main_task)

    notes_column = ft.Column(expand=True, spacing=3)
    notes_priorety_column = ft.Column(expand=True, spacing=3)
    
    def delete_note_button_do(e):
        id = delete_button_note.data
        print(id)
        delete_note(id)
        menu_delete_note_dismiss(e)
    
    def open_create_repeat(e):
        if create_repeat.open == False : create_repeat.open = True
        page.update()

    def set_new_repeat_status(e, status):
        id = create_repeat.data
        print(id, status)
        set_repeat_status(id, status=status)
        set_task_settings(None, id)
        close_all_menu()
    
    def delete_do_it_value(e, id):
        delete_auto_do(id)
        set_task_settings(None, idd=id)

    def menu_delete_note_dismiss(e):
        menu_bar.open = False
        Notes_Column_upd(page, notes_column)
        page.update()
    
    def delete_repeat(e):
        id = delete_repeat_button.data
        delete_repeat_status(id)
        set_task_settings(None, id)
        close_all_menu()

    delete_button_note = ft.TextButton(text= "Удалить", scale=1.5, style=ft.ButtonStyle(color=ft.Colors.RED), data=1, on_click=delete_note_button_do)

    delete_repeat_button = ft.Container(
                                        content=ft.Icon(ft.Icons.CANCEL_OUTLINED, color=ft.Colors.GREY, size=18),
                                        margin=ft.margin.only(right= 5),
                                        on_click=delete_repeat
                                        #UI
                            )

    menu_bar = ft.BottomSheet(
        content= ft.Container(
                    content= ft.Row(
                        controls=[
                            ft.TextButton(text= "Отмена", scale=1.5, on_click=menu_delete_note_dismiss),
                            delete_button_note
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                height = 80,
                alignment= ft.alignment.center,
                margin=ft.margin.symmetric(horizontal=40)
        ),
        use_safe_area=True,
        shape=ft.RoundedRectangleBorder(10),
        open=False,
        maintain_bottom_view_insets_padding = True
    )

    page.overlay.extend([create_task_menu, time_picker, date_picker, do_it_date_picker, create_notifications_menu, create_do_it_menu, menu_bar, create_repeat])

    print(notes_column)
    Notes_Column_upd(page, notes_column)
    
    page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.ORANGE,
                on_primary=ft.Colors.BLACK,
                secondary=ft.Colors.WHITE,  # Это может влиять на иконки
            )
        )    

    menu = ft.PopupMenuButton(
        content=ft.Icon(ft.Icons.MENU, color=ft.Colors.ORANGE),
        items=[
            ft.PopupMenuItem(icon=ft.Icons.SUNNY, text= "Сменить тему", on_click=change_theme),
            ft.PopupMenuItem(icon=ft.Icons.TASK, text= "Задачи", on_click=set_todo_page)
        ]
    )
    
    top_center = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text( 
                        value = "Заметки",                 
                        size = 30,
                        font_family="SFProDisplay-Bold",
                        color=ft.Colors.ORANGE
                    ),
                    margin= ft.margin.symmetric(horizontal=5),
                    expand=True
                ),
                notes_priorety_column,
                notes_column
            ],
            spacing= 3,
            expand=True
        )
    
    text_notificatons_interface = ft.Text(font_family="SFProDisplay-Bold", size=14, value="Напомнить", color=ft.Colors.GREY)
    date_do_container_default = ft.Container(
                        content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.CALENDAR_MONTH, size=20, color=ft.Colors.GREY),
                                        ft.Text(font_family="SFProDisplay-Bold", size=14, value="Добавить дату выполнения", color=ft.Colors.GREY)
                                    ], spacing=20
                        ),
                        height=page.height/14,
                        margin=ft.margin.symmetric(horizontal=5),
                        on_click=open_do_it_menu
                    )
    repeat_task_container_default = ft.Container(
                        content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.RECYCLING_OUTLINED, size=20, color=ft.Colors.GREY),
                                        ft.Text(font_family="SFProDisplay-Bold", size=14, value="Повтор", color=ft.Colors.GREY)
                                    ], spacing=20
                        ),
                        height=page.height/14,
                        margin=ft.margin.symmetric(horizontal=5),
                        on_click=open_create_repeat
                    )

    def delete_task_user(e, id):
        delete_task(id)
        print("i can")
        set_todo_page(e)
    
    def change_priorety_task(e, id):
        e.control.selected = not e.control.selected
        print(id)
        if e.control.selected:
            update_task_priorety(id, True)
        else:
            update_task_priorety(id, False) 
        print(e.control.selected)
        add_all_tasks()
        page.update()
    
    def change_priorety_note(e, id):
        e.control.selected = not e.control.selected
        print(id)
        if e.control.selected:
            update_note_priorety(id, True)
        else:
            update_note_priorety(id, False)
        print(e.control.selected)
        Notes_Column_upd(page, notes_column)
        page.update()

    def get_weekday_simple(dates):
            if 'T' in dates:
                date_obj = datetime.datetime.strptime(dates, "%Y-%m-%dT%H:%M:%S")
            else:
                date_obj = datetime.datetime.strptime(dates, "%Y-%m-%d")
            days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
            return days[date_obj.weekday()]
    def get_month(dates):
        if 'T' in dates:
            date_obj = datetime.datetime.strptime(dates, "%Y-%m-%dT%H:%M:%S")
        else:
            date_obj = datetime.datetime.strptime(dates, "%Y-%m-%d")
        months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
        months_short = ['янв.', 'фев.', 'марта', 'апр.', 'мая', 'июня', 'июля', 'авг.', 'сент.', 'окт.', 'ноя.', 'дек.',]
        months_number = date_obj.month
        return {
            "full-months": months[months_number-1],
            "short-monts": months_short[months_number-1]
        }
    def cancel_notification(e, id):
        delete_date_and_time(id)
        set_task_settings(None, idd=id)
        page.update()

    def set_task_settings(e, idd=None):
        if e is None: id = idd
        else: id = e.control.data

        all_info = get_info_task(id)
        
        date_picker.data = id
        do_it_date_picker.data = id
        create_repeat.data = id
        delete_repeat_button.data = id

        time = all_info[5]
        date_picker.user_time = str(time[:5]) if time is not None else "22:00"
        delete_button.on_click = lambda e: delete_task_user(e, id)
 
        def change_value(e):
            update_task(id, text_field.value)

        text = all_info[1]
        status = True if all_info[2] == 1 else False
        priorety = True if all_info[3] == 1 else False
        date = all_info[4]
        date_create = all_info[6]
        date_do_it = all_info[7]
        repeat_status = all_info[8]

        day = get_weekday_simple(date_create)
        month = get_month(date_create)

        if date_do_it is not None and date_do_it != "None":
            print("get_it", date_do_it)
            day_do_it = get_weekday_simple(date_do_it)
            month_do_it = get_month(date_do_it)["full-months"]
            date_num = date_do_it[8:10] if date_do_it[8] != '0' else f' {date_do_it[9]}'
        else:
            day_do_it = ""
            month_do_it = ""
            date_num = ""
        
        change_bottom_bar("task_settings")
        change_app_bar("task_settings")

        do_date_text = ft.Text(value=f"{day_do_it}, {date_num} {month_do_it}", font_family="SFProDisplay-Bold", size=12, color=ft.Colors.ORANGE)
        text_notificatons_interface = ft.Text(font_family="SFProDisplay-Bold", size=14, value="Напомнить", color=ft.Colors.GREY)
        text_field = ft.TextField(value=text, text_style=ft.TextStyle(font_family="SFProDisplay-Bold"), text_size=20, border=ft.InputBorder.NONE, expand=True, on_change=change_value)
        bottom_delete_task.controls = [
            ft.Container(),
            ft.Text(font_family="SFProDisplay-Bold",size=12, value=f"Создано {day}, {date_create[-2:]} {month["short-monts"]}", color=ft.Colors.GREY),
            delete_button
        ]
        text_delete_task = ft.Row(
        controls=[
            ft.Checkbox(
                    value = status,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    on_change=lambda e, task_id=id, status=status: update_task_do_status(task_id, not status)
            ),
            text_field,
            ft.IconButton(icon=ft.Icons.STAR_BORDER, selected_icon=ft.Icons.STAR, selected= priorety, on_click= lambda e: change_priorety_task(e, id), icon_size=18)
        ]
    )
        
        if date_do_it is not None and date_do_it != "None":
            date_do_container = ft.Container(
                        content=ft.Row(controls=[
                            ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.CALENDAR_MONTH, size=20, color=ft.Colors.ORANGE),
                                        ft.Column(
                                            controls=[
                                                ft.Text(font_family="SFProDisplay-Bold", size=14, value="Дата выполнения:", color=ft.Colors.ORANGE),
                                                do_date_text
                                            ], spacing=1
                                        )
                                    ], spacing=20
                            ),
                            ft.Container(
                                        content=ft.Icon(ft.Icons.CANCEL_OUTLINED, color=ft.Colors.GREY, size=18),
                                        margin=ft.margin.only(right= 5),
                                        on_click=lambda e, idd = id: delete_do_it_value(e, idd)
                                        #UI
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        height=page.height/14,
                        margin=ft.margin.symmetric(horizontal=5)
                    )

        if (date is not None and str(date) != "None" and time is not None and str(time) != "None"):
            
            if date_do_it is None or date_do_it == "None": date_do_container = date_do_container_default
            if repeat_status is not None and repeat_status != "None": 
                repeat_task_container = ft.Container(
                        content=ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.RECYCLING_OUTLINED, size=20, color=ft.Colors.ORANGE),
                                                ft.Column(
                                                    controls= 
                                                    [
                                                        ft.Text(font_family="SFProDisplay-Bold", size=14, value="Повтор: ", color=ft.Colors.ORANGE),
                                                        repeat_values[repeat_status]
                                                    ], spacing=1
                                                )
                                            ], spacing=20
                                        ),
                                        delete_repeat_button
                                    ], spacing=20, alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        height=page.height/14,
                        margin=ft.margin.symmetric(horizontal=5)
                    )
            else: repeat_task_container = repeat_task_container_default

            day = get_weekday_simple(str(date))
            times = time[0:5]
            month = get_month(date)
            text_notificatons_interface = ft.Column(
                controls=[
                    ft.Text(font_family="SFProDisplay-Bold", size=14, value=f"Напомнить мне в {times}", color=ft.Colors.ORANGE),
                    ft.Text(font_family="SFProDisplay-Bold", size=12, value=f"{day}, {date[8:10]} {month["full-months"]}", color=ft.Colors.ORANGE)
                ], spacing=1
            )
            interface_under_text_in_task_settingss = ft.Column(
                controls=
                [
                    ft.Divider(height=1),
                    ft.Container(
                        content= ft.Row(
                            controls= [
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.NOTIFICATIONS, size=20, color=ft.Colors.ORANGE),
                                        text_notificatons_interface
                                    ], spacing=20
                                ), 
                                ft.Container(
                                    content=ft.Icon(ft.Icons.CANCEL_OUTLINED, color=ft.Colors.GREY, size=18),
                                    margin=ft.margin.only(right= 5),
                                    on_click=lambda e, idd = id: cancel_notification(e, id= idd)
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        height=page.height/14,
                        margin=ft.margin.only(left = 5, right = 5, top = 10, bottom=0),
                        alignment=ft.alignment.center
                    ),
                    date_do_container,
                    repeat_task_container
                ], spacing=0
            )
        else:
            if date_do_it is None or date_do_it == "None": date_do_container = date_do_container_default
            if repeat_status is not None and repeat_status != "None": 
                repeat_task_container = ft.Container(
                        content=ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.RECYCLING_OUTLINED, size=20, color=ft.Colors.ORANGE),
                                                ft.Column(
                                                    controls= 
                                                    [
                                                        ft.Text(font_family="SFProDisplay-Bold", size=14, value="Повтор: ", color=ft.Colors.ORANGE),
                                                        repeat_values[repeat_status]
                                                    ], spacing=1
                                                )
                                            ], spacing=20
                                        ),
                                        delete_repeat_button
                                    ], spacing=20, alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        height=page.height/14,
                        margin=ft.margin.symmetric(horizontal=5)
                    )
            else: repeat_task_container = repeat_task_container_default
            interface_under_text_in_task_settingss = ft.Column(
                controls=
                [
                    ft.Divider(height=1),
                    ft.Container(
                        content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.NOTIFICATIONS, size=20, color=ft.Colors.GREY),
                                        text_notificatons_interface
                                    ], spacing=20,
                        ),
                        height=page.height/14,
                        margin=ft.margin.symmetric(horizontal=5),
                        on_click=lambda e: open_notifications_menu(e)
                    ),
                    date_do_container,
                    repeat_task_container
                ], spacing=0
            )
            print(date)
            print(time)
        
        page.clean()
        page.add(ft.Column(
                controls=[
                    text_delete_task,
                    interface_under_text_in_task_settingss
                ], spacing=5
            ))

    delete_button = ft.IconButton(icon=ft.Icons.DELETE, icon_size=20, icon_color=ft.Colors.GREY) 

    bottom_delete_task = ft.Row(
        controls=[
            ft.Text(font_family="SFProDisplay-Bold",size=12, value="Создано Вт, 27 сент.", color=ft.Colors.GREY),
            delete_button
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=0
    )
    
    app_bars = {
        "main_notes": ft.BottomAppBar(
                        content=ft.Row(
                                        controls=[
                                            ft.Container(expand=True),
                                            ft.IconButton(ft.CupertinoIcons.MIC),
                                            ft.IconButton(ft.CupertinoIcons.ADD_CIRCLED, on_click=create_note)  
                                        ],
                                        vertical_alignment=ft.CrossAxisAlignment.START
                        ),
                        padding= ft.padding.symmetric(vertical=5, horizontal=10),
                        height = page.height/14,
                        bgcolor= ft.Colors.SURFACE 
                    ),
        "do_notes": ft.BottomAppBar(
                        content=ft.IconButton(ft.CupertinoIcons.MIC),
                        padding= ft.padding.symmetric(vertical=5, horizontal=10),
                        height = page.height/14,
                        bgcolor= ft.Colors.SURFACE 
                    ),
        "main_task": ft.BottomAppBar(
                        content=bottom_add_task_btn,
                        padding= ft.padding.symmetric(vertical=10, horizontal=10),
                        height = page.height/10,
                        bgcolor= ft.Colors.SURFACE 
                    ),
        "task_settings": ft.BottomAppBar(
                        content=bottom_delete_task,
                        padding= ft.padding.symmetric(vertical=10, horizontal=10),
                        height = page.height/10,
                        bgcolor= ft.Colors.SURFACE
                    )               
    }

    top_app_bars = {
        "main_notes": ft.AppBar(
            leading=menu,
            actions=[
                ft.IconButton(ft.CupertinoIcons.SEARCH, icon_size=23, icon_color=ft.Colors.ORANGE),
                ft.IconButton(ft.Icons.NOTIFICATIONS, icon_size=23, icon_color=ft.Colors.ORANGE)
            ]
        ),
        "do_notes": ft.AppBar(
            leading=ft.IconButton(ft.CupertinoIcons.BACK, on_click=set_main_screen, icon_color=ft.Colors.ORANGE),
            actions=[
                ft.IconButton(ft.Icons.MENU_OPEN, icon_color=ft.Colors.ORANGE),
                ft.Container()
            ]
        ),
        "main_task": ft.AppBar(
            leading=None,  # Убираем левый элемент
            leading_width=0,  # Обнуляем ширину leading
            title=ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.CupertinoIcons.BACK, on_click=set_main_screen, icon_size=25, icon_color= ft.Colors.ORANGE),
                            ft.Container(expand = True),
                            ft.Text(value = "Задачи", size=20, font_family= "SFProDisplay-Bold", color=ft.Colors.ORANGE),
                            ft.Container(expand = True),
                            ft.IconButton(ft.Icons.MORE_HORIZ, icon_size=25, icon_color= ft.Colors.ORANGE)
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True
                    ),
            actions=[]
        ),
        "task_settings": ft.AppBar(
            leading=ft.Row(
                controls=[
                    ft.IconButton(icon=ft.CupertinoIcons.BACK, on_click=set_todo_page, icon_size=20, icon_color=ft.Colors.ORANGE), 
                    ft.Text(value = "Задачи", size=16, font_family= "SFProDisplay-Bold", color=ft.Colors.ORANGE)
                ], spacing=1
            )
        )
    }


    change_bottom_bar("main_notes")
    change_app_bar("main_notes")
    
    main_screen = top_center
    page.add(
        main_screen
    )

if __name__ == "__main__":
    ft.app(target= main, view=ft.AppView.FLET_APP) 
