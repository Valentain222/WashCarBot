'''Data_opertor menu'''
# else:
#     # Создание главного меню
#     self.state.key = callback.data[len("filling_worker_"):]
#     self.state.button_text = self.sql.read("parametr_settings", callback.data[len("filling_worker_"):])
#     b_setting = [[f"filling_worker_f_but_{i}", text[0]] for i, text in enumerate(self.state.button_text) if
#                  text[0] is not None]
#     text = "Выберите из перечня"

# # Сохранение данных в БД
#             e = False
#             column = ''
#             add_data = ''
#
#             for key, data in self.worker_data.__dict__.items():
#                 column += f'{key},'
#                 if data != "" and data != 0:
#                     add_data += f"'{data}',"
#                 else:
#                     # Заполнено не все
#                     e = True
#                     break
#
#             if not e:
#                 # Сохранение данных
#                 self.sql.add_to_table("car_washing_table", f"{column}username",
#                                       f"({add_data}'@{callback.from_user.username}')")
#                 self.worker_data = self.WorkerData()
#                 # self.filling_state = self.FillingState()
#                 text = "Данные успешно занесены в таблицу"
#                 b_setting = [('main_menu', 'Вернуться в главное меню'), ('next', 'Заполнить еще')]
#             else:
#                 text = 'Вы занесли не все данные!'
#                 b_setting = [('next', 'Обратно')]
async def admin_interaction(self, callback: types.CallbackQuery) -> tuple[str, list, bool, str | None, int]:
    a = callback.message

    b_settings = []
    spawn_new = False
    cb = ''
    text = ''
    row = 3
    parse_mode = None
    constant = 'settings_main'
    is_constant_mode = False
    black_men_state = None
    if callback.data.endswith('end_loging_in'):
        # Создание сообщения с главными настройками
        is_constant_mode = True
        cb = 'next'
    elif callback.data.startswith('filling_boss_long_menu_back_'):
        # Вернуться обратно из длинного меню к предидущему сообщению
        is_constant_mode = True
        constant = callback.data.split('|')[-1]
        cb = 'filling_boss_setting'

        if callback.data.split('|')[0].split('_')[-1] == 'True':
            await self.delete_long_menu()
    elif callback.data.startswith('filling_boss_edit'):
        # Создание менюшек для редактирования базы данных
        self.state_user = ''
        self.from_table[callback.data[19:]] = self.sql.read(callback.data[19:], '*')
        self.temporary_from_table = copy.deepcopy(self.from_table)

        if callback.data[19:] == 'black_list_user_id':
            row = 1
            b_settings, text, cb, spawn_new = await self.spawn_long_menu(callback.data[19:], callback.message, 2,
                                                                         'settings_main', 'Разблокировать',
                                                                         'filling_boss_lift', callback.data,
                                                                         table_name='black_list_user_id')

            b_settings.append(('filling_boss_|black_list_user_id2|search', 'Найти по юзу или никнейму'))
        elif callback.data[19:] == 'passwords':
            row = 1
            b_settings, text, cb, spawn_new = await self.spawn_long_menu(callback.data[19:], callback.message, 2,
                                                                         'settings_main', 'Изменить',
                                                                         'filling_boss_new_password_', callback.data,
                                                                         spoller=True,
                                                                         additionally=['Администратор', 'Рабочий'],
                                                                         table_name='passwords',
                                                                         parse_mode='MarkdownV2')
        elif callback.data[19:] == 'parametr_settings':
            is_constant_mode = True
            constant = 'edit_parametr'
            cb = 'filling_boss_setting'
    elif callback.data.startswith('filling_boss_lift'):
        # Удаление человека из черного списка
        numbers = ''.join(filter(str.isdigit, callback.data))
        string_id = int(numbers) if len(numbers) != 0 else None

        if string_id is not None:
            self.sql.delete_from_table("black_list_user_id", string_id, 'user_id, nick_name', 'NULL')
            await self.delete_long_menu()
            text = 'Пользователь успешно разблокирован'
            cb = 'filling_boss_edit0_black_list_user_id'
            black_men_state = next((i for i in self.from_table['black_list_user_id'] if i[0] == int(string_id)),
                                   None)
            await self.users.reset('Вы были разблокированы', callback.message, black_men_state[1])
        else:
            text = 'Произошла ошибка, попробуйте снова или напишите разработчику @sasval1'
            cb = 'back'

        await self.delete_long_menu()
    elif callback.data.startswith('filling_boss_new_password'):
        # Создание нового пароля
        self.state_user = 'new_data(password)'
        self.state.user = callback.data[-1]
        text = 'Введите новый пароль'
        cb = 'filling_boss_edit2_passwords'
        await self.delete_long_menu()
    elif callback.data.endswith('edit'):
        # Создание меню для работы с шаблонными данными
        row = 1
        state = 'parametr_settings'
        column = callback.data[15:].replace('_parametr_edit', '')
        b_settings, text, cb, spawn_new = await self.spawn_long_menu(state, callback.message, int(callback.data[13]),
                                                                     'edit_parametr', 'Удалить',
                                                                     f'filling_boss_parametr_del_|{column}',
                                                                     callback.data, table_name='parametr_settings')

        b_settings.extend([(f'filling_boss_parametr_add_{column}', 'Добавить элементы'),
                           (f'filling_boss_|parametr_settings{callback.data[13]}|search', 'Найти по тексту')])
    elif callback.data.startswith('filling_boss_parametr'):
        # Редактирвоание шаблонных данных
        if callback.data[22:25] == 'del':
            if callback.data.split('|')[-1] == 'service':
                column_num = 1
            else:
                column_num = 3

            if self.having_value(self.temporary_from_table['parametr_settings'], column_num, 'number of valid',
                                 'not None') > 1:
                text = 'Данные успешно удалены'
                self.sql.delete_from_table('parametr_settings', int(callback.data[-1]), callback.data[27:-1],
                                           "NULL")
            else:
                text = 'Не может быть 0 параметров!'

            cb = 'filling_boss_edit1_parametr_settings'
        else:
            text = 'Введите значение'
            cb = 'filling_boss_edit1_parametr_settings'
            self.state_user = 'new_data(parametr)'
            self.state.user = callback.data[26:]

        await self.delete_long_menu()
    elif callback.data.startswith('filling_boss_warning_reset'):
        # Предупреждение перед сбросом таблицы
        text = 'Вы уверены? \nВ случае сброса все данные таблицы будут сброшены до заводских настроек, наример, ' \
               'параметры (и услуги, и автомойки) скинуться до изначального уровня'
        cb = 'filling_boss_edit1_parametr_settings'
        b_settings = [(f'filling_boss_reset|{callback.data.split("|")[1]}', 'Я уверен')]

        await self.delete_long_menu()
    elif callback.data.startswith('filling_boss_reset'):
        # Сброс таблицы
        value = getattr(self.CONSTANT, callback.data.split('|')[1])
        text = 'Данные таблицы были сброшены'
        cb = value[1]
        meaning = ''
        column = ''
        if not value[0]:
            text += ' (И услуги, и автомойки)'
            meaning = ', '.join([f"({','.join(value[3][i])})" for i in range(len(value[3]))])
            column = ','.join(value[2])

        self.sql.reset(value[0], callback.data.split('|')[1], meaning, column)
    elif callback.data.endswith('search'):
        # Создание поискового меню
        self.from_table = copy.deepcopy(self.temporary_from_table)
        if self.long_menu_messages:
            self.state.mini_mes = self.long_menu_messages[0].reply_markup.inline_keyboard[0][0]
        self.state_user = callback.data.split('|')[-1]
        self.state.user = callback.data.split('|')[1]
        self.state.last_m_bot = self.state.m_bot

        text = 'Введите значение для поиска'
        cb = f'filling_boss_edits_{self.state.user[:-1]}'
        await self.delete_long_menu()
    elif callback.data.endswith('show_more'):
        # Открывает еще +2 найденных элемента таблицы
        row = 1
        data_list = self.state.long_arguments
        text_b = self.long_menu_messages[0].reply_markup.inline_keyboard[0][0].text
        b_settings, text, _, spawn_new = await self.spawn_long_menu(data_list[0], callback.message, data_list[1], '___',
                                                                    text_b, data_list[2], 'filling_boss_show_more')
        cb = data_list[3]
    else:
        text = 'Произошла ошибка, напиишите разработчику @sasval1'

    if is_constant_mode:
        # Если настройки меню есть в константе, то они распаковываюстя здесь
        constant_list = getattr(self.CONSTANT, constant, None)
        b_settings = constant_list[:-2]
        row = constant_list[-2]
        text = constant_list[-1]

    b_settings.append((cb, 'Обратно'))
    await self.create_message_with_buttons(callback.message, text, b_settings, spawn_new, row)
    return text, b_settings, spawn_new, parse_mode, row
    # if black_men_state is not None:
    #     return black_men_state[1]


async def analyst_interaction(self, callback: types.CallbackQuery) -> tuple[str, list, bool, str | None, int]:
    """Функция, взаимодейтсвующая с
       администратором и статистикой"""

    text = ''
    row = 2
    b_setting = []
    spawn_new = False
    parse_mode = None
    back = ''
    if callback.data.endswith('end_loging_in'):
        row = 1
        b_setting = [('view_boss_statistics_visualization', 'Перейти к статистике'),
                     ('view_boss_statistics_setting', 'Настроить стаитистику')]
        text = 'Выберите действие'
        back = 'next'
        # photo = [
        #     InputMediaPhoto(media=FSInputFile('scale_1200.jpg')),
        #     InputMediaPhoto(media=FSInputFile('i.jpg'))
        # ]

        # statistics = self.visual.
    elif callback.data.endswith('visualization'):
        row = 1
        back = 'view_boss_statistics_main'
        text = 'Выберите'

        b_setting = copy.deepcopy(self.CONSTANT.statistics_b_setting)
    elif 'media_group' in callback.data:
        text = 'Выберите'
        spawn_new = True
        back = 'view_boss_statistics_visualization'

        charts = self.visual.generating_statistics()
        await self.bot.delete_message(chat_id=callback.message.chat.id, message_id=self.state.m_bot.message_id)
        self.state.m_bot_photos = await callback.message.answer_media_group(media=charts)
    elif callback.data.endswith('setting'):
        row = 1
        if self.state.m_bot_photos:
            await self.del_photos()
        if self.long_menu_messages:
            await self.delete_long_menu()
        back = 'view_boss_statistics_main'
        text = 'Выберите'
        b_setting = [('view_boss_statistics_interval', 'Выбрать диапазон дат'),
                     ('view_boss_statistics_car_wash', 'Выбрать автомойку')]
    elif callback.data.endswith('сетка'):
        pass
        pass
    elif callback.data.endswith('interval'):
        text = 'Настройте выборку по дате. \n' \
               'По умолчанию первая дата условия выборки равна самому старому дню в таблице. ' \
               'Вторая дата условия выборки равна сегодняшнему дню.'
        b_setting = [('view_boss_statistics_input_first_date', 'Ввести первую дату'),
                     ('view_boss_statistics_input_second_date', 'Ввести последнюю дату')]
        back = 'view_boss_statistics_setting'
    elif callback.data.endswith('date'):
        text = 'Выберите'
        back = 'view_boss_statistics_interval'
        cb = f'view_boss_statistics|{callback.data[27:]}|'
        b_setting = [(f'{cb}input', 'Выбрать вручную'), (f'{cb}select', 'Выбрать сегодняшнюю')]
    elif callback.data.endswith('select'):
        text = 'Данные успешно сохранены ✅'
        back = 'view_boss_statistics_interval'
        self.setting_selection[callback.data.split('|')[1]] = date.today()
    elif callback.data.endswith('input'):
        text = 'Введите дату в формате гггг-мм-дд'
        back = f'view_boss_statistics_input_{callback.data.split("|")[1]}'
        self.state_user = 'input date'
        self.state.key = callback.data.split("|")[1]
    elif callback.data.endswith('car_wash'):
        self.from_table['parametr_settings'] = self.sql.read('parametr_settings', 'id, name_car_wash')
        b_settings, text, back, spawn_new = await self.spawn_long_menu('parametr_settings', callback.message, 1,
                                                                       'setting', 'Выбрать',
                                                                       'view_boss_statistics_wash_id',
                                                                       'view_boss_statistics_car_wash',
                                                                       path='view_boss_statistics_')
        text = 'Обратно'
    elif callback.data.startswith('view_boss_statistics_wash_id'):
        await self.delete_long_menu()
        self.setting_selection['name_car_wash'] = next((i[1] for i in self.from_table['parametr_settings']
                                                        if i[0] == int(callback.data[-1])), None)
        text = 'Вы успешно выбрали автомойку!'
        b_setting = [('view_boss_statistics_car_wash', 'Выбрать другую автомойку')]
        back = 'view_boss_statistics_setting'
    else:
        text = 'произошла ошибка'
        back = 'view_boss_statistics_main'
    b_setting.append((back, 'Обратно'))
    await self.create_message_with_buttons(callback.message, text, b_setting, spawn_new, rows=row)
    return text, b_setting, spawn_new, parse_mode, row