import os


def _help(target_parts, file_parts, i, j):
    if i == len(target_parts) and j == len(file_parts):
        return True

    if i < len(target_parts) and j < len(file_parts):
        if target_parts[i] == '*':
            return _help(target_parts, file_parts, i + 1, j + 1)
        elif target_parts[i] == '**':
            return (_help(target_parts, file_parts, i + 1, j) or  # ** match 0
                    _help(target_parts, file_parts, i, j + 1) or  # ** match >1
                    _help(target_parts, file_parts, i + 1, j + 1))  # ** match 1 folder
        elif target_parts[i] == file_parts[j]:
            return _help(target_parts, file_parts, i + 1, j + 1)

    return False


def check_file_path(target_path, file_path):
    target_parts = target_path.split('/')
    file_parts = file_path.split(os.path.sep)
    return _help(target_parts, file_parts, 0, 0)
