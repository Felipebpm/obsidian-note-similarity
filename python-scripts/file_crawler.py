import os

class FileCrawler:
    """
    Example usage:
        from file_crawler import FileCrawler
        crawler = FileCrawler('.')
        crawler.get_dependency_graph('.py')
    """

    def __init__(self, directory):
        crawler_hash_key = ''
        self.__supported_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.md']
        self.__directory = directory
        self.__initignore = self.__init_ignore()
        self.__starter_files = []
        crawler_payload = self.__crawl()
        self.__files, self.__roots, self.__filesystem, self.__filesystem_dump, self.__default_file, self.__starter_files = crawler_payload

    # Public functions

    def get_files(self):
        return self.__files

    def get_filesystem(self):
        return self.__filesystem

    def get_roots(self):
        return self.__roots

    # Private functions

    def __crawl(self):
        """
        Returns all filenames in a given directory.
        """
        directory_files = {}
        roots = []
        filesystem = []
        filesystem_dump = {}
        curr_index = 0
        parent_index = None
        parent_indices = []
        default_file = None
        for root, directories, files in os.walk(self.__directory):
            if self.__match(root, self.__initignore):
                continue
            roots.append(root)
            if len(parent_indices):
                parent_index = parent_indices.pop(0)
            else:
                parent_index = None
            dir_index = 0
            for directory in directories:
                if self.__match(root + '/' + directory, self.__initignore):
                    continue
                file_path_no_root = os.path.relpath(root + '/' + directory, start = self.__directory)
                depth = len(file_path_no_root.split('/')) - 1
                file_data = {
                    "index": curr_index,
                    "id": file_path_no_root,
                    "filename": directory,
                    "type": "directory",
                    "children": [],
                    "parent": parent_index,
                    "depth": depth
                }
                filesystem.append(file_data)
                filesystem_dump[file_path_no_root] = file_data
                if parent_index != None:
                    filesystem[parent_index]["children"].append(curr_index)
                parent_indices.insert(dir_index, curr_index)
                curr_index += 1
                dir_index += 1
            for file in files:
                _, extension = os.path.splitext(file)
                if extension not in self.__supported_extensions or \
                        self.__match(root + '/' + file, self.__initignore):
                    continue
                elif extension not in directory_files:
                    directory_files[extension] = []
                directory_files[extension].append(root + '/' + file)

                file_path_no_root = os.path.relpath(root + '/' + file, start = self.__directory)
                depth = len(file_path_no_root.split('/')) - 1

                file_rendering_id = os.path.relpath(root + '/' + file, start = self.__directory + '/..')
                file_rendering_id = file_rendering_id.replace('/', '-')
                file_rendering_id = f'{file_rendering_id}.js'

                file_data = {
                    "index": curr_index,
                    "id": file_rendering_id,
                    "filename": file,
                    "type": extension,
                    "children": [],
                    "parent": parent_index,
                    "depth": depth,
                    "fullPath": file_path_no_root,
                }
                if depth == 0 and extension == '.md':
                    file_data["name"] = file_path_no_root
                    file_data["path"] = file_path_no_root
                    self.__starter_files.append(file_data)
                if (not default_file) and file_path_no_root.lower() == 'readme.md':
                    default_file = file_data
                filesystem.append(file_data)
                filesystem_dump[file_path_no_root] = file_data
                if parent_index != None:
                    filesystem[parent_index]["children"].append(curr_index)
                curr_index += 1
        return directory_files, roots, filesystem, filesystem_dump, default_file, self.__starter_files

    def __init_ignore(self):
        ignore_file = self.__directory + '/.initignore'
        if os.path.exists(ignore_file):
            initignore = open(ignore_file).readlines()
        else:
            initignore = []
        return initignore

    def __match(self, file, ignore):
        # implement with regex?
        path = file.split('/')
        if 'node_modules' in path: # For js testing purposes
            return True
        return False or self.__is_hidden(file)

    def __is_hidden(self, path):
        path = os.path.realpath(path)
        subdirectories = path.split('/')[1:]
        for subdirectory in subdirectories:
            if subdirectory[0] == '.':
                return True
        return False
