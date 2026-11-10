#!/usr/bin/env python3
"""Reject unwired or unsupported generated Apple Shortcuts before signing."""
import plistlib,sys,re,collections,json
path=sys.argv[1] if len(sys.argv)>1 else 'build/sen.unsigned.shortcut'
wf=plistlib.load(open(path,'rb'))
actions=wf['WFWorkflowActions']
types=collections.Counter(a['WFWorkflowActionIdentifier'] for a in actions)
allow={v for v in (
'gettext setvariable getvariable getvalueforkey choosefromlist conditional repeat.count repeat.each detect.dictionary detect.contacts properties.contacts text.replace showresult setclipboard notification exit nothing'
).split()}
if len(actions)<50 or len(actions)>110:raise ValueError('Unexpected action count')
defined=set();ids=set();stack=[];problems=[]
def validate_text(v,n):
    if not isinstance(v,dict) or v.get('WFSerializationType')!='WFTextTokenString':return
    vv=v['Value'];positions=vv.get('attachmentsByRange',{});s=vv.get('string','')
    if s.count('\ufffc')!=len(positions):problems.append((n,'mismatched text tokens'))
    for key in positions:
        m=re.fullmatch(r'\{(\d+), 1\}',key)
        if not m or (idx:=int(m.group(1)))>=len(s) or s[idx]!='\ufffc':
            problems.append((n,'invalid token position '+key))
for n,a in enumerate(actions):
    aid=a['WFWorkflowActionIdentifier'].removeprefix('is.workflow.actions.')
    p=a['WFWorkflowActionParameters']
    if aid not in allow:problems.append((n,'unknown action '+aid))
    if p['UUID'] in ids:problems.append((n,'duplicate UUID'))
    ids.add(p['UUID'])
    for k,v in p.items():validate_text(v,n)
    if aid in ('setvariable','getvalueforkey','choosefromlist','detect.dictionary',
             'detect.contacts','properties.contacts','text.replace','setclipboard') and 'WFInput' not in p:
        problems.append((n,'missing WFInput for '+aid))
    if aid=='setvariable':
        if not p.get('WFVariableName'):problems.append((n,'blank variable name'))
        defined.add(p.get('WFVariableName',''))
    if aid=='choosefromlist':
        if not p.get('WFChooseFromListActionPrompt'):problems.append((n,'missing menu prompt'))
    if aid=='conditional' and p.get('WFControlFlowMode')==0:
        if not isinstance(p.get('WFCondition'),int) or p.get('WFInput',{}).get('Type')!='Variable':
            problems.append((n,'invalid If configuration'))
        if p.get('WFCondition') in (4,5,8,9,99) and 'WFConditionalActionString' not in p:
            problems.append((n,'missing If comparison'))
        if p.get('WFCondition')==4 and p.get('WFConditionalActionString') in ('','\n'):
            problems.append((n,'blank visual If comparison'))
    mode=p.get('WFControlFlowMode');gid=p.get('GroupingIdentifier')
    if mode==0:stack.append((aid,gid))
    elif mode==2:
        if not stack or stack.pop()!=(aid,gid):problems.append((n,'mismatched flow group'))
    if aid=='repeat.each' and mode==0 and 'WFInput' not in p:
        problems.append((n,'blank repeat input'))
if stack:problems.append(('EOF','unclosed groups'))
required={'Catalog','SubmenuMap','OptionMap','CodeMap','Cache','MainContacts','Main','Picked','Candidate'}
if not required.issubset(defined):problems.append(('names','missing '+str(required-defined)))
if types['is.workflow.actions.choosefromlist']!=3:problems.append(('flow','expected three menus'))
if types['is.workflow.actions.setclipboard']!=1:problems.append(('flow','expected one clipboard action'))
if types['is.workflow.actions.conditional']<12:problems.append(('flow','missing branch flow'))
if problems:raise AssertionError(problems)
print(json.dumps({'status':'PASS','actions':len(actions),'action_ids':dict(types),'named_vars':len(defined)},ensure_ascii=False))
