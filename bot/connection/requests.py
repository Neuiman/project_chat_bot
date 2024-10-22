import aiohttp
import asyncio
import os
import logging

from dotenv import load_dotenv


load_dotenv()
token = os.getenv('SHTAB_TOKEN')
header = {'Authorization-Team': token,
          }
params = {
    'date_from': '1970-01-01',
    'date_until': '2024-01-17',
}


async def get_team_id():
    async with aiohttp.request('GET', f'https://my.shtab.app/public/api/teams/', headers=header) as resp:
        dict_command_data = await resp.json()
        team_id = dict_command_data.get('id')
        return team_id


async def get_team_members():
    async with aiohttp.request('GET', 'https://my.shtab.app/public/api/teams/members/', headers=header) as resp:
        command_data = await resp.json()
        return command_data


async def team_activity():
    async with aiohttp.request('get', f'https://my.shtab.app/public/api/reports/activity/'
                                      f'{await get_team_id()}/list/', headers=header, params=params) as resp:
        print(await resp.text())


async def login_check_for_access():
    async with aiohttp.request('GET', 'https://my.shtab.app/public/api/teams/members/', headers=header) as resp:
        team_member_list = (await resp.json())[0]
        user_data = team_member_list.get('user')
        login = user_data.get('username')

        print(user_data)
        return team_member_list.get('name')


async def print_user_activity(team_member, date):
    team_id = await get_team_id()
    if 'parametrs' not in locals():
        parametrs = {}
    if date:
        parametrs['date'] = date
    async with aiohttp.ClientSession() as session:
        async with aiohttp.request('GET', f'https://my.shtab.app/public/api/reports/activity'f'/'
                                          f'{team_id}/calendar/{team_member}/', headers=header,
                                   params=parametrs) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                print(f'Error: {resp.status}')
                return None


async def create_task(task):
    from app.middlewares import get_current_date
    current_date = get_current_date()
    task_params_dict = {'name': task['task_name'], 'datasource': 0, 'description': task['task_description'],
                        'type': 0, 'date_start': current_date}

    async with aiohttp.ClientSession() as session:
        async with aiohttp.request('POST', f'https://my.shtab.app/public/api/tasks/task/create/',
                                   headers=header, json=task_params_dict) as resp:
            if resp.status == 200:
                result = await resp.json()
                create_response = await create_task_executor(result.get('id'), task)
                return result, create_response
            else:
                return f'Error: {resp.status}'


async def create_task_executor(task_id, task):
    task_executor_dict = {'task_id': task_id, 'executor': task.get('task_executor_id')}
    async with aiohttp.request('POST', f'https://my.shtab.app/public/api/tasks/executors/{task_id}/create/',
                               headers=header, json=task_executor_dict) as resp:
        if resp.status == 200:
            result = await resp.json()
            create_manager_result = await create_task_manager(task_id, task)
            return result, create_manager_result
        else:
            return f'Error: {resp.status}'


async def create_task_manager(task_id, task):
    task_manager_dict = {'task_id': task_id, 'responsible': task.get('task_manager')}
    async with aiohttp.request('POST', f'https://my.shtab.app/public/api/tasks/executors/{task_id}/create/',
                               headers=header, json=task_manager_dict) as resp:
        if resp.status == 200:
            result = await resp.json()
            return result
        else:
            return f'Error: {resp.status}'


async def get_tasks_list():
    async with aiohttp.ClientSession() as session:
        async with aiohttp.request('get', 'https://my.shtab.app/public/api/tasks/task/list/',
                                   headers=header) as resp:
            return await resp.json()


async def delete_task(task_id):
    async with aiohttp.request('del', f'https://my.shtab.app/public/api/tasks/task/{task_id}/delete/',
                               headers=header) as resp:
        if resp.status == 200:
            result = await resp.json()
            return result
        else:
            return f'Error: {resp.status}'


async def make_request():
    from app.middlewares import get_deadline_list

    async with aiohttp.ClientSession() as session:
        async with session.get('https://my.shtab.app/public/api/tasks/task/list/') as resp:
            if resp.status == 200:
                await get_deadline_list(resp.json())
            else:
                return f'Request failed with status {resp.status}'


async def general():
    user_list = await create_task()

    print(user_list)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(general())
    except KeyboardInterrupt:
        print('Interrupted')
