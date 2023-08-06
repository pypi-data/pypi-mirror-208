import shutil
import zipfile
from pureml.schema import PredictSchema
import os


# def zip_content(src_path, dst_path):
#     print(src_path)
#     ignore_patterns = shutil.ignore_patterns(".pureml", "*.venv", "*.pyc")

#     # Create a zip archive of the folder
#     shutil.make_archive(
#         base_dir=src_path,
#         root_dir=src_path,
#         format=PredictSchema().resource_format,
#         base_name=dst_path,
#         ignore=ignore_patterns,
#     )


def remove_dirs(dirs):
    dirs_to_ignore = PredictSchema().dirs_to_ignore

    for d in dirs_to_ignore:
        if d in dirs:
            # print('Removing ', d)
            dirs.remove(d)
    # print(dirs)

    return dirs


def zip_content(src_path, dst_path):

    # [".pureml", ".venv", "__pycache__"]
    dirs_to_ignore = PredictSchema().dirs_to_ignore

    # Create a zip archive of the folder, excluding the specified folder
    with zipfile.ZipFile(dst_path, "w", zipfile.ZIP_DEFLATED) as zip_file:

        for root, dirs, files in os.walk(src_path):
            # print("dirs", dirs)
            dirs = remove_dirs(dirs)

            for file in files:
                file_path = os.path.join(root, file)
                # print("outside for loop", file_path)
                if not any(file_path.startswith(folder) for folder in dirs_to_ignore):
                    zip_file.write(file_path, file_path)
                    print(file_path)

    print("Resources are collected")


def unzip_content(src_path, dst_path):
    shutil.unpack_archive(src_path, dst_path, format=PredictSchema().resource_format)

    # Delete the zip file
    # os.remove(src_path)
