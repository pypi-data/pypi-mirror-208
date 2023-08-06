import json


def mensagem_formatada(novas_notas):
  symbols =['$insert', '$delete', '$update', '$replace']
  avaliacoes_dic = {'A1': 'Avaliação 1', 'A2': 'Avaliação 2', 'A3': 'Avaliação 3', 'A4': 'Avaliação 4', 'RE': 'Recuperação'}
  msg = ''
  quant_disciplinas = len(novas_notas.keys())
  msg += f'Há novas notas em {quant_disciplinas} disciplina(s)\n\n'
  for disciplina, etapas in novas_notas.items():
    msg += ' '.join(disciplina.split()[1::])
    for sigla_etapa, avaliacoes in etapas.items():
      if avaliacoes is None:
        continue
      primeira_chave = list(avaliacoes.keys())[0]
      if primeira_chave in symbols:
        avaliacoes = avaliacoes[primeira_chave]
      notas = avaliacoes.values()
      quant_notas = len(notas) - list(notas).count(None)
      msg += f' -> {quant_notas} nova(s) nota(s) inserida(s)\n'
      for sigla_av, nota in avaliacoes.items():
        if nota is None:
          continue
        msg += f'{avaliacoes_dic[sigla_av]}: {nota}\n'
    msg += '\n'
  return msg
