import inspect
import os
import sys


class ExpressionError(Exception):
    def __init__(self, expression):
        self.__m_expression = expression
        self.__m_traceback_filename = inspect.getframeinfo(inspect.currentframe().f_back).filename
        self.__m_tracebakc_lineno = inspect.currentframe().f_back.f_lineno
        self.__m_message = "invalid expression"
        # Use Python default exception handler to handle this exception.
        sys.last_type = type(self)
        sys.last_value = self
        sys.last_traceback = self.__traceback__

    def __str__(self):
        if self.__m_expression.count(
                "as") > 1:  # If the expression contains more than one "as" keyword, find the error index and indicate it.
            error_index = self.__m_expression.find("as", self.__m_expression.find("as") + 1)
            error_message = f"""File \"{os.path.abspath(self.__m_traceback_filename)}\", line {self.__m_tracebakc_lineno}\
            \n\t{self.__m_expression}\
            \n\t{' ' * error_index}^\
            \nExpressionError: {self.__m_message}
            """
        return error_message


class LangDictSearchError(Exception):
    # Error type.
    UNIVERSAL_WORD_EXIST_ERROR = 1
    SOURCE_LANG_DICT_MATCH_ERROR = 2
    TARGET_LANG_DICT_MATCH_ERROR = 3

    def __init__(self, error_type, error_word, source_lang, target_lang):
        self.__m_error_type = error_type
        self.__m_error_word = error_word
        self.__m_error_position = None
        self.__m_message = ""

        # Different error situations.
        if self.__m_error_type == LangDictSearchError.UNIVERSAL_WORD_EXIST_ERROR:
            self.__m_message = f"'{self.__m_error_word}' is not a universal word in language dictionaries"
        elif self.__m_error_type == LangDictSearchError.SOURCE_LANG_DICT_MATCH_ERROR:
            self.__m_error_position = source_lang
            self.__m_message = f"'{self.__m_error_word}' is not a native word in '{self.__m_error_position}' dictionary"
        elif self.__m_error_type == LangDictSearchError.TARGET_LANG_DICT_MATCH_ERROR:
            self.__m_error_position = target_lang
            self.__m_message = f"'{self.__m_error_word}' can not be converted to the native word in '{self.__m_error_position}' dictionary"

    def __str__(self):
        return self.__m_message

    @property
    def type(self):
        return self.__m_error_type

    @property
    def word(self):
        return self.__m_error_word

    @property
    def position(self):
        return self.__m_error_position
