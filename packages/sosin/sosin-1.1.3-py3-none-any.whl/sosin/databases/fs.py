import json, os, re

# 파일 삭제
# 폴더 삭제
# 폴더 생성
# 현재 디렉토리 절대경로 가져오기

print(os.path.abspath('.'))

class FileMaker():
    def __init__(self, FOLDER_PATH='./Datas/', MAX_DATAS = 50000, FILE_TYPE = '.txt'):
        self.FOLDER_PATH = FOLDER_PATH
        self.MAX_DATAS = MAX_DATAS
        self.FILE_TYPE = FILE_TYPE
        self.DATA_COUNT = 0

    def Check_Folder(self, TARGET_FOLDER = ''):
        if TARGET_FOLDER:
            self.MAKE_TYPE = 0
            FOLDER_DIR = TARGET_FOLDER + '/'
            self.FILE_PATH = Create_Folder(FOLDER_DIR)
            self.FILE_NUMBER = len(File_Search(FOLDER_DIR, self.FILE_TYPE)) + 1
            return self.FILE_PATH
        else:
            self.MAKE_TYPE = 1
            self.DATA_COUNT = 0
            # 폴더 탐색 & 폴더 생성
            for li in range(65, 91):
                for si in range(65, 91):
                    FOLDER_DIR = self.FOLDER_PATH + chr(li) + chr(si) + '/'
                    try:
                        fc = len(File_Search(FOLDER_DIR, self.FILE_TYPE))
                        if fc != 100:
                            self.FILE_NUMBER = fc + 1
                            self.FILE_PATH = Create_Folder(FOLDER_DIR)
                            return self.FILE_PATH
                    except:
                        self.FILE_NUMBER = 1
                        self.FILE_PATH = Create_Folder(FOLDER_DIR)
                        return self.FILE_PATH

    def Make_File(self):
        self.FILE = open(self.FILE_PATH + str(self.FILE_NUMBER).zfill(3) + self.FILE_TYPE, 'a', -1, 'utf-8')
    
    def Write_Data(self, data, spliter='\n'):
        if self.DATA_COUNT:
            self.FILE.write(spliter + data)
        else:
            self.FILE.write(data)

        self.DATA_COUNT += 1

        if self.DATA_COUNT==self.MAX_DATAS:
            self.Close_File()
            self.DATA_COUNT = 0
            self.FILE_NUMBER += 1
            if self.MAKE_TYPE and self.FILE_NUMBER == 101:
                self.Check_Folder()
                self.FILE_NUMBER = 1
            self.Make_File()

    def Start(self):
        if self.FOLDER_PATH != './Datas/':
            self.Check_Folder(self.FOLDER_PATH)
        else:
            self.Check_Folder()
        self.Make_File()

    def Close_File(self):
        self.FILE.close()

class JsonMaker(FileMaker):
    def __init__(self, FOLDER_PATH='./Datas/', MAX_DATAS=50000):
        super().__init__(FOLDER_PATH, MAX_DATAS, FILE_TYPE='.json')
        self.FILE_TYPE='.json'

    def Make_File(self):
        super().Make_File()
        self.FILE.write('[')
    
    def Write_Data(self, data):
        if self.DATA_COUNT:
            super().Write_Data(json.dumps(data), spliter=',\n')
        else:
            self.FILE.write('\n')
            super().Write_Data(json.dumps(data))

    def Close_File(self):
        self.FILE.write('\n]')
        super().Close_File()

class CSVMaker(FileMaker):
    def __init__(self, FOLDER_PATH='./Datas/', MAX_DATAS=50000):
        super().__init__(FOLDER_PATH, MAX_DATAS, FILE_TYPE='.csv')
        self.FILE_TYPE='.csv'

    def Make_File(self, COLUMN_NAMES = ''):
        super().Make_File()
        if COLUMN_NAMES:
            self.COLUMN_NAMES = COLUMN_NAMES.split(' ')
            self.FILE.write(','.join(self.COLUMN_NAMES)+'\n')
    
    def Write_Data(self, data):
        super().Write_Data(','.join(data)+'\n')
        if self.DATA_COUNT == 0:
            self.FILE.write(','.join(self.COLUMN_NAMES)+'\n')

    def Start(self, COLUMNS_NAMES = ''):
        if self.FOLDER_PATH != './Datas/':
            self.Check_Folder(self.FOLDER_PATH)
        else:
            self.Check_Folder()
        self.Make_File(COLUMNS_NAMES)

def Create_Folder(FOLDER_DIR):
    try:
        if not os.path.exists(FOLDER_DIR):
            os.makedirs(FOLDER_DIR)
        return FOLDER_DIR
    except OSError:
        print('Error: Creating Directory' + FOLDER_DIR)

def File_Search(FOLDER_DIR, FILE_TYPE='.', ONLY_FOLDER=False):
    FILE_NAMES = os.listdir(FOLDER_DIR)
    if ONLY_FOLDER:
        return list(filter(os.path.isdir, list(map(lambda i : os.path.join(FOLDER_DIR, i), FILE_NAMES))))
    if FILE_TYPE == '.':
        return list(map(lambda i : os.path.join(FOLDER_DIR, i), FILE_NAMES))
    else:
        FILE_NAMES = list(filter(lambda i : i if FILE_TYPE in i else None, FILE_NAMES))
        return list(map(lambda i : os.path.join(FOLDER_DIR, i), FILE_NAMES))

def Change_Name(FOLDER_PATH, FILE_TYPE, TARGET_NAME, TARGET_TYPE):
    for i, name in enumerate(File_Search(FOLDER_PATH, FILE_TYPE)):
        os.rename(name, os.path.join(FOLDER_PATH, '%s_%s%s'%(TARGET_NAME, i, TARGET_TYPE)))

# 파일 삭제
# os.remove(path, option)
# 디렉토리 삭제
# os.rmdir(path, option)