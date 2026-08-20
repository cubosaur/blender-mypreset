import bpy, json, sys, os

OUT = os.environ.get("DUMP_OUT")

SKIP_TYPES = {'POINTER'}

def ser_prop(owner, prop, depth, path, seen):
    pid = prop.identifier
    try:
        val = getattr(owner, pid)
    except Exception as e:
        return "<<err %s>>" % e
    t = prop.type
    if t == 'COLLECTION':
        return "<<collection len=%d>>" % len(val)
    if t == 'POINTER':
        if val is None:
            return None
        if depth <= 0:
            return "<<ptr depth>>"
        key = id(val)
        if key in seen:
            return "<<cycle>>"
        seen = seen | {key}
        return walk(val, depth - 1, path + "." + pid, seen)
    if getattr(prop, "is_array", False):
        try:
            return list(val)
        except Exception:
            return str(val)
    if t == 'ENUM' and getattr(prop, 'is_enum_flag', False):
        try:
            return sorted(val)
        except Exception:
            return str(val)
    if t in ('STRING', 'ENUM', 'BOOLEAN', 'INT', 'FLOAT'):
        if t == 'FLOAT':
            try:
                return round(float(val), 6)
            except Exception:
                return str(val)
        return val
    return str(val)

def walk(struct, depth, path, seen=frozenset()):
    out = {}
    try:
        props = struct.bl_rna.properties
    except Exception:
        return str(struct)
    for prop in props:
        if prop.identifier == 'rna_type':
            continue
        out[prop.identifier] = ser_prop(struct, prop, depth, path, seen)
    return out

prefs = bpy.context.preferences

data = {}
data['blender_version'] = bpy.app.version_string
data['factory'] = '--factory-startup' in sys.argv

# --- Preferences top-level sub-structs ---
for section in ('view', 'edit', 'inputs', 'keymap', 'system', 'filepaths', 'apps', 'experimental'):
    try:
        sub = getattr(prefs, section)
        data[section] = walk(sub, 3, section)
    except Exception as e:
        data[section] = "<<err %s>>" % e

# scalar prefs on the root
root = {}
for prop in prefs.bl_rna.properties:
    if prop.identifier == 'rna_type':
        continue
    if prop.type in ('POINTER', 'COLLECTION'):
        continue
    root[prop.identifier] = ser_prop(prefs, prop, 0, 'prefs', frozenset())
data['root'] = root

# --- Studio lights / walk nav ---
try:
    data['walk_navigation'] = walk(prefs.inputs.walk_navigation, 2, 'walk')
except Exception:
    pass

# --- Addons ---
addons = []
for a in prefs.addons:
    entry = {'module': a.module}
    try:
        p = a.preferences
        if p is not None:
            entry['preferences'] = walk(p, 2, 'addon.' + a.module)
    except Exception as e:
        entry['preferences_err'] = str(e)
    addons.append(entry)
data['addons'] = sorted(addons, key=lambda x: x['module'])

# --- Themes (name + selected non-default hints) ---
try:
    data['theme_preset'] = prefs.themes[0].name if len(prefs.themes) else None
except Exception:
    pass

# --- Extension repos ---
repos = []
try:
    for r in prefs.extensions.repos:
        repos.append({k: getattr(r, k) for k in ('name','module','directory','remote_url','enabled','use_remote_url','use_custom_directory','source') if hasattr(r, k)})
except Exception as e:
    repos = ["<<err %s>>" % e]
data['extension_repos'] = repos

# --- Keymap dump ---
wm = bpy.context.window_manager
try:
    bpy.utils.keyconfig_init()
except Exception as e:
    print('keyconfig_init err', e)
kcs = wm.keyconfigs

def kmi_dict(kmi):
    d = {
        'idname': kmi.idname,
        'type': kmi.type,
        'value': kmi.value,
        'ctrl': kmi.ctrl, 'alt': kmi.alt, 'shift': kmi.shift, 'oskey': kmi.oskey,
        'any': kmi.any,
        'key_modifier': kmi.key_modifier,
        'active': kmi.active,
        'map_type': kmi.map_type,
        'repeat': kmi.repeat,
        'is_user_defined': kmi.is_user_defined,
        'is_user_modified': kmi.is_user_modified,
        'id': kmi.id,
        'name': kmi.name,
    }
    for extra in ('direction', 'ctrl_ui', 'alt_ui', 'shift_ui', 'oskey_ui', 'hyper'):
        if hasattr(kmi, extra):
            try:
                d[extra] = getattr(kmi, extra)
            except Exception:
                pass
    props = {}
    try:
        p = kmi.properties
        if p is not None:
            for prop in p.bl_rna.properties:
                if prop.identifier == 'rna_type':
                    continue
                if p.is_property_set(prop.identifier):
                    props[prop.identifier] = ser_prop(p, prop, 1, 'kmiprop', frozenset())
    except Exception as e:
        props['<<err>>'] = str(e)
    d['properties'] = props
    return d

def dump_kc(kc):
    o = []
    for km in kc.keymaps:
        entry = {
            'name': km.name,
            'space_type': km.space_type,
            'region_type': km.region_type,
            'is_modal': km.is_modal,
            'is_user_modified': km.is_user_modified,
            'items': [kmi_dict(k) for k in km.keymap_items],
        }
        o.append(entry)
    return o

data['keyconfig_active_name'] = kcs.active.name if kcs.active else None
data['keyconfig_names'] = [k.name for k in kcs]
data['keymap_user'] = dump_kc(kcs.user)
try:
    data['keymap_default'] = dump_kc(kcs.default)
except Exception as e:
    data['keymap_default_err'] = str(e)

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=1, default=str)
print("WROTE", OUT)
