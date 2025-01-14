#----------<Library>----------
import zipfile
import os
#----------<Functions>----------
def Zip(FolderPath : str, Password : str):
    if not os.path.isdir(FolderPath):
        return False

    zip_filename = FolderPath.rstrip(os.sep) + ".zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if Password:
            zipf.setpassword(Password.encode('utf-8'))
        for root, _, files in os.walk(FolderPath):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, FolderPath)
                zipf.write(file_path, arcname)
    return zip_filename

def Extract(FilePath : str, Password : str = ""):
    if not os.path.isfile(FilePath):
        return False

    extract_to = FilePath.rstrip('.zip')
    with zipfile.ZipFile(FilePath, 'r') as zipf:
        if Password:
            zipf.setpassword(Password.encode('utf-8'))
        zipf.extractall(path=extract_to)
    return extract_to
