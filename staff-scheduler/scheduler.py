import pandas as pd
import numpy as np
from random import sample

def read_file(path):
    df = pd.read_csv(path, header=0, index_col=0, sep=';', dayfirst=True, parse_dates=['timestamp'])
    return df


def insert_person(ins_stuff, schedule, timestamp):
    """
    Функция добавляет указанного сотрудника в указанном расписании в указанную дату на первое свободное место
    param:
    ins_stuff - строка dataframe с столбцами (person, room)
    schedule - dataframe с столбцами
        timestamp - дата в формате numpy.datetime64
        month - наименование месяца в формате String
        week - номер недели в формате Integer
        day_of_week - наименовение дня недели в формате String
        room - Номер комнаты в формате Integer
        place - Номер места в формате Integer
        staff - Фамилия и имя сотрудника в фомрмате String


    """
    room = ins_stuff['room']
    place = schedule.loc[(schedule['timestamp'] == timestamp) & (schedule['room'] == room)
                         & (schedule['staff'] == 'Free'), 'place'].min()
    schedule.loc[(schedule['timestamp'] == timestamp) & (schedule['room'] == room)
                 & (schedule['place'] == place), 'staff'] = ins_stuff['staff']
    return 0


def sort_place(schedule):
    """
    Функция переносит строки "Бронирование" на последние дни. Функция изменяет входящий dataframe
    param:
    schedule - dataframe с столбцами:
        timestamp - дата в формате numpy.datetime64
        month - наименование месяца в формате String
        week - номер недели в формате Integer
        day_of_week - наименовение дня недели в формате String
        room - Номер комнаты в формате Integer
        place - Номер места в формате Integer
        staff - Фамилия и имя сотрудника в фомрмате String

    """
    week = schedule['week'].unique()

    for w in week:
        days = schedule.loc[schedule['week'] == w, 'day_of_week'].unique()
        for d in days:
            rooms = schedule.loc[(schedule['week'] == w) & (schedule['day_of_week'] == d), 'room'].unique()
            for r in rooms:
                places = schedule.loc[(schedule['week'] == w) & (schedule['day_of_week'] == d)
                                      & (schedule['room'] == r), 'place'].unique()
                flag = True
                while flag:
                    flag = False
                    for p in places[:-1]:
                        s_1 = schedule.loc[(schedule['week'] == w) & (schedule['day_of_week'] == d)
                                           & (schedule['place'] == p) & (schedule['room'] == r)]
                        s_2 = schedule.loc[(schedule['week'] == w) & (schedule['day_of_week'] == d) & (
                                    schedule['place'] == (p + 1)) & (schedule['room'] == r)]
                        if s_1['staff'].values == 'Бронирование' and s_2['staff'].values != 'Бронирование':
                            schedule['staff'].loc[(schedule['week'] == w) & (schedule['day_of_week'] == d)
                                                  & (schedule['place'] == p) & (schedule['room'] == r)] = s_2[
                                'staff'].values
                            schedule['staff'].loc[(schedule['week'] == w) & (schedule['day_of_week'] == d)
                                                  & (schedule['place'] == (p + 1)) & (
                                                              schedule['room'] == r)] = 'Бронирование'
                            flag = True
    return 0


def insert_group(staffs, weeks, schedule):
    """
    Функция вставляет группу сотрудников, которые должны выходить в один день
    param:
    staffs - dataframe, содержащий столбцы
        staff - Фамилия и имя сотрудника в формате String
        room - номер комнаты к которой в которой размещается сотрудник в формате Integer

    weeks -  список недель, в которые размещается группа
    schedule - DataFrame с столбцами:
        timestamp - дата в формате numpy.datetime64
        month - наименование месяца в формате String
        week - номер недели в формате Integer
        day_of_week - наименовение дня недели в формате String
        room - Номер комнаты в формате Integer
        place - Номер места в формате Integer
        staff - Фамилия и имя сотрудника в формате String
    """
    count_staff = staffs['staff'].count()
    for week in weeks:
        free_days = []
        days = schedule.loc[schedule['week'] == week, 'timestamp'].unique()

        # Получае все дни на неделе, в которые может уместиться группа
        for d in days:
            if schedule.loc[
                (schedule['timestamp'] == d) & (schedule['staff'] == 'Free'), 'staff'].count() > count_staff:
                free_days.append(d)

        # Записываем группу в случайный день

        if free_days:
            day = sample(free_days, 1)
            for i in staffs.index:
                per = staffs.loc[i]
                insert_person(per, schedule, day[0])
    return 0


def random_insert_person(person, days, schedule):
    """
    Распределеяет случайным образом cотрудника person по дням, указанным в days по  dataframe schedule
    param:
    person - dataframe с столбцами:
        staff - Фамилия и имя сотрудника в формате String
        room - номер комнаты к которой в которой размещается сотрудник в формате Integer

    days - список дней в которые необходимо вывести сотрудника

    schedule - DataFrame с столбцами:
        timestamp - дата в формате numpy.datetime64
        month - наименование месяца в формате String
        week - номер недели в формате Integer
        day_of_week - наименовение дня недели в формате String
        room - Номер комнаты в формате Integer
        place - Номер места в формате Integer
        staff - Фамилия и имя сотрудника в формате String

    """
    # Создаем датафрейм с датами и количеством свободных мест в кабинете сотрудника
    dt_days = pd.DataFrame([[x, schedule.loc[(schedule['timestamp'] == x)
                                             & (schedule['room'] == person['room']) & (
                                                     schedule['staff'] == 'Free'), 'staff'].count()] for x in days],
                           columns=['days', 'count place'])

    # Получае максимальное количество свободных кабинетов
    max_place = dt_days['count place'].max()
    # Случайно выбираем один день для размещения сотрудника
    max_days = dt_days.loc[dt_days['count place'] == max_place, 'days'].to_list()
    if max_days:
        day = sample(max_days, 1)
        insert_person(person, schedule, day[0])

    return 0
