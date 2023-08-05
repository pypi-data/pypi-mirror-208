from secrets import token_hex


def gen(length: int):
    return token_hex(length)[:length]


def create_random_new_unique_uid(length: int, uids_list: set):
    token = gen(length)
    count = 1
    while token in uids_list:
        token = gen(length)
        count += 1
        if count > 16 * length:
            length += 1
    return token


def create_custom_new_uid(uids_list: set, custom: str, append_to_custom: bool, sep: str | None):
    sep = '-' if sep is None else sep
    #
    if custom in uids_list:
        if not append_to_custom:
            raise ValueError('Custom Link is already exists!')
        length = 1
        custom_appended_to = f'{custom}{sep}{gen(length)}'
        count = 1
        while custom_appended_to in uids_list:
            custom_appended_to = f'{custom}{sep}{gen(length)}'
            count += 1
            if count > 16 * length:
                length += 1
        return custom_appended_to
    else:
        return custom
