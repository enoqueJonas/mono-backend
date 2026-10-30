from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from collections import Counter
from lxml import etree
from PIL import Image, ImageDraw, ImageFont
import hashlib, os

SRC=Path('/mnt/data/Monografia_Canonica_Ilustracoes_Auditadas_30102026.docx')
DST=Path('/mnt/data/Monografia_Canonica_Terminologia_Visual_Uniformizada_30102026.docx')
OUT=Path('/mnt/data/mono_term_qa');OUT.mkdir(exist_ok=True)

R={
  'word/document.xml':{
   'Importa distinguir a cifragem simétrica, a criptografia assimétrica, as assinaturas digitais e as funções hash:':
   'Importa distinguir a cifragem (simétrica ou assimétrica), as assinaturas digitais e as funções hash:',
   'Colecta': 'Recolha',
  },
  'word/diagrams/data4.xml':{'Wallets':'Carteiras digitais'},
  'word/diagrams/drawing4.xml':{'Wallets':'Carteiras digitais'},
  'word/diagrams/data8.xml':{'Colecta e/ou refinamento de requisitos':'Recolha e refinamento de requisitos'},
  'word/diagrams/drawing8.xml':{'Colecta e/ou refinamento de requisitos':'Recolha e refinamento de requisitos'},
}

def patch_xml(raw, replacements):
  root=etree.fromstring(raw)
  counts=Counter()
  for t in root.xpath('//*[local-name()="t"]'):
    if t.text:
      for old,new in replacements.items():
        if old in t.text:
          t.text=t.text.replace(old,new)
          counts[old]+=1
  missing=set(replacements)-set(counts)
  if missing:raise RuntimeError(f'Missing text {missing}')
  # Repair one redundant REF field discovered during visual QA: the page 41
  # intro already hard-coded "A Figura 2.7.2" and an automatic REF was
  # attached after "etapas:", producing "etapas:2.7.2" in PDF.
  # Relocate the *existing* field into the sentence, rather than deleting it.
  if 'Colecta' in replacements:
    hits=[]
    for p in root.xpath('//*[local-name()="p"]'):
      ts=p.xpath('./*[local-name()="r"]/*[local-name()="t"]')
      if not ts or not (ts[0].text or '').startswith('A Figura 2.7.2 sintetiza um ciclo'):
        continue
      intro='A Figura 2.7.2 sintetiza um ciclo possível de prototipagem, composto pelas seguintes etapas:'
      assert ts[0].text==intro
      refs=[t for t in p.xpath('./*[local-name()="r"]/*[local-name()="instrText"]') if 'MonoRefF_2_7_2' in (t.text or '')]
      assert len(refs)==1
      assert len(ts)==3
      ts[0].text='A Figura '
      ts[1].text='2.7.2'    # cached field result
      ts[2].text=' sintetiza um ciclo possível de prototipagem, composto pelas seguintes etapas:'
      ts[2].set('{http://www.w3.org/XML/1998/namespace}space','preserve')
      hits.append(p)
    assert len(hits)==1, len(hits)
    counts['repaired_REFs']=1
  return etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True),dict(counts)

with ZipFile(SRC) as i:
  original=Image.open(BytesIO(i.read('word/media/image4.png'))).convert('RGBA')
  assert original.size==(1900,780)
  # The title is the only image element being changed. Recreate it using
  # the font, size, alignment and colour specified in the authored SVG.
  d=ImageDraw.Draw(original)
  bg=original.getpixel((0,0))
  d.rectangle((0,0,1899,83), fill=bg)
  title='CRIPTOGRAFIA SIMÉTRICA'
  ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',57)
  bbox=d.textbbox((0,0),title,font=ft)
  # SVG baseline y=72, PIL drawing coordinates adjusted by glyph bbox:
  x=(1900-(bbox[2]-bbox[0]))/2-bbox[0]
  y=28-bbox[1]
  d.text((x,y),title,fill='#15394E',font=ft)
  assert d.textbbox((x,y),title,font=ft)[2]<1850
  b=BytesIO();original.save(b,format='PNG',compress_level=6)
  new_image=b.getvalue()
  original.save(OUT/'figure_233_title_fixed.png')
  patched={}
  with ZipFile(DST,'w') as o:
    for it in i.infolist():
      raw=i.read(it.filename)
      if it.filename=='word/media/image4.png':
        raw=new_image
        patched[it.filename]={'change':'title only','from':'CIFRAGEM SIMÉTRICA','to':title}
      elif it.filename in R:
        raw,changes=patch_xml(raw,R[it.filename]);patched[it.filename]=changes
      o.writestr(it,raw)

with ZipFile(SRC) as a, ZipFile(DST) as b:
  assert b.testzip() is None
  assert set(a.namelist())==set(b.namelist())
  different={x for x in b.namelist() if a.read(x)!=b.read(x)}
  assert different==set(patched)
  assert len([x for x in b.namelist() if x.startswith('word/media/')])==len([x for x in a.namelist() if x.startswith('word/media/')])
  for term in ['SEQ','REF','TOC']:
    assert a.read('word/document.xml').count((' '+term+' ').encode())==b.read('word/document.xml').count((' '+term+' ').encode())
  # Captions and the figure-list cache must remain exactly correct.
  from docx import Document
  from io import BytesIO
  doc=Document(BytesIO(b.read('word/document.xml')) if False else DST)
  caps=[p.text for p in doc.paragraphs if p.style.name=='CaptionFigura' and p.text.startswith('Figura')]
  assert len(caps)==43, len(caps)
  assert any('Figura 2.3.3 Criptografia simétrica' in p for p in caps)
  assert any('Figura 2.3.4 Criptografia assimétrica' in p for p in caps)
  assert not any('Figura 2.3.4 Criptografia simétrica' in p for p in caps)

print('OUT',str(DST))
print('SHA',hashlib.sha256(DST.read_bytes()).hexdigest())
print('PARTS',list(patched))
print('PATCHES',patched)
print('SIZE',DST.stat().st_size)