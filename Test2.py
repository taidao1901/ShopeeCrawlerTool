import json

with open('data.json', 'r+', encoding='utf-8') as f:
    data = json.loads(f.read())
    # f.seek(0)
    # f.truncate()
    # data.extend(
    #     [
    #         {
    #             "a" :"asff"
    #         }
    #     ]
    # )
    # json.dump(data, f, ensure_ascii=False, indent=4)
for item in data:
    # if "CustomerCategoryId" not in item.keys():
    #     print(item) 
    if item["CustomerCategoryId"] not in ["11035571","11035570"]:
        print(item["ItemId"]) 
print(type(data))