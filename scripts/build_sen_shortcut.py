#!/usr/bin/env python3
"""Generate SEN Image Commands plist. Pure Python, offline at build-time."""
import json,plistlib,uuid,sys,pathlib
SRC=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'data/commands.v1.json')
OUT=pathlib.Path(sys.argv[2] if len(sys.argv)>2 else 'build/SEN Image Commands.unsigned.shortcut')
data=json.loads(SRC.read_text(encoding='utf-8'))
assert len(data['categories'])==12
A=[]
def uid():return str(uuid.uuid4()).upper()
def act(n,**p):
    A.append({'WFWorkflowActionIdentifier':'is.workflow.actions.'+n,'WFWorkflowActionParameters':{'UUID':uid(),**p}})
def var(n):return {'Value':{'Type':'Variable','VariableName':n},'WFSerializationType':'WFTextTokenAttachment'}
def composite(parts):
    s='';at={}
    for p in parts:
        if isinstance(p,tuple):
            i=len(s);s+='\uFFFC';at[f'{{{i}, 1}}']={'Type':'Variable','VariableName':p[1]}
        else:s+=str(p)
    return {'Value':{'string':s,'attachmentsByRange':at},'WFSerializationType':'WFTextTokenString'}
def text(x):act('gettext',WFTextActionText=x)
def gv(n):act('getvariable',WFVariable=var(n))
def sv(n):act('setvariable',WFVariableName=n)
def dk(key,d):
    act('getvalueforkey',WFDictionaryKey=key if isinstance(key,str) else var(key[1]),WFGetDictionaryValueType='Value',WFInput=var(d))
def ch(prompt,multiple=False):act('choosefromlist',WFChooseFromListActionPrompt=prompt,WFChooseFromListActionSelectMultiple=multiple)
def iff(n,condition,value,yes,no=None):
    g=uid();a={'GroupingIdentifier':g,'WFControlFlowMode':0,'WFInput':var(n),'WFCondition':condition}
    if value is not None:
        if n=='SubCount': a['WFNumberValue']=int(value)
        else: a['WFConditionalActionString']=value
    act('conditional',**a);yes()
    if no is not None:
        act('conditional',GroupingIdentifier=g,WFControlFlowMode=1);no()
    act('conditional',GroupingIdentifier=g,WFControlFlowMode=2)
def loop(n,body):
    g=uid();act('repeat.count',GroupingIdentifier=g,WFControlFlowMode=0,WFRepeatCount=n)
    body();act('repeat.count',GroupingIdentifier=g,WFControlFlowMode=2)
def foreach(n,body):
    g=uid();act('repeat.each',GroupingIdentifier=g,WFControlFlowMode=0,WFInput=var(n))
    body();act('repeat.each',GroupingIdentifier=g,WFControlFlowMode=2)
emojis=['🖼️','🔐','🔄','😊','📷','☀️','👔','🎨','🛠️','📐','🔤','🛡️']
menus={};opts={};codes={};main=[]
for idx,category in enumerate(data['categories']):
    label=emojis[idx]+' '+category['title'];main.append(label);subs=[]
    for group in category['submenus']:
        sub='📁 '+group['title'].title();subs.append(sub)
        assert sub not in opts
        opts[sub]=[row['label'] for row in group['items']]
        for row in group['items']:
            assert row['label'] not in codes
            codes[row['label']]=row['code']
    menus[label]=subs
PREVIEW='📋 Xem mã đang chọn'
FINISH='✅ Hoàn tất · Sao chép'
RESET='🗑️ Xóa lựa chọn'
main.extend([PREVIEW,FINISH,RESET])
assert len(codes)==357
assert all(code.startswith('/') and not code.endswith('=') for code in codes.values())
text(json.dumps({'submenus':menus,'options':opts,'codes':codes},ensure_ascii=False,separators=(',',':')))
act('detect.dictionary');sv('Catalog')
for key,target in [('submenus','SubmenuMap'),('options','OptionMap'),('codes','CodeMap')]:
    dk(key,'Catalog');sv(target)
text('\n');sv('Cache')
cards=[]
def escape(s):return s.replace('\\','\\\\').replace(';','\\;').replace(',','\\,').replace('\n','\\n')
for title in main:
    cards.append('BEGIN:VCARD\nVERSION:3.0\nFN:'+escape(title)+'\nN:;'+escape(title)+';;;\nNOTE:© Sentechtipsvn\nEND:VCARD')
text('\n'.join(cards))
act('detect.contacts');sv('MainContacts')
def preview():
    gv('Cache');act('trimwhitespace');sv('CleanPreview');act('showresult',Text=var('CleanPreview'))
def finish():
    def copy():
        gv('Cache');act('trimwhitespace');act('setclipboard',WFLocalOnly=True)
        act('notification',WFNotificationActionTitle='SEN Image Commands',WFNotificationActionBody='Đã sao chép mã AI.',WFNotificationActionSound=False)
        act('exit')
    iff('Cache',4,'\n',lambda:act('showresult',Text='Chưa chọn mã nào.'),copy)
def reset():
    text('\n');sv('Cache')
def category():
    dk(('var','Main'),'SubmenuMap');sv('SubmenuList')
    gv('SubmenuList');act('count',WFCountType='Items',Input=var('SubmenuList'),WFInput=var('SubmenuList'));sv('SubCount')
    def direct():
        gv('SubmenuList');act('getitemfromlist',WFItemSpecifier='First Item');sv('Group')
    def subchoice():
        gv('SubmenuList');ch('Chọn nhóm quy ước');sv('Group')
    iff('SubCount',4,'1',direct,subchoice)
    dk(('var','Group'),'OptionMap');ch('Chọn nhiều khóa · Xong để quay lại Menu',True);sv('Picked')
    def item():
        dk(('var','Repeat Item'),'CodeMap');sv('Candidate')
        text(composite(['\n',('var','Candidate'),'\n']));sv('Needle')
        def append():
            text(composite([('var','Cache'),('var','Candidate'),'\n']));sv('Cache')
        iff('Cache',9,var('Needle'),append)
    foreach('Picked',item)
def mainloop():
    gv('MainContacts');ch('SEN IMAGE COMMANDS · Chọn danh mục')
    act('properties.contacts',WFContentItemPropertyName='Name');sv('Main')
    iff('Main',4,FINISH,finish,lambda:
      iff('Main',4,PREVIEW,preview,lambda:
        iff('Main',4,RESET,reset,category)))
loop(150,mainloop)
wf={'WFWorkflowClientVersion':'1300','WFWorkflowClientRelease':'18.0','WFWorkflowMinimumClientVersion':1300,
    'WFWorkflowMinimumClientVersionString':'1300',
    'WFWorkflowIcon':{'WFWorkflowIconStartColor':4282601983,'WFWorkflowIconGlyphNumber':61440},
    'WFWorkflowInputContentItemClasses':['WFTextContentItem'],'WFWorkflowOutputContentItemClasses':[],
    'WFWorkflowTypes':['ActionExtension'],'WFWorkflowHasOutputFallback':False,'WFWorkflowActions':A}
stack=[]
for a in A:
    p=a['WFWorkflowActionParameters'];m=p.get('WFControlFlowMode');g=p.get('GroupingIdentifier')
    if m==0:stack.append((g,a['WFWorkflowActionIdentifier']))
    if m==2:assert stack and stack.pop()==(g,a['WFWorkflowActionIdentifier'])
assert not stack
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_bytes(plistlib.dumps(wf,fmt=plistlib.FMT_XML,sort_keys=False))
print(f'VALID {len(A)} actions, {len(codes)} codes, {len(menus)} categories, {len(opts)} groups, {OUT.stat().st_size} bytes')
