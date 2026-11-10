#!/usr/bin/env python3
"""Generate SEN Image Commands plist. Pure Python, offline at build-time."""
import json,plistlib,uuid,sys,pathlib
SRC=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'data/commands.v1.json')
OUT=pathlib.Path(sys.argv[2] if len(sys.argv)>2 else 'build/SEN Image Commands.unsigned.shortcut')
data=json.loads(SRC.read_text(encoding='utf-8'))
assert len(data['categories'])==12
A=[]
def uid():return str(uuid.uuid4()).upper()
LAST=None
ALLOWED={'gettext','getvariable','setvariable','getvalueforkey','choosefromlist','conditional','repeat.count','repeat.each','detect.dictionary','detect.contacts','properties.contacts','count','getitemfromlist','text.replace','showresult','setclipboard','notification','exit','nothing'}
def act(n,**p):
    global LAST
    assert n in ALLOWED, f"Unrecognized action: {n}"
    u=uid()
    A.append({'WFWorkflowActionIdentifier':'is.workflow.actions.'+n,'WFWorkflowActionParameters':{'UUID':u,**p}})
    LAST=u
    return u
def output(u):return {'Value':{'Type':'ActionOutput','OutputUUID':u},'WFSerializationType':'WFTextTokenAttachment'}
def conditional_input(name):return {'Type':'Variable','Variable':var(name)}
def from_previous():return output(LAST)
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
def sv(n):act('setvariable',WFVariableName=n,WFInput=from_previous())
def dk(key,d):
    act('getvalueforkey',WFDictionaryKey=key if isinstance(key,str) else composite([('var',key[1])]),WFGetDictionaryValueType='Value',WFInput=var(d))
def ch(prompt,multiple=False):act('choosefromlist',WFInput=from_previous(),WFChooseFromListActionPrompt=prompt,WFChooseFromListActionSelectMultiple=multiple)
def iff(n,condition,value,yes,no=None):
    g=uid();a={'GroupingIdentifier':g,'WFControlFlowMode':0,'WFInput':conditional_input(n),'WFCondition':condition}
    if value is not None:
        if condition in (0,1,2,3): a['WFNumberValue']=str(value)
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
act('detect.dictionary',WFInput=from_previous());sv('Catalog')
for key,target in [('submenus','SubmenuMap'),('options','OptionMap'),('codes','CodeMap')]:
    dk(key,'Catalog');sv(target)
text('__SEN__\n');sv('Cache')
cards=[]
def escape(s):return s.replace('\\','\\\\').replace(';','\\;').replace(',','\\,').replace('\n','\\n')
for title in main:
    cards.append('BEGIN:VCARD\nVERSION:3.0\nFN:'+escape(title)+'\nN:;'+escape(title)+';;;\nNOTE:© Sentechtipsvn\nEND:VCARD')
text('\n'.join(cards))
act('detect.contacts',WFInput=from_previous());sv('MainContacts')
def clean():
    act('text.replace',WFInput=var('Cache'),WFReplaceTextFind='^__SEN__\n|\n$',WFReplaceTextReplace='',WFReplaceTextRegularExpression=True,WFReplaceTextCaseSensitive=True)
def preview():
    clean();sv('CleanPreview')
    act('showresult',Text=composite([('var','CleanPreview')]))
def finish():
    def copy():
        clean();sv('CleanPreview')
        act('setclipboard',WFInput=var('CleanPreview'),WFLocalOnly=True)
        act('notification',WFNotificationActionTitle='SEN Image Commands',WFNotificationActionBody='Đã sao chép mã AI.',WFNotificationActionSound=False)
        act('exit')
    iff('Cache',4,'__SEN__\n',lambda:act('showresult',Text='Chưa chọn mã nào.'),copy)
def reset():
    text('__SEN__\n');sv('Cache')
def category():
    dk(('var','Main'),'SubmenuMap');sv('SubmenuList')
    gv('SubmenuList');ch('Chọn nhóm quy ước');sv('Group')
    dk(('var','Group'),'OptionMap');ch('Chọn nhiều khóa · Xong để quay lại Menu',True);sv('Picked')
    def item():
        dk(('var','Repeat Item'),'CodeMap');sv('Candidate')
        text(composite(['\n',('var','Candidate'),'\n']));sv('Needle')
        def append():
            text(composite([('var','Cache'),('var','Candidate'),'\n']));sv('Cache')
        iff('Cache',99,composite([('var','Needle')]),lambda:act('nothing'),append)
    foreach('Picked',item)
def mainloop():
    gv('MainContacts');ch('SEN IMAGE COMMANDS · Chọn danh mục')
    act('properties.contacts',WFContentItemPropertyName='Name',WFInput=from_previous());sv('Main')
    iff('Main',4,FINISH,finish,lambda:
      iff('Main',4,PREVIEW,preview,lambda:
        iff('Main',4,RESET,reset,category)))
loop(150,mainloop)
wf={'WFWorkflowClientVersion':'1300','WFWorkflowClientRelease':'18.0','WFWorkflowMinimumClientVersion':1300,
    'WFWorkflowMinimumClientVersionString':'1300',
    'WFWorkflowIcon':{'WFWorkflowIconStartColor':4282601983,'WFWorkflowIconGlyphNumber':61440},
    'WFWorkflowInputContentItemClasses':[],'WFWorkflowOutputContentItemClasses':[],
    'WFWorkflowTypes':['NCWidget'],'WFWorkflowHasOutputFallback':False,'WFWorkflowActions':A}
stack=[]
for a in A:
    p=a['WFWorkflowActionParameters'];m=p.get('WFControlFlowMode');g=p.get('GroupingIdentifier')
    if m==0:stack.append((g,a['WFWorkflowActionIdentifier']))
    if m==2:assert stack and stack.pop()==(g,a['WFWorkflowActionIdentifier'])
assert not stack
# Mandatory wiring audit: fail the build rather than publish malformed actions.
required={'setvariable','detect.dictionary','detect.contacts','getvalueforkey',
          'choosefromlist','properties.contacts','text.replace','setclipboard'}
for i,a in enumerate(A):
    k=a['WFWorkflowActionIdentifier'].split('is.workflow.actions.',1)[1]
    p=a['WFWorkflowActionParameters']
    if k in required: assert 'WFInput' in p, (i,k,'WFInput missing')
    if k=='conditional' and p.get('WFControlFlowMode')==0:
        assert p.get('WFInput',{}).get('Type')=='Variable', (i,'bad If input')
        assert isinstance(p.get('WFCondition'),int), (i,'bad If code')
        if p['WFCondition'] in (4,5,8,9,99):
            assert 'WFConditionalActionString' in p,(i,'bad If comparison')
    if k=='repeat.each' and p.get('WFControlFlowMode')==0:
        assert 'WFInput' in p,(i,'bad Repeat input')
    for key,v in p.items():
        if isinstance(v,dict) and v.get('WFSerializationType')=='WFTextTokenString':
            assert len(v['Value']['attachmentsByRange'])==v['Value']['string'].count('\ufffc'),(i,key)
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_bytes(plistlib.dumps(wf,fmt=plistlib.FMT_BINARY,sort_keys=False))
print(f'VALID {len(A)} actions, {len(codes)} codes, {len(menus)} categories, {len(opts)} groups, {OUT.stat().st_size} bytes')
,WFReplaceTextReplace='',WFReplaceTextRegularExpression=True,WFReplaceTextCaseSensitive=True)
def preview():
    clean();sv('CleanPreview')
    act('showresult',Text=composite([('var','CleanPreview')]))
def finish():
    def copy():
        clean();sv('CleanPreview')
        act('setclipboard',WFInput=var('CleanPreview'),WFLocalOnly=True)
        act('notification',WFNotificationActionTitle='SEN Image Commands',WFNotificationActionBody='Đã sao chép mã AI.',WFNotificationActionSound=False)
        act('exit')
    iff('Cache',4,'\n',lambda:act('showresult',Text='Chưa chọn mã nào.'),copy)
def reset():
    text('\n');sv('Cache')
def category():
    dk(('var','Main'),'SubmenuMap');sv('SubmenuList')
    gv('SubmenuList');ch('Chọn nhóm quy ước');sv('Group')
    dk(('var','Group'),'OptionMap');ch('Chọn nhiều khóa · Xong để quay lại Menu',True);sv('Picked')
    def item():
        dk(('var','Repeat Item'),'CodeMap');sv('Candidate')
        text(composite(['\n',('var','Candidate'),'\n']));sv('Needle')
        def append():
            text(composite([('var','Cache'),('var','Candidate'),'\n']));sv('Cache')
        iff('Cache',99,composite([('var','Needle')]),lambda:act('nothing'),append)
    foreach('Picked',item)
def mainloop():
    gv('MainContacts');ch('SEN IMAGE COMMANDS · Chọn danh mục')
    act('properties.contacts',WFContentItemPropertyName='Name',WFInput=from_previous());sv('Main')
    iff('Main',4,FINISH,finish,lambda:
      iff('Main',4,PREVIEW,preview,lambda:
        iff('Main',4,RESET,reset,category)))
loop(150,mainloop)
wf={'WFWorkflowClientVersion':'1300','WFWorkflowClientRelease':'18.0','WFWorkflowMinimumClientVersion':1300,
    'WFWorkflowMinimumClientVersionString':'1300',
    'WFWorkflowIcon':{'WFWorkflowIconStartColor':4282601983,'WFWorkflowIconGlyphNumber':61440},
    'WFWorkflowInputContentItemClasses':[],'WFWorkflowOutputContentItemClasses':[],
    'WFWorkflowTypes':['NCWidget'],'WFWorkflowHasOutputFallback':False,'WFWorkflowActions':A}
stack=[]
for a in A:
    p=a['WFWorkflowActionParameters'];m=p.get('WFControlFlowMode');g=p.get('GroupingIdentifier')
    if m==0:stack.append((g,a['WFWorkflowActionIdentifier']))
    if m==2:assert stack and stack.pop()==(g,a['WFWorkflowActionIdentifier'])
assert not stack
# Mandatory wiring audit: fail the build rather than publish malformed actions.
required={'setvariable','detect.dictionary','detect.contacts','getvalueforkey',
          'choosefromlist','properties.contacts','text.replace','setclipboard'}
for i,a in enumerate(A):
    k=a['WFWorkflowActionIdentifier'].split('is.workflow.actions.',1)[1]
    p=a['WFWorkflowActionParameters']
    if k in required: assert 'WFInput' in p, (i,k,'WFInput missing')
    if k=='conditional' and p.get('WFControlFlowMode')==0:
        assert p.get('WFInput',{}).get('Type')=='Variable', (i,'bad If input')
        assert isinstance(p.get('WFCondition'),int), (i,'bad If code')
        if p['WFCondition'] in (4,5,8,9,99):
            assert 'WFConditionalActionString' in p,(i,'bad If comparison')
    if k=='repeat.each' and p.get('WFControlFlowMode')==0:
        assert 'WFInput' in p,(i,'bad Repeat input')
    for key,v in p.items():
        if isinstance(v,dict) and v.get('WFSerializationType')=='WFTextTokenString':
            assert len(v['Value']['attachmentsByRange'])==v['Value']['string'].count('\ufffc'),(i,key)
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_bytes(plistlib.dumps(wf,fmt=plistlib.FMT_BINARY,sort_keys=False))
print(f'VALID {len(A)} actions, {len(codes)} codes, {len(menus)} categories, {len(opts)} groups, {OUT.stat().st_size} bytes')
