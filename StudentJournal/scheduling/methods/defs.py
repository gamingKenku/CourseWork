import datetime
from dateutil.relativedelta import relativedelta


def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    return from_date - relativedelta(years=years)


def num_years(begin, end=None):
    if type(begin) == str:
        begin = datetime.datetime.strptime(begin, "%Y-%m-%d").date()
    elif type(begin) == datetime.datetime:
        begin = begin.date()

    if end is None:
        end = datetime.date.today()
    num_years = int((end - begin).days / 365.2425)
    if begin > yearsago(num_years, end):
        return num_years - 1
    else:
        return num_years
    

def is_student(user):
    return user.groups.filter(name='student').exists()


def is_parent(user):
    return user.groups.filter(name='parent').exists()


def is_teacher(user):
    return user.groups.filter(name='teacher').exists()


def is_head_teacher(user):
    return user.groups.filter(name='head_teacher').exists()


def is_director(user):
    return user.groups.filter(name='director').exists()