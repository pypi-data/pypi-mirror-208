import zipfile
import tempfile
import os


def zip_folder(folder_path):
    # 创建一个临时文件来保存zip文件
    zip_file_path = None
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tf:
        zip_file_path = tf.name
    if zip_file_path is None:
        return None

    # 压缩文件夹
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # 构造文件的绝对路径
                file_path = os.path.join(root, file)
                # 将文件添加到zip文件中
                zf.write(file_path, os.path.relpath(file_path, folder_path))

    return zip_file_path
