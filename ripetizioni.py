import json

import requests
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import Screen, NoTransition, SlideTransition
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine, MDExpansionPanelOneLine
from kivy.core.window import Window

Window.size = (500, 700)


class GroceryApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.list_items = []

        payload = {"action": "corsi"}
        r = requests.get('http://localhost:8080/Ripetizioni/ServletRipetizioni', params=payload)
        self.category_list = (json.loads(r.text)["data"])
        print(self.category_list)
        self.currentCourse = None
        self.currentTeacher = None
        self.dialog = None
        self.card_file = {'Recipes': [{'title': 'Steamed Bass', 'directions': 'steam the fish',
                                       'shopping list': ['Fish', 'parchment paper', 'tomatoes']},
                                      {'title': 'Cheese Burger', 'directions': 'cook, flip, melt, eat',
                                       'shopping list': ['ground beef', 'cheese', 'buns']},
                                      ]}

    def build(self):
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.theme_style = "Dark"
        return Builder.load_file('main.kv')

    def on_start(self):

        for course in self.category_list:
            self.currentCourse = course
            panel = MDExpansionPanel(content=ContentScreen(), panel_cls=MDExpansionPanelTwoLine(
                text=course['title'], secondary_text="Tap to view teachers"))

            self.root.ids.sm.get_screen('menu').ids.rlist.add_widget(panel)

    def showinfo(self, widget):
        self.dialog = MDDialog(size_hint=(0.8, 0.8), text="Ingredients:", auto_dismiss=True)
        self.dialog.open()

        for recipe in self.card_file['Recipes']:
            print(f"{recipe['shopping list']}")

    def verify(self, email, password):
        print(email)
        print(password)
        payload = {"username": email, "password": password, "action": "login"}
        r = requests.get('http://localhost:8080/Ripetizioni/ServletRipetizioni', params=payload)
        print(r.text)
        user = (json.loads(r.text)["loginControl"])
        print(user)
        self.root.ids.sm.current = "profile"


class MenuScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class ProfileScreen(Screen):
    pass


class TableScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        print('teacher: %s' % MDApp.get_running_app().currentTeacher['id'])
        print('course: %s' % MDApp.get_running_app().currentCourse['id'])

        payload = {"docente": MDApp.get_running_app().currentTeacher['id'],
                   "corso": MDApp.get_running_app().currentCourse['id'], "action": "getRipetizioniForDocente"}
        r = requests.get('http://localhost:8080/Ripetizioni/ServletRipetizioni', params=payload)
        # stampa effettivamente i valori a console. Ora stampali nella GUI
        print(r)
        repetitions = (json.loads(r.text)["data"])
        print(repetitions)
        # instanziamo liste di valori che dovranno essere inseriti nella tabella
        days = []
        timetables = []

        table = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.9, 0.6),
            column_data=[
                ("Giorno", dp(30)),
                ("Slot", dp(30))
            ]
        )
        for repetition in repetitions:
            print(repetition['giorno'])
            print(repetition['slot'])

            table.row_data.insert(len(table.row_data), (repetition['giorno'], repetition['slot']))
        self.ids.card.add_widget(table)


class ContentScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        payload = {"corso": MDApp.get_running_app().currentCourse['title'], "action": "insegnanti"}
        r = requests.get('http://localhost:8080/Ripetizioni/ServletRipetizioni', params=payload)
        teachers = (json.loads(r.text)["data"])

        for teacher in teachers:
            MDApp.get_running_app().currentTeacher = teacher
            self.ids.panel_container.add_widget(
                MDExpansionPanel(
                    content=TableScreen(),
                    panel_cls=MDExpansionPanelOneLine(
                        text=teacher['surname'],
                    )
                )
            )


GroceryApp().run()
