import CYKParse
import Tree
import Api
import re

foodInfo = dict()

requestInfo = {
        'name': '',
        'time': '',
        'time2': '',
        'compare': '',
        'location': ''
}
haveGreeted = False
haveGreetedFood = False
userName = ''

# Add empty foodinfo dict 
def addFoodInfo():
    id = len(foodInfo)
    foodInfo[id] = {
        'name': '',
        'number': 1,
        'fun fact': [],
        'meal types': [],
        'diet types': [],
        'ingredients': [],
        'nutritional label': [],
        'time': False,
        'this': False,
        'random': False,
        'similar': False,
        'suggestion': False,
        'instruction': False,
        'nutritional breakdown': False, 
    }
    return id

# Processes the leaves of the parse tree to pull out the user's request.
def updateFoodInfo(Tr):
    id = addFoodInfo()
    lookingForBreakdown = False
    lookingForFood = False
    lookingForNutritional = False
    lookingForMealType = False
    lookingForIngredient = False
    lookingForIt = False
    lastItem = False
    isStart = False
    lookingForFact = False
    lookingForUser = False
    global haveGreetedFood 
    global userName 

    for i, leaf in enumerate(Tr.getLeaves()):
        # print(leaf)
        if lookingForFact and leaf[0] == 'Adjective':
            if lastItem:
                foodInfo[id]['fun fact'].append(leaf[1])
                lastItem = False
            else:
                foodInfo[id]['fun fact'].append(leaf[1])
                
        if isStart and leaf[0] == 'Noun' and not leaf[1] == 'this' and not leaf[1] == 'it':
            foodInfo[id]['name'] = leaf[1]
            isStart = False
            lookingForFact = True
        if i == 0 and leaf[1] == 'is':
            isStart = True

        if leaf[0] == 'Adjective':
            if leaf[1] == 'nutritional': 
                lookingForBreakdown = True
        if lookingForBreakdown and leaf[0] == 'Noun' and leaf[1] == 'breakdown':
            foodInfo[id]['nutritional breakdown'] = True
            lookingForBreakdown = False
        
        if leaf[1] in ['of', 'to', 'does'] and 'in' not in Tr.getLeaves()[-2]:
            lookingForFood = True
        if leaf[1] == 'in':
            lookingForFood = True
        if leaf[1] == 'cook' or leaf[1] == 'make':
            foodInfo[id]['instruction'] = True
            lookingForFood = True
        if lookingForFood and leaf[0] == 'Noun' and (leaf[1] not in ['recipe', 'recipes', 'breakdown', 'amount']):
            foodInfo[id]['name'] = leaf[1]
            lookingForFood = False

        if (leaf[0] == 'Noun' and leaf[1] == 'amount') or (leaf[0] == 'Adjective' and leaf[1] == 'much'):
            lookingForNutritional = True
        if lookingForNutritional and leaf[0] == 'Noun' and not leaf[1] == 'amount':
            foodInfo[id]['nutritional label'].append(leaf[1])
        if lookingForNutritional and leaf[1] == 'in':
            lookingForNutritional = False

        if leaf[0] == 'MealTag':
            foodInfo[id]['meal types'].append(leaf[1])

        if leaf[0] == 'Number':
            foodInfo[id]['number'] = leaf[1]

        if leaf[1] == 'random':
            foodInfo[id]['random'] = True

        if leaf[1] == 'similar':
            foodInfo[id]['similar'] = True
        
        if leaf[1] == 'with' or leaf[1] == 'contain' or leaf[1] == 'contains':
            lookingForIngredient = True
            foodInfo[id]['instruction'] = False
        
        if leaf[1] == 'and':
            lastItem = True
        
        if lookingForIngredient and leaf[0] == 'Noun':
            if lastItem:
                foodInfo[id]['ingredients'].append(leaf[1])
                lookingForIngredient = False
            else:
                foodInfo[id]['ingredients'].append(leaf[1])

        if leaf[0] == 'Diet':
            foodInfo[id]['diet types'].append(leaf[1])

        if leaf[1] == 'this' or leaf[1] == 'it':
            foodInfo[id]['this'] = True
            lookingForFact = True

        if (leaf[1] == 'make' or leaf[1] == 'cook') and foodInfo[id]['this'] == True:
            foodInfo[id]['this'] = False
        
        if leaf[1] == 'long':
            foodInfo[id]['time'] = True
        
        if leaf[1] == 'should':
            foodInfo[id]['suggestion'] = True

        if leaf[0] == 'Name' and lookingForUser:
            userName = leaf[1]
            haveGreetedFood = True
            lookingForUser = False

        if leaf[0] == 'Greeting' or leaf[1] == 'name':
            lookingForUser = True
    


# Format a reply to the user, based on what the user wrote. For Part 3: Food Chat Bot
def replyFood():
    # print(foodInfo)
    key = list(foodInfo.keys())
    i = -1
    last = key[i]
    name = foodInfo[last]['name']
    number = foodInfo[last]['number']
    result = ''
    global haveGreetedFood
    global userName 
    
    if haveGreetedFood:
        haveGreetedFood = False
        foodInfo.popitem()
        userName = userName[0].upper() + userName[1:]
        return f'Hello {userName}, how can I help you?'

    # Error Prevention: If "this" is ture but no prior query
    if foodInfo[last]['this'] and len(key) == 1:
        foodInfo.pop(last)
        return 'Huhh, what food are you trying to refer to? I suggest you ask something else first!'
    
    # Replay : How long does it take to make [name of food]
    if foodInfo[last]['time']:
        if foodInfo[last]['this']:
            while (name == 'it' or not name) and -i <= len(key):
                i -= 1
                temp = key[i]
                name = foodInfo[temp]['name']
            if -i > len(key):
                return 'What are you giving me? This is not valid!'

        result, foodName = Api.getFoodFact(name, True)

        if foodName:
            id = addFoodInfo()
            foodInfo[id]['name'] = foodName

        if foodInfo[last]['this']:
            foodInfo.pop(last)

        if result: 
            return result
        return "I can't find it, you need to give me another foodname."
    

    # Replay : [What is / Give me] the nutritional breakdown of [name of food]
    if foodInfo[last]['nutritional breakdown']:
        if foodInfo[last]['this']:
            while (name == 'it' or not name) and -i <= len(key):
                i -= 1
                temp = key[i]
                name = foodInfo[temp]['name']
            if -i > len(key):
                return 'What are you giving me? This is not valid!'

        result = Api.getNutrition(name, breakdown = True)

        if foodInfo[last]['this']:
            foodInfo.pop(last)

        if result: 
            return result
        return f'SOoooo, you want the nutritional breakdown of {name}?'


    # Replay : What is the amount of [nutritional label] in [name of food]
    if foodInfo[last]['nutritional label']:
        temp = foodInfo[last]['nutritional label']
        # print(temp)
        if foodInfo[last]['this']:
            while (name == 'it' or not name) and -i <= len(key):
                i -= 1
                temp = key[i]
                name = foodInfo[temp]['name']
            if -i > len(key):
                return 'What are you giving me? This is not valid!'

        result = Api.getNutrition(name, foodInfo[last]['nutritional label'])

        if foodInfo[last]['this']:
            temp = foodInfo.pop(last)
            temp = temp['nutritional label']

        if result:
            return result
        return f"I wonder the same! Maybe {name} has a lot of {str(temp)}."
    
    # Replay : How to cook [name of food] for [meal type]
    if foodInfo[last]['instruction']:
        mealType = foodInfo[last]['meal types']

        if foodInfo[last]['this']:
            while (name == 'it' or not name) and -i <= len(key):
                i -= 1
                temp = key[i]
                name = foodInfo[temp]['name']
            if -i > len(key):
                return 'What are you giving me? This is not valid!'
        
        if foodInfo[last]['meal types']:
            result = Api.getHowTo(name, types = mealType)
        else:
            result = Api.getHowTo(name)
        
        if foodInfo[last]['this']:
            foodInfo.pop(last)

        if result:
            return result
        return f'It must be nice to know how to cook {name}!'

    # Replay : Give me [#] random [meal type/ diet type] recipes
    if foodInfo[last]['random']:
        if foodInfo[last]['meal types'] or foodInfo[last]['diet types']:
            l = foodInfo[last]['meal types']+foodInfo[last]['diet types']
            result, foodName = Api.getRandomRecipes(int(number), l)
        else: 
            result, foodName = Api.getRandomRecipes(int(number))
        
        if foodName:
            id = addFoodInfo()
            foodInfo[id]['name'] = foodName

        if result:
            return result
        return f'Seems like there is no random recipes.'

    # Replay : [What is / Give me] [#] similar recipe(s) to [name of food]
    if foodInfo[last]['similar']:
        result, foodName = Api.getSimilarRecipes(name, int(number))

        if foodName:
            id = addFoodInfo()
            foodInfo[id]['name'] = foodName

        if result:
            return result
        return f'Seems like there is no similar recipes.'
    
    # Replay : What can I make with apple 
    if not foodInfo[last]['instruction'] and not foodInfo[last]['random'] and foodInfo[last]['ingredients']:
        result, foodName = Api.getIngredientRecipes(foodInfo[last]['ingredients'], int(number))
        
        if foodName:
            id = addFoodInfo()
            foodInfo[id]['name'] = foodName
        
        if result:
            return result
        return "I don't think you can make anything with this."
    
    # Replay : Is [this/ it/ [name of food]] [Diet/fact]
    if foodInfo[last]['fun fact'] or foodInfo[last]['diet types']:
        fact = foodInfo[last]['fun fact']
        diet = foodInfo[last]['diet types']

        if foodInfo[last]['this']:
            while (name == 'it' or not name) and -i <= len(key):
                i -= 1
                temp = key[i]
                name = foodInfo[temp]['name']
            if -i > len(key):
                return 'What are you giving me? This is not valid!'
            

        result, foodName = Api.getFoodFact(name, False, fact, diet)

        if foodName:
            id = addFoodInfo()
            foodInfo[id]['name'] = foodName

        if foodInfo[last]['this']:
            foodInfo.pop(last)

        if result:
            return result
        return f"That\'s a good question! Is {name} really it?"
    
    # Replay : What should I eat today in [City]
    if foodInfo[last]['suggestion']:
        foodInfo.pop(last)
        id = addFoodInfo()

        temper = getTemperature(requestInfo['location'], 'now')
        
        if int(temper) <= 100:
            result, title = Api.getRandomRecipes(1, ['soup'])
            if title:
                foodInfo[id]['name'] = title
                return f'It\'s chilly in Irvine right now. I would suggest you get some {title} to stay warm.'\
                ' Even better, go eat with friends or love ones!'
            else:
                return "I don't have any suggestion! Google might be your best choice here."
        else:
            result, title = Api.getRandomRecipes(1, ['beverage'])
            if title:
                foodInfo[id]['name'] = title
                return f'It\'s hot right now. Isn\'t it? I would suggest you get {title}.'
            else:
                return "I don't have any suggestion! Google might be your best choice here."

    return "Seems like you are giving me an invalid query. Check your spelling or change your sentence structure!"

# Given the collection of parse trees returned by CYKParse, this function
# returns the one corresponding to the complete sentence.
def getSentenceParse(T):
    try:
        maxNum = 0
        index = 0 
        sentenceTrees = { k: v for k,v in T.items() if k.startswith('S/0') }
        for i in sentenceTrees.keys():
            temp = i.split('/')
            num = int(temp[2]) - int(temp[1]) 
            if num > maxNum:
                mazNum = num
                index = i
        # print('getSentenceParse', sentenceTrees)
        return T[index]
    except:
        print('Bot: Your query is invalid! Ask again!\n')
        return 0

# Processes the leaves of the parse tree to pull out the user's request.
def updateRequestInfo(Tr):
    global requestInfo
    lookingForLocation = False
    lookingForName = False
    lookingForTime2 = False
    for leaf in Tr.getLeaves():
        # print(leaf[0], leaf[1])
        if leaf[0] == 'Adverb':
            # print(leaf[1])
            if lookingForTime2 == False:
                requestInfo['time'] = leaf[1]
                lookingForTime2 = True
            else:
                requestInfo['time2'] = leaf[1]
                lookingForTime2 = False
                
        if lookingForLocation and leaf[0] == 'Name':
            requestInfo['location'] = leaf[1]
        if leaf[0] == 'Preposition' and leaf[1] == 'in':
            lookingForLocation = True
        else:
            lookingForLocation = False
        if leaf[0] == 'Noun' and leaf[1] == 'name':
            lookingForName = True
        if lookingForName and leaf[0] == 'Name':
            requestInfo['name'] = leaf[1]
        if leaf[0] == 'Adjective' and leaf[1] == 'hotter':
            requestInfo['compare'] = leaf[1]

# This function contains the data known by our simple chatbot
def getTemperature(location, time):
    if location == 'Irvine':
        if time == 'now':
            return '68'
        elif time == 'tomorrow':
            return '70'
        elif time == 'yesterday':
            return '50'
        elif time == 'today':
            return '40'
        else:
            return 'unknown'
    
    if location == 'Pasadena':
        if time == 'now':
            return '68'
        elif time == 'tomorrow':
            return '70'
        elif time == 'yesterday':
            return '50'
        elif time == 'today':
            return '40'
        else:
            return 'unknown'

    if location == 'Tustin':
        if time == 'now':
            return '68'
        elif time == 'tomorrow':
            return '70'
        elif time == 'yesterday':
            return '50'
        elif time == 'today':
            return '40'
        else:
            return 'unknown'

# Format a reply to the user, based on what the user wrote.
def reply():
    global requestInfo
    global haveGreeted
    if not haveGreeted and requestInfo['name'] != '':
        print("Hello", requestInfo['name'] + '.')
        haveGreeted = True
        return
    time = 'now' # the default
    if requestInfo['time'] != '':
        time = requestInfo['time']
    time2 = ''
    if requestInfo['time2'] != '':
        time2 = requestInfo['time2']
    salutation = ''
    if requestInfo['name'] != '':
        salutation = requestInfo['name'] + ', '
    compare = ''
    if requestInfo['compare'] != '':
        compare = requestInfo['compare'] 

    if time2 != '':
        if getTemperature(requestInfo['location'], time) > getTemperature(requestInfo['location'], time2) and compare == 'hotter':
            print(salutation + 'Yes, the temperature in ' + requestInfo['location'] + ' ' + time + ' is ' + getTemperature(requestInfo['location'], time) + ' and the temperature in '+ requestInfo['location'] + ' ' +
                time2 + ' is ' + getTemperature(requestInfo['location'], time2) + '.')
        else:
            print(salutation + 'No, the temperature in ' + requestInfo['location'] + ' ' + time + ' is ' + getTemperature(requestInfo['location'], time) + ' and the temperature in '+ requestInfo['location'] + ' ' +
                time2 + ' is ' + getTemperature(requestInfo['location'], time2) + '.')
    else:
        print(salutation + 'the temperature in ' + requestInfo['location'] + ' ' +
            time + ' is ' + getTemperature(requestInfo['location'], time) + '.')


def checkNutrientInput(ingredientList):
    for i, j in enumerate(ingredientList):
        if 'vitamin' in j or 'folic' in j or 'fat' in j or 'net' in j:
            ingredientList[i] = j.replace('_', ' ')
    
    return ingredientList


def getFoodName(sentence):
    ingredientList = []
    name = []
    m = re.search(r'in (?:the|an|a) (\w+)$|in (.*)$| of (\w+)$| of (?:the|an|a) (\w+)$|cook (.*) for|cook (.*)$|with (.*)$|to (?!cook|make)(.*)|^is (\w+)\b|make (\w+) for|make (\w+)$', sentence)
    n = re.search(r'my name is (.*)$', sentence)

    if m:
        for i in range(1,12):
            # print(m.group(i))
            if m.group(i):
                ingredientList += m.group(i).lower().split(' ')
        
        ingredientList = list(set(ingredientList)) 
        if 'and' in ingredientList:
            ingredientList.remove('and')
        
        if 'this' in ingredientList:
            ingredientList.remove('this')

    if n: 
        name.append(n.group(1))

    # print(ingredientList, name)
    return ingredientList, name

# A simple hard-coded proof of concept.
def main():
    global requestInfo
    print(" ".join(['hi', 'my', 'name', 'is', 'Peter']))
    T, P = CYKParse.CYKParse(['hi', 'my', 'name', 'is', 'Peter'], CYKParse.getGrammarWeather())
    sentenceTree = getSentenceParse(T)
    updateRequestInfo(sentenceTree)
    reply()

    print()
    print(" ".join(['what', 'is', 'the', 'temperature', 'in', 'Irvine', 'yesterday']))
    T, P = CYKParse.CYKParse(['what', 'is', 'the', 'temperature', 'in', 'Irvine', 'yesterday'], CYKParse.getGrammarWeather())
    sentenceTree = getSentenceParse(T)
    updateRequestInfo(sentenceTree)
    reply()

    g = "Will tomorrow be hotter than today in Irvine"
    print()
    print(g)
    r = g.split()
    T, P = CYKParse.CYKParse(r, CYKParse.getGrammarWeather())
    sentenceTree = getSentenceParse(T)
    updateRequestInfo(sentenceTree)
    reply()

    g = "Will yesterday be hotter than tomorrow in Pasadena"
    print()
    print(g)
    r = g.split()
    T, P = CYKParse.CYKParse(r, CYKParse.getGrammarWeather())
    sentenceTree = getSentenceParse(T)
    updateRequestInfo(sentenceTree)
    reply()
    

def sampleMain():
    # PreQueries ----------------------------------------------------------------------------------------------------------------------
    queries = [
        "What is the nutritional breakdown of a Pineapple", "Give me the nutritional breakdown of a Pineapple", 
        "What is the amount of Sugar in Pineapple", "How much fiber is in Pineapple", "How to cook egg",
        "How to cook banana for breakfast", 
        "Give me 3 random Italian recipes", "What is a similar recipe to pizza",
        "Give me 2 similar recipe to Pasta", "What can I make with apple", 
        "Give me 3 recipes that contain apple sugar salt flour and banana", "How long does it take", 
        "Is this dairy_free vegan popular and healthy", "Is pizza dairy_free and vegan", "Give me a random Vegan recipe",
        "How long does it take to make pizza",
    ]

    continueQueries = [
        "What should I eat today in Irvine", "Is this Gluten_Free", "Is it Healthy", "How long does it take"
    ]

    print('-'*100, '\nNon-sequential Example')
    print('-'*100)
    for q in queries:
        print('User:',q)

        ingredientList, name = getFoodName(q.strip().lower())
        r = q.lower().split()
        r = checkNutrientInput(r)

        T, P = CYKParse.CYKParse(r, CYKParse.getGrammarFood(ingredientList, name))
        sentenceTree = getSentenceParse(T)
        updateFoodInfo(sentenceTree)
        print('Bot:', replyFood())
        print()

    
    print('-'*100, '\nExpand Version of WeatherBot')
    print('-'*100)
    foodInfo.clear()

    print(" ".join(['hi', 'my', 'name', 'is', 'Peter']))
    T, P = CYKParse.CYKParse(['hi', 'my', 'name', 'is', 'Peter'], CYKParse.getGrammarWeather())
    sentenceTree = getSentenceParse(T)
    updateRequestInfo(sentenceTree)
    reply()
    print()

    print(" ".join(['what', 'is', 'the', 'temperature', 'in', 'Irvine', 'today']))
    T, P = CYKParse.CYKParse(['what', 'is', 'the', 'temperature', 'in', 'Irvine', 'yesterday'], CYKParse.getGrammarWeather())
    sentenceTree = getSentenceParse(T)
    updateRequestInfo(sentenceTree)
    reply()
    print()

    for q in continueQueries:
        print("User:",q)
        r = q.lower().split()
        T, P = CYKParse.CYKParse(r, CYKParse.getGrammarFood())
        sentenceTree = getSentenceParse(T)
        updateFoodInfo(sentenceTree)
        print("Bot:",replyFood())
        print()


def infinitMain():
    # Infinit Loop 

    print('-'*100, '\nInfinit Bot')
    print('-'*100)
    ingredientList = []

    q = input("Hello user what's your name?\nUser: ")
    while q not in ['q', 'quit']:
        ingredientList, name = getFoodName(q.strip().lower())

        r = q.lower().split()
        r = checkNutrientInput(r)

        T, P = CYKParse.CYKParse(r, CYKParse.getGrammarFood(ingredientList, name))
        sentenceTree = getSentenceParse(T)

        if sentenceTree:
            if len(sentenceTree.getLeaves()) == len(r):
                updateFoodInfo(sentenceTree)
                print('Bot:', replyFood())
                print()
            else:
                print('Bot: check your spelling, something seems off!\n')

        q = input('User: ')


if __name__ == '__main__':
    # main()
    # sampleMain()
    infinitMain()