import datetime


class SimpleTradeLog:
    LEVEL_SILLY = 'SILLY'
    LEVEL_INFO = 'INFO'
    LEVEL_ERROR = 'ERROR'
    __LEVEL_INFO_COLOR = '\033[92m'
    __LEVEL_SILLY_COLOR = '\033[95m'
    __LEVEL_ERROR_COLOR = '\033[91m'
    __ENDC = '\033[0m'

    def __init__(self, level):
        self.level = level

    def __log(self, level, message):
        if self.__is_silly(level):
            return
        print('{}[{}] [{}]{}'.format(
            self.__get_level_color(level),
            datetime.datetime.now(),
            level,
            self.__ENDC
        ), message)

    def __get_level_color(self, level):
        if level == self.LEVEL_INFO:
            return self.__LEVEL_INFO_COLOR
        if level == self.LEVEL_SILLY:
            return self.__LEVEL_SILLY_COLOR
        return self.__LEVEL_ERROR_COLOR

    def __is_silly(self, level):
        return level == self.LEVEL_SILLY and self.level != self.LEVEL_SILLY

    def error(self, message):
        self.__log(self.LEVEL_ERROR, message)

    def silly(self, message):
        self.__log(self.LEVEL_SILLY, message)

    def info(self, message):
        self.__log(self.LEVEL_INFO, message)
