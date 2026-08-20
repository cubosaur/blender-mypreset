import bpy, json, os
OUT=os.environ['DUMP_OUT']; XML=os.environ['THEME_XML']
bpy.ops.script.execute_preset(filepath=XML, menu_idname="USERPREF_MT_interface_theme_presets")
def walk(s, depth=6, seen=frozenset()):
    if depth<=0: return '<<depth>>'
    out={}
    try: props=s.bl_rna.properties
    except Exception: return str(s)
    for p in props:
        if p.identifier=='rna_type': continue
        try: v=getattr(s,p.identifier)
        except Exception: continue
        if p.type=='POINTER':
            out[p.identifier]=None if v is None else ('<<cycle>>' if id(v) in seen else walk(v,depth-1,seen|{id(v)}))
        elif p.type=='COLLECTION':
            out[p.identifier]=[walk(i,depth-1,seen) for i in v] if len(v)<60 else '<<big>>'
        elif getattr(p,'is_array',False):
            out[p.identifier]=[round(float(x),4) if isinstance(x,float) else x for x in v]
        elif p.type=='FLOAT': out[p.identifier]=round(float(v),4)
        else: out[p.identifier]=v
    return out
json.dump({'name':bpy.context.preferences.themes[0].name,'theme':walk(bpy.context.preferences.themes[0])}, open(OUT,'w',encoding='utf-8'), indent=1, default=str)
print('WROTE',OUT)
