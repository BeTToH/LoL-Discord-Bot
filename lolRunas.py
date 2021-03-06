import nest_asyncio
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
from math import ceil, floor
import re
import convertapi

nest_asyncio.apply()

convertapi.api_secret = CONVERT_API_SECRET

matriz_runas = [['+9 Força Adaptativa', '+10% Velocidade de Ataque', '+8 Aceleração de Habilidade'],
                ['+9 Força Adaptativa', '+6 Armadura', '+8 Resistência Mágica'],
                ['+15-140 Vida', '+6 Armadura', '+8 Resistência Mágica']]


# GERAIS
async def get_html(url):
    session = AsyncHTMLSession()

    resp = await session.get(url)
    await resp.html.arender()
    html = resp.html.raw_html

    return html


def casas_apos_virgula(num):
    count = 0
    while num >= 10:
        num /= 10
        count += 1

    return count


async def convert_html_png(largura):
    result = convertapi.convert('png', {'File': 'sample.html', 'ImageWidth': largura, 'ScaleProportions': 'False'})

    # save to file
    result.file.save('img.png')


# RUNAS
async def get_runas(champ, lane=""):
    champ = champ.replace(" ", '').replace("'", '')
    url = f'https://br.op.gg/champion/{champ}/statistics/{lane + "/" if lane != "" else ""}build'
    forecast = await get_html(url)
    runas, winrate, largura = extract_runas_html(forecast)
    await convert_html_png(largura)
    return runas, winrate


def extract_runas_html(html):
    page_soup = BeautifulSoup(html, 'html.parser')

    tb_todas_runas = page_soup.find_all("tbody", {"class": "tabItem ChampionKeystoneRune-1"})[0]
    primeira_runa = tb_todas_runas.find_all('tr')[0]

    winrate = primeira_runa.find('span', {'class': 'win-ratio__text'}).findNext('strong')
    winrate = winrate.contents[0]

    linhas = primeira_runa.find_all('div', {"class": 'perk-page__row'})

    frases = []

    count = 0
    html_img = '<section style="background-color: #211722; text-align: center">'

    largura_maior_icone = 82
    largura = largura_maior_icone * 4 + 40

    tipo_runa = primeira_runa.find_all('div', {'class': 'perk-page__item--mark'})
    for runa in tipo_runa:
        runa['style'] = f'width: {largura_maior_icone * 3 / 5}px; padding: 10px 0 10px 0; margin: 0 auto;'

    for linha in linhas:
        if count == 0:
            html_img += str(tipo_runa[0])
        elif count == 5:
            html_img += str(tipo_runa[1])

        ativo = linha.find('div', {'class': 'perk-page__item--active'})

        if ativo is not None:
            txt = ativo.find('img')['alt']
            frases.append(txt)

        runas = linha.find_all('div', {'class': 'perk-page__image'})

        html_img += '<div style="display: flex; justify-content: space-evenly; padding: 10px 0 10px 0;">'
        for runa in runas:
            runa_img = runa.find('img')
            if count == 1:
                runa_img['class'] = ''
                runa_img['style'] = f'width: {largura_maior_icone}px'
            else:
                runa_img['class'] = ''
                runa_img['style'] = f'width: {largura_maior_icone * 4 / 5}px'
            html_img += str(runa_img)

        count += 1
        html_img += "</div>"

    linhas = primeira_runa.find_all('div', {"class": 'fragment__row'})

    for linha in linhas:
        count_col = 0
        runas = linha.find_all('img')

        html_img += '<div style="display: flex; justify-content: center; column-gap: 20px; padding: 10px 0 10px 0;">'
        for runa in runas:
            html_img += str(runa)
            if 'grayscale' not in runa['src']:
                frases.append(matriz_runas[count-9][count_col])
            count_col += 1
        html_img += "</div>"
        count += 1

    file = open("sample.html", "w")

    file.write(html_img)
    file.close()

    return frases, winrate, largura


# Progressão Winrate
async def get_progression(qntd_linha=5):
    url = 'https://www.leagueofgraphs.com/pt/champions/progressions'
    html_page = await get_html(url)
    return extract_progression_html(html_page, int(qntd_linha) + 1)


def extract_progression_html(page, qntd_linhas):
    page_soup = BeautifulSoup(page, 'html.parser')
    tabela = page_soup.find_all('table', {"class": "data_table sortable_table"})
    linhas = tabela[0].find_all('tr')

    txt = ""
    champs = []
    max_size = 0

    for i in range(1, qntd_linhas):
        champ_img = linhas[i].find_all('img')
        champ = champ_img[0]['alt']
        champs.append(champ)
        if max_size < len(champ):
            max_size = len(champ)

    for i in range(1, qntd_linhas):
        winrate = linhas[i].find_all('progressbar')
        dif = max_size - len(champs[i - 1])
        qntd_space = int(floor(dif / 2))
        space = qntd_space * ' '
        space_dps = space
        if dif % 2 == 1:
            space_dps += ' '
        posicao = ''
        if qntd_linhas >= 10:
            posicao = ' ' * (casas_apos_virgula(qntd_linhas) - casas_apos_virgula(i)) + str(i)
        txt += posicao + '- ' + space + champs[i - 1] + space_dps + ' -> Winrate: ' + str(
            round(float(winrate[0]['data-value']), 3) * 100) + '% | Progressão: ' + str(
            round(float(winrate[1]['data-value']), 2) * 100) + '%\n'

    return txt


# Melhores (por winrate)
async def get_best_champs(qntd_linhas=5):
    url = 'https://www.leagueofgraphs.com/'
    forecast = await get_html(url)
    txt = extract_best_html(forecast, qntd_linhas)
    return txt


def extract_best_html(page, qntd_linhas):
    page_soup = BeautifulSoup(page, 'html.parser')
    tabela = page_soup.find_all('table', {"class": "fast_stat_table"})
    tbody = tabela[1].find_all('tbody')

    rows = tbody[0].find_all('tr')

    html = ""
    count = 0
    for row in rows:
        cols = row.find_all('td')
        champ = cols[0].text.replace(' ', '')

        html += champ

        winrate = cols[1].find_all('div')
        html += ' -> Winrate: ' + winrate[0].text + ' #'

        count += 1
        if count == (qntd_linhas + 1):
            break

    return html


# Get Build Champ
async def get_build_champ(champ_name, lane=""):
    if lane == "":
        url = 'https://www.leagueofgraphs.com/pt/champions/builds/' + champ_name.replace("'", "").lower()
    else:
        url = 'https://www.leagueofgraphs.com/pt/champions/builds/' + champ_name.replace("'", "") + "/" + lane.lower()
    forecast = await get_html(url)
    build = extract_build_html(forecast, champ_name)
    return build


def extract_build_html(page, champ):
    page_soup = BeautifulSoup(page, 'html.parser')
    main = page_soup.find('div', {"id": "mainContent"})

    vet_a = main.find_all('a')
    div1 = vet_a[2].find_all('div')[0]

    builds_rows = div1.find_all('div')

    dict_itens = {"core-build": [], "end-build": [], "boots": []}

    # Core build
    div_core_itens = builds_rows[0].find_all('div', {'class': 'medium-13 columns'})[0]
    core_build = div_core_itens.find_all('img')
    core_build.pop(0)
    for item in core_build:
        dict_itens["core-build"].append(str(item['alt']))
    core_extra_info = div_core_itens.find_all('div')[0].find_next_sibling('div').text
    core_extra_info = re.findall("\d+\.\d+", core_extra_info)
    for value in core_extra_info:
        dict_itens["core-build"].append(value)

    # Boots
    div_boots = builds_rows[0].find_next_sibling('div').find_all('div', {'class': 'medium-11 columns'})[0]
    boots = div_boots.find_all('img')[0]['alt']
    dict_itens["boots"].append(boots)
    boots_extra_info = div_boots.find_all('div')[0].find_next_sibling('div').text
    boots_extra_info = re.findall("\d+\.\d+", boots_extra_info)
    for value in boots_extra_info:
        dict_itens["boots"].append(value)

    # End build
    div_end_build = builds_rows[0].find_next_sibling('div').find_all('div', {'class': 'medium-13 columns'})[0]
    end_build = div_end_build.find_all('img')
    for item in end_build:
        dict_itens["end-build"].append(str(item['alt']))

    return dict_itens


# GET LAST UPDATE
async def get_last_update(lang='pt-br'):
    url = f'https://br.leagueoflegends.com/{lang}/news/game-updates/'
    forecast = await get_html(url)
    link, num_att = extract_last_update_link(forecast)

    url = 'https://br.leagueoflegends.com' + link
    forecast = await get_html(url)
    img_link = extract_last_update(forecast)
    return img_link, num_att


def extract_last_update_link(page):
    link = ""
    num_att = 0.0

    page_soup = BeautifulSoup(page, 'html.parser')
    lista = page_soup.find_all('h2')
    for item in lista:
        if 'Notas da Atualização' in item.text and 'Teamfight Tactics' not in item.text:
            link = item.parent.parent.parent.parent['href']
            num_att = re.findall("\d+\.\d+", item.text)
            break

    return link, num_att[0]


def extract_last_update(page):
    page_soup = BeautifulSoup(page, 'html.parser')
    img_link = page_soup.find_all('a', {'class': 'skins cboxElement'})[0]
    return img_link['href']
