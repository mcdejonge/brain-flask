import sys 
import os

class BrainDir:
    """
    Create a list of items in a directory. Recursively.
    Each item looks like this:
    title : the title to display, meaning the file name without the extension or the directory name if it's a directory.
    type : the file type (None if it's a directory)
    path : the file system path
    children : items below this item (only relevant for directories - None for files).
    """
    __basedir = None

    __contents = [] 


    def __init__(self, basedir):
        self.__basedir = basedir

    def traverse(self):
        """
        Traverse the base dir and build a data structure with everything it contains.
        """
        # Create a dictionary with the full path as the key and its contents as the, uhm, contents.
        dir_dict = {
        }
        
        for root, dirs, files in os.walk(self.__basedir):
            """
            print("------------------")
            print(root)
            print(dirs)
            print(files)
            sys.exit();
            """
            dir_dict[root] = {
                    'files' : [os.path.join(root, file_path) for file_path in files],
                    'dirs' : [os.path.join(root, dir_path) for dir_path in dirs]
            }

        # Now starting from the root sort and flatten the list of its children (both directories and files).

        self.__contents = self.__flatten(dir_dict, dir_dict[self.__basedir])

    def get_contents(self):
        """
        Return the contents of the base dir.
        """
        if len(self.__contents) == 0:
            self.traverse()
        return self.__contents


    def __flatten(self, dir_dict, dir_dict_item):
        """
        Private helper method for retrieving data from a specific starting point.
        """
        processed_items = []
        for file_path in dir_dict_item['files']:
            filename, file_extension = os.path.splitext(file_path)
            title = os.path.basename(filename).lower()
            if title.startswith('.'):
                continue
            processed_items.append({
                'type'  : file_extension.replace('.', '').lower(),
                'path'  : os.path.relpath(file_path, self.__basedir),
                'title' : title,
                'children' : None
            })

        for dir_path in dir_dict_item['dirs']:
            title = os.path.basename(dir_path).lower()
            if title.startswith('.'):
                continue
            children = self.__flatten(dir_dict, dir_dict[dir_path])
            item = {
                'type'  : None,
                'path'  : os.path.relpath(dir_path, self.__basedir),
                'title' : title,
                'children' : children
            }
            processed_items.append(item)

        return sorted(processed_items, key=lambda item: item['title'])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " path/to/base/dir")
        sys.exit()
    
    braindir = BrainDir(sys.argv[1])

    print(braindir.get_contents())

