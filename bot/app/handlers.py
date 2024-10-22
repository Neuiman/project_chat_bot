from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from connection.requests import *
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from functools import wraps


import database.DBrequests as DB


from app.middlewares import (get_team_member_dict,
                             get_member_data_by_email,
                             get_role_by_email,
                             check_correct_email)

from database.DBrequests import (get_user_role,
                                 shtab_id_by_tg_id,
                                 tg_id_by_stab_id,
                                 is_authorized,
                                 is_owner)


router = Router()


async def authorized_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if not is_authorized(message.from_user.id):
            await message.answer('You are not authorized to use this command.')
            return
        else:
            await func(message, *args, **kwargs)
    return wrapper


async def owner_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if not is_owner(message.from_user.id):
            await message.answer('You are not have enough permissions for this action ')
            return
        else:
            await func(message, *args, **kwargs)
    return wrapper


@router.message(Command('role'))
@authorized_only
async def user_role(message:Message) -> None:
    await message.answer(await get_user_role(message.from_user.id))


@router.message(Command('start'))
async def start_command(message: Message) -> None:
    await message.answer(f'Привет, {message.from_user.first_name},'
                         f' ты попал в бота, интрегрированного с системой управления проектами', reply_markup=kb.register_keyboard)


@router.message(Command('clear'))
@owner_only
async def clear_command(message: Message, bot: Bot) -> None:
    try:
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.chat.id, i)
    except TelegramBadRequest as ex:
        if ex.message == 'Bad Request: message to delete not found':
            print("Щеф, я все удалить!")


@router.message(Command('update_task'))
@authorized_only
async def update_task(message: Message) -> None:
    await message.answer(f'данная команда в будущем будет изменять уже созданную задачу для пользователя '
                         f'{message.from_user.first_name}')


@router.message(Command('delete_task'))
@authorized_only
async def delete_task(message: Message) -> None:
    await message.answer(f'данная команда в будущем будет удалять уже созданную задачу для пользователя '
                         f'{message.from_user.first_name}')


@router.message(Command('show_task_list'))
@authorized_only
async def show_tast_list(message: Message) -> None:
    await message.answer(f'данная команда в будущем будет показывать список задач пользователя '
                         f'{message.from_user.first_name}')


@router.message(Command('show_team_id'))
@authorized_only
async def show_team_member_list(message: Message) -> None:
    await message.answer(f'ID команды - {str(await get_team_id())}')


@router.message(Command('help'))
@authorized_only
async def help_command(message: Message) -> None:
    await message.answer('/start - команда для запуска бота\n'
                         '/help -  справка по всем доступным командам\n'
                         '/clear - отчистка истории чата'
                         '/create_task - создание нового task\'a\n'
                         '/delete_task - удаление task\'a\n'
                         '/show_task_list @user - вывод списка task\'ов пользователя @user\n'
                         '/show_team_id - вывод текущего ID команды\n')


@router.message(Command('delete_task'))
@authorized_only
async def user_markup(message: Message) -> None:
    await message.answer('выберите задачу, которую необходимо удалить', reply_markup=await kb.reply_members())


@router.message()
async def heandler_answer(message: Message):
    task_id = message.text
    await delete_task(task_id)


class Form(StatesGroup):
    email = State()
    password = State()
    shtab_id = State()
    tg_id = State()
    name = State()
    surname = State()
    role = State()


@router.message(F.text == 'Зарегистрироваться')
async def registration(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.set_state(Form.email)
    await bot.send_message(message.from_user.id, "Напишите email")


@router.message(Form.email)
async def process_email(message: Message, state: FSMContext, bot: Bot) -> None:
    check_result = await DB.check_user_in_BD(message.from_user.id, message.text)
    if not check_result:
        await state.update_data(email=str(message.text))
        await state.set_state(Form.password)
        data = await state.get_data()
        email = data['email']
        if await check_correct_email(email) == 'incorrect email':
            await state.clear()
            await bot.send_message(message.from_user.id, 'email не найден в системе управления проектами')
            return None

        await bot.send_message(message.from_user.id, 'Введите новый пароль: ')
    else:
        await state.clear()
        await bot.send_message(message.from_user.id, 'данный аккаунт зарегестрирован')
        return None


@router.message(Form.password)
async def process_email(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(password=str(message.text))
    await state.set_state(Form.shtab_id)
    await bot.send_message(message.from_user.id, 'производится поиск сотрудника с указанным email в '
                         'системе SHTAB', reply_markup=kb.next)


@router.message(Form.shtab_id)
async def process_shtab_id(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    email = data['email']
    shtab_id = await get_member_data_by_email(email, 'id')
    await state.update_data(shtab_id=int(shtab_id))
    await state.set_state(Form.tg_id)
    await bot.send_message(message.from_user.id, 'получение id телеграм аккаунта',
                               reply_markup=kb.next)


@router.message(Form.tg_id)
async def process_tg_id(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(tg_id=int(message.from_user.id))
    await state.set_state(Form.name)
    await bot.send_message(message.from_user.id, 'Получение имени из SHTAB',
                               reply_markup=kb.next)


@router.message(Form.name)
async def process_name(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    email = data['email']
    shtab_name = await get_member_data_by_email(email, 'first_name')
    await state.update_data(name=str(shtab_name))
    await state.set_state(Form.surname)
    await bot.send_message(message.from_user.id, 'получение имени',
                               reply_markup=kb.next)


@router.message(Form.surname)
async def process_surname(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    email = data['email']
    shtab_surname = await get_member_data_by_email(email, 'last_name')
    await state.update_data(surname=str(shtab_surname))
    await state.set_state(Form.role)
    await bot.send_message(message.from_user.id, 'Получение роли из Shtab',
                               reply_markup=kb.next)


@router.message(Form.role)
async def process_role(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    email = data['email']
    shtab_role = await get_role_by_email(email)
    await state.update_data(role=str(shtab_role))
    await bot.send_message(message.from_user.id, 'Регистрация завершена, проверьте данные')
    data = await state.get_data()
    await function(data, message)


async def function(data, message):
    await message.reply(str(data), reply_markup=kb.choice_for_registration)


@router.callback_query(F.data == 'cancel')
async def cancel_handler(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id-1)

    await state.clear()

    await callback.answer('регистрация прервана')


@router.callback_query(F.data == 'yes')
async def process_on_yes_choice(callback: CallbackQuery, state:FSMContext, bot: Bot) -> None:
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id-1)

    await callback.answer('вы успешно прошли регистрацию', show_alert=True)

    data = await state.get_data()

    tg_id = data['tg_id']
    email = data['email']
    password = data['password']
    shtab_id = data['shtab_id']
    name = data['name']
    surname = data['surname']
    role = data['role']
    await DB.set_user(tg_id, email, password, shtab_id, name, surname, role)  #send data to bd method

    await state.clear()
    await callback.message.answer('данные внесены в базу данных')


class Task(StatesGroup):
    task_name = State()
    task_maker = State()
    task_description = State()
    task_manager = State()


@router.message(Command('create_task'))
@authorized_only
async def task_creator(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(Task.task_name)
    await bot.send_message(message.from_user.id, 'Введите название задачи')


@router.message(Task.task_name)
async def create_task_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(task_name=message.text)
    await state.set_state(Task.task_maker)
    await bot.send_message(message.from_user.id, 'Введите исполнителя задачи')


@router.message(Task.task_maker)
async def create_task_maker(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(task_maker=message.text)
    await state.set_state(Task.task_description)
    await bot.send_message(message.from_user.id, 'Введите описание задачи')


@router.message(Task.task_description)
async def create_task_description(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(task_description=message.text)
    await state.set_state(Task.task_manager)
    await bot.send_message(message.from_user.id, 'Введите контролирующего')


@router.message(Task.task_manager)
async def create_task_manager(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(task_manager=message.text)
    data = await state.get_data()
    await bot.send_message(message.from_user.id, 'проверьте корректность введенных данных')
    name = data['task_name']
    maker = data['task_maker']
    description = data['task_description']
    manager = data['task_manager']
    await bot.send_message(message.from_user.id, f'Название задачи: {name}\n'
                                                 f'Исполнитель: {maker}\n'
                                                 f'Описание: {description}\n'
                                                 f'Контролирующий: {manager}', reply_markup=kb.choice_for_task)
    task_dict_for_request = {'task_name': name,
                             'task_description': description, 'task_executor_id': shtab_id_by_tg_id(maker.id),
                             'task_manager': shtab_id_by_tg_id(manager.id)}
    response = await create_task(task_dict_for_request)
    await message.answer(response)


@router.callback_query(F.data == 'cancel2')
async def cancel_handler(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.clear()

    await callback.answer("Создание task'a прервано")


async def send_message_to_executor(task_name, task_date, task_executor, bot: Bot):
    tg_id = await tg_id_by_stab_id(task_executor)
    await bot.send_message(chat_id=tg_id, text=f'срок исполнения задачи {task_name} подгодит к концу.'
                                               f'Необходимо завершить работу до - {task_date} ')


@router.callback_query(F.data == 'yes2')
async def process_on_yes_choice(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:

    await callback.answer('вы успешно создали task', show_alert=True)

    await state.clear()
    await callback.message.answer('данные записаны в систему управления проектами')