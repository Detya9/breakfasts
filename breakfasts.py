import os.path
from bs4 import BeautifulSoup
import requests
import json

url = 'https://eda.ru/recepty/zavtraki?page='

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}

# for item in range(1, 166):
#     page_url = f'{url}{item}'
#     req = requests.get(page_url, headers=headers)
#     src = req.text
#
#     with open(f'data/html/{item}_breakfasts.html', 'w', encoding='utf-8') as file:
#         file.write(src)
#
#     print(f'Итерация #{item}')

# all_breakfast_dict = {}
# for number in range(1, 166):
#     with open(f'data/html/{number}_breakfasts.html', encoding='utf-8') as file:
#         src = file.read()
#
#     soup = BeautifulSoup(src, 'lxml')
#     all_breakfast_href = soup.find_all(class_='emotion-m0u77r')
#     for item in all_breakfast_href:
#         item_text = item.find(class_='emotion-1eugp2w').find('span', class_='emotion-1pdj9vu').text
#         item_href = 'https://eda.ru' + item.find(class_='emotion-4o0liq').find('a').get('href')
#         all_breakfast_dict[item_text] = item_href
#
# with open('data/all_breakfast.json', mode='a', encoding='utf-8') as file:
#      json.dump(all_breakfast_dict, file, indent=4, ensure_ascii=False)
def energy_value_check(name):
    control = energy_value.find('span', itemprop=f'{name[:-1]}Content' if name != 'calories' else f'{name}')
    if control is None:
        return '0'
    else:
        return control.text

with open('data/all_breakfast.json', encoding='utf-8') as file:
    all_breakfast = json.load(file)

n = len(all_breakfast) - 1
count, i = 0, 1
for dish_name, dish_href in all_breakfast.items():
    rep = [',', " ", "-", "'", '/']
    for item in rep:
        if item in dish_name:
            dish_name = dish_name.replace(item, '_')

    folder_name = f'data/txt/{i}'
    if os.path.exists(folder_name):
        pass
    else:
        os.mkdir(folder_name)
    if count > 50 * i:
        i += 1

    req = requests.get(dish_href, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')

    check_desription = soup.find('span', class_='emotion-aiknw3')
    if check_desription is None:
        description = 'Нет описания'
    else:
        description = ' '.join((check_desription).text.split()).replace('. ', '.\n')

    energy_value = soup.find('div', class_='emotion-1bpeio7').find('span', itemprop='nutrition')
    calories = energy_value_check('calories') + ' ккал'
    proteins = energy_value_check('proteins') + ' г'
    fats = energy_value_check('fats') + ' г'
    carbohydrates = energy_value_check('carbohydrates') + ' г'

    ingredients = soup.find(class_='emotion-yj4j4j').find_all(class_='emotion-7yevpr')
    all_needed_ingredients = {}
    for item in ingredients:
        item_name = item.find('span', itemprop='recipeIngredient').text
        item_quantity = item.find('span', class_='emotion-bsdd3p').text
        all_needed_ingredients[item_name] = item_quantity

    number_of_servings = soup.find(class_='emotion-yj4j4j').find(class_='emotion-1047m5l').text
    recipe = soup.find(class_='emotion-n2r7jc').find_all(itemprop="recipeInstructions")
    cooking_instruction = []
    for item in recipe:
        item_text = item.find('span', itemprop='text').string
        cooking_instruction.append(' '.join(item_text.split()))

    with open(f'{folder_name}/{count}_{dish_name}.txt', 'w', encoding='utf-8') as file:
        file.write(f'Описание:\n{description}\n')
        file.write(f'Энергетическая ценность:\n'
                   f'Калорийность: {calories}\n'
                   f'Белки: {proteins}\n'
                   f'Жиры: {fats}\n'
                   f'Углеводы: {carbohydrates}\n')
        file.write('Ингридиенты:\n')
        for ingredient, quantity in all_needed_ingredients.items():
            file.write(f'{ingredient}: {quantity}\n')
        file.write(f'Получаемое количество порций: {number_of_servings}\n')
        for number, item in enumerate(cooking_instruction, start=1):
            file.write(f'{number}. {item}\n')

    print(f'Осталось итераций: {n - count} из {n}')
    count += 1
