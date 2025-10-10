import flet as ft
from Info_from_bases import *


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
                                      expand= True)
        self.namefield = ft.TextField(border=ft.InputBorder.NONE,
                                      min_lines=1,
                                      max_lines=1,
                                      max_length=28,
                                      text_size=20,
                                      text_style=ft.TextStyle(font_family="SFProDisplay-Bold"),
                                      on_change=self.save_name,
                                      content_padding=10,
                                      cursor_color="orange")
        
        self.current_name = "save.txt"
        self.id = id
        self.data = get_info(self.id)
        #####
    def save_text(self, e: ft.ControlEvent) -> None:
        update_text(self.id, self.textfield.value)
    
    def save_name(self, e:ft.ControlEvent):
        update_Name(self.id, self.namefield.value)

    def read_text(self) -> str | None:
        self.textfield.value = self.data[2]
    
    def read_name(self):
        self.namefield.value = self.data[1]
    
    def build(self) -> ft.TextField:
        self.read_text()
        self.read_name()
        return ft.Column(controls=[self.namefield, self.textfield], spacing=-10)

