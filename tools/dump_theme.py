import bpy, json, os
OUT = os.environ['DUMP_OUT']
def walk(s, depth=6, seen=frozenset()):
    if depth <= 0: return '<<depth>>'
    out = {}
    try: props = s.bl_rna.properties
    except Exception: return str(s)
    for p in props:
        if p.identifier == 'rna_type': continue
        try: v = getattr(s, p.identifier)
        except Exception: continue
        if p.type == 'POINTER':
            if v is None: out[p.identifier] = None
            elif id(v) in seen: out[p.identifier] = '<<cycle>>'
            else: out[p.identifier] = walk(v, depth-1, seen | {id(v)})
        elif p.type == 'COLLECTION':
            out[p.identifier] = [walk(i, depth-1, seen) for i in v] if len(v) < 60 else '<<big>>'
        elif getattr(p, 'is_array', False):
            out[p.identifier] = [round(float(x),4) if isinstance(x,float) else x for x in v]
        elif p.type == 'FLOAT':
            out[p.identifier] = round(float(v), 4)
        else:
            out[p.identifier] = v
    return out
th = bpy.context.preferences.themes[0]
data = {'name': th.name, 'theme': walk(th)}
# also grab per-addon prefs that we may have missed
prefs = bpy.context.preferences
ad = {}
for a in prefs.addons:
    try:
        if a.preferences is not None:
            ad[a.module] = walk(a.preferences, 4)
    except Exception as e:
        ad[a.module] = str(e)
data['addon_prefs'] = ad
# keyconfig preferences
try:
    bpy.utils.keyconfig_init()
except Exception: pass
kcp = {}
for kc in bpy.context.window_manager.keyconfigs:
    try:
        p = kc.preferences
        kcp[kc.name] = walk(p, 3) if p else None
    except Exception as e:
        kcp[kc.name] = str(e)
data['keyconfig_prefs'] = kcp
json.dump(data, open(OUT,'w',encoding='utf-8'), indent=1, default=str)
print('WROTE', OUT)
