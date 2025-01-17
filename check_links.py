import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from tqdm import tqdm



def check_link_status(link):
    """
    Verifica se um link é válido com base no status HTTP.
    Retorna o código de status HTTP.
    """
    try:
        # Faz uma requisição HEAD para obter o status do link
        response = requests.head(link, allow_redirects=True, timeout=10)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Erro ao verificar o link: {e}")
        return "Erro"  # Retorna "Erro" em caso de exceção

def retorna_links_de_uma_pagina(url, driver):
    """
    Usa Selenium para acessar uma página e retorna todos os links encontrados.
    """
    print(f"Acessando: {url}")
    try:
        driver.get(url)  # Abre a página no navegador
        # Captura todas as tags <a> com atributo href
        links = {a.get_attribute('href') for a in driver.find_elements(By.TAG_NAME, 'a') if a.get_attribute('href')}
        return links
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return set()

def list_unique_links_selenium(pages):
    """
    Percorre todas as páginas da lista e retorna um conjunto com links únicos.
    """
    # Configurações do Selenium
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Executa o navegador em modo headless (sem interface gráfica)
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    # Inicia o WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    unique_links = set()
    try:
        for page in pages:
            links = retorna_links_de_uma_pagina(page, driver)
            # União entre unique_links e links
            unique_links = unique_links | links
    finally:
        driver.quit()  # Fecha o navegador

    return unique_links

def generate_html(links_status):
    """
    Gera um arquivo HTML para exibir os links, seus status HTTP e uma imagem do http.cat.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Links e Status HTTP</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f4f4f4;
            }
            img {
                width: 500px;
                height: auto;
            }
        </style>
    </head>
    <body>
        <h1>Links e Status HTTP</h1>
        <table>
            <thead>
                <tr>
                    <th>Link</th>
                    <th>Status HTTP</th>
                    <th>Imagem</th>
                </tr>
            </thead>
            <tbody>
    """
    for link, status in links_status:
        img_url = f"https://http.cat/{status}" if isinstance(status, int) else "https://http.cat/404"
        html_content += f"""
        <tr>
            <td><a href="{link}" target="_blank">{link}</a></td>
            <td>{status}</td>
            <td><img src="{img_url}" alt="HTTP {status}"></td>
        </tr>
        """
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    # Salvar o HTML em um arquivo
    with open("links_status.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    print("Arquivo HTML gerado: links_status.html")

def main():
    # Lista de URLs para verificar
    pages = [
        'https://www.meusite.com.br',
    ]
    print("Iniciando scraping das páginas com Selenium...\n")
    unique_links = list_unique_links_selenium(pages)

    # Verifica o status HTTP de cada link
    links_status = []
    print("\nVerificando status HTTP dos links encontrados:")
    for link in tqdm(sorted(unique_links), desc="Verificando links", unit="link"):
        status = check_link_status(link)
        links_status.append((link, status))

    # Gera o HTML com os links, status e imagens
    generate_html(links_status)

if __name__ == "__main__":
    main()
