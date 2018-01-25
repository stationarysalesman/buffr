import csv
import re
import sys # if you've been really naughty
import copy

# we gonna do some parsin babyyy
import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc


def initFormulaWeightMap():
    formulaWeights = dict()
    f = open('formula_weights.csv', 'rB')
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        formulaWeights[row['Reagent']] = float(row['Formula Weight']) 
    f.close()
    return formulaWeights


formulaWeights = initFormulaWeightMap()
reagentMap = dict()
totalVolume = 0

# List of token names
tokens = (
    'INTEGER',
    'FLOAT',
    'VOLUME',
    'CONCENTRATION',
    'WORD'
)

# Regular expression rules for tokens

CONCENTRATION = r'[0-9]+(mM|M)'
@TOKEN(CONCENTRATION)
def t_CONCENTRATION(t):
    r'[0-9]+(mM|M)'
    return t


INTEGER = r'[0-9]+'
@TOKEN(INTEGER)
def t_INTEGER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

FLOAT = r'(' + INTEGER + r'\.' + INTEGER + r')'
@TOKEN(FLOAT)
def t_FLOAT(t):
    r'(' + INTEGER +r'\.' + INTEGER + r')'
    t.value = float(t.value)
    return t


VOLUME = r'(mL|L)'
@TOKEN(VOLUME)
def t_VOLUME(t):
    r'(mL|L)'
    return t


t_WORD = r'[a-zA-Z]+'
t_ignore = ' \t'


# yacc stuff
def p_buffer(p):
    'buffer : INTEGER VOLUME rgen'
    global totalVolume
    if p[2] == 'mL':
        totalVolume = float(p[1] / 1000.)
    elif p[2] == 'L':
        totalVolume = float(p[1])
    else:
        print('man what the fuck. mL or L. none of whatever the hell you typed.')
        sys.exit(1)   
    p[0] = str(str(p[1]) + p[2] + p[3])


def p_rgen(p):
    '''rgen : reagent rgen
             | reagent'''
    if len(p) == 3:
        p[0] = str(p[1] + p[2])
    else:
        p[0] = p[1]


def p_compound(p):
    '''compound : WORD compound
                | WORD'''
    if len(p) == 3:
        p[0] = str(p[1] + ' ' + p[2])
    else:
        p[0] = p[1]
     
def p_concentration(p):
    'concentration : CONCENTRATION'
    if p[1][-2] == 'm':
        p[0] = float(p[1][:len(p[1])-2] / 1000.)
    elif p[1][-1] == 'M':
        p[0] = float(p[1][:len(p[1])-1])
    else:
        print('man what the fuck kinda concentration is that, use M or mM my dude')
        sys.exit(1)


def p_reagent(p):
    'reagent : compound concentration'
    if p[1] not in formulaWeights:
        print('what is this {} of which you speak?'.format(p[1]))
        sys.exit(1)

    else:
        reagentMap[p[1]] = p[2]
        p[0] = str(p[1] + str(p[2]))

def p_error(p):
    print('syntax error: {}'.format(p))
lexer = lex.lex()
parser = yacc.yacc()

buffr_input_format = 'Volume[mL,L] [Reagent name]concentration[M,mM]'
buffr_input_example = '200L Tris HCl 20mM NaCl 150mM'


def main():
    print('Welcome to Buffr, the slightly useful python script designed to calculate buffer components.')
    print('Please enter your buffer components in the following format:')
    print buffr_input_format
    print('e.g. \"{}\"').format(buffr_input_example)

    # make a buffer
    in_str = raw_input('Specify desired buffer.\n')
    result = parser.parse(in_str, lexer=lexer)
    for reagent,conc in reagentMap.items():
        print('{}, {}'.format(reagent, conc))
        moles = conc * float(totalVolume)
        amt = moles * formulaWeights[reagent]
        print('{}g of {}'.format(amt, reagent))

    return

if __name__ == '__main__':
    main()
