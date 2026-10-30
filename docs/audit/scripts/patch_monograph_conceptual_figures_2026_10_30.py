"""Remove non-diagrammatic footnotes and make all conceptual graphics concise.

Base is the last confirmed 156-page canonical before the previous overbroad masks;
only image media and native SmartArt text are touched. No document XML mutation.
"""
from collections import Counter
from io import BytesIO
from lxml import etree
from PIL import Image, ImageDraw
from zipfile import ZipFile
import hashlib
import os

BASE='/mnt/data/Monografia_Canonica_Telas_Reorganizadas_30102026.docx'
OUT='/mnt/data/Monografia_Canonica_Ilustracoes_Auditadas_30102026.docx'
# Carefully measured footer-only pixels, outside diagrams themselves.
MASKS={
 'image2.png':(0,651,1200,740),
 'image3.png':(0,745,1800,870),
 'image4.png':(0,630,1900,780),
 'image5.png':(0,703,1900,800),
 'image6.png':(0,404,1920,520),
 'image7.png':(0,372,1920,465),
 'image8.png':(0,757,940,930),
 'image9.png':(0,757,940,930),
 'image10.png':(0,632,1200,742),
}
SMARTART={
  1:{
    'Pelo menos 2 membros, sejam amigos, familiares ou outros, unem-se com base na confiança.':'Os participantes constituem um grupo com regras acordadas.',
    'Estabelecimento de um valor a contribuir por membro, mediante voto, e a frequência de contribuição que pode ser diária, semanal, quinzenal, mensal, trimestral ou outra.':'Definição conjunta do valor e da periodicidade das contribuições.',
    'A cada período previamente determinado, um membro recebe o montante total arrecadado.':'Em cada ciclo, um membro recebe o montante acordado.',
  },
  2:{
    'Transparência e imutabilidade do registo':'Auditabilidade de registos confirmados',
    'Criptografia e consenso distribuído':'Validação segundo regras de consenso',
    'Redução de intermediários e custos':'Partilha de registos entre entidades',
    'Integridade permanente dos dados':'Detecção de alterações posteriores',
    'Privacidade reduzida e exposição pública':'Riscos de exposição de dados',
    'Vulnerabilidade a ataques 51% em redes pequenas':'Riscos de concentração da validação',
    'Escalabilidade limitada em redes públicas':'Limitações de desempenho e escala',
    'Consumo energético elevado (PoW)':'Custos energéticos de PoW',
  },
  4:{
    'Registo opcional que pode apoiar a verificação conforme o método DID':'Apoia a verificação conforme o método DID',
    'Declarações com mecanismos de autenticidade e integridade, não necessariamente cifradas':'Declarações assinadas e verificáveis',
    'Aplicação que pode permitir ao titular gerir e apresentar credenciais verificáveis':'Gestão e apresentação de credenciais',
  },
  6:{
    'Identificadores e credenciais verificáveis podem apoiar a emissão de comprovativos de contribuições em grupos de Xitique. As provas criptográficas detectam determinadas alterações posteriores, mas não garantem que o pagamento declarado tenha ocorrido.':'Comprovativos verificáveis; não comprovam a ocorrência do pagamento.',
    'Provas criptográficas podem facilitar auditorias dos registos e detectar alterações posteriores. A qualidade dos dados de origem e a responsabilidade pelos registos continuam essenciais.':'Detecção de alterações posteriores, dependente de registos de origem fiáveis.',
    'Um histórico digital pode documentar a participação dos membros e ser apresentado a terceiros. A aceitação por bancos ou outras instituições depende de critérios de confiança e acordos ainda não avaliados neste estudo.':'Histórico contributivo consultável; aceitação externa não demonstrada.',
    'DIDs e credenciais podem apoiar trocas de informação entre sistemas compatíveis. No protótipo, a confirmação de pagamentos por carteira móvel foi simulada; não houve ligação real a M-Pesa ou e-Mola.':'Partilha entre sistemas compatíveis; pagamentos móveis apenas simulados.',
  },
  7:{
    'Protótipo descartável: usado para explorar uma ideia ou requisito; o código pode ser descartado após a avaliação.':'Descartável: explora requisitos sem integrar necessariamente o sistema final.',
    'Protótipo evolutivo: refinado e ampliado em iterações, podendo servir de base ao sistema final.':'Evolutivo: refinado em iterações até poder integrar o sistema final.',
    'Baixa fidelidade: ':'Baixa fidelidade: esboços de estrutura e navegação.',
    'esboços simples para explorar estrutura, fluxos e navegação com poucos recursos.':'',
    'Alta fidelidade: protótipos detalhados que simulam o ':'Alta fidelidade: representação detalhada da interface e da interacção.',
    'look and feel':'',
    ' e a interactividade':'',
    ' da interface; permitem avaliar aspectos da ':'',
    'experiência do utilizador':'',
    ' (UX).':'',
  },
}

def patch_xml(raw, repl):
    root=etree.fromstring(raw)
    counter=Counter()
    for el in root.iter():
        if etree.QName(el).localname=='t' and el.text in repl:
            counter[el.text]+=1
            el.text=repl[el.text]
    misses=set(repl)-set(counter)
    if misses:raise ValueError('Missing texts: '+repr(misses))
    return etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True),counter

changed=[]
with ZipFile(BASE,'r') as inp, ZipFile(OUT,'w') as out:
    for it in inp.infolist():
        raw=inp.read(it.filename)
        bn=os.path.basename(it.filename)
        if it.filename.startswith('word/media/') and bn in MASKS:
            im=Image.open(BytesIO(raw)).convert('RGBA')
            rect=MASKS[bn]
            assert rect[2:] == im.size, (bn,rect,im.size)
            bg=im.getpixel((0,0))
            ImageDraw.Draw(im).rectangle((rect[0],rect[1],rect[2]-1,rect[3]-1),fill=bg)
            buf=BytesIO();im.save(buf,format='PNG');raw=buf.getvalue();changed.append(it.filename)
        elif it.filename=='word/media/image11.png':
            im=Image.open(BytesIO(raw)).convert('RGBA')
            # Background of trust-register box, *not* outer white page.
            fill=im.getpixel((800,735))
            ImageDraw.Draw(im).rectangle((275,825,1330,877),fill=fill)
            buf=BytesIO();im.save(buf,format='PNG');raw=buf.getvalue();changed.append(it.filename)
        else:
            for n,repl in SMARTART.items():
                if it.filename in (f'word/diagrams/data{n}.xml',f'word/diagrams/drawing{n}.xml'):
                    raw,cnt=patch_xml(raw,repl)
                    if it.filename=='word/diagrams/drawing6.xml':
                        root=etree.fromstring(raw)
                        n_centered=0
                        for t in root.xpath('//*[local-name()="t"]'):
                            if (t.text or '').startswith(('Comprovativos verificáveis','Detecção de alterações','Histórico contributivo','Partilha entre sistemas')):
                                parent=t
                                while parent is not None and etree.QName(parent).localname!='sp':parent=parent.getparent()
                                if parent is not None:
                                    bp=parent.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}bodyPr')
                                    bp.set('anchor','ctr');n_centered+=1
                        assert n_centered==4
                        raw=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
                    changed.append(it.filename)
                    break
        out.writestr(it,raw)
with ZipFile(OUT) as o:
    assert o.testzip() is None
    assert len(o.namelist())==len(ZipFile(BASE).namelist())
    actual=[p for p in o.namelist() if o.read(p)!=ZipFile(BASE).read(p)]
    assert sorted(actual)==sorted(changed)
    doc=o.read('word/document.xml')
    assert doc==ZipFile(BASE).read('word/document.xml')
    for term in (b'caption',b'comment'):pass
print('output',OUT)
print('sha256',hashlib.sha256(open(OUT,'rb').read()).hexdigest())
print('changed count',len(changed),changed)