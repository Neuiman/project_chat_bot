from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardRemove)
from app.middlewares import get_team_member_dict
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


choice_for_registration = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes')],
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
],
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    input_field_placeholder='верны ли данные?')


choice_for_task = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes2')],
    [InlineKeyboardButton(text='Отмена', callback_data='cancel2')]
],
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    input_field_placeholder='верны ли данные?')


next = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='далее')]],
                    resize_keyboard=True,
                    one_time_keyboard=True,
)

register_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Зарегистрироваться'
        )
    ]
],
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    input_field_placeholder='для продолжения нажмите кнопку')


async def reply_members():
    teams_dict = await get_team_member_dict()
    team_id_list = list(teams_dict.keys())
    team_list = list(teams_dict.values())
    keyboard = ReplyKeyboardBuilder()
    for i in range(len(team_list)):
        keyboard.add(KeyboardButton(text=team_list[i], callback_data=team_id_list[i], resize_keyboard=True))
    return keyboard.adjust(2).as_markup()
