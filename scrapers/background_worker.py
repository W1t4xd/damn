import time
import json
import os
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Define o caminho para o arquivo de dados
OUTPUT_DIR = 'output'
RESULTS_FILE = os.path.join(OUTPUT_DIR, 'results.json')
# Intervalo de verificação em segundos
INTERVALO_CHECK = 0.5

def extrair_resultados_bacbo(url: str):
    """
    Navega até a URL fornecida, aguarda o carregamento do histórico de resultados
    e extrai os dados de cada rodada.
    """
    resultados = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=60000)
            page.wait_for_selector('div.round-history', state='visible', timeout=30000)
            time.sleep(5)

            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            historico_div = soup.find('div', class_='round-history')
            if not historico_div:
                return []

            celulas_resultado = historico_div.find_all('button', class_='cell--bac_bo')

            for celula in celulas_resultado:
                try:
                    class_string = " ".join(celula.get('class', []))
                    
                    id_match = re.search(r'data-id-([a-f0-9-]+)', class_string)
                    resultado_id = id_match.group(1) if id_match else 'N/A'

                    # --- MODIFICAÇÃO AQUI ---
                    type_match = re.search(r'data-type-(\w+)', class_string)
                    vencedor = type_match.group(1) if type_match else 'N/A' # Usa o valor original (banker, player, tie)
                    # --- FIM DA MODIFICAÇÃO ---

                    result_match = re.search(r'data-result-([0-9]+)', class_string)
                    valor_str = result_match.group(1) if result_match else '0'
                    valor = int(valor_str) if valor_str.isdigit() else 0
                    
                    tooltip_div = celula.find_previous_sibling('div', class_='cell__tooltip')
                    data_hora_completa = tooltip_div.text if tooltip_div else 'N/A'
                    
                    horario_div = celula.find('div', class_='cell__date')
                    horario = horario_div.text.strip() if horario_div else 'N/A'

                    resultados.append({
                        'id': resultado_id,
                        'data_hora': data_hora_completa,
                        'horario_rodada': horario,
                        'vencedor': vencedor,
                        'valor': valor
                    })
                except (AttributeError, ValueError, TypeError):
                    continue
        except Exception as e:
            print(f"[{time.ctime()}] Erro no scraping: {e}")
            return None
        finally:
            browser.close()
    return resultados

def ler_resultados_salvos():
    if not os.path.exists(RESULTS_FILE):
        return []
    try:
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def salvar_resultados(dados: list):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    url_alvo = "https://www.tipminer.com/br/historico/jonbet/bac-bo"
    print(f"[{time.ctime()}] Iniciando monitoramento de resultados do Bac Bo...")
    
    while True:
        resultados_salvos = ler_resultados_salvos()
        novos_resultados = extrair_resultados_bacbo(url_alvo)

        if novos_resultados is None:
            print(f"[{time.ctime()}] Falha no scraping. Tentando novamente em {INTERVALO_CHECK} segundos.")
            time.sleep(INTERVALO_CHECK)
            continue

        if not resultados_salvos or (novos_resultados and novos_resultados[0]['id'] != resultados_salvos[0]['id']):
            print(f"[{time.ctime()}] Novos resultados detectados! Atualizando arquivo...")
            salvar_resultados(novos_resultados)
        else:
            print(f"[{time.ctime()}] Sem novos resultados. Próxima verificação em {INTERVALO_CHECK} segundos.")
        
        time.sleep(INTERVALO_CHECK)