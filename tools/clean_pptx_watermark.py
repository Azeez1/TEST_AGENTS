import zipfile, shutil, re, os, sys
from lxml import etree

src = r'C:\Users\sabaa\Downloads\The_$500K_Revenue_Blueprint_(3).pptx'
out = r'C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\social_media\natural_body_teardown_carousel.pptx'
tmp = out + '.tmp'

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
REL_EMBED = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
REL_LINK = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}link'
P_PIC = '{http://schemas.openxmlformats.org/presentationml/2006/main}pic'
A_BLIP = '{http://schemas.openxmlformats.org/drawingml/2006/main}blip'

removed_shapes = 0
removed_rels = set()
skipped_media = set()

with zipfile.ZipFile(src, 'r') as zin:
    names = zin.namelist()
    slide_names = [n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n)]
    slide_to_drop_rids = {}
    cleaned = {}

    for sn in slide_names:
        tree = etree.fromstring(zin.read(sn))
        drop_rids = set()
        for pic in list(tree.iter(P_PIC)):
            cNvPr = pic.find('.//p:nvPicPr/p:cNvPr', NS)
            if cNvPr is not None and cNvPr.get('name', '').lower().startswith('audio'):
                for blip in pic.iter(A_BLIP):
                    for attr in (REL_EMBED, REL_LINK):
                        rid = blip.get(attr)
                        if rid:
                            drop_rids.add(rid)
                pic.getparent().remove(pic)
                removed_shapes += 1
        slide_to_drop_rids[sn] = drop_rids
        cleaned[sn] = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)

    cleaned_rels = {}
    media_to_drop = set()
    for sn, drop_rids in slide_to_drop_rids.items():
        if not drop_rids:
            continue
        rels_name = sn.replace('ppt/slides/', 'ppt/slides/_rels/') + '.rels'
        if rels_name not in names:
            continue
        rtree = etree.fromstring(zin.read(rels_name))
        for rel in list(rtree):
            rid = rel.get('Id')
            if rid in drop_rids:
                target = rel.get('Target', '')
                if target.startswith('../'):
                    media_path = 'ppt/' + target[3:]
                else:
                    media_path = target
                media_to_drop.add(media_path.replace('\\', '/'))
                rtree.remove(rel)
                removed_rels.add(rid)
        cleaned_rels[rels_name] = etree.tostring(rtree, xml_declaration=True, encoding='UTF-8', standalone=True)

    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            name = item.filename
            if name in media_to_drop:
                skipped_media.add(name)
                continue
            if name in cleaned:
                zout.writestr(item, cleaned[name])
            elif name in cleaned_rels:
                zout.writestr(item, cleaned_rels[name])
            else:
                zout.writestr(item, zin.read(name))

shutil.move(tmp, out)
print(f'Removed shapes: {removed_shapes}')
print(f'Removed rels:   {len(removed_rels)}')
print(f'Dropped media:  {len(skipped_media)}')
for m in sorted(skipped_media)[:5]:
    print(f'   - {m}')
print(f'Size: {os.path.getsize(out)/1024/1024:.1f} MB')
