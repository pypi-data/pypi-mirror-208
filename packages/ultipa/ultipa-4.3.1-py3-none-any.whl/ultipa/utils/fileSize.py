import os


def get_fileSize(FilePath:str):
    fsize = os.path.getsize(FilePath)
    fsize = fsize/float(1024*1024)
    return round(fsize,2)


def read_in_chunks(filePath, chunk_size=1024*1024):
    """
    Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1M
    You can set your own chunk size
    """
    file_object = open(filePath,'rb')
    while True:
        chunk_data = file_object.read(chunk_size)
        if not chunk_data:
            file_object.close()
            break
        yield chunk_data

if __name__ == "__main__":
    filePath = '/Users/ultipa/work/ultipa-python-sdk2/algo/khop_all.yml'
    for chunk in read_in_chunks(filePath):
        print(type(chunk))