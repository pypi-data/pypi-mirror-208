import time
import httpx
import asyncio
import json
from suap_scraper.config import *
from suap_scraper import SUAP

arq = ''
with open('./boletim.json', 'r') as f:
  arq = f.read()

boletim = json.loads(arq)
ref = json.loads(arq)

async def get_session():
  suap = SUAP()
  await suap.loginSessionId('ijsjqch7apws19x5m3mworasxtrtxi78')
  return suap.session

async def get_urls(session):
  links = []
  for materia, etapas in ref.items():
    for sigla_etapa, avaliacoes in etapas.items():
      res = await session.get(LINK_SUAP + avaliacoes)
      links.append(LINK_SUAP + avaliacoes)
  return links

async def subgerador(link, session):
  link, id = link
  response = await session.get(link)
  print(response, id)
  return response, id

async def resolve_urls():
  global inicio
  session = await get_session()
  links = await get_urls(session)
  links = zip(links, [int(i) for i in range(len(links))])
  return await asyncio.gather(*[subgerador(link, session) for link in links])

inicio = time.time()
asyncio.run(resolve_urls())
fim = time.time()
print(f'{(fim - inicio):.2f}s')
