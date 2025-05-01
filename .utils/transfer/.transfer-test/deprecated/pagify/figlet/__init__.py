#!/usr/bin/env python
from __future__ import print_function,unicode_literals
w='left'
v='center'
u='ascii'
t='figlet'
s=sorted
r=property
q=Exception
g='right'
f=':'
e=open
c='left-to-right'
b='rb'
a='figlet.fonts'
Z='replace'
Y=exit
X=classmethod
U=int
Q='right-to-left'
P=ord
O=print
M='UTF-8'
L=list
K='auto'
J=range
H='\n'
G=False
F=' '
D=None
B=len
A=''
import itertools as x,importlib.resources,os as C,pathlib as h,re as I,shutil as i,sys as E,zipfile as R
from optparse import OptionParser as y
S='standard'
V={'BLACK':30,'RED':31,'GREEN':32,'YELLOW':33,'BLUE':34,'MAGENTA':35,'CYAN':36,'LIGHT_GRAY':37,'DEFAULT':39,'DARK_GRAY':90,'LIGHT_RED':91,'LIGHT_GREEN':92,'LIGHT_YELLOW':93,'LIGHT_BLUE':94,'LIGHT_MAGENTA':95,'LIGHT_CYAN':96,'WHITE':97,'RESET':0}
j=b'\x1b[0m'
if E.platform=='win32':N=C.path.join(C.environ['APPDATA'],t)
else:N='/usr/local/share/figlet/'
def z(text,font=S,**A):B=n(font,**A);return B.renderText(text)
def A6(text,font=S,colors=f,**B):
	A=p(colors)
	if A:E.stdout.write(A)
	O(z(text,font,**B))
	if A:E.stdout.write(j.decode(M,Z));E.stdout.flush()
class W(q):
	def __init__(A,error):A.error=error
	def __str__(A):return A.error
class A0(W):0
class k(W):0
class d(W):0
class l(W):0
class T:
	reMagicNumber=I.compile('^[tf]lf2.');reEndMarker=I.compile('(.)\\s*$')
	def __init__(B,font=S):B.font=font;B.comment=A;B.chars={};B.width={};B.data=B.preloadFont(font);B.loadFont()
	@X
	def preloadFont(cls,font):
		A=D;B=D
		for J in('tlf','flf'):
			F='%s.%s'%(font,J);G=importlib.resources.files(a).joinpath(F)
			if G.exists():B=G;break
			else:
				for K in('./',N):
					H=C.path.join(K,F)
					if C.path.isfile(H):B=h.Path(H);break
		if B:
			with B.open(b)as E:
				if R.is_zipfile(E):
					with R.ZipFile(E)as I:L=I.open(I.namelist()[0]);A=L.read()
				else:E.seek(0);A=E.read()
		if A:return A.decode(M,Z)
		else:raise k(font)
	@X
	def isValidFont(cls,font):
		B=font
		if not B.endswith(('.flf','.tlf')):return G
		A=D;E=C.path.join(N,B)
		if C.path.isfile(B):A=e(B,b)
		elif C.path.isfile(E):A=e(E,b)
		else:A=importlib.resources.files(a).joinpath(B).open(b)
		if R.is_zipfile(A):
			with R.ZipFile(A)as F:I=F.open(F.namelist()[0]);H=I.readline().decode(M,Z)
		else:A.seek(0);H=A.readline().decode(M,Z)
		A.close();return cls.reMagicNumber.search(H)
	@X
	def getFonts(cls):
		A=importlib.resources.files(a).iterdir()
		if C.path.isdir(N):A=x.chain(A,h.Path(N).iterdir())
		return[A.name.split('.',2)[0]for A in A if A.is_file()and cls.isValidFont(A.name)]
	@X
	def infoFont(cls,font,short=G):
		C=T.preloadFont(font);B=[];E=I.compile('\n            ^(FONT|COMMENT|FONTNAME_REGISTRY|FAMILY_NAME|FOUNDRY|WEIGHT_NAME|\n              SETWIDTH_NAME|SLANT|ADD_STYLE_NAME|PIXEL_SIZE|POINT_SIZE|\n              RESOLUTION_X|RESOLUTION_Y|SPACING|AVERAGE_WIDTH|\n              FONT_DESCENT|FONT_ASCENT|CAP_HEIGHT|X_HEIGHT|FACE_NAME|FULL_NAME|\n              COPYRIGHT|_DEC_|DEFAULT_CHAR|NOTICE|RELATIVE_).*',I.VERBOSE);F=I.compile('^.*[@#$]$')
		for A in C.splitlines()[0:100]:
			if cls.reMagicNumber.search(A)is D and E.search(A)is D and F.search(A)is D:B.append(A)
		return H.join(B)if not short else B[0]
	@staticmethod
	def installFonts(file_name):
		B=file_name
		if hasattr(importlib.resources.files(t),'resolve'):A=str(importlib.resources.files(a))
		else:A=N
		O('Installing {} to {}'.format(B,A))
		if not C.path.exists(A):C.makedirs(A)
		if C.path.splitext(B)[1].lower()=='.zip':
			with R.ZipFile(B)as D:
				for E in D.namelist():
					F=C.path.basename(E)
					if not F:continue
					with D.open(E)as G:
						with e(C.path.join(A,F),'wb')as H:i.copyfileobj(G,H)
		else:i.copy(B,A)
	def loadFont(C):
		try:
			H=I.sub('[\\u0085\\u2028\\u2029]',F,C.data);H=H.splitlines();G=H.pop(0)
			if C.reMagicNumber.search(G)is D:raise d('%s is not a valid figlet font'%C.font)
			G=C.reMagicNumber.sub(A,G);G=G.split()
			if B(G)<6:raise d('malformed header for %s'%C.font)
			S=G[0];Q,Y,Z,N,T=map(U,G[1:6]);R=L=D
			if B(G)>6:R=U(G[6])
			if B(G)>7:L=U(G[7])
			if L is D:
				if N==0:L=64
				elif N<0:L=0
				else:L=N&31|128
			C.height=Q;C.hardBlank=S;C.printDirection=R;C.smushMode=L
			for E in J(0,T):C.comment+=H.pop(0)
			def O(data):
				F=D;G=0;H=[]
				for K in J(0,Q):
					E=data.pop(0)
					if F is D:F=C.reEndMarker.search(E).group(1);F=I.compile(I.escape(F)+'{1,2}\\s*$')
					E=F.sub(A,E)
					if B(E)>G:G=B(E)
					H.append(E)
				return G,H
			for E in J(32,127):
				M,K=O(H)
				if E==32 or A.join(K)!=A:C.chars[E]=K;C.width[E]=M
			if H:
				for E in'ÄÖÜäöüß':
					M,K=O(H)
					if A.join(K)!=A:C.chars[P(E)]=K;C.width[P(E)]=M
			while H:
				V=H.pop(0).strip();E=V.split(F,1)[0]
				if E==A:continue
				W=I.search('^0x',E,I.IGNORECASE)
				if W is not D:
					E=U(E,16);M,K=O(H)
					if A.join(K)!=A:C.chars[E]=K;C.width[E]=M
		except q as X:raise d('problem parsing %s font: %s'%(C.font,X))
	def __str__(A):return'<FigletFont object: %s>'%A.font
A1=type(A.encode(u).decode(u))
class m(A1):
	__reverse_map__='\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\')(*+,-.\\0123456789:;>=<?@ABCDEFGHIJKLMNOPQRSTUVWXYZ]/[^_`abcdefghijklmnopqrstuvwxyz}|{~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬\xad®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ';__flip_map__='\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-.\\0123456789:;<=>?@VBCDEFGHIJKLWNObQbSTUAMXYZ[/]v-`aPcdefghijklwnopqrstu^mxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬\xad®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ'
	def reverse(A):
		B=[]
		for C in A.splitlines():B.append(C.translate(A.__reverse_map__)[::-1])
		return A.newFromList(B)
	def flip(A):
		B=[]
		for C in A.splitlines()[::-1]:B.append(C.translate(A.__flip_map__))
		return A.newFromList(B)
	def strip_surrounding_newlines(B):
		C=[];D=G
		for E in B.splitlines():
			if E.strip()!=A or D:D=True;C.append(E)
		return B.newFromList(C).rstrip()
	def normalize_surrounding_newlines(A):return H+A.strip_surrounding_newlines()+H
	def newFromList(A,list):return m(H.join(list)+H)
class A2:
	def __init__(A,base=D):A.base=base
	def render(A,text):
		B=A4(text,A.base.Font,A.base.direction,A.base.width,A.base.justify)
		while B.isNotFinished():B.addCharToProduct();B.goToNextChar()
		return B.returnProduct()
class A3:
	def __init__(B):B.queue=L();B.buffer_string=A
	def append(A,buffer):A.queue.append(buffer)
	def getString(A):return m(A.buffer_string)
class A4:
	def __init__(B,text,font,direction,width,justify):B.text=L(map(P,L(text)));B.direction=direction;B.width=width;B.font=font;B.justify=justify;B.iterator=0;B.maxSmush=0;B.newBlankRegistered=G;B.curCharWidth=0;B.prevCharWidth=0;B.currentTotalWidth=0;B.blankMarkers=L();B.product=A3();B.buffer=[A for B in J(B.font.height)];B.SM_EQUAL=1;B.SM_LOWLINE=2;B.SM_HIERARCHY=4;B.SM_PAIR=8;B.SM_BIGX=16;B.SM_HARDBLANK=32;B.SM_KERN=64;B.SM_SMUSH=128
	def addCharToProduct(A):
		C=A.getCurChar()
		if A.text[A.iterator]==P(H):A.blankMarkers.append(([A for A in A.buffer],A.iterator));A.handleNewLine();return
		if C is D:return
		if A.width<A.getCurWidth():raise A0('Width is not enough to print this character')
		A.curCharWidth=A.getCurWidth();A.maxSmush=A.currentSmushAmount(C);A.currentTotalWidth=B(A.buffer[0])+A.curCharWidth-A.maxSmush
		if A.text[A.iterator]==P(F):A.blankMarkers.append(([A for A in A.buffer],A.iterator))
		if A.text[A.iterator]==P(H):A.blankMarkers.append(([A for A in A.buffer],A.iterator));A.handleNewLine()
		if A.currentTotalWidth>=A.width:A.handleNewLine()
		else:
			for E in J(0,A.font.height):A.addCurCharRowToBufferRow(C,E)
		A.prevCharWidth=A.curCharWidth
	def goToNextChar(A):A.iterator+=1
	def returnProduct(B):
		if B.buffer[0]!=A:B.flushLastBuffer()
		B.formatProduct();return B.product.getString()
	def isNotFinished(A):C=A.iterator<B(A.text);return C
	def flushLastBuffer(A):A.product.append(A.buffer)
	def formatProduct(B):
		D=A
		for C in B.product.queue:C=B.justifyString(B.justify,C);D+=B.replaceHardblanks(C)
		B.product.buffer_string=D
	def getCharAt(A,i):
		if i<0 or i>=B(L(A.text)):return
		C=A.text[i]
		if C not in A.font.chars:return
		else:return A.font.chars[C]
	def getCharWidthAt(A,i):
		if i<0 or i>=B(A.text):return
		C=A.text[i]
		if C not in A.font.chars:return
		else:return A.font.width[C]
	def getCurChar(A):return A.getCharAt(A.iterator)
	def getCurWidth(A):return A.getCharWidthAt(A.iterator)
	def getLeftSmushedChar(F,i,addLeft):
		D=addLeft;C=B(D)-F.maxSmush+i
		if C>=0 and C<B(D):E=D[C]
		else:E=A
		return E,C
	def currentSmushAmount(A,curChar):return A.smushAmount(A.buffer,curChar)
	def updateSmushedCharInLeftBuffer(F,addLeft,idx,smushed):
		D=idx;C=addLeft;E=L(C)
		if D<0 or D>B(E):return C
		E[D]=smushed;C=A.join(E);return C
	def smushRow(A,curChar,row):
		B=A.buffer[row];C=curChar[row]
		if A.direction==Q:B,C=C,B
		for D in J(0,A.maxSmush):E,F=A.getLeftSmushedChar(D,B);G=C[D];H=A.smushChars(left=E,right=G);B=A.updateSmushedCharInLeftBuffer(B,F,H)
		return B,C
	def addCurCharRowToBufferRow(A,curChar,row):B,C=A.smushRow(curChar,row);A.buffer[row]=B+C[A.maxSmush:]
	def cutBufferCommon(B):
		B.currentTotalWidth=0;B.buffer=[A for B in J(B.font.height)];B.blankMarkers=L();B.prevCharWidth=0;C=B.getCurChar()
		if C is D:return
		B.maxSmush=B.currentSmushAmount(C)
	def cutBufferAtLastBlank(A,saved_buffer,saved_iterator):A.product.append(saved_buffer);A.iterator=saved_iterator;A.cutBufferCommon()
	def cutBufferAtLastChar(A):A.product.append(A.buffer);A.iterator-=1;A.cutBufferCommon()
	def blankExist(A,last_blank):return last_blank!=-1
	def getLastBlank(A):
		try:B,C=A.blankMarkers.pop()
		except IndexError:return-1,-1
		return B,C
	def handleNewLine(A):
		C,B=A.getLastBlank()
		if A.blankExist(B):A.cutBufferAtLastBlank(C,B)
		else:A.cutBufferAtLastChar()
	def justifyString(D,justify,buffer):
		E=justify;A=buffer
		if E==g:
			for C in J(0,D.font.height):A[C]=F*(D.width-B(A[C])-1)+A[C]
		elif E==v:
			for C in J(0,D.font.height):A[C]=F*U((D.width-B(A[C]))/2)+A[C]
		return A
	def replaceHardblanks(B,buffer):A=H.join(buffer)+H;A=A.replace(B.font.hardBlank,F);return A
	def smushAmount(C,buffer=[],curChar=[]):
		if C.font.smushMode&(C.SM_SMUSH|C.SM_KERN)==0:return 0
		M=C.curCharWidth
		for O in J(0,C.font.height):
			G=buffer[O];E=curChar[O]
			if C.direction==Q:G,E=E,G
			H=B(G.rstrip(F))-1
			if H<0:H=0
			if H<B(G):I=G[H]
			else:H=0;I=A
			K=B(E)-B(E.lstrip(F))
			if K<B(E):N=E[K]
			else:K=B(E);N=A
			L=K+B(G)-1-H
			if I==A or I==F:L+=1
			elif N!=A and C.smushChars(left=I,right=N)is not D:L+=1
			if L<M:M=L
		return M
	def smushChars(A,left=A,right=A):
		E='|';C=right;B=left
		if B==F:return C
		if C==F:return B
		if A.prevCharWidth<2 or A.curCharWidth<2:return
		if A.font.smushMode&A.SM_SMUSH==0:return
		if A.font.smushMode&63==0:
			if B==A.font.hardBlank:return C
			if C==A.font.hardBlank:return B
			if A.direction==Q:return B
			else:return C
		if A.font.smushMode&A.SM_HARDBLANK:
			if B==A.font.hardBlank and C==A.font.hardBlank:return B
		if B==A.font.hardBlank or C==A.font.hardBlank:return
		if A.font.smushMode&A.SM_EQUAL:
			if B==C:return B
		D=()
		if A.font.smushMode&A.SM_LOWLINE:D+=('_','|/\\[]{}()<>'),
		if A.font.smushMode&A.SM_HIERARCHY:D+=(E,'/\\[]{}()<>'),('\\/','[]{}()<>'),('[]','{}()<>'),('{}','()<>'),('()','<>')
		for(G,H)in D:
			if B in G and C in H:return C
			if C in G and B in H:return B
		if A.font.smushMode&A.SM_PAIR:
			for I in[B+C,C+B]:
				if I in['[]','{}','()']:return E
		if A.font.smushMode&A.SM_BIGX:
			if B=='/'and C=='\\':return E
			if C=='/'and B=='\\':return'Y'
			if B=='>'and C=='<':return'X'
class n:
	def __init__(A,font=S,direction=K,justify=K,width=80):A.font=font;A._direction=direction;A._justify=justify;A.width=width;A.setFont();A.engine=A2(base=A)
	def setFont(A,**B):
		C='font'
		if C in B:A.font=B[C]
		A.Font=T(font=A.font)
	def getDirection(A):
		if A._direction==K:
			B=A.Font.printDirection
			if B==0:return c
			elif B==1:return Q
			else:return c
		else:return A._direction
	direction=r(getDirection)
	def getJustify(A):
		if A._justify==K:
			if A.direction==c:return w
			elif A.direction==Q:return g
		else:return A._justify
	justify=r(getJustify)
	def renderText(A,text):return A.engine.render(text)
	def getFonts(A):return A.Font.getFonts()
def o(color,isBackground):
	E=isBackground;D=';';B=color
	if not B:return A
	B=B.upper()
	if B.count(D)>0 and B.count(D)!=2:raise l("Specified color '{}' not a valid color in R;G;B format")
	elif B.count(D)==0 and B not in V:raise l("Specified color '{}' not found in ANSI COLOR_CODES list".format(B))
	if B in V:
		C=V[B]
		if E:C+=10
	else:C=48 if E else 38;C='{};2;{}'.format(C,B)
	return'\x1b[{}m'.format(C)
def p(color):A,E,B=color.partition(f);C=o(A,isBackground=G);D=o(B,isBackground=True);return C+D
def A5():
	P='choice';J='store_true';C=y(version='1.0.2',usage='%prog [options] [text..]');C.add_option('-f','--font',default=S,help='font to render with (default: %default)',metavar='FONT');C.add_option('-D','--direction',type=P,choices=(K,c,Q),default=K,metavar='DIRECTION',help='set direction text will be formatted in (default: %default)');C.add_option('-j','--justify',type=P,choices=(K,w,v,g),default=K,metavar='SIDE',help='set justification, defaults to print direction');C.add_option('-w','--width',type='int',default=80,metavar='COLS',help='set terminal width for wrapping/justification (default: %default)');C.add_option('-r','--reverse',action=J,default=G,help='shows mirror image of output text');C.add_option('-n','--normalize-surrounding-newlines',action=J,default=G,help='output has one empty line before and after');C.add_option('-s','--strip-surrounding-newlines',action=J,default=G,help='removes empty leading and trailing lines');C.add_option('-F','--flip',action=J,default=G,help='flips rendered output text over');C.add_option('-l','--list_fonts',action=J,default=G,help='show installed fonts list');C.add_option('-i','--info_font',action=J,default=G,help="show font's information, use with -f FONT");C.add_option('-L','--load',default=D,help='load and install the specified font definition');C.add_option('-c','--color',default=f,help='prints text with passed foreground color,\n                            --color=foreground:background\n                            --color=:background\t\t\t # only background\n                            --color=foreground | foreground:\t # only foreground\n                            --color=list\t\t\t # list all colors\n                            COLOR = list[COLOR] | [0-255];[0-255];[0-255] (RGB)');A,L=C.parse_args()
	if A.list_fonts:O(H.join(s(T.getFonts())));Y(0)
	if A.color=='list':O('[0-255];[0-255];[0-255] # RGB\n'+H.join(s(V.keys())));Y(0)
	if A.info_font:O(T.infoFont(A.font));Y(0)
	if A.load:T.installFonts(A.load);Y(0)
	if B(L)==0:C.print_help();return 1
	if E.version_info<(3,):L=[A.decode(M)for A in L]
	R=F.join(L)
	try:U=n(font=A.font,direction=A.direction,justify=A.justify,width=A.width)
	except k as W:O(f"figlet error: requested font {A.font!r} not found.");return 1
	I=U.renderText(R)
	if A.reverse:I=I.reverse()
	if A.flip:I=I.flip()
	if A.strip_surrounding_newlines:I=I.strip_surrounding_newlines()
	elif A.normalize_surrounding_newlines:I=I.normalize_surrounding_newlines()
	if E.version_info>(3,):E.stdout=E.stdout.detach()
	N=p(A.color)
	if N:E.stdout.write(N.encode(M))
	E.stdout.write(I.encode(M));E.stdout.write(b'\n')
	if N:E.stdout.write(j)
	return 0
if __name__=='__main__':E.exit(A5())