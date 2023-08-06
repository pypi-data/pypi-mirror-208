# -*- coding: UTF-8 -*-

def get_result_key(app_code: str, task_name: str, task_id: str):
    return f'celery_result:{app_code}:{task_name}:{task_id}'


def get_task_id_from_key(key: str):
    arr = key.split(':')
    if arr and len(arr) == 4:
        return arr[3]


def get_result_key_filter(app_code: str):
    return f'celery_result:{app_code}:*'
