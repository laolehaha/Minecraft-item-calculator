#!/usr/bin/env python
# coding: utf-8

#递归搜索配方
import yaml
import pprint

#https://github.com/AsherGlick/ResourceCalculator/raw/master/resource_lists/minecraft/resources.yaml
with open('resources.yaml', 'r') as file:
    recipes_data = yaml.safe_load(file)

group_resource = {}
for block in recipes_data['requirement_groups']:
    group_resource[block]=recipes_data['requirement_groups'][block]

def get_recipes(resource_id):
    for block in recipes_data["resources"]:
        if block==resource_id:
            return recipes_data["resources"][block]['recipes']
    for group in group_resource:
        if resource_id in group_resource:
            return [{'recipe_type': 'Raw Resource'}]
    return None


def get_material(item_id,s=1):
    step = get_recipes(item_id)
    
    if step:
        if step[0]['recipe_type']=='Raw Resource':
            return {item_id:s}
        materials={}
        output = step[0]['output']
        
        for mat,quan in step[0]['requirements'].items():
            x = get_material(mat,abs(quan)/output)
            #print(x,mat)
            for id_,qu in x.items():
                if id_ in materials:
                    materials[id_]+=qu*s
                else:
                    materials[id_]=qu*s
        return materials;
    return None

#获取译名对照表
import bs4,requests
res = requests.get(r'https://zh.minecraft.wiki/w/Minecraft_Wiki:%E8%AF%91%E5%90%8D%E6%A0%87%E5%87%86%E5%8C%96')
soup=bs4.BeautifulSoup(res.text,'lxml')

soup=bs4.BeautifulSoup(z,'lxml')
all_content=soup.find('div',id='mw-content-text')
all_table=all_content.find_all('table',class_='data-table')
#print(all_table)
ifcontinue=True
zh2en={}
en2zh={}
for table in all_table:
    trs=table.find_all('tr')[1:]
    if(ifcontinue):
        for tr in trs:
            tds=tr.find_all('td')
            if tds[2].text=='悦灵':    #无法形容
                ifcontinue=False
                break
            #print(tds[2])
            en=str(tds[1].text)
            zh=str(tds[2].text)
            zh2en[zh]=en
            en2zh[en]=zh
    else:
        break

#读取材料列表
import csv
items = []

def read_csv_to_array(file_path):
    data_array = []
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data_array.append(row)
    return data_array

csv_file_path = input('path:')
result = read_csv_to_array(csv_file_path)[1:]

for row in result:
    #print(row)
    if(int(row[1])-int(row[3])>0):
        items.append([row[0],int(row[1])-int(row[3])])


#计算
result = {}

for item,quantity in items:
    try:
        item = zh2en[item]
        materials_needed = get_material(item,quantity)
        if materials_needed:
            temp = []
            for material, quantity_ in materials_needed.items():
                temp.append([material,quantity_])
            result[item]=temp
        else:
            print(f"未找到 {item} 的配方。")
            result[item]=[[item,quantity]]
    except:
        print(f"未找到 {item} 的英文")


def stuck(num):
    if num>64:
        return f"{num//64}组+{num%64}个"
    else:
        return f"{num}个"


import pandas as pd

def write_to_csv_and_sum(dictionary, output_file):
    df = pd.DataFrame(columns=['Block'] + list(set(en2zh.get(material, material) for materials_list in dictionary.values() for material, _ in materials_list)))

    totals = {}
    for block, materials_list in dictionary.items():
        row_data = {'Block': en2zh.get(block, block)}

        for material, quantity in materials_list:
            original_quantity = int(quantity)
            row_data[en2zh.get(material, material)] = str(stuck(original_quantity))
            # 更新总和
            totals[en2zh.get(material, material)] = totals.get(en2zh.get(material, material), 0) + original_quantity

        df = df.append(row_data, ignore_index=True)
    for material, total_quantity in totals.items():             #总和处理成几组
        totals[material] = stuck(total_quantity)              

    # 添加总和行
    df = df.append({'Block': 'Total', **totals}, ignore_index=True)

    # 将 DataFrame 写入 CSV 文件
    df.to_csv(output_file, index=False, encoding='ANSI')
    # df.to_csv(output_file, index=False, encoding='utf-8')

output_filename = 'output.csv'
write_to_csv_and_sum(result, output_filename)


