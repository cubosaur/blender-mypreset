import os
import json, sys
SP = os.environ.get("EZ_DUMP_DIR", ".")
u = json.load(open(SP+'/dump/user.json', encoding='utf-8'))

MODS = (('ctrl','Ctrl'),('alt','Alt'),('shift','Shift'),('oskey','OS'))
def combo(it):
    parts = [n for k,n in MODS if it.get(k)]
    if it.get('any'): parts = ['Any']
    t = it['type']
    if it.get('key_modifier') and it['key_modifier'] != 'NONE':
        t = it['key_modifier'] + ' ' + t
    return ('+'.join(parts + [t])) + (' ('+it['value']+')' if it['value'] not in ('PRESS',) else '')

# Flags: is_user_defined => added by user; is_user_modified => default item changed
added, modified, disabled = [], [], []
for km in u['keymap_user']:
    for it in km['items']:
        rec = dict(it); rec['_km'] = km['name']; rec['_space'] = km['space_type']; rec['_region'] = km['region_type']
        if not it['active']:
            disabled.append(rec)
        elif it['is_user_defined']:
            added.append(rec)
        elif it['is_user_modified']:
            modified.append(rec)

# For modified/disabled items, find the factory counterpart by id within same keymap
f = json.load(open(SP+'/dump/factory.json', encoding='utf-8'))
fac = {}
for km in f['keymap_user']:
    for it in km['items']:
        fac.setdefault((km['name'], it['id']), it)
facd = {}
for km in f['keymap_default']:
    for it in km['items']:
        facd.setdefault((km['name'], it['id']), it)

def factory_of(rec):
    k = (rec['_km'], rec['id'])
    return fac.get(k) or facd.get(k)

def show(rec, tag):
    fo = factory_of(rec)
    line = "  [%s] %-22s | %-30s -> %s" % (tag, rec['_km'], combo(rec), rec['idname'] or '<'+rec['map_type']+'>')
    if rec['properties']:
        line += "  " + json.dumps(rec['properties'])
    print(line)
    if fo is not None:
        fline = "        factory: %-30s -> %s" % (combo(fo), fo['idname'] or '<'+fo['map_type']+'>')
        if fo['properties']:
            fline += "  " + json.dumps(fo['properties'])
        print(fline)
    else:
        print("        factory: <not found by id>")

print("="*100); print("USER-ADDED KEYMAP ITEMS (%d)" % len(added)); print("="*100)
for r in sorted(added, key=lambda x:(x['_km'], x['type'])): show(r, 'ADD')
print(); print("="*100); print("MODIFIED DEFAULT ITEMS (%d)" % len(modified)); print("="*100)
for r in sorted(modified, key=lambda x:(x['_km'], x['type'])): show(r, 'MOD')
print(); print("="*100); print("DISABLED ITEMS (%d)" % len(disabled)); print("="*100)
for r in sorted(disabled, key=lambda x:(x['_km'], x['type'])): show(r, 'OFF')
