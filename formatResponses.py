from discord import embeds
from discord import Colour
from discord import File


def format_build(champ: str, build_dict: dict):
    title = champ.upper() + " BUILD :crossed_swords:"
    embed = embeds.Embed(
        title=title,
        colour=Colour.random()
    )

    txt = ""
    count = 0
    for item in build_dict["core-build"]:
        if count < 3:
            txt += str(count+1) + '. ' + item + '\n\n'
        elif count == 3:
            txt += "\nPopularidade: " + item + "%\n"
        else:
            txt += " Win rate: " + item + "%\n"
        count += 1

    embed.add_field(name="Principal", value=txt, inline=True)

    txt = ''
    for item in build_dict["end-build"]:
        txt += item + '\n'

    txt += "\n**Bota**\n"
    info_botas = build_dict['boots']
    txt += info_botas[0] + '\n\n'
    txt += " Popularidade: " + info_botas[1] + "%\n"
    txt += " Win rate: " + info_botas[2] + "%\n"

    embed.add_field(name="Outros", value=txt, inline=True)

    return embed


def format_runas(champ, lane, runas, winrate):
    txt = "***" + champ.upper() + ' RUNAS***\n'

    txt += '*Win rate: ' + winrate + '*\n\n'

    for i in range(0, 4):
        txt += runas[i] + ' | '

    txt = txt[:-3] + '\n'
    for i in range(4, 7):
        txt += runas[i] + ' | '

    txt = txt[:-3] + '\n' + runas[7] + ' | ' + runas[8] + ' | ' + runas[9]

    return txt


def format_commands(symbol, commands):
    title = "COMMANDS :scroll:"

    txt = ""
    for com in commands:
        txt += symbol + com + '\n'

    embed = embeds.Embed(
        title=title,
        colour=Colour.random(),
        description=txt
    )

    return embed


def format_last_update(img_link, num_att):
    embed = embeds.Embed(
        title="ATUALIZAÇÃO " + str(num_att),
        colour=Colour.random()
    )

    embed.set_image(url=img_link)

    return embed



