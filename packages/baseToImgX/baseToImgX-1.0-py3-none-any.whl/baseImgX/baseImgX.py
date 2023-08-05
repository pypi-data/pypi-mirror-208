# -*- coding=utf-8 -*- 
# github: night_handsomer
# csdn: 惜年_night
# mirror: https://pypi.tuna.tsinghua.edu.cn/simple/

import os
import json
import base64


class baseToImg():

    def __init__(self, path):
        self.path = path
        self.parent = os.path.dirname(self.path)
        self.images = self.parent + '/images'
        if not os.path.exists(self.images):
            os.mkdir(self.images)
        try:
            self.json_list = os.listdir(path)
        except Exception as error:
            raise error
    def imgFormat(self, file_name, format='jpg'):

        file_path = self.images + '/' + file_name + '.' + format
        return file_path

    def toImg(self):
        for files in self.json_list:
            files_name = files.split('.')[0]
            file_path = self.imgFormat(files_name)
            real_path = self.path + '/' + files
            try:
                with open(real_path, "r", encoding='utf-8') as json_file:
                    json_data = json.load(json_file)
            except UnicodeError as ex:      # invalid encoding error
                with open(real_path, "r") as json_file:
                    json_data = json.load(json_file)

            imageBase = json_data.get("imageData")
            if imageBase is not None:
                imageData = base64.b64decode(imageBase)
                # 将字节码以二进制形式存入图片文件中，注意 'wb'
                with open(file_path, 'wb') as jpg_file:
                    jpg_file.write(imageData)

    def check_null(self, show=False):

        check_list = os.listdir(self.images)
        if not check_list:  # []
            return True
        else:
            if show:
                os.system("start {}".format(self.images))

                # explorer is open the documents,
                # and start is open the files
                # caution that in cmd, start isnt work, explorer in contrary.
                # os.system("explorer '{}'".format(self.images))
            return False


if __name__ == "__main__":
    json_path = ''      # your json path
    p = baseToImg(json_path)
    # if p.check_null(show=True):
    if p.check_null():
        p.toImg()
    else:
        p.check_null(show=True)



