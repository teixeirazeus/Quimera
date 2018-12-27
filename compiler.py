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
   print(">>>",cut)
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
      if var[x]:
          cFile.write('printf("%f",'+str(x)+')'+';')
      else:
          cFile.write('printf("%i",'+str(x)+')'+';')
   if line[:7] == 'println': cFile.write('printf("\\n");')

def addVar(var, data):
   #adiciona variaveis a tabela var
   for x in data[1]:
      var[x] = data[0]

def let(cFile, line, type):
   #declaraçao de variaveis
   size = len(type)
   list = line[size:].split()
   cFile.write(type+' '+(','.join(list))+';')
   if size == 3: return False, list #inteiro
   return True, list #float

def op(cFile, line, op):
   #line = 'OP 5 2 5 > x'
   tmp = line.split('>>')
   tmp[0] = tmp[0].split(op)[1]
   tmp[0] = op.join(tmp[0].split())
   cFile.write(tmp[1]+'='+tmp[0]+';')

def loopFor(cFile, line, var):
    line = line.split()
    var[line[1]] = 0
    inicial = 'int '+line[1]+'='+line[2]
    final = line[4].replace(':','')
    step = False

    #passo
    if len(line) > 5:
        jump = line[5].replace(':','')
        if '.' in jump:
            inicial = 'float '+line[1]+'='+line[2]
            var[line[1]] = 1
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



def main(args):

   name = args[1].split('.')[0]

   #Leitura
   file = open(args[1], 'r')
   program = file.read()
   file.close()
   #print(program)

   program = program.split('\n')

   #tabelas de simbolos
   var = {} #False = inteiro, True = float

   #tab
   tabBalance = 0

   #gravação
   cFile = open(name+'.c', 'w')
   cFile.write("#include <stdio.h> \n int main(int argc, char **argv){")
   ###

   for line in program:
      if line in ['', ' ']: continue

      print('>',line)
      if line[0] == "#": continue

      if tabCounter(line) < tabBalance:
         cFile.write('}')
         if line == "else:":
            cFile.write('else{')
            tabBalance += 1
         tabBalance -= 1

      line = cleanS(line)

      #operações
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

      #declarações
      elif line[:5] ==  'float':  addVar(var, let(cFile, line, 'float'))
      elif line[:3] ==  'int':  addVar(var, let(cFile, line, 'int'))
      elif '>>' in line: assign(cFile, line)

   ###
   #final do programa
   for x in range(tabBalance): cFile.write('}')

   cFile.write('return 0;}')
   cFile.close()

   os.system("gcc "+name+".c -O3 -o "+name)
   os.system('./'+name)

   return 0

if __name__ == '__main__':
   import sys
   sys.exit(main(sys.argv))
