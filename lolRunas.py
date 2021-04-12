import asyncio
import nest_asyncio
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
from math import ceil, floor
import re
import convertapi

nest_asyncio.apply()

convertapi.api_secret = 'convert api secret' # used to convert html to png


# GENERAL
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


def convert_html_png(size):
    largura = round(int(size[0]) + 1)

    result = convertapi.convert('png', {'File': 'sample.html', 'ImageHeight': int(size[1]), 'ImageWidth': largura,
                                        'ScaleProportions': 'False'})

    # save to file
    result.file.save('img.png')


# RUNES
def get_runas(champ, lane):
    loop = asyncio.get_event_loop()
    url = 'https://www.leagueofgraphs.com/pt/champions/runes/' + champ.replace(" ", '').replace("'", '') + '/' + lane
    forecast = loop.run_until_complete(get_html(url))
    runas, winrate, size = extract_runas_html(forecast)
    convert_html_png(size)
    return runas, winrate


def extract_runas_html(html):
    page_soup = BeautifulSoup(html, 'html.parser')
    winrate = page_soup.find_all('div', {"class": "progressBarTxt"})
    winrate = winrate[1].contents[0]
    page_soup = page_soup.find_all("table", {"class": "data_table perksTable perksTableLight"})
    page_soup = page_soup[0].find('tbody')

    linhas = page_soup.find_all('tr')

    frases = []
    pequenas = []
    count = 0
    txt = ""
    html = '<section style="background-color: #211722; text-align: center">'
    largura = 0
    altura = 0
    for linha in linhas:
        cols = linha.find_all('td')
        less = 0
        flag = 0
        html += "<div>"

        for col in cols:
            img = col.find('img')

            if count == 0:
                largura += float(img['width'])
            if count < 4:
                if img.has_attr('style'):
                    op = float(img['style'].split(' ')[1].replace(';', ''))
                    html += str(img) + ' \n'
                    if op > less:
                        less = op
                        menor = img
                        txt = img['alt']

            elif count < 7:
                if img.has_attr('style'):
                    op = float(img['style'].split(' ')[1].replace(';', ''))
                    html += str(img) + " \n"
                    if op > less:
                        less = op
                        menor = img
                        txt = img['alt']

            else:
                if img.parent.has_attr('style') and img.parent['style'] == '':
                    menor = img
                    txt = img['alt']
                    flag = 1

        if flag == 1:
            pequenas.append(str(menor))

        if count == 9:
            for el in pequenas:
                html += el + " \n"

        frases.append(txt)

        count += 1
        html += "</div>"
        altura += float(img['height'])

    html += "</section>"

    file = open("sample.html", "w")

    file.write(html)
    file.close()

    return frases, winrate, (largura * 1.3, altura)


# WINRATE PROGRESSION
def get_progression(qntd_linha=5):
    loop = asyncio.get_event_loop()
    url = 'https://www.leagueofgraphs.com/pt/champions/progressions'
    html_page = loop.run_until_complete(get_html(url))
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


# BEST CHAMPS (by winrate)
def get_best_champs(qntd_linhas=5):
    loop = asyncio.get_event_loop()
    url = 'https://www.leagueofgraphs.com/'
    forecast = loop.run_until_complete(get_html(url))
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


# GET CHAMPION'S BUILD
def get_build_champ(champ_name, lane=""):
    loop = asyncio.get_event_loop()
    if lane == "":
        url = 'https://www.leagueofgraphs.com/pt/champions/builds/' + champ_name.replace("'", "").lower()
    else:
        url = 'https://www.leagueofgraphs.com/pt/champions/builds/' + champ_name.replace("'", "") + "/" + lane.lower()
    forecast = loop.run_until_complete(get_html(url))
    build = extract_build_html(forecast, champ_name)
    return build


def extract_build_html(page, champ):
    page_soup = BeautifulSoup(page, 'html.parser')
    main = page_soup.find('div', {"id": "mainContent"})
    #vet_a = main.find('a', {'href', '/pt/champions/items/' + champ.lower()})
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
def get_last_update():
    loop = asyncio.get_event_loop()
    url = 'https://br.leagueoflegends.com/pt-br/news/game-updates/'
    forecast = loop.run_until_complete(get_html(url))
    link, num_att = extract_last_update_link(forecast)

    url = 'https://br.leagueoflegends.com' + link
    forecast = loop.run_until_complete(get_html(url))
    img_link = extract_last_update(forecast)
    return img_link, num_att


def extract_last_update_link(page):
    link = ""
    num_att = 0.0

    page_soup = BeautifulSoup(page, 'html.parser')
    lista = page_soup.find_all('h2', {"class": "style__Title-i44rc3-8 jprNto"})
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
