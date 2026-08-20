import os
import json
SP = os.environ.get("EZ_DUMP_DIR", ".")
u = json.load(open(SP+'/dump/user.json', encoding='utf-8'))
f = json.load(open(SP+'/dump/factory.json', encoding='utf-8'))

IGNORE_SUBSTR = ('filepath','directory','temporary_directory','font_directory','texture_directory',
                 'sound_directory','render_output_directory','script_directory','i18n_branches',
                 'render_cache_directory','asset_libraries','memory_cache_limit','recent_files',
                 'version','is_dirty','active_section','gl_texture_limit','solid_lights',
                 'light_ambient','sequencer_disk_cache')

def flatten(d, prefix=''):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            key = prefix + '.' + k if prefix else k
            if isinstance(v, dict):
                out.update(flatten(v, key))
            else:
                out[key] = v
    else:
        out[prefix] = d
    return out

SECTIONS = ['view','edit','inputs','keymap','system','apps','experimental','root','walk_navigation']
diffs = []
for sec in SECTIONS:
    fu, ff = flatten(u.get(sec, {}), sec), flatten(f.get(sec, {}), sec)
    for k in sorted(set(fu) | set(ff)):
        if any(s in k for s in IGNORE_SUBSTR):
            continue
        a, b = fu.get(k, '<absent>'), ff.get(k, '<absent>')
        if isinstance(a, float) and isinstance(b, float):
            if abs(a-b) < 1e-6: continue
        if a != b:
            diffs.append((k, b, a))

print("="*104)
print("PREFERENCE DIFFS  (%d)   [ path | FACTORY | YOURS ]" % len(diffs))
print("="*104)
for k, fac, usr in diffs:
    print("%-58s %-20s -> %s" % (k, json.dumps(fac), json.dumps(usr)))

print()
print("="*104); print("ADDONS ENABLED"); print("="*104)
fmods = {a['module'] for a in f['addons']}
for a in u['addons']:
    mark = ' ' if a['module'] in fmods else '+'
    print(" %s %s" % (mark, a['module']))
    if 'preferences' in a and a['preferences']:
        fa = next((x for x in f['addons'] if x['module']==a['module']), None)
        fp = flatten(fa.get('preferences', {})) if fa else {}
        up = flatten(a['preferences'])
        for k in sorted(up):
            if up[k] != fp.get(k, '<absent>'):
                print("        %-46s %-18s -> %s" % (k, json.dumps(fp.get(k,'<absent>')), json.dumps(up[k])))
print()
print("factory-only addons (you disabled):")
for m in sorted(fmods - {a['module'] for a in u['addons']}):
    print("  - %s" % m)
print()
print("theme:", u.get('theme_preset'), " | factory:", f.get('theme_preset'))
print("keyconfig active:", u.get('keyconfig_active_name'), "| names:", u.get('keyconfig_names'))
print()
print("extension repos:"); print(json.dumps(u.get('extension_repos'), indent=1))
