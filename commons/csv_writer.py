import datetime
import re

emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002500-\U00002BEF"  # chinese char
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           u"\U0001f926-\U0001f937"
                           u"\U00010000-\U0010ffff"
                           u"\u2640-\u2642"
                           u"\u2600-\u2B55"
                           u"\u200d"
                           u"\u23cf"
                           u"\u23e9"
                           u"\u231a"
                           u"\ufe0f"  # dingbats
                           u"\u3030"
                           u"\xb2"
                           "]+", flags=re.UNICODE)


def _sanitize(row):
    return emoji_pattern.sub(r'', row)


def _prepare_header(content: list):
    header = []
    if len(content) > 0:
        for key in content[0]:
            header.append(key)
    return header


def _prepare_row(headers_row, item):
    row = []
    for header in headers_row:
        value = ""
        if header in item:
            value = "\"" + str(item[header]) + "\""
        row.append(value)
    return row


def write(file: str, content: list[dict], separator: str = ";", headers: list[str] = None):
    headers_row = headers if headers is not None else _prepare_header(content)
    with open(file.replace("{timestamp}", datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")), "w", encoding="utf-8") as f:
        f.write(separator.join(headers_row) + "\n")
        for item in content:
            row = _prepare_row(headers_row, item)
            f.write(_sanitize(separator.join(row)) + "\n")
