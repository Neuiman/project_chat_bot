from connection.requests import get_team_members, get_tasks_list, make_request
import asyncio
import logging
from datetime import datetime, timedelta
from app.handlers import send_message_to_executor


async def get_team_member_dict():
    team_members_list = await get_team_members()
    users_dict = {}
    for i in range(len(team_members_list)):
        user_first_name = team_members_list[i].get('user').get('first_name')
        user_id = team_members_list[i].get('user').get('id')
        users_dict[user_id] = user_first_name
    return users_dict


async def get_member_data_by_email(tg_email, datatype):

    team_members_list = await get_team_members()
    users_dict = {}
    for i in range(len(team_members_list)):
        shtab_email = team_members_list[i].get('user').get('username')
        if tg_email == shtab_email:
            return team_members_list[i].get('user').get(datatype)
    return 'incorrect email'


async def get_deadline_list(task_list):
    while task_list is True:
        users_dict = {}
        for i in range(len(task_list)):
            task_date = task_list[i].get('task').get('deadline')
            task_name = task_list[i].get('task').get('name')
            task_executor = task_list[i].get('task').get('executor')
            if is_less_than_one_day_left_from_now(task_date):
                return send_message_to_executor(task_date, task_executor, task_name)


async def is_less_than_one_day_left_from_now(date):
    if not isinstance(date, datetime):
        raise ValueError("Argument must be a datetime object")

    if date < datetime.now():
        return False

    time_left = date - datetime.now()
    if time_left < timedelta(days=1):
        return True
    else:
        return False


async def check_correct_email(tg_email):

    team_members_list = await get_team_members()
    users_dict = {}
    for i in range(len(team_members_list)):
        shtab_email = team_members_list[i].get('user').get('username')
        if tg_email == shtab_email:
            return 'Ok'
    return 'incorrect email'


async def task_list_pars():
    task_list = get_tasks_list()


async def daily_task():
    while True:
        now = datetime.now()
        next_run = datetime(now.year, now.month, now.day, 0, 0, 0) + timedelta(days=1)
        delay = (next_run - now).total_seconds()
        await asyncio.sleep(delay)
        await make_request()


async def get_role_by_email(tg_email):
    team_members_list = await get_team_members()
    users_dict = {}
    for i in range(len(team_members_list)):
        shtab_email = team_members_list[i].get('user').get('username')
        if tg_email == shtab_email:
            return team_members_list[i].get('role')
    return 'incorrect email'


async def get_current_date():
    current_date = datetime.date.today().isoformat()
    return current_date


async def general():
    await get_current_date()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(general())
    except KeyboardInterrupt:
        print('Interrupted')