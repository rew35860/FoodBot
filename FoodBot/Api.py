import requests
import json

apiKey = "?apiKey=da7c93cd65e040118e476df9521dea88"
# apiKey = "?apiKey=efe4fdd5a1f548a6859a8321e859c6f1"
foodData = dict()


def addFoodData(name, id):
    if name not in foodData:
        foodData[name] = id 


def getIngredientId(ingredient): 
    try:
        url = f"https://api.spoonacular.com/food/ingredients/search{apiKey}&query={ingredient}&number=1"
        response = requests.request("GET", url)
        
        with open('sample.json', 'w') as outfile:
            json.dump(response.json(), outfile)

        name = response.json()['results'][0]['name']
        id = str(response.json()['results'][0]['id'])
        addFoodData(name, id)

        return name
    except:
        print('\nID ingredient not found! Due to:')
        print('\t'+response.json()['message']+'\n')
        return 0


def getRecipeId(foodName, number = 1, cuisines = None, types = None, diets = None):
    try:
        if cuisines:
            cuisines = ','.join(cuisines)
        if types:
            types = ','.join(types)
        if diets:
            diets = ','.join(diets)
      
        url = f'https://api.spoonacular.com/recipes/complexSearch{apiKey}&query={foodName}&number={number}&cuisine={cuisines}&type={types}&diet={diets}'
        response = requests.request("GET", url)

        name = response.json()['results'][0]['title']
        id = str(response.json()['results'][0]['id'])
        addFoodData(name, id)

        with open('sample.json', 'w') as outfile:
            json.dump(response.json(), outfile)

        return name
    except:
        print('ID food name not found! Due to:')
        print('\t'+response.json()['message']+'\n')
        return 0


def getNutrition(ingredient, nutrients = None, breakdown = False):
    try:
        if ingredient not in foodData:
            ingredient = getIngredientId(ingredient)

        if ingredient == 0:
            return None

        id = foodData[ingredient]

        temp = f"https://api.spoonacular.com/food/ingredients/{id}/information{apiKey}&amount=1"
        response = requests.request("GET", temp)
        results = response.json()['nutrition']
        result = dict()
        result = ''

        with open('sample.json', 'w') as outfile:
            json.dump(response.json(), outfile)

        if breakdown:
            info = results['caloricBreakdown']
            
            for i, j in info.items(): 
                result += f'{i}: {j}%, '
            return f'This is the nutritional breakdown of {ingredient}: {result[:-2]}.'

        if nutrients:
            info = results['nutrients']

            for i in info: 
                if i['title'].lower() in nutrients:
                    result += '{}: {} {}, '.format(i['title'], i['amount'], i['unit'])
            return f'{ingredient} has {result[:-2]}.'

        return final
    except:
        print("Can't get Nutritional fact!")
        return 0


def getHowTo(foodName, number = 1, cuisines = None, types = None, diets = None):
    try: 
        if foodName not in foodData:
            foodName = getRecipeId(foodName, number, cuisines, types, diets)
        
        if foodName == 0:
            return None

        id = foodData[foodName]
        url = f"https://api.spoonacular.com/recipes/{id}/analyzedInstructions{apiKey}"
        response = requests.request("GET", url)
        text = response.json()
    
        step = f'This is how you make {foodName}:'
        count = 1
        for j in range(len(text)):
            step += text[j]['name']+'\n'
            count = 1
            for i in text[j]['steps']:
                step += f'step {count}: '+i['step']+'\n'
                count += 1 
        
        return step
    except: 
        print("Can't find instruction!")
        return 0 


def getRandomRecipes(number=1, tags=None):
    try:
        if tags:
            tags = ','.join(tags)

        url = f'https://api.spoonacular.com/recipes/random{apiKey}&tags={tags}&number={number}'
        response = requests.request("GET", url)
        text = response.json()

        with open('sample.json', 'w') as outfile:
            json.dump(text, outfile)

        if number == 1: 
            result = f'Here is {number} random recipe: '
        else: 
            result = f'Here are {number} random recipes: '

        for i in range(number-1): 
            title = text["recipes"][i]["title"] #the int is the #th recipe 
            addFoodData(title, text["recipes"][i]["id"])
            result += f'{title}, '

        if number == 1:
            title = text["recipes"][number-1]["title"] #the int is the #th recipe 
            addFoodData(title, text["recipes"][number-1]["id"])
            result += f'{title}.'
        else:
            title = text["recipes"][number-1]["title"] #the int is the #th recipe 
            addFoodData(title, text["recipes"][number-1]["id"])
            result += f'and {title}.'
        
        return result, title
    except:
        print("Can't find random recipes!")
        return None, None


def getSimilarRecipes(foodName, number=1):
    try:
        if foodName not in foodData:
            foodName = getRecipeId(foodName, number)

        if foodName == 0: 
            return None, None

        id = foodData[foodName]
        url = f"https://api.spoonacular.com/recipes/{id}/similar{apiKey}&number={number}"
        response = requests.request("GET", url)
        text = response.json()
        reuslt = ''

        if number == 1:
            result = f'Here you go, a similar recipe to {foodName}: '
        else:
            result = f'Here you go, {number} similar recipes to {foodName}: '

        for i in range(number-1):
            title = text[i]['title']
            time = text[i]['readyInMinutes']
            source = text[i]['sourceUrl']

            addFoodData(title, text[i]['id'])
            result += f'{title} ready in {time} minutes by {source}, '

        if number == 1:
            title = text[number -1]['title']
            time = text[number -1]['readyInMinutes']
            source = text[number -1]['sourceUrl']

            addFoodData(title, text[number -1]['id'])
            result += f'{title} ready in {time} minutes by {source}.'
        else:
            title = text[number -1]['title']
            time = text[number -1]['readyInMinutes']
            source = text[number -1]['sourceUrl']

            addFoodData(title, text[number -1]['id'])
            result += f'and {title} ready in {time} minutes by {source}.'
            
        return result, title
    except:
        print("Can't find similar recipes!")
        return None, None


def getIngredientRecipes(ingredients, number=1):
    try:
        ingredients = ','.join(ingredients)
        url = f'https://api.spoonacular.com/recipes/findByIngredients{apiKey}&ingredients={ingredients}&number={number}'
        response = requests.request("GET", url)
        text = response.json()

        with open('sample.json', 'w') as outfile:
            json.dump(text, outfile)
        
        if number == 1:
            result = f'You can make this recipe with {ingredients}: '
        else:
            result = f'You can make {number} recipes with {ingredients}: '

        for i in range(number-1):
            title = text[i]['title'] 
            addFoodData(title, text[i]['id'])
            result += f'{title}, '
        
        if number == 1:
            title = text[number-1]['title'] 
            addFoodData(title, text[number-1]['id'])
            result += f'{title}.'
        else:
            title = text[number-1]['title'] 
            addFoodData(title, text[number-1]['id'])
            result += f'and {title}.'
        
        return result, title
    except:
        print("Can't find recipes from ingredient(s)!") 
        return None, None


""" Sample getting recipe information -> how long / popular / healty / vegan etc (no nutritional fact)
89274 = Pizza Bites 
"""
def getFoodFact(foodName, time = False, fact = None, diet = None):
    try:
        if foodName not in foodData:
            foodName = getRecipeId(foodName)

        if foodName == 0: 
            return None, None

        id = foodData[foodName]
       
        url = f"https://api.spoonacular.com/recipes/{id}/information{apiKey}"
        response = requests.request("GET", url)
        text = response.json()

        with open('sample.json', 'w') as outfile:
            json.dump(text, outfile)

        result = f'{foodName}: ' 

        if time: 
            t = text['readyInMinutes']
            result += f'Just {t} minutes of your time! '
        
        if fact:
            if 'healthy' in fact:
                if text['veryHealthy']:
                    result += f'Yup, this is healty and you’re on the right track! '
                else:
                    result += f'What is Healthy? This? Psh. '

            if 'popular' in fact:
                if text['veryPopular']:
                    result += f'This is a popular dish. '
                else:
                    result += f"This is not a popular dish; but hey, it's worth the try. "
        
        if diet:
            result += f'This is '
            for i in diet: 
                if i == 'gluten_free':
                    i = 'glutenFree'
                
                if i == 'dairy_free':
                    i = 'dairyFree'
                
                if text[i]:
                    result += f"{i}, "
                else:
                    result += f"not {i}, "
        
        return (result[:-2]+"."), foodName
    except:
        print("Can't find facts!")
        return None, None

if __name__ == '__main__':
    pass
