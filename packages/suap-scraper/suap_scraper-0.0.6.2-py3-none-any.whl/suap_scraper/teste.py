from SUAP import SUAP
from time import time
import asyncio

async def main():

  suap = SUAP()
  try:
    suap.matricula = '202010040036'
    await suap.loginSessionId("ybb3t58iqwjbpmmgiejyb29v205ldtda")
    boletim = await suap.getBoletim()
    print(boletim)
  finally:
    await suap.session.aclose()


start = time()
asyncio.run(main())
end = time()
print(f"{(end - start):.2f}s")
