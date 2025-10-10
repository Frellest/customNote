import flet as ft
import datetime
from calendar import monthrange

def main(page: ft.Page):
    page.title = "Выбор даты и времени"
    
    # Текущая дата для инициализации
    current_date = datetime.date.today()
    current_year = current_date.year
    current_month = current_date.month
    
    # Переменные для хранения выбранных значений
    selected_date = ft.Text(f"{current_date.strftime('%d.%m.%Y')}")
    selected_time = ft.Text("15:00")
    
    # Функция для создания календаря
    def create_calendar(year, month):
        # Получаем первый день месяца и количество дней
        first_weekday, num_days = monthrange(year, month)
        
        # Создаем строку с названиями дней недели
        week_days = ["Пн", "Вт", " Ср", "Чт", "Пт", "Сб", "Вс"]
        header_row = [ft.Container(
            content=ft.Text(day, size=14, weight=ft.FontWeight.BOLD),
            width=32,
            height=32,
            alignment=ft.alignment.center
        ) for day in week_days]
        
        # Создаем дни календаря
        days_grid = []
        
        # Добавляем пустые ячейки для дней предыдущего месяца
        for _ in range(first_weekday):
            days_grid.append(
                ft.Container(
                    width=32,
                    height=32,
                    border_radius=16,
                )
            )
        
        # Добавляем дни текущего месяца
        for day in range(1, num_days + 1):
            day_str = str(day)
            is_today = (day == current_date.day and month == current_date.month and year == current_date.year)
            
            days_grid.append(
                ft.Container(
                    content=ft.Text(day_str, size=14),
                    width=32,
                    height=32,
                    border_radius=16,
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.BLUE if is_today else None,
                    data=datetime.date(year, month, day),
                    on_click=select_date
                )
            )
        
        return header_row, days_grid
    
    # Функция выбора даты
    def select_date(e):
        # Сбрасываем фон у всех дней
        for control in days_container.controls:
            if hasattr(control, 'bgcolor'):
                control.bgcolor = None
        
        # Устанавливаем фон выбранному дню
        e.control.bgcolor = ft.Colors.BLUE_100
        selected_date.value = e.control.data.strftime("%d.%m.%Y")
        
        # Обновляем отображение
        page.update()
    
    # Функция выбора времени
    def select_time(e):
        selected_time.value = e.control.data
        time_picker_header.value = f"Выберите время - {selected_time.value}"
        page.update()
    
    # Создаем начальный календарь
    header_days, days = create_calendar(current_year, current_month)
    
    # Контейнер для дней
    days_container = ft.GridView(
        controls=days,
        runs_count=7,
        max_extent=32,
        spacing=5,
        run_spacing=5,
    )
    
    # Заголовок выбора времени
    time_picker_header = ft.Text("Выберите время - 15:00", size=16, weight=ft.FontWeight.BOLD)
    
    # Временные варианты
    time_options = [
        "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", 
        "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"
    ]
    
    # Создаем кнопки времени
    time_buttons = []
    for time in time_options:
        time_buttons.append(
            ft.ElevatedButton(
                text=time,
                data=time,
                on_click=select_time,
                style=ft.ButtonStyle(
                    color=ft.Colors.BLACK,
                    bgcolor=ft.Colors.BLUE_100 if time == "15:00" else ft.Colors.GREY_100,
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                )
            )
        )
    
    # Сетка для кнопок времени
    time_grid = ft.GridView(
        controls=time_buttons,
        runs_count=3,
        max_extent=100,
        spacing=10,
        run_spacing=10,
    )
    # Содержимое bottom sheet
    bottom_sheet_content = ft.Column(
        controls=[
            # Заголовок календаря
            ft.Row(
                controls=[
                    ft.Text("Октябрь 2025г.", size=16, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            
            # Дни недели
            ft.Row(
                controls=header_days,
                alignment=ft.MainAxisAlignment.SPACE_EVENLY
            ),
            
            # Дни месяца
            days_container,
            
            # Разделитель
            ft.Divider(height=20),
            
            # Выбор времени
            time_picker_header,
            
            # Кнопки времени
            time_grid,
            
            # Кнопки действий
            ft.Row(
                controls=[
                    ft.TextButton("Отмена", on_click=lambda _: page.close(bottom_sheet)),
                    ft.ElevatedButton("Сохранить", on_click=lambda _: save_selection()),
                ],
                alignment=ft.MainAxisAlignment.END
            )
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        height=500
    )
    
    def save_selection():
        print(f"Выбрана дата: {selected_date.value}, время: {selected_time.value}")
        page.close(bottom_sheet)
        # Здесь можно добавить логику сохранения выбранных значений
    
    # Создаем bottom sheet
    bottom_sheet = ft.BottomSheet(
        content=bottom_sheet_content,
        open=True,
        on_dismiss=lambda _: print("Bottom sheet закрыт")
    )
    
    # Добавляем bottom sheet на страницу
    page.overlay.append(bottom_sheet)
    
    # Кнопка для открытия bottom sheet (для демонстрации)
    open_btn = ft.ElevatedButton(
        "Открыть выбор даты и времени",
        on_click=lambda _: page.open(bottom_sheet)
    )
    
    # Отображение выбранных значений
    selection_display = ft.Column(
        controls=[
            ft.Text("Выбранные значения:", size=18, weight=ft.FontWeight.BOLD),
            ft.Text(f"Дата: {selected_date.value}"),
            ft.Text(f"Время: {selected_time.value}"),
        ]
    )
    
    page.add(open_btn, selection_display)

if __name__ == "__main__":
    ft.app(target=main)