#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  compiler.py
#
#  Copyright 2018 Thiago da Silva Teixeira <teixeira.zeus@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import os

def assign(cFile, line):
   cut = line.split('>>')
   cFile.write(cut[1]+'='+cut[0]+';')

def whileS(cFile, line):
   line = cleanS((line.replace(':','')).replace('while',''))
   cFile.write('while('+line+'){')
   return 1

def tabCounter(line):
   tabSize = 0
   for x in line:
      if x != ' ': break
      tabSize += 1
   return tabSize/3

def ifS(cFile, line):
   line = cleanS((line.replace(':','')).replace('if',''))
   line = line.replace(' = ','==')
   cFile.write('if('+line+'){')
   return 1

def cleanS(string):
   while string[0] == ' ' or string[-1] == ' ':
      if string[0] == ' ': string = string[1:]
      if string[-1] == ' ': string = string[:-1]
   return string

def printf(cFile, line, var):
   #string, variaveis, e print line
   if '"' in line:
      cFile.write('printf('+'"'+line.split('"')[1]+'"'+');')
   else:
      x = cleanS(line.split()[1])
      cFile.write('printf("%'+var[x]+'",'+str(x)+')'+';')

   if line[:7] == 'println': cFile.write('printf("\\n");')

def addVar(var, data):
   #adiciona variaveis a tabela var
   #print(var,data)
   tp = {'int':'i','float':'f','char':'c'}
   for x in data[1]:
      var[x] = tp[data[0]]

def let(cFile, line, varibleType):
   #declaraçao de variaveis
   size = len(varibleType)
   variblesList = line[size:].split()
   cFile.write(varibleType + ' ' + (','.join(variblesList)) + ';')
   return varibleType, variblesList

def op(cFile, line, op):
   #line = 'OP 5 2 5 > x'
   tmp = line.split('>>')
   tmp[0] = tmp[0].split(op)[1]
   tmp[0] = op.join(tmp[0].split())
   cFile.write(tmp[1]+'='+tmp[0]+';')


# noinspection PyUnboundLocalVariable
def loopFor(cFile, line, var):
    line = line.split()
    var[line[1]] = 'i'
    inicial = 'int '+line[1]+'='+line[2]
    final = line[4].replace(':','')
    step = False

    #passo
    if len(line) > 5:
        jump = line[5].replace(':','')
        if '.' in jump:
            inicial = 'float '+line[1]+'='+line[2]
            var[line[1]] = 'f'
        step = True

    if int(line[2]) < int(final):
        #cFile.write('for('+inicial+';'+line[1]+'<='+final+';'+line[1]+'++){')
        cFile.write('for('+inicial+';'+line[1]+'<='+final+';')
        if step:
            cFile.write(line[1]+'+='+jump+'){')
        else:
            cFile.write(line[1]+'++){')
    else:
        #cFile.write('for('+inicial+';'+line[1]+'>='+final+';'+line[1]+'--){')
        cFile.write('for('+inicial+';'+line[1]+'>='+final+';')
        if step:
            cFile.write(line[1]+'-='+jump+'){')
        else:
            cFile.write(line[1]+'--){')

    return 1

def smartSplit(string):
    #corta pedaço de um codigo fora das aspas
    #ignorando ',' dentro de string
    #fast
    if ',' not in string: return [string]

    block = ""
    aspas = False
    blockList = []
    for c in string:
        if c == '"': aspas = not aspas
        block += c
        if not aspas and c == ',':
            blockList.append(block.replace(',',''))
            block = ''
    blockList.append(block)
    return blockList

def holyPrint(cFile, line, var):
    dataList = smartSplit(line)

    cFile.write('printf("')
    tmp = []
    for x in dataList:
        if x not in var.keys():
            #cFile.write('%s ')
            if '"' in x: tmp.append('%s')
            elif '.' in x: tmp.append('%.'+str(len(x.split('.')[1]))+'f')
            else: tmp.append('%i')
        else:
            #cFile.write('%'+var[x]+' ')
            tmp.append('%'+var[x])
    cFile.write(' '.join(tmp))
    cFile.write('",'+(','.join(dataList))+');\n')

def defineF(cFile, line):
    #def somador int x, int y >> int:
    split = line.split(">>")
    ret = split[1].replace(":","")
    name = split[0].split()[1]
    args = split[0][split[0].index(name)+len(name):]
    cFile.write(ret+' '+name+'('+args+')'+'{')
    return 1

def returnF(cFile, line):
    cFile.write(line.replace('>>','return')+';'+'}')
    return 1

def splitMain(code):
    functions = []
    mainF = []
    define = False
    for line in code:
        if tabCounter(line) == 0: define = False
        if define:
            functions.append(line)
            continue
        if line[:3] == 'def':
            define = True
            functions.append(line)
            continue
        mainF.append(line)
    return functions, mainF

def parse(code, cFile):
    #tabelas de simbolos
    var = {} #variaveis
    #old <> 0 = inteiro, 1 = float, 2 = char
    #i = inteiro, f = float, c = char

    #tab
    tabBalance = 0

    for line in code:
      if line in ['', ' ']: continue

      #print('>',line)
      if line[0] == "#": continue

      if tabCounter(line) < tabBalance:
         cFile.write('}')
         if line == "else:":
            cFile.write('else{')
            tabBalance += 1
         tabBalance -= 1
         continue

      line = cleanS(line)

      #operações
      #otimizar com dicionario e "ponteiro" as funções
      #argumentos como uma lista apos funcao
      if line[0] ==  '+':  op(cFile, line, '+')
      elif line[0] ==  '-':  op(cFile, line, '-')
      elif line[0] ==  '/':  op(cFile, line, '/')
      elif line[0] ==  '*':  op(cFile, line, '*')

      #Codigo em C
      elif line[0] == '{': cFile.write(line[1:-1])

      #condições
      elif line[:2] ==  'if':  tabBalance += ifS(cFile, line)
      elif line[:5] == 'while': tabBalance += whileS(cFile, line)

      #loop
      elif line[:3] == 'for': tabBalance += loopFor(cFile, line, var)

      #funções
      elif line[:5] == 'print': printf(cFile, line, var)
      elif line[:3] == 'def': tabBalance += defineF(cFile, line)
      elif line[:2] == '>>': tabBalance -= returnF(cFile, line)

      #declarações
      elif line[:5] ==  'float':  addVar(var, let(cFile, line, 'float'))
      elif line[:4] ==  'char':  addVar(var, let(cFile, line, 'char'))
      elif line[:3] ==  'int':  addVar(var, let(cFile, line, 'int'))
      elif '>>' in line: assign(cFile, line)
      else: holyPrint(cFile, line, var)

    ##
    #final do programa
    for x in range(tabBalance): cFile.write('}')


def main(args):
    if len(args) == 1:
        print("Quimera compiler version 1.0.1")
        print("Use:")
        print("./compiler <QUIMERA_CODE.qui> <OPTIONS>")
        print("Options:")
        print("-c: compile with gcc")
        print("-r: run after compile")
        return 0

    name = args[1].split('.')[0]

    #Leitura
    #with open("configs/" + file, 'r') as filename:
        #filename = filename.readlines()

    file = open(args[1], 'r')
    program = file.read()
    file.close()
    #print(program)

    program = program.split('\n')
    codeSplit = splitMain(program)

    #gravação
    cFile = open(name+'.c', 'w')

    #header
    cFile.write("#include <stdio.h> \n")

    #funçoes
    parse(codeSplit[0], cFile)

    #__main__
    cFile.write("int main(int argc, char **argv){")
    parse(codeSplit[1], cFile)
    cFile.write('return 0;}')


    cFile.close()

    if "-c" in args: os.system("gcc "+name+".c -O3 -o "+name)
    if "-r" in args: os.system('./'+name)

    return 0

if __name__ == '__main__':
   import sys
   sys.exit(main(sys.argv))
