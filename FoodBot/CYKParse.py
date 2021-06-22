# Code for CS 171, Winter, 2021

import Tree

verbose = False
def printV(*args):
    if verbose:
        print(*args)

# A Python implementation of the AIMA CYK-Parse algorithm in Fig. 23.5 (p. 837).
def CYKParse(words, grammar):
    T = {}
    P = {}
    # Instead of explicitly initializing all P[X, i, k] to 0, store
    # only non-0 keys, and use this helper function to return 0 as needed.
    def getP(X, i, k):
        key = str(X) + '/' + str(i) + '/' + str(k)
        if key in P:
            return P[key]
        else:
            return 0
    # Insert lexical categories for each word
    for i in range(len(words)):
        for X, p in getGrammarLexicalRules(grammar, words[i]):
            P[X + '/' + str(i) + '/' + str(i)] = p
            T[X + '/' + str(i) + '/' + str(i)] = Tree.Tree(X, None, None, lexiconItem=words[i])
    printV('P:', P)
    printV('T:', [str(t)+':'+str(T[t]) for t in T])
    # Construct X_i:j from Y_i:j + Z_j+i:k, shortest spans first
    for i, j, k in subspans(len(words)):

        # print("-------------------")
        for X, Y, Z, p in getGrammarSyntaxRules(grammar):
            PY = getP(Y, i, j) * p
            if PY > getP(X, i, k):
                printV(X, Y, "i:", i, "j:", j, "k:", k, " ", X, "->", Y, Z, "["+str(P)+"]", "PY =", getP(Y,i,j), p, "=", PY)
                P[X + '/' + str(i) + '/' + str(j)] = PY
                T[X + '/' + str(i) + '/' + str(j)] = Tree.Tree(X, T[Y+'/'+str(i)+'/'+str(j)], '')
                break

        for X, Y, Z, p in getGrammarSyntaxRules(grammar):
            # printV('i:', i, 'j:', j, 'k:', k, '', X, '->', Y, Z, '['+str(p)+']', 
            #         'PYZ =' ,getP(Y, i, j), getP(Z, j+1, k), p, '=', getP(Y, i, j) * getP(Z, j+1, k) * p)
            PYZ = getP(Y, i, j) * getP(Z, j+1, k) * p
            if PYZ > getP(X, i, k):
                # printV('     inserting from', i, '-', k, ' ', X, '->', T[Y+'/'+str(i)+'/'+str(j)], T[Z+'/'+str(j+1)+'/'+str(k)],
                #             'because', PYZ, '=', getP(Y, i, j), '*', getP(Z, j+1, k), '*', p, '>', getP(X, i, k), '=',
                            # 'getP(' + X + ',' + str(i) + ',' + str(k) + ')')
                P[X + '/' + str(i) + '/' + str(k)] = PYZ
                T[X + '/' + str(i) + '/' + str(k)] = Tree.Tree(X, T[Y+'/'+str(i)+'/'+str(j)], T[Z+'/'+str(j+1)+'/'+str(k)])
        

    printV('T:', [str(t)+':'+str(T[t]) for t in T])
    return T, P

# Python uses 0-based indexing, requiring some changes from the book's
# 1-based indexing: i starts at 0 instead of 1
def subspans(N):
    for length in range(2, N+1):
        for i in range(N+1 - length):
            k = i + length - 1
            for j in range(i, k):
                yield i, j, k

# These two getXXX functions use yield instead of return so that a single pair can be sent back,
# and since that pair is a tuple, Python permits a friendly 'X, p' syntax
# in the calling routine.
def getGrammarLexicalRules(grammar, word):
    for rule in grammar['lexicon']:
        if rule[1] == word:
            yield rule[0], rule[2]

def getGrammarSyntaxRules(grammar):
    rulelist = []
    for rule in grammar['syntax']:
        yield rule[0], rule[1], rule[2], rule[3]

# 'Grammar' here is used to include both the syntax part and the lexicon part.

# E0 from AIMA, ps. 834.  Note that some syntax rules were added or modified 
# to shoehorn the rules into Chomsky Normal Form. 
def getGrammarE0():
    return {
        'syntax' : [
            ['S', 'NP', 'VP', 0.9 * 0.45 * 0.6],
            # ['S', 'Pronoun', 'VP', 0.9 * 0.25 * 0.6],
            ['S', 'Name', 'VP', 0.9 * 0.10 * 0.6],
            ['S', 'Noun', 'VP', 0.9 * 0.10 * 0.6],
            ['S', 'NP', 'Verb', 0.9 * 0.45 * 0.4],
            # ['S', 'Pronoun', 'Verb', 0.9 * 0.25 * 0.4],
            ['S', 'Name', 'Verb', 0.9 * 0.10 * 0.4],
            ['S', 'Noun', 'Verb', 0.9 * 0.10 * 0.4],
            ['S', 'S', 'Conj+S', 0.1],
            ['Conj+S', 'Conj', 'S', 1.0],
            ['NP', 'Article', 'Noun', 0.25],
            ['NP', 'Article+Adjs', 'Noun', 0.15],
            ['NP', 'Article+Adjective', 'Noun', 0.05], 
            ['NP', 'Digit', 'Digit', 0.15],
            ['NP', 'NP', 'PP', 0.2],
            ['NP', 'NP', 'RelClause', 0.15],
            ['NP', 'NP', 'Conj+NP', 0.05],
            ['Article+Adjs', 'Article', 'Adjs', 1.0],
            ['Article+Adjective', 'Article', 'Adjective', 1.0],
            ['Conj+NP', 'Conj', 'NP', 1.0],
            ['VP', 'VP', 'NP', 0.6 * 0.55],
            ['VP', 'VP', 'Adjective', 0.6 * 0.1],
            ['VP', 'VP', 'PP', 0.6 * 0.2],
            ['VP', 'VP', 'Adverb', 0.6 * 0.15],
            ['VP', 'Verb', 'NP', 0.4 * 0.55],
            ['VP', 'Verb', 'Adjective', 0.4 * 0.1],
            ['VP', 'Verb', 'PP', 0.4 * 0.2],
            ['VP', 'Verb', 'Adverb', 0.4 * 0.15],
            ['Adjs', 'Adjective', 'Adjs', 0.8],
            ['PP', 'Prep', 'NP', 0.65],
            ['PP', 'Prep', 'Pronoun', 0.2],
            ['PP', 'Prep', 'Name', 0.1],
            ['PP', 'Prep', 'Noun', 0.05],
            ['RelClause', 'RelPro', 'VP', 0.6],
            ['RelClause', 'RelPro', 'Verb', 0.4],
            ['Noun', 'Pronoun', '',  0.4],
        ],
        'lexicon' : [
            ['Noun', 'stench', 0.05],
            ['Noun', 'breeze', 0.05],
            ['Noun', 'wumpus', 0.05],
            ['Noun', 'pits', 0.05],
            ['Noun', 'dungeon', 0.05],
            ['Noun', 'frog', 0.05],
            ['Noun', 'balrog', 0.7],
            ['Verb', 'is', 0.1],
            ['Verb', 'feel', 0.1],
            ['Verb', 'smells', 0.1],
            ['Verb', 'stinks', 0.05],
            ['Verb', 'wanders', 0.65],
            ['Adjective', 'right', 0.1],
            ['Adjective', 'dead', 0.05],
            ['Adjective', 'smelly', 0.02],
            ['Adjective', 'breezy', 0.02],
            ['Adjective', 'green', 0.81],
            ['Adverb', 'here', 0.05],
            ['Adverb', 'ahead', 0.05],
            ['Adverb', 'nearby', 0.02],
            ['Adverb', 'below', 0.88],
            ['Pronoun', 'me', 0.1],
            ['Pronoun', 'you', 0.03],
            ['Pronoun', 'I', 0.1],
            ['Pronoun', 'it', 0.1],
            ['Pronoun', 'she', 0.67],
            ['RelPro', 'that', 0.4],
            ['RelPro', 'which', 0.15],
            ['RelPro', 'who', 0.2],
            ['RelPro', 'whom', 0.02],
            ['RelPro', 'whoever', 0.23],
            ['Name', 'Ali', 0.01],
            ['Name', 'Bo', 0.01],
            ['Name', 'Boston', 0.01],
            ['Name', 'Marios', 0.97],
            ['Article', 'the', 0.4],
            ['Article', 'a', 0.3],
            ['Article', 'an', 0.05],
            ['Article', 'every', 0.05],
            ['Prep', 'to', 0.2],
            ['Prep', 'in', 0.1],
            ['Prep', 'on', 0.05],
            ['Prep', 'near', 0.10],
            ['Prep', 'alongside', 0.55],
            ['Conj', 'and', 0.5],
            ['Conj', 'or', 0.1],
            ['Conj', 'but', 0.2],
            ['Conj', 'yet', 0.2],
            ['Digit', '0', 0.1],
            ['Digit', '1', 0.1],
            ['Digit', '2', 0.1],
            ['Digit', '3', 0.1],
            ['Digit', '4', 0.1],
            ['Digit', '5', 0.1],
            ['Digit', '6', 0.1],
            ['Digit', '7', 0.1],
            ['Digit', '8', 0.1],
            ['Digit', '9', 0.1]
        ]
    }

# Sample sentences:
# Hi, I am Peter. I am Peter. Hi, my name is Peter. My name is Peter.
# What is the temperature in Irvine? What is the temperature in Irvine now? 
# What is the temperature in Irvine tomorrow? 
# 
def getGrammarWeather():
    return {
        'syntax' : [
            ['S', 'Greeting', 'S', 0.25],
            # ['S', 'NP', 'VP', 0.25],
            # ['S', 'Pronoun', 'VP', 0.25],
            ['S', 'WQuestion', 'VP', 0.25],
            ['VP', 'Verb', 'NP', 0.4],
            ['VP', 'Verb', 'Name', 0.2],
            # ['VP', 'Verb', 'NP', 0.1],
            ['VP', 'Verb', 'NP+AdverbPhrase', 0.3],
            ['NP', 'Article', 'Noun', 0.5],
            ['NP', 'Adjective', 'Noun', 0.5],
            ['NP+AdverbPhrase', 'NP', 'AdverbPhrase', 0.2],
            ['NP+AdverbPhrase', 'Noun', 'AdverbPhrase', 0.2],
            ['NP+AdverbPhrase', 'Noun', 'Adverb', 0.2],
            ['NP+AdverbPhrase', 'NP', 'Adverb', 0.15],
            ['NP+AdverbPhrase', 'AdverbPhrase', 'NP', 0.05],
            ['NP+AdverbPhrase', 'AdverbPhrase', 'Noun', 0.05],
            # ['NP+AdverbPhrase', 'Adverb', 'Noun', 0.1],
            # ['NP+AdverbPhrase', 'Adverb', 'NP+AdverbPhrase', 0.1],
            # ['NP+AdverbPhrase', 'Adverb', 'NP', 0.1],
            ['AdverbPhrase', 'Preposition', 'NP', 0.2],
            ['Adverb', 'Preposition', 'Name', 0.2],
            # ['AdverbPhrase', 'Adverb', 'AdverbPhrase', 0.2],
            ['AdverbPhrase', 'AdverbPhrase', 'Adverb', 0.4],
            

            ['VP', 'Verb', '', 0.25],
            ['NP', 'Pronoun', '', 0.1],
            ['NP', 'Name', '', 0.1],
            ['NP', 'Noun', '', 0.05],
            ['Adjective', 'Adjective', '', 0.9],

            ['S', 'NP', 'VP', 0.4],
            ['VP', 'Pronoun', 'Verb', 0.25],
            ['S', 'VP', 'Name', 0.25],
            ['S', 'WQuestion', 'S', 0.25],
            # ['NP', 'Adverb', 'Verb', 0.25],
            ['NP', 'Adverb', '', 0.5],
            ['S', 'AdverbPhrase', '', 0.25],
            # ['AdverbPhrase', 'Adverb', '', 0.25]
            # ['VP','Adverb', 'VP', 0.25]
        ],
        'lexicon' : [
            ['Greeting', 'hi', 0.5],
            ['Greeting', 'hello', 0.5],
            ['WQuestion', 'what', 0.5],
            ['WQuestion', 'when', 0.25],
            ['WQuestion', 'which', 0.25],
            ['Verb', 'am', 0.5],
            ['Verb', 'is', 0.5],
            ['Name', 'Peter', 0.1],
            ['Name', 'Sue', 0.1],
            ['Name', 'Irvine', 0.8],
            ['Pronoun', 'I', 1.0],
            ['Noun', 'man', 0.2],
            ['Noun', 'name', 0.2],
            ['Noun', 'temperature', 0.6],
            ['Article', 'the', 0.7],
            ['Article', 'a', 0.3],
            ['Adjective', 'my', 0.4],
            ['Adverb', 'now', 0.4],
            ['Adverb', 'today', 0.3],
            ['Adverb', 'tomorrow', 0.3],
            ['Preposition', 'with', 0.5],
            ['Preposition', 'in', 0.5],

            ['Name', 'Tustin', 0.8],
            ['Name', 'Pasadena', 0.8],
            ['Adverb', 'yesterday', 0.5],
            ['WQuestion', 'Will', 0.5],
            ['Verb', 'be', 0.7],
            ['Adjective', 'hotter', 0.5],
            ['Preposition', 'than', 0.5],
         ]
    }

# Grammer for project part 3 
def getGrammarFood(Ingredients = None, Name = None):
    d =    {
        'syntax' : [
            ['S', 'NP', 'VP', 0.25],
            ['S', 'Greeting', 'S', 0.25],
            ['S', 'WQuestion', 'VP', 0.25],
            ['S', 'WQuestion', 'PP', 0.25],
            ['S', 'QuestionPhrase', 'NP', 0.25],
            ['S', 'QuestionPhrase', 'VP', 0.25],
            ['S', 'QuestionPhrase', 'Noun', 0.25],
            ['S', 'QuestionPhrase', 'Diet', 0.25],
            ['S', 'QuestionPhrase', 'Adjective', 0.25],
            ['NP', 'NP', 'PP', 0.25],
            ['NP', 'NP', 'VP', 0.25],
            ['NP', 'NP', 'NP', 0.25], #
            ['NP', 'NP', 'Verb', 0.25],#
            ['NP', 'NP', 'Noun', 0.25],
            ['NP', 'Diet', 'NP', 0.25], 
            ['NP', 'Pronoun', 'Verb', 0.25],
            ['NP', 'Diet', 'Diet', 0.25], 
            ['NP', 'Article', 'NP', 0.25],
            ['NP', 'Number', 'Noun', 0.25],
            ['NP', 'Number', 'NP', 0.25],
            ['NP', 'Adjective', 'NP', 0.25], 
            ['NP', 'Article', 'Noun', 0.25],
            ['NP', 'Adjective', 'Diet', 0.25], 
            ['NP', 'Diet', 'Adjective', 0.25], 
            ['NP', 'Adjective', 'Adjective', 0.25], 
            ['NP', 'ConjunctionPhrase', 'PP', 0.25], #
            ['NP', 'NP', 'ConjunctionPhrase', 0.25],
            ['NP', 'Number', 'AdjectivePhrase', 0.25],
            ['NP', 'Article+Adjective', 'Noun', 0.25],
            ['NP', 'Article', 'AdjectivePhrase', 0.25],
            ['NP', 'Adjective', 'ConjunctionPhrase', 0.25],
            ['VP', 'VP', 'PP', 0.25],
            ['VP', 'Verb', 'NP', 0.25],
            ['VP', 'Verb', 'Noun', 0.25],
            ['VP', 'Verb', 'Name', 0.25],
            ['VP', 'Verb', 'Adverb', 0.25],
            ['VP', 'Verb', 'Pronoun', 0.25],
            ['PP', 'Preposition', 'NP', 0.25],
            ['PP', 'Preposition', 'VP', 0.25],
            ['PP', 'Preposition', 'Verb', 0.25],
            ['PP', 'Preposition', 'Noun', 0.25],
            ['PP', 'Preposition', 'Name', 0.25],
            ['PP', 'Preposition', 'MealTag', 0.25],
            ['PP', 'Preposition', 'Pronoun', 0.25],
            ['ConjunctionPhrase', 'Conjunction', 'VP', 0.25],
            ['ConjunctionPhrase', 'Conjunction', 'Noun', 0.25],
            ['ConjunctionPhrase', 'Conjunction', 'Diet', 0.25],
            ['ConjunctionPhrase', 'Conjunction', 'MealTag', 0.25], #
            ['ConjunctionPhrase', 'Conjunction', 'Adjective', 0.25],
            ['QuestionPhrase', 'VP', 'Noun', 0.25],
            ['QuestionPhrase', 'VP', 'Pronoun', 0.25],
            ['QuestionPhrase', 'WQuestion', 'Adjective', 0.25],
            ['AdjectivePhrase', 'Adjectives', 'Noun', 0.25],
            ['Adjectives', 'Adjective', 'MealTag', 0.25], 
            ['Adjectives', 'Adjective', 'MealTagPhrase', 0.25], #
            ['Article+Adjective', 'Article', 'Adjective', 0.25],
            ['MealTagPhrase', 'MealTag', 'MealTag', 0.25], #
            ['MealTagPhrase', 'MealTagPhrase', 'ConjunctionPhrase', 0.25], #

            ['VP', 'Verb', '', 0.25],
            ['NP', 'Pronoun', '', 0.25],
            ['NP', 'Name', '', 0.1],
            ['NP', 'Noun', '', 0.05],
            ['NP', 'Diet', '', 0.25],
            ['Adjectives', 'Adjective', '', 0.25],
            ['S', 'Greeting', '', 0.25],
        ],
        'lexicon' : [
                # Previous : from weather bot
                ['Greeting', 'hi', 0.5],
                ['Greeting', 'hello', 0.5],
                ['WQuestion', 'what', 0.5],
                ['WQuestion', 'when', 0.25],
                ['WQuestion', 'which', 0.25],
                ['Verb', 'am', 0.5],
                ['Verb', 'is', 0.5],
                ['Name', 'peter', 0.1],
                ['Name', 'sue', 0.1],
                ['Name', 'Irvine', 0.8],
                ['Pronoun', 'I', 1.0],
                ['Pronoun', 'i', 1.0],
                ['Noun', 'man', 0.2],
                ['Noun', 'name', 0.2],
                ['Noun', 'temperature', 0.6],
                ['Article', 'the', 0.7],
                ['Article', 'a', 0.3],
                ['Adjective', 'my', 0.4],
                ['Adverb', 'now', 0.4],
                ['Adverb', 'today', 0.3],
                ['Adverb', 'tomorrow', 0.3],
                ['Preposition', 'with', 0.5],
                ['Preposition', 'in', 0.5],

                ['Name', 'Tustin', 0.8],
                ['Name', 'Pasadena', 0.8],
                ['Adverb', 'yesterday', 0.5],
                ['WQuestion', 'Will', 0.5],
                ['Verb', 'be', 0.7],
                ['Adjective', 'hotter', 0.5],
                ['Preposition', 'than', 0.5],

                ['Verb', 'are', 0.5], 

                # Additonal For Part 3
                # Nutritional Chat Sample -------------------------------------------------------------------
                # Sample Sentence: What is the nutritional breakdown of a/an/the [Name of food]
                ['Adjective', 'nutritional', 0.5],
                ['Noun', 'breakdown', 0.5],
                ['Preposition', 'of', 0.5],
                ['Article', 'an', 0.5],

                # Sample Sentence: Give me the nutritional breakdown of a/an/the [Name of food]
                ['Verb', 'give', 0.5],
                ['Pronoun', 'me', 0.5],

                # Sample Sentence: What is the amount of [nutritional label] in a/an/the [Name of food]
                ['Noun', 'amount', 0.5],
                
                # Sample Sentnmce: How much [nutritional label] is in a/an/the [Name of food]
                ['WQuestion', 'how', 0.5],
                ['Adjective', 'much', 0.5],

                # Recipe Chat Sample ------------------------------------------------------------------------
                # Sample Sentence: How to cook [Name of food] 
                ['Preposition', 'to', 0.5],
                ['Verb', 'cook', 0.5],
                ['Preposition', 'for', 0.5],

                # Sample Sentence: Give me [# of Recipe] random [Tags: diets, meal types, cuisines, or intolerances] recipe(s)
                ['Noun', 'recipe', 0.5],
                ['Noun', 'recipes', 0.5],
                ['Adjective', 'random', 0.5],

                # Sample Sentence: What is a similar recipe to [Name of food]
                # Sample Sentence: Give me a similar recipe to [Name of food]
                ['Adjective', 'similar', 0.5],

                # Sample Sentence: What can I make with [list or non-list of Ingredients]
                ['Verb', 'can', 0.5],
                ['Verb', 'make', 0.5],
                ['Preposition', 'with', 0.5],
                ['Conjunction', 'and', 0.5],

                # Sample Sentence: Give me [# of Recipe] recipe(s) that contain(s) [list or non-list of Ingredients]
                ['Verb', 'contains', 0.5],
                ['Verb', 'contain', 0.5],
                ['Conjunction', 'that', 0.5],

                # Sample Sentence: Is this [Diet/Fun Fact]
                ['Pronoun', 'this', 0.5],

                # Sample Sentence: How long does it take to make [name of food]
                ['Adjective', 'long', 0.5],
                ['Verb', 'does', 0.5],
                ['Pronoun', 'it', 0.5],
                ['Verb', 'take', 0.5],

                # Sample Sentence: What should I eat today in Irvine
                ['Verb', 'should', 0.5],
                ['Verb', 'eat', 0.5],

                # Nutritional Labels 
                ['Noun', 'zinc', 0.5], 
                ['Noun', 'calories', 0.5], 
                ['Noun', 'calcium', 0.5], 
                ['Noun', 'phosphorus', 0.5], 
                ['Noun', 'vitamin b12', 0.5], 
                ['Noun', 'alcohol', 0.5], 
                ['Noun', 'sugar', 0.5], 
                ['Noun', 'vitamin e', 0.5], 
                ['Noun', 'cholesterol', 0.5], 
                ['Noun', 'potassium', 0.5], 
                ['Noun', 'fluoride', 0.5], 
                ['Noun', 'vitamin b5', 0.5], 
                ['Noun', 'vitamin k', 0.5], 
                ['Noun', 'vitamin b1', 0.5], 
                ['Noun', 'fiber', 0.5], 
                ['Noun', 'vitamin b6', 0.5], 
                ['Noun', 'choline', 0.5], 
                ['Noun', 'vitamin b2', 0.5], 
                ['Noun', 'poly unsaturated fat', 0.5], 
                ['Noun', 'vitamin a', 0.5], 
                ['Noun', 'saturated fat', 0.5], 
                ['Noun', 'net carbohydrates', 0.5], 
                ['Noun', 'protein', 0.5], 
                ['Noun', 'sodium', 0.5], 
                ['Noun', 'vitamin b3', 0.5], 
                ['Noun', 'fat', 0.5], 
                ['Noun', 'selenium', 0.5],
                ['Noun', 'caffeine', 0.5], 
                ['Noun', 'iron', 0.5], 
                ['Noun', 'manganese', 0.5], 
                ['Noun', 'folate', 0.5], 
                ['Noun', 'vitamin c', 0.5], 
                ['Noun', 'mono unsaturated fat', 0.5], 
                ['Noun', 'carbohydrates', 0.5], 
                ['Noun', 'folic acid', 0.5], 
                ['Noun', 'copper', 0.5], 
                ['Noun', 'vitamin d', 0.5], 
                ['Noun', 'magnesium', 0.5],

                #Diet 
                ['Diet', 'gluten_free', 0.5],
                ['Diet', 'dairy_free', 0.5],
                ['Diet', 'vegetarian', 0.5],
                ['Diet', 'vegan', 0.5],

                #Fun Fact
                ['Adjective', 'popular', 0.5],
                ['Adjective', 'healthy', 0.5],

                #Meal Types
                ['MealTag', 'main_course', 0.5], 
                ['MealTag', 'side_dish', 0.5], 
                ['MealTag', 'dessert', 0.5], 
                ['MealTag', 'appetizer', 0.5], 
                ['MealTag', 'salad', 0.5], 
                ['MealTag', 'bread', 0.5], 
                ['MealTag', 'breakfast', 0.5], 
                ['MealTag', 'soup', 0.5], 
                ['MealTag', 'beverage', 0.5], 
                ['MealTag', 'sauce', 0.5], 
                ['MealTag', 'marinade', 0.5], 
                ['MealTag', 'fingerfood', 0.5], 
                ['MealTag', 'snack', 0.5], 
                ['MealTag', 'drink', 0.5],

                #Cuisines
                ['MealTag', 'african', 0.5], 
                ['MealTag', 'american', 0.5], 
                ['MealTag', 'british', 0.5], 
                ['MealTag', 'cajun', 0.5], 
                ['MealTag', 'caribbean', 0.5], 
                ['MealTag', 'chinese', 0.5], 
                ['MealTag', 'eastern_european', 0.5], 
                ['MealTag', 'european', 0.5], 
                ['MealTag', 'french', 0.5], 
                ['MealTag', 'german', 0.5], 
                ['MealTag', 'greek', 0.5], 
                ['MealTag', 'indian', 0.5], 
                ['MealTag', 'irish', 0.5], 
                ['MealTag', 'italian', 0.5], 
                ['MealTag', 'japanese', 0.5], 
                ['MealTag', 'jewish', 0.5], 
                ['MealTag', 'korean', 0.5], 
                ['MealTag', 'latin_american', 0.5], 
                ['MealTag', 'mediterranean', 0.5], 
                ['MealTag', 'mexican', 0.5], 
                ['MealTag', 'middle_eastern', 0.5], 
                ['MealTag', 'nordic', 0.5], 
                ['MealTag', 'southern', 0.5], 
                ['MealTag', 'spanish', 0.5], 
                ['MealTag', 'thai', 0.5], 
                ['MealTag', 'vietnamese', 0.5]
        ]}

    if Ingredients:
        for ingredient in Ingredients:
            d['lexicon'].append(['Noun', ingredient, 0.5])
    
    for i in range(1,101):
        d['lexicon'].append(['Number', str(i), 0.5])
    
    if Name:
        for i in Name:
            d['lexicon'].append(['Name', i, 0.5])

    return d 
    

# Unit testing code
if __name__ == '__main__':
    verbose = True
    #CYKParse(['the', 'wumpus', 'is', 'dead'], getGrammarE0())
    #CYKParse(['the', 'old', 'man', 'the', 'boat'], getGrammarGardenPath())
    #CYKParse(['I', 'saw', 'a', 'man', 'with', 'my', 'telescope'], getGrammarTelescope())
    # CYKParse(['my', 'name', 'is'], getGrammarWeather())
    # CYKParse(['hi', 'I', 'am', 'Peter'], getGrammarFood())
    # CYKParse(['what', 'is', 'the', 'temperature', 'in', 'Irvine'], getGrammarWeather())
    #CYKParse(['what', 'is', 'the', 'temperature', 'in', 'Irvine', 'now'], getGrammarWeather())
    #CYKParse(['what', 'is', 'the', 'temperature', 'now', 'in', 'Irvine'], getGrammarWeather())
    # CYKParse(['what', 'is', 'now', 'the', 'temperature', 'in', 'Irvine'], getGrammarWeather())
    # CYKParse(['I','is'], getGrammarWeather())
    # CYKParse(['the', 'wumpus', 'is'], getGrammarE0())

    # CYKParse(['hi', 'my', 'name', 'is', 'Peter'], getGrammarWeather())
    # CYKParse(['Will', 'tomorrow', 'be', 'hotter', 'than', 'today', 'in', 'Irvine'], getGrammarWeather())
    # CYKParse(['Tustin'], getGrammarWeather())

    # r = "what is the nutritional breakdown of a Pineapple".split()
    # CYKParse(r, getGrammarFood(["Pineapple"]))

    # r = "give me the nutritional breakdown of a carrot".split()
    # CYKParse(r, getGrammarFood(["carrot"]))

    # r = "what is the amount of fat in a carrot".split()
    # CYKParse(r, getGrammarFood(["carrot"]))

    # r = "how much fat fiber protein and sugar is in a carrot".split()
    # CYKParse(r, getGrammarFood(["carrot"]))

    # r = "how to cook an egg".split()
    # CYKParse(r, getGrammarFood(["egg"]))

    # r = "how to cook banana for breakfast".split()
    # CYKParse(r, getGrammarFood(["banana"]))
    
    # r = "give me 2 random italian recipes".split()
    # CYKParse(r, getGrammarFood())
    
    # r = "give me a random vegetarian and italian recipe".split() 
    # CYKParse(r, getGrammarFood())

    # r = "what is a similar recipe to Pad-Thai".split()
    # CYKParse(r, getGrammarFood(Ingredients = ['Pad-Thai']))

    # r = "give me a similar recipe to Pasta".split()
    # CYKParse(r, getGrammarFood(Ingredients = ['Pasta']))

    # r = "give me 3 random italian recipes".split()
    # CYKParse(r, getGrammarFood(Ingredients = ['Pasta']))

    # r = "what can I make with apple".split()
    # CYKParse(r, getGrammarFood(Ingredients = ['apple']))

    # r = "what can I make with sugar and apple".split()
    # CYKParse(r, getGrammarFood(['sugar', 'apple']))

    # r = "what can I make with sugar flour and apple".split()
    # CYKParse(r, getGrammarFood(['sugar', 'flour', 'apple']))

    # r = "what can I make with sugar banana flour and apple".split()
    # CYKParse(r, getGrammarFood(['sugar', 'banana', 'flour', 'apple']))

    # r = "give me 3 recipes that contain apple sugar salt flour and banana".split()
    # CYKParse(r, getGrammarFood(['apple', 'sugar', 'sault','banana', 'flour']))

    # r = "is this dairy_free and vegan".split()
    # CYKParse(r, getGrammarFood())

    # r = "is pizza dairy_free and vegan".split()
    # CYKParse(r, getGrammarFood(["pizza"]))

    # r = "is this dairy_free vegan popular and healthy".split()
    # CYKParse(r, getGrammarFood())

    # r = "how long does it take".split()
    # CYKParse(r, getGrammarFood())

    # r = "how long does it take to make this".split()
    # CYKParse(r, getGrammarFood())

    # r = "how much fat sugar and fiber is in this".split()
    # CYKParse(r, getGrammarFood())

    # r = "how long does pizza take".split()
    # CYKParse(r, getGrammarFood(['pizza']))

    # r = "what should I eat today in Irvine".split()
    # CYKParse(r, getGrammarFood("carrot"))

    r = "my name is ere-ere".split()
    CYKParse(r, getGrammarFood(['ere-ere']))

    # r = ['what', 'is', 'the', 'amount', 'of', 'sugar', 'fiber', 'vitamin b1', 'fat', 'and', 'vitamin b12', 'in', 'potato']  #
    # CYKParse(r, getGrammarFood(Ingredients = ['potato']))

# Hi, I am Peter. I am Peter. Hi, my name is Peter. My name is Peter.
# What is the temperature in Irvine? What is the temperature in Irvine now? 
# What is the temperature in Irvine tomorrow? 
