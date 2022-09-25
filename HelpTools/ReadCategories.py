import json

class Categories: 
    def __init__(self,pathFile):
        with open(pathFile, 'r', encoding="utf8") as cate:
            self.Categories = json.load(cate)
    def __GetPaths(self, data, path, ret):
        if data["ChildrenCount"] == 0:
            path += "." + data['Id']
            ret.append("https://shopee.vn/"+data["Name"].replace(" ","-")+'-cat'+path)
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
    def GetSpecificPath(self):
        

# categories = GetCategories("Categories.json")
# ret = []
# getPaths(categories, '', ret)
# print(ret)
# # Unnest(categories)
# # print(categories)

# cates = Categories('Categories.json')

# categories = cates.GetAllPaths()

# print(categories)
# print(len(categories))