from enum import Enum

"""
An enumeration representing two loading modes.

- ``REALTIME``: Static data files are read for each conversion.
- ``ONETIME``: Static data files are only read once when the object is instantiated for the first time.
"""
class LoadMode(Enum):
    REALTIME = 0
    ONETIME = 1


from easierfile import File
from ._errors import ExpressionError
from ._errors import LangDictSearchError
from ._lang_dict_parser import LangTypeLangDict


class _LangUniversal():
    def __init__(self, super_self, lang_dicts):
        self.__m_dict = lang_dicts
        self.__m_super_self = super_self

    def __getattr__(self, universal_word_form_call):
        """
        Chained calls enable the universal word to support object-oriented expression without string quotes in the code.
        """
        universal_word_form_call_chain = [universal_word_form_call]
        super_self = self.__m_super_self
        lang_dicts = self.__m_dict

        class ChainedClass:
            def __getattr__(self, universal_word_form_call):
                universal_word_form_call_chain.append(universal_word_form_call)
                return ChainedClass()

            def __repr__(self):
                """
                Final settlement of Chained Calls.
                """
                if universal_word_form_call_chain[-1] in lang_dicts.keys():
                    return super_self.str('.'.join(universal_word_form_call_chain[0:-1]), None, universal_word_form_call_chain[-1])
                else:
                    return super_self.str('.'.join(universal_word_form_call_chain))

        return ChainedClass()


class LangSwitcher:
    def __init__(self, include=(), load_mode=LoadMode.REALTIME):
        self.__m_dict = {}
        self._m_load_mode = load_mode

        # None represents the universal word.
        self.__m_default_source_lang = None
        self.__m_default_target_lang = None

        # Avoid parsing a tuple with only one element as a single string.
        if isinstance(include, tuple):
            for expression in include:
                self.__parse_expression(expression)
        else:
            self.__parse_expression(include)

        # One-time loading mode.
        if self._m_load_mode == LoadMode.ONETIME:
            self.__load_lang_dict()

    def __parse_expression(self,expression):
        """
        Parses expressions imported into language dictionaries via param<include>.

        There are two forms of this expression, one is full and the other is short.

        For example:

        1. ``full``: './en_us.lang as en_us'
        2. ``short``: './en_us.lang'

        Note that when using the short form, the name of the associated language will be the name of the file.
        """
        if expression.find("as") != -1:
            if expression.count("as") == 1:
                """
                A list of strings representing the distinct terms of the expression after it is parsed.

                - ``expression_parsing[0]``: The file path of the language dictionary.
                - ``expression_parsing[1]``: The associated language of the language dictionary.
                """
                expression_parsing = [expression_unit.strip() for expression_unit in expression.split("as")]
                dictionary_file = File(expression_parsing[0], False, False)
                dictionary_associated_lang = expression_parsing[1]
            else:
                raise ExpressionError(expression)
        else:
            dictionary_file = File(expression, False, False)
            dictionary_associated_lang = dictionary_file.info["name"]

        # Store language dictionary file information for different languages into member:private<self.__m_dict>.
        if not dictionary_file.state["exist"]:
            raise FileNotFoundError("Language dictionary not found: " + dictionary_file.info["path"])
        else:
            if dictionary_associated_lang in self.__m_dict.keys():
                self.__m_dict[dictionary_associated_lang].append(dictionary_file.info["path"])
            else:
                self.__m_dict[dictionary_associated_lang] = [dictionary_file.info["path"]]

    def __load_lang_dict(self):
        new_dict = self.__m_dict.copy()
        for dictionary_associated_lang, dictionary in self.__m_dict.items():
            if isinstance(dictionary, list):  # Indicates that var<dictionary> is a list of lang dict file path.
                new_dict[dictionary_associated_lang] = {}
                for dictionary_file_path in dictionary:
                    dict_file = File(dictionary_file_path, False, False)
                    if dict_file.info["ext"] == "lang":  # Parse the lang dict of lang type data.
                        new_dict[dictionary_associated_lang].update(LangTypeLangDict.loads(dict_file.content))
        self.__m_dict = new_dict

    def default_lang(self, source_lang="", target_lang=""):
        if source_lang != "":
            self.__m_default_source_lang = source_lang
        if target_lang != "":
            self.__m_default_target_lang = target_lang

    def str(self, word, source_lang="", target_lang=""):
        # Whether are default langs setting.
        if source_lang == "":
            source_lang = self.__m_default_source_lang
        if target_lang == "":
            target_lang = self.__m_default_target_lang

        # Real-time loading mode.
        if self._m_load_mode == LoadMode.REALTIME:
            self.__load_lang_dict()

        # Initialize lang dict search transition values.
        source_word = word
        universal_word = None
        target_word = None

        # Search for the universal word corresponding to the native word.
        if source_lang is None:
            is_matched = False
            for dictionary in self.__m_dict.values():
                if source_word in dictionary.keys():
                    universal_word = source_word
                    is_matched = True
            if not is_matched:
                raise LangDictSearchError(
                    LangDictSearchError.UNIVERSAL_WORD_EXIST_ERROR, source_word, source_lang, target_lang)
        else:
            is_matched = False
            for dictionary_universal_word, dictionary_native_word in self.__m_dict[source_lang].items():
                if dictionary_native_word == source_word:
                    universal_word = dictionary_universal_word
                    is_matched = True
            if not is_matched:
                raise LangDictSearchError(
                    LangDictSearchError.SOURCE_LANG_DICT_MATCH_ERROR, source_word, source_lang, target_lang)

        # Search for the native word corresponding to the universal word.
        if target_lang is None:
            target_word = universal_word
        else:
            is_matched = False
            for dictionary_universal_word, dictionary_native_word in self.__m_dict[target_lang].items():
                if dictionary_universal_word == universal_word:
                    target_word = dictionary_native_word
                    is_matched =True
            if not is_matched:
                raise LangDictSearchError(
                    LangDictSearchError.TARGET_LANG_DICT_MATCH_ERROR, source_word, source_lang, target_lang)
            
        return target_word

    @property
    def universal(self):
        return _LangUniversal(self, self.__m_dict)
