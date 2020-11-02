import datetime
import random

import pygsheets
from pygsheets.worksheet import Worksheet

from static import consts
from static.config import TIMETABLE_URL, QUOTES_URL, service_file_path
import src.subject as sub

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')

EMPTY_WEEKDAY_TIMETABLE = {'online': [], 'offline': []}


class Server:
    """
    Server class is responsible for talking with different API's and parsing their data

    APIs:
    Google Sheet API - for parsing tables with data such as timetables deadlines and more
    """

    # Server is singleton
    __instance = None

    # --- params for parsing timetable ---
    # timetable rectangle
    __tt_top_left = 'B1'
    __tt_bottom_right = 'O49'

    # wight of timetable
    __tt_number_of_cols = 14

    # attendance cols
    __tt_attendance = {
        consts.ATTENDANCE_OFFLINE: [0, 6],
        consts.ATTENDANCE_ONLINE: [7, 13],
        consts.ATTENDANCE_BOTH: [0, 13],
    }

    # weekdays in timetable
    __tt__weekdays_map = {
        consts.MONDAY: 'пн',
        consts.TUESDAY: 'вт',
        consts.WEDNESDAY: 'ср',
        consts.THURSDAY: 'чт',
        consts.FRIDAY: 'пт',
        consts.SATURDAY: 'сб',
    }

    # parity in timetable
    __tt_week_parity_map = {
        'ч': consts.WEEK_EVEN,
        'н': consts.WEEK_ODD,
        'ч/нч': consts.WEEK_BOTH,
    }

    # --- params for parsing deadlines ---
    __dl_column = (4, 14)
    __dl_days_start = 'B2'
    __zero_day_id = datetime.date(2020, 10, 26).toordinal()

    def __init__(self):
        logger.info('Starting Server...')
        if not Server.__instance:
            self.__gc = pygsheets.authorize(service_file=service_file_path)

            # timetable
            self.__sh_tt = self.__gc.open_by_url(TIMETABLE_URL)
            self.__wks_tt: Worksheet = self.__sh_tt.sheet1

            # quotes
            self.__sh_qu = self.__gc.open_by_url(QUOTES_URL)
            self.__wks_qu: Worksheet = self.__sh_qu.sheet1

        logger.info('Server started successfully')

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Server()
        return cls.__instance

    # ------ TIMETABLE ------

    def get_weekday_timetable(self, weekday, valid_subject_names, attendance, week_parity) -> dict:
        """returns weekday as dict {attendance: list of subjects}"""

        # get all values
        values = self.__get_tt_values()
        # get the filter for user's subjects
        subject_filter = Server.__subject_compare(valid_subject_names)

        return Server.__make_weekday_table(
            values=values, weekday=weekday,
            attendance=attendance, week_parity=week_parity,
            subject_filter=subject_filter,
        )

    def get_subject_timetable(self, subject, subtype, attendance) -> dict:
        """get timetable for specified subject"""

        # get all values
        values = self.__get_tt_values()
        # get the filter for the subject
        subject_filter = Server.__subject_compare(subject_set=sub.SUBJECTS[subject].get_all_timetable_names(subtype))
        # dict {weekday: {online: tt, offline: tt}} - values maybe None
        retval = {}
        for weekday in Server.__tt__weekdays_map.keys():
            weekday_table = Server.__make_weekday_table(
                values=values, weekday=weekday,
                attendance=attendance, week_parity=consts.WEEK_BOTH,
                subject_filter=subject_filter,
            )
            if weekday_table != EMPTY_WEEKDAY_TIMETABLE:
                retval[weekday] = weekday_table
        return retval

    @staticmethod
    def __make_weekday_table(values, weekday, attendance, subject_filter, week_parity=consts.WEEK_BOTH) -> dict:
        """returns dict {'online': tt1, 'offline': tt1}"""

        # get weekday frame
        start_row, end_row = Server.__find_weekday_frame(values, weekday)

        # make dicts according to attendance
        online_dict = (Server.__parse_and_make(
            values=values,
            start_row=start_row, end_row=end_row,
            attendance=consts.ATTENDANCE_ONLINE, week_parity=week_parity,
            subject_filter=subject_filter,
        ) if attendance != consts.ATTENDANCE_OFFLINE else [])
        offline_dict = (Server.__parse_and_make(
            values=values,
            start_row=start_row, end_row=end_row,
            attendance=consts.ATTENDANCE_OFFLINE, week_parity=week_parity,
            subject_filter=subject_filter,
        ) if attendance != consts.ATTENDANCE_ONLINE else [])

        return {'online': online_dict, 'offline': offline_dict}

    def __get_tt_values(self):
        """gets timetable from google sheets"""
        return self.__wks_tt.get_values(self.__tt_top_left, self.__tt_bottom_right)

    @staticmethod
    def __true_filter(*args, **kwargs):
        """returns True"""
        return True

    @staticmethod
    def __subject_compare(subject_set: set):
        """filter for subjects, checks if provided row is for valid subject"""

        # row: [time, parity, subject, teacher, place]
        def inner(row):
            return row[2] in subject_set

        return inner

    @staticmethod
    def __accept_parity(sub_parity, required_parity) -> bool:
        """checks if subject's parity meets the requirements"""
        return sub_parity == required_parity or sub_parity == consts.WEEK_BOTH or required_parity == consts.WEEK_BOTH

    @staticmethod
    def __find_weekday_frame(table, weekday):
        """finds frame for weekday in timetable"""
        table_weekday = Server.__tt__weekdays_map[weekday]
        found_start = False
        start_row = None
        end_row = None
        # [start_row, end_row)
        for row in range(len(table)):
            # first row of next weekday or the ending of the table
            if found_start and (table[row][0] in Server.__tt__weekdays_map.values() or row == len(table) - 1):
                end_row = row
                break
            # first row of the frame
            if table[row][0] == table_weekday:
                start_row = row + 1
                found_start = True
        return start_row, end_row

    @staticmethod
    def __parse_and_make(values, start_row, end_row, attendance, week_parity=consts.WEEK_BOTH, subject_filter=None):
        """takes rows from weekday frame and makes dict"""
        table = Server.__parse_table(values, start_row, end_row, attendance)
        return Server.__make_subject_dict(table, week_parity, subject_filter)

    @staticmethod
    def __parse_table(table, start_row, end_row, attendance):
        """takes not empty rows from weekday's frame"""
        [start_col, end_col] = Server.__tt_attendance[attendance]
        # cols: [id, time, parity, subject, teacher, place]
        retval = []
        for row in range(start_row, end_row):
            # check if subject's row is empty, as time col might be empty
            if table[row][start_col + 2] != '':
                retval.append(table[row][start_col + 1:end_col - Server.__tt_number_of_cols])
        return retval

    @staticmethod
    def __make_subject_dict(raw_subjects, week_parity=consts.WEEK_BOTH, subject_filter=None) -> list:
        """makes as dict out of each row"""
        if subject_filter is None:
            subject_filter = Server.__true_filter
        retval = []
        for row in raw_subjects:
            subject_parity = Server.__tt_week_parity_map[row[1]]
            if Server.__accept_parity(subject_parity, week_parity) and subject_filter(row):
                subject = {
                    'time': row[0],
                    'parity': row[1],
                    'subject': row[2],
                    'teacher': row[3],
                    'place': row[4]
                }
                retval.append(subject)
        return retval

    # ------ QUOTE ------

    def get_random_quote(self):
        values = self.__get_quotes()
        count = len(values)
        index = random.randint(0, count - 1)
        quote, author = values[index]
        while not author and index > 0:
            index = index - 1
            author = values[index][1]
        return quote, author

    def __get_quotes(self):
        return self.__wks_qu.get_all_values(
            include_tailing_empty_rows=False,
        )[1:]


Server.get_instance().get_random_quote()
