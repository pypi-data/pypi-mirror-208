# coding=utf-8
'''
Copyright (C) 2022-2023 Siogeen

Created on 14.11.2022

@author: Reimund Renner
'''

import webbrowser
import os

from threading import Thread

os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivymd.app import MDApp as App
from kivymd.uix.button import MDFillRoundFlatButton as Button
#from kivymd.uix.tooltip.tooltip import MDTooltip
from kivymd.uix.button import MDFloatingActionButtonSpeedDial as FloatingButton
from kivymd.uix.textfield.textfield import MDTextFieldRect as TextInput
from kivymd.uix.selectioncontrol.selectioncontrol import MDCheckbox as CheckBox
#from kivymd.uix.behaviors.toggle_behavior import MDToggleButton as ToggleButton
from kivymd.uix.label import MDLabel as Label
#from kivy.clock import Clock
from kivymd.uix.scrollview import MDScrollView as ScrollView
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout as BoxLayout
from kivymd.uix.floatlayout import MDFloatLayout as FloatLayout
from kivymd.uix.stacklayout import MDStackLayout as StackLayout
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock

from siogeen.tools import IoddComChecker

__version__ = "1.6.8"

class IoddComCheckerGui(App):
    def build(self):
        if __version__ == IoddComChecker.__version__:
            self.title = 'IoddComChecker ' + IoddComChecker.__version__
        else:
            self.title = f'IoddComChecker {IoddComChecker.__version__}' \
                f'  (Gui {__version__})'

        self.theme_cls.primary_palette = "Blue" # "Green"
        self.theme_cls.theme_style = "Dark"

        self.screenBox = FloatLayout()
        #self.mainBox = BoxLayout(orientation='horizontal', spacing=10)
        self.menuBox = BoxLayout(orientation='horizontal', spacing=20,
            size_hint=(0.88,None))
        self.autoBox = BoxLayout(orientation='horizontal', spacing=10)

        self.autoChk = CheckBox(size_hint=(.1,None), height=30, pos_hint={'y':0.07})
        self.autoLabel = Label(text='[ref=auto]auto ports: activate master ports'
            ' if all are disabled (changes master port configs)[/ref]',
            size_hint=(.7,None), height=30, on_ref_press=self.autoLabelPress,
            markup=True, pos_hint={'y':0.07})#, color=(184/255,240/255,1,1))

        self.addr = TextInput(hint_text='Search specific addresses ...'
            ' (e.g. 10.0.2.3, 192.168.178.25, ...)',
            size_hint=(.5,None), height=30)#, background_normal='',
            #background_color=(206/255,228/255,1,1))
        self.clearBtn = Button(text='Clear', on_press=self.clearAddr,
            size_hint=(.1,None), height=30)#, color=(0,0,0,1),
            #background_normal='', background_color=(206/255,228/255,1,1))
        self.scanBtn = Button(text='Scan', on_press=self.scan,
            size_hint=(.1,None), height=30)#, color=(0,0,0,1),
            #background_normal='', background_color=(161/255,1,0,1))
        self.scanText = Label(height=400, size_hint_y=None)
        self.scrollView = ScrollView(size_hint=(1,.84), pos_hint={'y':.14},
            bar_width=7)
        self.scrollView.add_widget(self.scanText)

        self.autoBox.add_widget(self.autoChk)
        self.autoBox.add_widget(self.autoLabel)
        self.autoBox.add_widget(Button(text='Clear', on_press=self.clearText,
            size_hint=(.1,None), height=30, pos_hint={'y':0.07}))#, color=(0,0,0,1),
            #background_normal='', background_color=(161/255,1,0,1)))
        self.autoBox.add_widget(Button(text='Copy', on_press=self.copyText,
            size_hint=(.1,None), height=30, pos_hint={'y':0.07}))#, color=(0,0,0,1),
            #background_normal='', background_color=(161/255,1,0,1)))

        self.floatMenu = FloatingButton(data={
            'Contact Support': ['lifebuoy', 'on_release', self.contactSupport],
            },
            icon="dots-vertical", size_hint=(0.13,None),
            bg_color_root_button="red", bg_color_stack_button="red")

        self.menuBox.add_widget(self.addr)
        self.menuBox.add_widget(self.clearBtn)
        self.menuBox.add_widget(self.scanBtn)

        self.autoBox.add_widget(self.floatMenu)

        self.screenBox.add_widget(self.scrollView)
        #self.screenBox.add_widget(self.mainBox)
        self.screenBox.add_widget(self.autoBox)
        self.screenBox.add_widget(self.menuBox)

        self.clock = None

        return self.screenBox

    def contactSupport(self, *args):
        webbrowser.open("https://siogeen.com/#contact")

    def clearAddr(self, instance):
        self.addr.text = ''

    def autoLabelPress(self, instance, value):
        self.autoChk._do_press()

    def clearText(self, instance):
        self.scanText.text = ''

    def copyText(self, instance):
        Clipboard.copy(self.scanText.text)

    def print(self, text=''):
        self.scanText.text += text + '\n'

    def updateTextSize(self, dt):
        self.scanText.height = self.scanText.texture_size[1]
        if self.scanText.height > self.scrollView.height:
            self.scrollView.scroll_y = 0

    def runChecker(self, *args):
        self.scanBtn.disabled = True
        try:
            self.clock = Clock.schedule_interval(self.updateTextSize, 0.25)
            IoddComChecker.check(*args)
        finally:
            self.scanText.text += '\n'

            self.clock.cancel()
            self.clock = None
            Clock.schedule_once(self.updateTextSize, 0.25)

            self.scanBtn.disabled = False

    def scan(self, instance):
        addrs = self.addr.text
        if addrs:
            addrs = addrs.split(',')
        t = Thread(target=self.runChecker, args=(addrs, self.autoChk.active, self.print))
        t.daemon = True
        t.start()

if __name__ == '__main__':
    IoddComCheckerGui().run()
