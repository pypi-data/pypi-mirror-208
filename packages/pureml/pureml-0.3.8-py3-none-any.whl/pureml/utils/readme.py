import os

def create_readme():
    file_content = 'Readme.md'
    file_type = 'md'

    return file_content, file_type

def load_readme(path:str=None):

    file_content, file_type = create_readme()


    if path is None:
        return file_content, file_type


    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                file_content = f.read()
                file_type = path.rsplit('.',1)[-1]
            except Exception as e:
                print('Unable to read the ReadME file.')
                print('Creating an Empty ReadME file')
    else:
        with open(path, 'w') as f:
            f.write(file_content)
        print('ReadME file does not exist.')
        print('Creating an Empty ReadME file')
        

        
    return file_content, file_type
        