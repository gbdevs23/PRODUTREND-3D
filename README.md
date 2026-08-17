# Agente diário de produtos imprimíveis em 3D

## O que ele faz

**`descobrir_produtos_3d.py`** — roda sozinho, 1x por dia, sem você digitar nada:
- Puxa buscas "em ascensão" no Google Trends Brasil dentro de categorias
  tipicamente imprimíveis em 3D (organizadores, suportes, ganchos, vasos,
  chaveiros, miniaturas, acessórios pet, itens de escritório etc).
- Filtra por palavras que indicam "isso dá pra imprimir em 3D" e descarta o
  que normalmente não dá (eletrônicos com bateria, líquidos, tecido, comida).
- Compara com o histórico e separa o que é **novo** desde a última execução.
- Salva tudo em `historico_candidatos.csv` (acumulado) e
  `candidatos_AAAA-MM-DD.csv` (snapshot do dia).

**`calcular_margem_3d.py`** — roda na mão, quando você quiser avaliar os
candidatos do dia:
- Pega o `candidatos_AAAA-MM-DD.csv` mais recente.
- Pergunta peso da peça, horas de impressão, preço de filamento e preço de
  venda pretendido — calcula custo de produção e margem já descontando a
  taxa da plataforma (ML, Shopee ou loja própria).
- Salva o ranking em `margem_AAAA-MM-DD.csv`.

## Instalar

```bash
pip install -r requirements.txt --break-system-packages
```

## Agendar para rodar 1x por dia SEM precisar da sua máquina ligada (GitHub Actions)

Isso roda no servidor do GitHub, de graça, mesmo com seu PC desligado.

**Passo a passo:**

1. Crie um repositório novo no GitHub (pode ser privado) — ex: `produtos-3d`.
2. Suba esta pasta inteira pra ele:
   ```bash
   cd product_finder
   git init
   git add .
   git commit -m "Setup inicial do agente de produtos 3D"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/produtos-3d.git
   git push -u origin main
   ```
3. No GitHub, vá em **Settings → Actions → General → Workflow permissions**
   e marque **"Read and write permissions"**. (Sem isso o workflow não
   consegue salvar os resultados de volta no repositório.)
4. Pronto. O workflow em `.github/workflows/descobrir_produtos_diario.yml`
   já está configurado pra rodar todo dia às 8h (horário de Brasília).
   Você pode testar na hora sem esperar o agendamento: vá na aba **Actions**
   do repositório → escolha o workflow → **"Run workflow"**.

**Onde ver os resultados:** depois de cada execução, o próprio workflow
commita `historico_candidatos.csv` e `candidatos_AAAA-MM-DD.csv` de volta no
repositório. Você abre o repositório (site ou app do GitHub no celular) e
olha esses arquivos — não precisa estar na sua máquina.

**Ajustar o horário:** edite a linha `cron: '0 11 * * *'` no arquivo do
workflow. O GitHub Actions usa horário UTC, então "0 11" = 8h de Brasília
(UTC-3). Um site como crontab.guru ajuda a montar outros horários.

### Alternativa local (se preferir não usar GitHub)

**Linux/Mac (cron):**
```bash
crontab -e
```
```
0 8 * * * cd /caminho/para/product_finder && /usr/bin/python3 descobrir_produtos_3d.py >> log_diario.txt 2>&1
```

**Windows (Agendador de Tarefas):** crie uma Tarefa Básica com gatilho
"Diariamente", ação "Iniciar um programa" → `python`, argumento
`descobrir_produtos_3d.py`, pasta inicial a do projeto. Essa opção exige
que o PC esteja ligado no horário agendado — por isso o GitHub Actions é
melhor se você quer independência da sua máquina.

## Fluxo do dia a dia

1. O agendador já rodou de manhã sozinho.
2. Você abre `historico_candidatos.csv` (ou o `log_diario.txt`) e olha o que
   entrou de novo.
3. Quando achar algo interessante, roda:
   ```bash
   python3 calcular_margem_3d.py
   ```
   pra ver se a margem compensa antes de modelar/imprimir.

## Limitações honestas

- **O filtro "parece imprimível em 3D" é uma lista de palavras**, não uma
  análise real do produto. Vai deixar passar ruído e pode descartar ideia
  boa com nome fora do padrão — trate como triagem, não veredito.
- **Não faz scraping de ML/Shopee.** Continua sendo manual checar quantos
  concorrentes já vendem a peça antes de investir tempo modelando.
- **A margem depende 100% dos números que você digita** (peso, horas de
  impressão, preço do filamento) — não tem como automatizar isso sem você
  ter pelo menos uma ideia aproximada da peça.
- **Google Trends pode bloquear** se rodar consultas demais muito rápido —
  o script já espera 2s entre categorias; se aparecer erro de "quota",
  espere um pouco e rode de novo.
