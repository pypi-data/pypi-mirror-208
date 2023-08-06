from os import (
    environ,
    getcwd,
    getenv
)
from os.path import isfile, join as path_join
from sys import argv, exit
from typing import List

from list_cli.processors import MultiProcessor, Processor


def _env_list_value(key, default='') -> List[str]:
    return list(filter(None, getenv(key, default).split(',')))


def _get_database_file_paths() -> List[str]:
    database_file_paths = _env_list_value('DATABASE_FILE_PATHS')
    if database_file_paths:
        return database_file_paths
    database_file_path = getenv('DATABASE_FILE_PATH')
    if database_file_path:
        return [database_file_path]
    database_names = _env_list_value('DATABASE_NAMES')
    if not database_names:
        database_names = [getenv('DATABASE_NAME', 'LIST')]
    database_file_paths = []
    for database_name in database_names:
        if isfile(database_name):
            database_file_paths.append(path_join(getcwd(), database_name))
            continue
        database_file_paths.append(
            path_join(
                environ['HOME'],
                '.list',
                database_name
            )
        )
    return database_file_paths


def _get_processor(database_file_paths: List[str]) -> MultiProcessor | Processor:
    if len(database_file_paths) > 1:
        return MultiProcessor(database_file_paths)
    return Processor(database_file_paths[0])


def main():
    database_file_paths = _get_database_file_paths()
    if not database_file_paths:
        exit(1)
    process_result = _get_processor(database_file_paths).process(*argv[1:])
    if process_result.had_error:
        exit(1)


if __name__ == '__main__':
    main()
