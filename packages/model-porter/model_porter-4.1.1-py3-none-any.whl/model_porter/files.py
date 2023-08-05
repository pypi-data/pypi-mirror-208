from django.conf import settings
from .storage import TempFolderStorage


def get_file_storage():
    file_storage = getattr(settings, "MODEL_PORTER_FILE_STORAGE", "tmp_file")
    if file_storage == "tmp_file":
        return TempFolderStorage

    raise Exception("Invalid file storage, must be 'tmp_file'")


def write_to_file_storage(import_file):

    FileStorage = get_file_storage()

    file_storage = FileStorage()

    data = bytes()

    for chunk in import_file.chunks():
        data += chunk

    file_storage.save(data)
    return file_storage


