from suap_scraper import SUAP
import os
import sys
import json
import jsondiff
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()
boletim_salvo = ''
with open('./boletim.json', 'r') as f:
  boletim_salvo = f.read()
session_id = os.getenv("SUAP_SESSION_ID")
suap = SUAP()
suap.loginSessionId(session_id)
novo_boletim = suap.getBoletim()
novas_notas = jsondiff.diff(boletim_salvo, novo_boletim, load=True, dump=False, marshal=True)

if not novas_notas:
  print('Sem novas notas!')
  sys.exit()

print(novas_notas)
"""
diferenca = json.dumps(novas_notas)
print(diferenca)

message = Mail(
    from_email='cavalcante@jao42.dev.br',
    to_emails='cavalcante.joao@protonmail.ch',
  subject='Nova nota postada!',
    html_content = diferenca)
try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)
"""
