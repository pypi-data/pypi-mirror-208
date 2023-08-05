class LangDictParser:
    """
    The data structure of each language dictionary is uniformly composed of pairs, each consisting of a universal word
    and its corresponding native word.

    - ``universal word``: Similar to the object-oriented usage, generally expressed in English.
    - ``native word``: Native word of the language associated with the lang dict.
    """

    @classmethod
    def loads(cls, lang_dict):
        pass

    @classmethod
    def dumps(cls, python_dict: dict):
        pass


class LangTypeLangDict(LangDictParser):
    @classmethod
    def loads(cls, lang_dict: str):
        python_dict = {}
        line_index = 1
        for line in lang_dict.split('\n'):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                line = line[:line.index("#")]
            if "=" not in line:
                raise ValueError(f"invalid lang type data, line {line_index} is missing at most one equals sign")
            key, value = line.split("=")
            python_dict[key.strip()] = value.strip()
            line_index += 1
        return python_dict

    @classmethod
    def dumps(cls, python_dict: dict):
        if not isinstance(python_dict, dict):
            raise ValueError("invalid dict")
        lang_dict = ""
        for key, value in python_dict.items():
            lang_dict += f"{key} = {value}\n"
        return lang_dict
