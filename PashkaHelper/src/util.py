def to_not_attendance(attendance):
    if attendance == 'online':
        return 'offline'
    elif attendance == 'offline':
        return 'online'
    elif attendance == 'both':
        return 'online'
    else:
        raise ValueError(f'Invalid attendance type : {attendance}')


def to_not_page(page):
    if page == 'main':
        return 'timetable'
    elif page == 'timetable':
        return 'main'
    else:
        raise ValueError(f'Invalid page type : {page}')


def if_none(a, b):
    return a if a is not None else b