import json
import requests

from requests import RequestException, Timeout
from typing import List
from flowhigh.auth import Authentication


class Formatter:

    _formatted_string: str

    def get_formatted_string(self) -> str:
        return self._formatted_string

    def __init__(self,  response: dict, format_option: str = "compact"):
        if response['format']:
            self._formatted_string = self.format_sql(response['format'], format_option)
        else:
            raise Exception("String with Markers Not Found")

    @classmethod
    def from_sql(cls, sql: str, format_option: str = "compact"):
        try:
            access_token = Authentication.authenticate_user()
            assert access_token, "UNAUTHENTICATED!"
            headers = {
                "User-Agent": "python/sqlanalyzer-0.0.1",
                "Content-type": "application/json",
                "Authorization": "Bearer " + access_token
            }
            url = "https://fhdev.sonra.io/api/formatter"
            # pre-processing to make sure that there is at least a space before a new line
            sql.replace("\n", " \n")
            data = {"sql": sql, "json": True, "xml": True}
            response = requests.post(url, json=data, headers=headers, timeout=5)
            # refresh token is invalid -> retry authentication
            if response.status_code == 401:
                access_token = Authentication.request_device_code()
                headers = {
                    "User-Agent": "python/sqlanalyzer-0.0.1",
                    "Content-type": "application/json",
                    "Authorization": "Bearer " + access_token
                }
                response = requests.post(url, json=data, headers=headers, timeout=5)
            # empty response from client
            if response.status_code == 204:
                raise RequestException("API is not available")
            # status code >= 400
            response.raise_for_status()
            json_data = json.loads(response.content)
            return cls(response=json_data, format_option=format_option)
        except Timeout as e:
            raise RequestException("API is not available") from e

    @classmethod
    def from_txt_response(cls, res: str, format_option: str = "compact"):
        json_data = json.loads(res)
        return cls(response=json_data, format_option=format_option)

    @classmethod
    def format_sql(cls, string: List[str], format_option: str) -> str:
        if len(string) == 0 or string is None:
            return ""

        sql_data: str = ""
        for i in range(len(string)):
            sql_data += _process_data(string[i], selected_option=format_option)

            if string[i].startswith("--") or string[i].startswith("//"):
                sql_data += "\n"
            elif len(string[i]) > 0 and i < len(string) - 1:
                sql_data += "\n"

        return sql_data


def _process_data(marked_sql: str, selected_option: str) -> str:
    _lines: List[dict] = []

    length: int = len(marked_sql)
    level: int = 0
    str_sql: str = ""
    pre_position: int = 0
    max_level: int = 0
    i = 0
    while i < length:
        letter = marked_sql[i]
        if letter == "➕":
            level += 1
            max_level = max(max_level, level)
        if letter == "➖":
            level -= 1
            if level < 0:
                return ""
        if letter == "⛓":
            str_sql += marked_sql[pre_position: i]
            pre_position = i + 1
            if selected_option == "comfortable":
                str_sql += "✖" + str(level) + " "
        if letter == "❌" or letter == "✖" or letter == "⚓":
            str_sql += marked_sql[pre_position: i]
            str_sql += letter + str(level) + " "
            pre_position = i + 1

        length = len(marked_sql)
        i += 1

    str_sql += marked_sql[pre_position:]
    _lines.append({"id": 0, "value": str_sql, "parent_id": -1})

    # 1. split lines
    for i_level in range(max_level + 1):
        for line in _lines:
            if line["value"] != "":
                _lines = _split_line(_lines, line, "❌", i_level)

    for i_level in range(max_level + 1):
        for line in _lines:
            if line["value"] != "":
                _lines = _split_line(_lines, line, "✖", i_level)

    # 2. order lines
    temp_lines = list(_lines)
    _lines = []
    _lines = _order_line(_lines, temp_lines)

    # 3. remove end spaces
    _lines = _compact_line(_lines, selected_option)

    # 4. arrange anchors
    offset = []
    for i_level in range(max_level + 1):
        offset.append(i_level * 4)

    _lines_copy = _lines.copy()
    for line in _lines_copy:
        _lines = _align_anchor(_lines, line, offset)

    # 5. clean markers
    for line in _lines:
        _clean_markers(line)

    # 6. make sql
    return _make_sql(_lines)


def _split_line(_lines, line_dict: dict, marker: str, level: int):
    length = len(line_dict["value"])
    line = line_dict["value"]
    # Need to add wrapping limits here if we implement it

    pre_position = 0
    i = 0
    while i < length:
        if line[i] == marker:
            j = i + 1
            while j < length:
                if line[j] == " ":
                    break
                length = len(line)
                j += 1

            # eslint-disable-next-line eqeqeq
            if int(line[i + 1: j]) == level:
                value = line[pre_position: i]
                _lines.append({
                    "id": len(_lines),
                    "value": value,
                    "parent_id": line_dict["id"]
                })
                pre_position = j + 1

            i = j

        length = len(line)
        i += 1

    if pre_position > 0:
        _lines.append({
            "id": len(_lines),
            "value": line[pre_position:],
            "parent_id": line_dict["id"]
        })

        line_dict["value"] = ""
    return _lines


def _order_line(_lines, temp_lines: List[dict], line_id: int = 0):
    child_ids = []
    for line in temp_lines:
        if line["parent_id"] == line_id:
            child_ids.append(line["id"])

    if len(child_ids) == 0:
        if temp_lines[line_id] and temp_lines[line_id]["value"] != "":
            _lines.append(temp_lines[line_id])
        return

    for child in child_ids:
        _order_line(_lines, temp_lines, child)
    return _lines


def _compact_line(_lines, selected_option: str):
    for line in _lines:
        if line["value"] != "":
            str_line = line["value"]

            # remove spaces after '\n'
            i = 0
            length = len(str_line)
            while i < length:
                if str_line[i] == "\n":
                    if str_line[i + 1:].replace(" ", "") == "":
                        line["value"] = str_line[0: i]
                        break

                length = len(str_line)
                i += 1

            # process black circle
            tokens: List[str] = line["value"].split("⚫")
            if len(tokens) > 1:
                line["value"] = ""
                for idx, token in enumerate(tokens):
                    if token:
                        token = token.strip()

                        if selected_option != "compact" and idx < len(tokens) - 1:
                            token = token + " "

                        line["value"] += token

    return _lines


def _align_anchor(_lines, line_dict: dict, offset: List):
    length = len(line_dict["value"])
    max_keyword_length = 7
    i = 0
    while i < length:
        if line_dict["value"][i] == "⚓":
            pad_length = 0
            if i < max_keyword_length:
                pad_length = max_keyword_length - i

            level = 0
            j = i + 1
            while j < length:
                if line_dict["value"][j] == " ":
                    level = int(line_dict["value"][i + 1: j])

                    # check next level in this line
                    k = j + 1
                    while k < length:
                        if line_dict["value"][k] == "⚓":
                            l = k + 1
                            while l < length:
                                if line_dict["value"][l] == " ":
                                    n_level = int(line_dict["value"][k + 1: l])
                                    if n_level > level:
                                        offset[n_level] = offset[n_level - 1] - max_keyword_length + k - 1
                                    break

                                length = len(line_dict["value"])
                                l += 1
                            break

                        length = len(line_dict["value"])
                        k += 1
                    break
                length = len(line_dict["value"])
                j += 1

            pad_length += offset[level]
            line_dict["value"] = line_dict["value"][0: i].rjust(pad_length + i - 1, " ") + line_dict["value"][j + 1:]

            break

        length = len(line_dict["value"])
        i += 1

    return _lines


def _clean_markers(line_dict: dict):
    is_back_arrow_line = False
    length = len(line_dict["value"])
    i = 0
    while i < length:
        letter = line_dict["value"][i]
        if letter == "⚓" or letter == "❌" or letter == "✖":
            j = i + 1
            while j < length:
                if line_dict["value"][j] == " ":
                    break
                length = len(line_dict["value"])
                j += 1
            line_dict["value"] = line_dict["value"][0: i] + line_dict["value"][j + 1:]
            i -= 1

        if letter == "➕" or letter == "➖":
            line_dict["value"] = line_dict["value"][0: i] + line_dict["value"][i + 1:]
            i = i - 1

        if letter == "←":
            line_dict["value"] = line_dict["value"][0: i] + line_dict["value"][i + 1:]
            i -= 1
            is_back_arrow_line = True

        # if letter == '⛓':
        #     line = line[0: i] +  '\n' if option == 'comfortable' else '' + line[i + 1:]
        #     i = i - 1
        #     break
        #

        if letter == "⧆":
            line_dict["value"] = line_dict["value"][0: i] + "" + line_dict["value"][i + 1:]
            i = i - 1

        length = len(line_dict["value"])
        i += 1

    if is_back_arrow_line:
        line_dict["value"].strip()


def _make_sql(_lines) -> str:
    sql = ""
    for index, line in enumerate(_lines):
        sql += line["value"]
        if index < len(_lines) - 1:
            sql += "\n"

    return sql


def split_to_substrings(string, n) -> List[str]:
    arr: List[str] = []

    prev = 0
    for index in range(len(string)):
        if index - prev >= n and string[index] == " ":
            arr.append(string[prev: index])
            prev = index

    arr.append(string[prev:])

    return arr
