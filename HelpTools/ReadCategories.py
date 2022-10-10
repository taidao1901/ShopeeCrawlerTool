import json
from tkinter.font import families

class Categories: 
    def __init__(self,pathFile):
        with open(pathFile, 'r', encoding="utf8") as cate:
            self.Categories = json.load(cate)
    def __GetPaths(self, data, path, ret):
        if data["ChildrenCount"] == 0:
            path += "." + data['Id']
            temp = data["Name"].replace("/","-")
            temp = temp.replace(" ","-")
            ret.append("https://shopee.vn/"+temp+'-cat'+path)
            return
        for child in data['ChildCategories']:
            patharr = []
            patharr.append(path)
            patharr[0] += '.' + data['Id']
            self.__GetPaths(child, patharr[0], ret)
    def GetAllPaths(self):
        paths =[]
        for data in self.Categories:
            path= ''
            ret = []
            self.__GetPaths(data, path, ret)
            paths.extend(ret)
        return paths
    def __GetPath(self,id,data,path):
        path.append({"Id":data["Id"], "Name": data["Name"]})
        if str(data["Id"]) == str(id):
            return True
        if data["ChildrenCount"]== 0:
            return False
        for child in data["ChildCategories"]:
            if(self.__GetPath(id,child, path)):
                return True       
        path.pop(-1)
        return False
    def GetPath(self, id):
        path =[]
        for data in self.Categories:
            if self.__GetPath(id, data, path):
                return path
        return []
        
    


cates = Categories('../Categories.json')
categories = cates.GetAllPaths()
print(len(categories))
category = cates.GetPath(11035568)

print(category)
#print(len(categories))
