import os

def create_file(mytext, filepath):
    try:
        os.remove(filepath)
    except OSError:
        pass
    with open(filepath, 'w') as f:
        f.write(mytext)

def remove_tmp_files():
    for i in ['test0.py', 'test1.py', 'test2.xx']:
        tmppath=os.path.abspath('.') + '/runtime_lib/' + i
        try:
            os.remove(tmppath)
        except OSError:
            pass

