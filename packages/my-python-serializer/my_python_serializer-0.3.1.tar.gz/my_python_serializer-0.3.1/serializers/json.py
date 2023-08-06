import frozendict
from serializers.constants import VALUE_FIELD, TYPE_FIELD
import re


def serialize_json(obj):
    ans = ""
    list_ = []
    current_flag = False

    if type(obj) == frozendict.frozendict or type(obj) == dict:
        for key, value in obj.items():
            if key == VALUE_FIELD or key == TYPE_FIELD:
                list_.append("" + serialize_json(key) + ": " + serialize_json(value) + "")
                current_flag = True

            else:
                list_.append("[" + serialize_json(key) + ", " + serialize_json(value) + "]")
                current_flag = False

        ans += ", ".join(list_)

        if current_flag:
            ans = "{" + ans + "}"

        else:
            ans = "[" + ans + "]"

        return f"{ans}"

    elif type(obj) == tuple:
        serialized = []

        for i in obj:
            serialized.append(f"{serialize_json(i)}")

        ans = ", ".join(serialized)

        return f"[{ans}]"

    else:
        return f"\"{str(obj)}\""


def deserialize_json(str_):  # string to obj
    if str_ == '{}':
        return frozendict.frozendict()

    elif str_[0] == '{':
        ans = dict()
        str_ = str_[1:len(str_) - 1]

        if re.match("\"VALUE\": \[\[", str_):
            temp = ""
            current_flag = False
            temp_i = 0
            list_ = []
            counter1 = 0
            counter2 = 0

            for i in range(8, len(str_)):
                if str_[i] == '[' and not current_flag:
                    counter1 += 1

                elif str_[i] == ']' and not current_flag:
                    counter1 -= 1

                if str_[i] == '[' and not current_flag and counter1 <= 2:
                    continue

                elif str_[i] == ']' and not current_flag and counter1 < 2:
                    continue

                elif str_[i] == '{' and not current_flag:
                    counter2 += 1

                elif str_[i] == '}' and not current_flag:
                    counter2 -= 1

                elif str_[i] == '\"':
                    current_flag = not current_flag

                elif str_[i] == ',' and not current_flag and counter2 == 0 and counter1 != 0:
                    if temp != "" and temp != "[]":
                        list_.append(deserialize_json(temp))

                    else:
                        list_.append({})

                    temp = ""
                    continue

                elif str_[i] == ' ' and not current_flag and counter2 == 0:
                    continue

                elif str_[i] == "," and not current_flag and counter1 == 0:
                    if temp != "" and temp != "[]":
                        list_.append(deserialize_json(temp))

                    else:
                        list_.append({})

                    temp_i = i
                    temp = ""

                    break

                temp += str_[i]

            ans[VALUE_FIELD] = {}

            list_ = tuple(list_)

            for i in range(0, len(list_), 2):
                ans[VALUE_FIELD][list_[i]] = list_[i + 1]

            temp = ""

            for i in range(temp_i + 11, len(str_)):
                if str_[i] == '\"':
                    ans[TYPE_FIELD] = temp
                    temp = ""

                    break

                else:
                    temp += str_[i]

        elif re.match("\"VALUE\": \[", str_):
            temp = ""
            current_flag = False
            temp_i = 0
            list_ = []
            counter = 0

            for i in range(10, len(str_)):
                if str_[i] == '{' and not current_flag:
                    counter += 1

                elif str_[i] == '}' and not current_flag:
                    counter -= 1

                if str_[i] == '\"':
                     current_flag = not current_flag

                elif str_[i] == ',' and not current_flag and counter == 0:
                    list_.append(deserialize_json(temp))
                    temp = ""

                    continue

                elif str_[i] == ' ' and not current_flag and counter == 0:
                    continue

                elif str_[i] == "]" and not current_flag and counter == 0:
                    if temp != "":
                        list_.append(deserialize_json(temp))

                    temp_i = i
                    temp = ""

                    break

                temp += str_[i]

            list_ = tuple(list_)
            ans[VALUE_FIELD] = list_

            for i in range(temp_i + 12, len(str_)):
                if str_[i] == '\"':
                    ans[TYPE_FIELD] = temp
                    temp = ""

                    break

                else:
                    temp += str_[i]

        elif re.match("\"VALUE\": \{", str_):
            temp = ""
            current_flag = False
            temp_i = 0
            counter = 0

            for i in range(9, len(str_)):
                if str_[i] == '{' and not current_flag:
                    counter += 1

                elif str_[i] == '}' and not current_flag:
                    counter -= 1

                elif str_[i] == '\"':
                    current_flag = not current_flag

                elif str_[i] == "," and not current_flag and counter == 0:
                    if temp != "":
                        ans[VALUE_FIELD] = deserialize_json(temp)

                    temp_i = i
                    temp = ""

                    break

                temp += str_[i]

            for i in range(temp_i + 11, len(str_)):
                if str_[i] == '\"':
                    ans[TYPE_FIELD] = temp
                    temp = ""

                    break

                else:
                    temp += str_[i]

        else:
            temp = ""
            current_flag = False
            i = 10

            while i < len(str_):
                if str_[i] == '\"' and not current_flag:
                    ans[VALUE_FIELD] = temp
                    temp = ""
                    current_flag = True
                    i += 11

                elif str_[i] == '\"' and current_flag:
                    ans[TYPE_FIELD] = temp
                    temp = ""

                    break

                else:
                    temp += str_[i]

                i += 1

        return frozendict.frozendict(ans)
