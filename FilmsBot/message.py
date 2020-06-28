def make_list(films: dict, header):
    text = header
    for ticked in films['ticked']:
        text += ticked + ticked_text + '\n\n'
    for unticked in films['unticked']:
        text += unticked + unticked_text + '\n\n'
    return text


start_text = '''
Доброго времени суток!
Я Ваш персональный бот-киноман, который поможет Вам добавлять фильмы в список, \
отмечать их в таблице, \
а также показывать доступные Вам и \
предлагать случайный фильм на выбор. \
И это далеко не все
Для начала, нужно войти в систему
Нажмите /log_in для входа
'''

log_in_text = '''
Для авторизизации в системе введите Ваше имя:
'''

unauthorized_text = '''
Вы не подтвердили свою личность

Пожалуйста, нажмите /log_in для авторизации
'''

logged_in_text = '''
Вы уже в системе
'''

log_out_text = '''
Вы успешно вышли из системы! 
'''

error_text = '''
Ошибка!
'''

bad_auth_text = '''
Данный пользователь уже вошел в систему
Пожалуйста, выберите друго пользователя
'''

echo_text = '''
Нажмите /help для получения списка доступных команд
'''

auth_text = '''
Приятно познакомится, {}!
Нажми /help для просмотра возможностей бота
'''

help_text = '''
Список доступных команд:
/tick - отметить фильм
/untick - убрать отметку фильма
/add - добавить фильмы в свой список
/remove - убрать фильмы из своего списка
/list - открыть список своих фильмов
/list_user - открыть список фильмов другого пользователя

Дополнительно:
/help - узнать список возможностей
/log_out - выйти из системы
<a href = "{}">table_link</a> - открыть таблицу в браузере 

Для админа:
/admin - открыть панель администрирования
'''

tick_text = '''
Пожалуйста, выберите фильмы, которые вы хотите отметить и нажмите <em>закончить</em>
'''

untick_text = '''
Пожалуйста, выберите фильмы, с которых вы хотите снять отметку и нажмите <em>закончить</em>
'''

complete_text = '''
Операция успешно выполнена!
'''

ticked_text = '''  — ✅'''

unticked_text = '''  — ❌'''

removed_text = '''  — 🚫'''

completed_text = '''закончить  — 🆗'''

need_to_complete_text = '''
Пожалуйста, выберите фильмы и нажмите <em>закончить</em>
'''

add_text = '''
Введите названия фильмов, которые вы хотите добавить 
Название каждого фильма должно быть на отдельной строке
'''

remove_text = '''
Выберите фильмы для удаления, а затем нажмите <em>закончить</em>
'''


self_films_list_text = '''
Список Ваших фильмов:

'''

enter_username_list_text = '''
Выберите пользователя, чей список вы хотите посмотреть 
'''

bad_username_text = '''
Пожалуйста, выберите пользователя 
'''

user_films_list_text = '''
Список фильмов пользователя {}:

'''

auth_admin_text = '''
Введите Ваш идентификатор администратора и пароль

ВНИМАНИЕ: ввод должен быть в следующем формате:
username
password1234
'''

auth_admin_error_text = '''
Ошибка: неправильный логин или пароль 

Проверьте корректность вводимых данных и формат ввода
Введите данные еще раз, либо нажмите /cancel, чтобы вернуться на главную страницу
'''

auth_admin_welcome_text = '''
Добро пожаловать на панель администратора!

Список доступных команд:
/all_users - список всех пользователей
/add_user - добавить нового пользователя
/change_user - изменить данные пользователя
/remove_user - удалить пользователя
/disconnect_user - отключить пользователя (утеря старого аккаунта и т.д.)
/disconnect_all_users - отключить всех пользователей
/all_admins - список всех администраторов \n<b>(функция суперадминистратора)</b>
/disconnect_admin - отключить администратора \n<b>(функция суперадминистратора)</b>
/disconnect_all_admins - отключить всех администраторов \n<b>(функция суперадминистратора)</b>
/format - изменить формат таблицы (временно недоступно)

Дополнительно:
/help_admin - посмостреть список всех команд администратора
/exit - выход на главный экран
'''

exit_text = '''
Вы вышли из панели администрирования
'''

echo_admin = '''
Для просмотра списка доступных команд, нажмите /help_admin
'''