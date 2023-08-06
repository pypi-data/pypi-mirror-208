import re
import sys
from dataclasses import dataclass
from typing import List
from bytez.tasks.super_resolution import SuperResolutionModels
from bytez.tasks.style_transfer import StyleTransferModels
from bytez.task_list import task_list


def concat_non_alphanumeric(arr):
    updated_arr = []
    for item in arr:
        updated_item = re.sub(r'\W+', '_', item)
        if re.match(r'^\d', updated_item):
            updated_item = '_' + updated_item
        updated_arr.append(updated_item)
    return updated_arr


def main(filename: str):
    with open(filename, 'r') as f:
        lines = f.readlines()

    task_class_started = False
    task_class_ended = False
    for i, line in enumerate(lines):
        if 'class task:' in line:
            task_class_started = True
        elif task_class_started and ':' in line:
            task_class_ended = True
            break

    task_names = concat_non_alphanumeric(task_list)
    task_class_code = '\n'.join(
        ['    ' + name + ' = None' for name in task_names])

    if task_class_started and not task_class_ended:
        # The Task class has already been defined, so we can add the task names to it
        for i, line in enumerate(lines):
            if 'class task:' in line:
                lines.insert(i+1, task_class_code)
                break
    else:
        # The Task class has not been defined, so we need to define it with the task names
        task_class_code = f"""
@dataclass
class Task:
{task_class_code}
"""
        lines.append(task_class_code)

    with open(filename, 'w') as f:
        f.write(''.join(lines))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python add_tasks_to_task_class.py <filename>')
    else:
        main(sys.argv[1])
