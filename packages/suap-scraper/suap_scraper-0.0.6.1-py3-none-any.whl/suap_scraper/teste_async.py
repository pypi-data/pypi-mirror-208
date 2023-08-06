from suap_scraper import SUAP
from time import time
import asyncio
import json
from config import *

async def main():
  start = time()

  suap = SUAP()
  await suap.loginSessionId("wxc4zuiri4grbvsnrpwss8a7xo9d85nn")
  boletim = await suap.getBoletim()

  end = time()
  with open('./boletim.json', 'w') as f:
    f.write(boletim)
  print(f"{(end - start):.2f}s")


arq = ''
with open('./boletim.json', 'r') as f:
  arq = f.read()
boletim = json.loads(arq)

links = []
for materia, etapas in boletim.items():
  links.extend(etapas.values())
links = [LINK_SUAP + i for i in links]

async def pegar_detalhar(link, session):
  global res
  r = await session.get(link)
  res.append(r.text)
  return

async def main2():
  suap = SUAP()
  await suap.loginSessionId("wxc4zuiri4grbvsnrpwss8a7xo9d85nn")
  session = suap.session
  res = []
  tasks = []
  for link in links:
    tasks.append(pegar_detalhar(link, session))
  await asyncio.gather(*tasks)
asyncio.run(main2())

