import sys

from .serializer_factory import SerializerFactory


def main():
    args = sys.argv

    if len(args) != 5:
        print("Invalid amount of arguments")
        exit()

    _, filepath_from, filepath_to, format_from, format_to = args

    try:
        from_serializer = SerializerFactory.serializer(format_from)
        to_serializer = SerializerFactory.serializer(format_to)
    except Exception as e:
        print(e)
        exit()

    try:
        with open(filepath_from, 'r') as file_from, open(filepath_to, 'w') as file_to:
            des_obj = from_serializer.load(file_from)
            to_serializer.dump(des_obj, file_to)
    except Exception as e:
        print(e)
        exit()
