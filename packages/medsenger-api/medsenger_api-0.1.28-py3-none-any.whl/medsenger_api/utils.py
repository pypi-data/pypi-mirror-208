import base64

def prepare_binary(name, data):
    import magic
    type = magic.from_buffer(data, mime=True)

    return {
        "name": name,
        "base64": base64.b64encode(data).decode('utf-8'),
        "type": type
    }


def prepare_file(filename):
    import magic
    import os

    type = magic.from_file(filename, mime=True)

    with open(filename, 'rb') as file:
        answer = {
            "name": filename.split(os.sep)[-1],
            "base64": base64.b64encode(file.read()).decode('utf-8'),
            "type": type
        }

    return answer
