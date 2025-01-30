from constants import constants, buttons, error_types, errors
from containers.bot_containers import ButtonSettings, MessageConfig, CallBackData
from containers.msg_mgmt_containers import MenuGroupContainer


class MenuManager:
    def __init__(self, len_menu: int = constants.LEN_MENU, menu_buttons_row: int = constants.MENU_BUTTONS_ROW,
                 menu_row: int = constants.MENU_ROW):
        self.group_menu = MenuGroupContainer(len_menu)
        self.prev_group_menu_settings = ()

        self.MENU_BUTTONS_ROW = menu_buttons_row
        self.MENU_ROW = menu_row

    def make_menu_keyboard(self, button_settings: tuple[ButtonSettings, ...], reset_path: str, back_path: str,
                           additional_keyboard: tuple[tuple[str, str], ...] | None = None):
        self.group_menu.clear()
        if button_settings:
            for button_setting in button_settings:
                self.group_menu.append(button_setting)
        else:
            raise errors.WRONG_MENU_KEYBOARD_DATA

        self.group_menu.add_back_path(back_path)
        self.group_menu.add_reset_path(reset_path)

        self.group_menu.add_additional_keyboard(additional_keyboard)

    def send_menu(self, text_menu: str, parse_mode: str | None = None) -> MessageConfig:
        button_settings = []
        row = []

        if self.group_menu:
            button_settings.append(self.group_menu.settings)
            row.append(self.MENU_ROW)

        is_end = self.group_menu.is_end_page
        len_menu = self.group_menu.len_pages
        back_button = buttons.BACK_BUTTON if not self.group_menu.page == 0 and len_menu > 1 else ()
        next_button = buttons.NEXT_BUTTON if len_menu > 1 and not is_end else ()
        menu_buttons = buttons.MENU_BUTTONS if len_menu > 1 else ()

        if self.group_menu.additional_keyboard is not None and self.group_menu.page == 0:
            button_settings.append(self.group_menu.additional_keyboard)
            row.append(1)

        button_settings.append(menu_buttons + (ButtonSettings(self.group_menu.reset_path,
                                                              buttons.RESET_TEXT_GROUP_MENU),
                                               ButtonSettings(self.group_menu.back_path,
                                                              buttons.BACK_TEXT_GROUP_MENU)))
        row.append(self.MENU_BUTTONS_ROW)

        if next_button or back_button:
            button_settings.append(back_button + next_button)
            row.append(len(button_settings[-1]))

        configs = MessageConfig(button_settings=tuple(button_settings),
                                row_buttons=tuple(row),
                                text_message=text_menu,
                                parse_mode=parse_mode)

        return configs

    def exit_menu(self):
        if self.group_menu:
            self.group_menu.clear()

    def browsing(self, event: str, text: str, parse_mode: str) -> MessageConfig:
        if event == 'back':
            self.group_menu.back_page()
        elif event == 'next':
            self.group_menu.next_page()

        configs = self.send_menu(text_menu=text, parse_mode=parse_mode)

        return configs

    def reset_menu(self, reset_path: str, button_text: str, text: str) -> MessageConfig:
        self.group_menu.clear()
        return MessageConfig(text_message=text,
                             button_settings=(ButtonSettings(reset_path, button_text),),
                             row_buttons=1)

    @staticmethod
    def number_button(event: str) -> int:
        if '_' not in event:
            raise error_types.EventSintaxisError(event)
        return int(event.split('_')[1])

    def restore_menu_button(self, number_button: int) -> int:
        page = self.group_menu.page
        size = self.group_menu.size

        return page * size + number_button

    def menu_keyboard(self, global_state: str, state: str,
                      event: str, texts_buttons: tuple[str, ...]) -> tuple[ButtonSettings, ...]:
        size = self.group_menu.size
        button_setting = []
        for number, text in zip(range(len(texts_buttons)), texts_buttons):
            button_setting.append(ButtonSettings(
                CallBackData.creating_callback(global_state, state, f'{event}_{number % size}'), text))
        return tuple(button_setting)
