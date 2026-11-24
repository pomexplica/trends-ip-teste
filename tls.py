"""Teste de variavel isolada: o 429 do explore do Google Trends depende da impressao digital TLS?
Mesmo IP (VPS). Fase 0: 3 palavras com urllib (linha de base). Fase 1: ate MAX palavras com curl_cffi
imitando o Chrome, sessao unica; para apos 5 falhas seguidas. Limite por codigo: MAX palavras."""
import sys, json, time, urllib.parse, urllib.request, http.cookiejar
from curl_cffi import requests as cr
MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 150
base = ("pix enem copa bitcoin iphone receita vacina futebol novela carnaval dolar inss fgts uber nubank shein "
        "tiktok chatgpt gasolina natal pascoa ferias praia chuva calor frio dengue gripe covid eleicao lula "
        "bolsonaro stf senado camara imposto salario emprego vaga curso faculdade sisu prouni fies concurso "
        "loteria megasena quina lotofacil flamengo palmeiras corinthians santos gremio cruzeiro atletico vasco "
        "botafogo fluminense neymar vinicius messi ronaldo formula1 ufc nba nfl tenis volei basquete netflix "
        "globoplay disney spotify youtube instagram whatsapp telegram twitter kwai shopee amazon mercadolivre "
        "magalu americanas casasbahia temu aliexpress ifood rappi nike adidas samsung motorola xiaomi playstation "
        "xbox nintendo minecraft roblox fortnite freefire gta fifa valorant pizza hamburguer acai sushi churrasco "
        "cerveja vinho cafe chocolate bolo receitas dieta academia creatina whey yoga corrida bicicleta carro moto "
        "onibus metro aviao passagem hotel airbnb turismo gramado fortaleza salvador recife natal2 manaus belem "
        "curitiba florianopolis portoalegre goiania brasilia saopaulo riodejaneiro bh").split()
import os; j=int(os.environ.get("J","0")); words = base[j*30:j*30+MAX]

def urllib_word(k):
    cj = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36")]
    try: op.open("https://trends.google.com/trends/explore?geo=BR", timeout=30).read()
    except Exception: pass
    req = {"comparisonItem": [{"keyword": k, "geo": "BR", "time": "today 12-m"}], "category": 0, "property": ""}
    try:
        r = op.open("https://trends.google.com/trends/api/explore?hl=pt-BR&tz=180&req=" + urllib.parse.quote(json.dumps(req)), timeout=30)
        return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception: return -1

print("fase0 urllib:", [urllib_word(k) for k in ("previsao do tempo", "horoscopo", "jogo do bicho")]); sys.stdout.flush()

MODE=os.environ.get("MODE","chrome"); SL=float(os.environ.get("SL","0.4"))
class U:
    def __init__(s):
        cj=http.cookiejar.CookieJar(); s.op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)); s.op.addheaders=[("User-Agent","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36")]
    def get(s,u,timeout=30):
        class R: pass
        r=R()
        try: x=s.op.open(u,timeout=timeout); r.status_code=x.status; r.text=x.read().decode()
        except urllib.error.HTTPError as e: r.status_code=e.code; r.text=""
        return r
s = cr.Session(impersonate="chrome") if MODE=="chrome" else U()
try: s.get("https://trends.google.com/trends/explore?geo=BR", timeout=30)
except Exception as e: print("abertura", e)
ok = 0; seq = []; falhas = 0; t0 = time.time()
for i, k in enumerate(words):
    req = {"comparisonItem": [{"keyword": k, "geo": "BR", "time": "today 12-m"}], "category": 0, "property": ""}
    try:
        r = s.get("https://trends.google.com/trends/api/explore?hl=pt-BR&tz=180&req=" + urllib.parse.quote(json.dumps(req)), timeout=30)
        st = r.status_code; st2 = None
        if st == 200:
            w = [x for x in json.loads(r.text.split("\n", 1)[1])["widgets"] if x["id"] == "TIMESERIES"][0]
            r2 = s.get("https://trends.google.com/trends/api/widgetdata/multiline?hl=pt-BR&tz=180&req=" + urllib.parse.quote(json.dumps(w["request"])) + "&token=" + w["token"], timeout=30)
            st2 = r2.status_code
    except Exception as e:
        st, st2 = -1, None
    seq.append(f"{st}/{st2}")
    if st == 200 and st2 == 200: ok += 1; falhas = 0
    else: falhas += 1
    if falhas >= 5: break
    time.sleep(SL)
print(f"fase1 {MODE} sl={SL}: {ok} de {len(seq)} palavras ok em {time.time()-t0:.0f} s")
print(" ".join(seq))
