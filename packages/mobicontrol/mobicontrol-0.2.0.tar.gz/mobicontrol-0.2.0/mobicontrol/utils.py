def get_file_contents(path):
    with open(path, 'rb') as file:
        read_file = file.read()
        bin_string = read_file.decode('latin_1')
        
        return bin_string

def get_filename_from_path(path):
    return path.split("/")[-1]