from random import randint
from os import system
def blackwhite(text):
	system('');D='';A=0;B=0;C=0
	for E in text.splitlines():
		D+=f"\033[38;2;{A};{B};{C}m{E}\033[0m\n"
		if not A==255 and not B==255 and not C==255:
			A+=20;B+=20;C+=20
			if A>255 and B>255 and C>255:A=255;B=255;C=255
	return D
def purplepink(text):
	system('');B='';A=40
	for C in text.splitlines():
		B+=f"\033[38;2;{A};0;220m{C}\033[0m\n"
		if not A==255:
			A+=15
			if A>255:A=255
	return B
def greenblue(text):
	system('');B='';A=100
	for C in text.splitlines():
		B+=f"\033[38;2;0;255;{A}m{C}\033[0m\n"
		if not A==255:
			A+=15
			if A>255:A=255
	return B
def pinkred(text):
	system('');B='';A=255
	for C in text.splitlines():
		B+=f"\033[38;2;255;0;{A}m{C}\033[0m\n"
		if not A==0:
			A-=20
			if A<0:A=0
	return B
def purpleblue(text):
	system('');B='';A=110
	for C in text.splitlines():
		B+=f"\033[38;2;{A};0;255m{C}\033[0m\n"
		if not A==0:
			A-=15
			if A<0:A=0
	return B
def water(text):
	system('');B='';A=10
	for C in text.splitlines():
		B+=f"\033[38;2;0;{A};255m{C}\033[0m\n"
		if not A==255:
			A+=15
			if A>255:A=255
	return B
def fire(text):
	system('');B='';A=250
	for C in text.splitlines():
		B+=f"\033[38;2;255;{A};0m{C}\033[0m\n"
		if not A==0:
			A-=25
			if A<0:A=0
	return B
def brazil(text):
	system('');B='';A=0
	for C in text.splitlines():
		B+=f"\033[38;2;{A};255;0m{C}\033[0m\n"
		if not A>200:A+=30
	return B

def random(text):
	system('');A=''
	for B in text.splitlines():
		for C in B:A+=f"\033[38;2;{randint(0,255)};{randint(0,255)};{randint(0,255)}m{C}\033[0m"
		A+='\n'
	return A

def sunset(text):
	system('');D='';A=255;B=100;C=0
	for E in text.splitlines():
		D+=f"\033[38;2;{A};{B};{C}m{E}\033[0m\n"
		if A > 0 and B < 255:
			A -= 5
			B += 5
	return D

def forest(text):
	system('');D='';A=0;B=100;C=0
	for E in text.splitlines():
		D+=f"\033[38;2;{A};{B};{C}m{E}\033[0m\n"
		if B < 255:
			B += 5
	return D

def german_red(text):
    system('');D='';A=30;B=30;C=30
    for E in text.splitlines():
        if A < 255:
            A += (255 - 30) // len(text.splitlines())
        elif A >= 255 and B < 255:
            B += 255 // len(text.splitlines())
            A = 255
        C = 0
        D += f"\033[38;2;{A};{B};{C}m{E}\033[0m\n"
    return D

def eintracht_frankfurt(text):
	system('');B='';r=230;g=0;b=0
	lines = text.splitlines()
	quarter = len(lines) // 4
	for i, C in enumerate(lines):
		B+=f"\033[38;2;{r};{g};{b}m{C}\033[0m\n"
		if i >= quarter:
			if r<255: r+=3
			if g<255: g+=40
			if b<255: b+=40
			if r>255: r=255
			if g>255: g=255
			if b>255: b=255
	return B
def northern_lights(text):
	system('');result='';r=10;g=200;b=120
	for line in text.splitlines():
		result+=f"\033[38;2;{r};{g};{b}m{line}\033[0m\n"
		if r < 100:
			r+=10
		if g > 100:
			g-=10
		if b < 255:
			b+=15
	return result

def gold_fever(text):
	system('');result='';r=255;g=215;b=0
	for line in text.splitlines():
		result+=f"\033[38;2;{r};{g};{b}m{line}\033[0m\n"
		if r > 180:
			r-=5
		if g > 150:
			g-=10
		if b < 100:
			b+=15
	return result

def ocean_depths(text):
	system('');result='';r=0;g=50;b=100
	for line in text.splitlines():
		result+=f"\033[38;2;{r};{g};{b}m{line}\033[0m\n"
		if g < 150:
			g+=10
		if b < 220:
			b+=12
	return result

def ukraine(text):
	system('');B='';r=0;g=87;b=183
	lines = text.splitlines()
	halfway = len(lines) // 2
	for i, C in enumerate(lines):
		B+=f"\033[38;2;{r};{g};{b}m{C}\033[0m\n"
		if i >= halfway - 1:
			if r<255: r+=50
			if g<215: g+=25
			if b>0: b-=35
			if r>255: r=255
			if g>215: g=215
			if b<0: b=0
	return B