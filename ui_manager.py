# Ui Manager for PySide2 & PyQt5
# Developed using Python3

__author__ = "Hkaar"

__copyright__ = "Copyright (c) 2021 Hkaar"
__license__ = "The MIT License (MIT)"
__version__ = 0.1

class QThemeManager:
    class LightTheme:
        stylesheets = {
        'default': ('color: rgb(47, 47, 47); background-color: rgb(227, 227, 227)'),
        'button': (
            ':enabled { color: rgb(47, 47, 47); background-color: rgb(227, 227, 227)}'
            ':disabled { color: rgb(47, 47, 47); background-color: rgb(213, 213, 213)}'
            ),
        'embeded window': ('color: rgb(47, 47, 47); background-color: rgb(213, 213, 213)'),
        }

    class DarkTheme:
        stylesheets = {
        'default': ('color: rgb(227, 227, 227); background-color: rgb(47, 47, 47)'),
        'button': (
            ':enabled { color: rgb(227, 227, 227); background-color: rgb(47, 47, 47)}'
            ':disabled { color: rgb(227, 227, 227); background-color: rgb(67, 67, 67)}'
            ),
        'embeded window': ('color: rgb(227, 227, 227); background-color: rgb(57, 57, 57)'),
        }

    def __init__(self, selected_theme='light'):
        self.fallback_theme = QThemeManager.LightTheme
        self.active_theme = None

        self.stored_widgets = {}

        self.stored_themes = {
        'light': QThemeManager.LightTheme,
        'dark': QThemeManager.DarkTheme
        }

        self.set_theme(selected_theme)

    def set_theme(self, selected_theme='light'):
        if isinstance(selected_theme, str):
            if selected_theme in self.stored_themes:
                self.active_theme = self.stored_themes[selected_theme]
            else:
                self.active_theme = self.fallback_theme
                print((f'WARNING!: Selected theme-{selected_theme} does not exist ' 
                    'within the known themes dictionary, default to fallback theme!'))
        else:
            print((f'WARNING!: Selected theme change to {selected_theme} cannot be done, '
                'because selected theme name was not a string!'))

    def import_theme(self, theme_file, theme_class, theme_name=None):
        theme_file = __import__(theme_file)
        theme_class = getattr(theme_file, theme_class)

        if hasattr(theme_class, 'stylesheets') and theme_class.stylesheets.get('default'):
            if theme_name != None:
                self.available_themes[theme_name] = theme_class
            else:
                self.available_themes[theme_class.__class__.__name__] = theme_class
        else:
            print(("WARNING!: Imported theme does not meet the neccesary requirements "
                "for a theme class to be imported, the requirements include: stylesheets " 
                "& 'default' within the stylesheets!"))

    def add_widget(self, widgets, theme_object='default'):
        def gen_id():
            for widget_id in range(0, 9999):
                if widget_id not in self.stored_widgets:
                    return widget_id
            return None

        if isinstance(theme_object, str):
            if isinstance(widgets, (tuple, list, set)):
                for widget in widgets:
                    self.stored_widgets[gen_id()] = (widget, theme_object)
            else:
                self.stored_widgets[gen_id()] = (widgets, theme_object)
        else:
            raise TypeError('Theme Object must be an str!')

    def set_widget_theme(self, widgets, theme_object='default'):
        def apply_theme(widget):
            if theme_object in ('palette', 'theme_palette') and hasattr(self.active_theme, 'theme_palette'):
                widget.setPalette(self.active_theme.theme_palette)
            else:
                widget.setStyleSheet(self.active_theme.stylesheets['default'])

                if theme_object in self.active_theme.stylesheets:
                    widget.setStyleSheet(self.active_theme.stylesheets[theme_object])

            if widget.__class__.__name__ != 'QApplication':
                widget.update()

        if isinstance(widgets, (tuple, list, set)):
            for widget in widgets:
                apply_theme(widget)
        else:
            apply_theme(widgets)

    def load_theme(self):
        for widget_id in self.stored_widgets:
            self.set_widget_theme(
                self.stored_widgets[widget_id][0], 
                self.stored_widgets[widget_id][1]
                )
        return None
