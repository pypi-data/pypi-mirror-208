from SUAP import SUAP
from time import time
import asyncio

async def main():

  suap = SUAP()
  await suap.loginSessionId("ijsjqch7apws19x5m3mworasxtrtxi78")
  boletim = await suap.getBoletim()
  print(boletim)


start = time()
asyncio.run(main())
end = time()
print(f"{(end - start):.2f}s")
