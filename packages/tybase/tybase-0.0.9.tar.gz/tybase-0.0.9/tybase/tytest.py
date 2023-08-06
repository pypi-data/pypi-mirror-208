import pkg_resources


def read_data_file():
    data_file_path = pkg_resources.resource_filename('tybase', 'datatest.txt')
    with open(data_file_path, 'r') as f:
        data = f.read()
    return data
