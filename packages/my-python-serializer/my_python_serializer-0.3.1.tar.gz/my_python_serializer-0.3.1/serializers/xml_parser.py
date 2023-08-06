from serializers.parser import Parser
from serializers.xml import from_string_objects, to_string_objects, from_dict, to_dict


class Xml(Parser):
    def dump(self, obj, file):
        with open(file, 'w+') as fw:
            fw.write(str(self.dumps(obj)))

    def dumps(self, obj):
        return to_string_objects(to_dict(obj))

    def load(self, file):
        with open(file, 'r') as fr:
            return self.loads(eval(fr.read()))

    def loads(self, string):
        return from_dict(from_string_objects(string))


if __name__ == "__main__":
    x = Xml()

    a = x.dumps(123)
    print(a)

    a = x.loads(a)
    print(a)
    print(type(a))