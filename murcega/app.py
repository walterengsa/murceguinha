import discord
from discord.ext import commands, tasks
import os
import sys
import aiohttp
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# CONFIGURAÇÕES
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

CANAL_BOAS_VINDAS = 1378375304904704097
CANAL_TESTE = 1506282571565109460
CANAL_PROTEGIDO = 1378387938571976754

ID_CANAL_REGRAS = 1378385276015087811
ID_CANAL_CRIPTA = 1378387938571976754
ID_CANAL_CARGOS = 1522218186710188273
ID_CANAL_AVISOS = 1522142065813754038

ID_CARGO_AUTOMATICO = 1420123782357717026

IMAGEM_BOAS = os.path.join("img", "IMAGEMboas.png")
IMAGEM_REGRAS = os.path.join("img", "cuzinho.png")

# ---------------------------------------------------------
# TWITCH (AVISO DE LIVE)
# ---------------------------------------------------------
# Crie um app em https://dev.twitch.tv/console/apps e cole o
# Client ID e o Client Secret abaixo.

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

TWITCH_USER_LOGIN = "murcega08"

ID_CANAL_LIVE = 1378385475412299817

INTERVALO_VERIFICACAO_LIVE = 30  # segundos (checagem se está online/offline)
INTERVALO_ATUALIZACAO_LIVE = 1800  # segundos (30 minutos - atualiza views/duração/imagem)

# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()

intents.members = True
intents.guilds = True
intents.message_content = True

# =========================================================
# BOT
# =========================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================================================
# ADVERTÊNCIAS
# =========================================================

advertencias = {}

# =========================================================
# ESTADO DO SISTEMA DE LIVE (TWITCH)
# =========================================================

twitch_access_token = None
live_esta_ativa = False
live_stream_id_atual = None
live_mensagem_atual = None
live_ultima_atualizacao = None

# =========================================================
# PALAVRAS PROIBIDAS
# =========================================================

palavras_proibidas = [

    "nigger",
    "nigga",
    "pretinho",
    "macaco",
    "monkey",
    "judeu",
    "kike",
    "spic",
    "chink",
    "jap",
    "gook",
    "towelhead",
    "sandnigger",
    "wetback",
    "beaner",
    "gypsy",
    "cigano",
    "indio",
    "crioulo",
    "preto",
    "nazi",
    "hitler",
    "retard",
    "mongoloid",
    "autista",
    "down",
    "traveco",
    "viadinho",
    "baitola",
    "bicha",
    "sapatão",
    "dyke",
    "faggot",
    "fag",
    "tranny",
    "puta",
    "vadia",
    "whore",
    "slut",
    "bitch",
    "cuck",
    "incel",
    "simp",
    "femoid",
    "roastie",
    "estuprador",
    "pedo",
    "pedófilo",
    "groomer",
    "fascista",
    "cp",
    "cepe",
    "cêpe",
    "golpe"
]

# =========================================================
# SISTEMA DE LOG
# =========================================================

def log(texto):

    horario = datetime.now().strftime("%H:%M:%S")

    print(f"[{horario}] {texto}")

# =========================================================
# EMBED DE BOAS-VINDAS
# =========================================================

def criar_embed(usuario, avatar_url=None):

    texto = (
        f"🦇 Bem-vindo(a), {usuario}\n\n"
        f"Você acaba de se tornar um Morceguinho e agora faz parte da nossa colônia.\n"
        f"Antes de explorar a caverna, visite os canais abaixo:\n\n"
        f"▶ **Regras**\n"
        f"Leia as regras da comunidade para manter este lugar agradável para todos.\n"
        f"<#{ID_CANAL_REGRAS}>\n\n"
        f"▶ **Cargos**\n"
        f"Descubra o significado do cargo de Morceguinho e conheça os demais cargos disponíveis no servidor.\n"
        f"<#{ID_CANAL_CARGOS}>\n\n"
        f"▶ **Avisos**\n"
        f"Acompanhe novidades, eventos, lives e anúncios importantes da comunidade.\n"
        f"<#{ID_CANAL_AVISOS}>\n\n"
        f"Seja bem-vindo(a) ao covil. 🖤"
    )

    embed = discord.Embed(
        description=texto,
        color=0x490206
    )

    # FOTO DE PERFIL
    if avatar_url:

        embed.set_thumbnail(
            url=avatar_url
        )

        log("Thumbnail adicionada na embed.")

    # IMAGEM GRANDE
    embed.set_image(
        url="attachment://IMAGEMboas.png"
    )

    log("Imagem principal adicionada na embed.")

    return embed

# =========================================================
# EMBED DE REGRAS (GUIA DA COLÔNIA)
# =========================================================

def criar_embed_regras():

    texto = (
        "✦ *Introdução*\n"
        "Seja bem-vindo(a) ao **Covil dos Morceguinhos**! 🖤\n"
        "Este guia reúne tudo o que você precisa saber sobre a comunidade, as lives "
        "e o funcionamento do servidor. A leitura é rápida e vai te ajudar a "
        "aproveitar melhor sua estadia por aqui.\n"
        "════════════════════\n"

        "✦ *Quem é a Murcega?*\n"
        "Prazer! Eu sou a **Murcega**, uma gótica apaixonada por games.\n"
        "Sou o tipo de pessoa que ri de qualquer coisa, fala muita besteira e "
        "adora interagir e conhecer gente nova.\n"
        "Gosto de jogos online competitivos (mesmo não sendo lá muito boa), adoro "
        "zerar — e, quando a coragem permite, platinar — jogos de campanha. Mas, "
        "acima de tudo, sou completamente apaixonada por terror, seja em jogos, "
        "filmes, livros ou histórias.\n"
        "A proposta do meu conteúdo é simples: viver boas experiências em live. "
        "Em um dia podemos estar enfrentando monstros, no outro assistindo alguma "
        "coisa juntos, reagindo a vídeos ou simplesmente fazendo alguma ideia "
        "aleatória que surgiu na hora.\n"
        "════════════════════\n"

        "✦ *Sobre as Lives*\n"
        "Aqui você vai encontrar um pouco de tudo.\n"
        "Entre os jogos que costumo jogar estão **Dead by Daylight**, "
        "**Valorant**, **Hunt: Showdown**, **League of Legends** e **Overwatch**, "
        "além de muitos jogos de terror, desde clássicos até lançamentos.\n"
        "Se quiser descobrir quais jogos você pode jogar comigo ou conferir todos "
        "os jogos de campanha que já zerei, acesse o canal abaixo.\n"
        "〔**Ver Biblioteca de Jogos**〕(https://bio.site/murcega)\n"
        "════════════════════\n"

        "✦ *Regras do Covil*\n"
        "Para manter o Covil um ambiente agradável para todos, siga estas regras:\n"
        "**1. Respeite todos os membros.**\n"
        "Não serão tolerados ataques pessoais, preconceito, discriminação ou "
        "qualquer forma de assédio.\n"
        "**2. Mantenha um ambiente saudável.**\n"
        "Evite discussões desnecessárias, provocações e brigas. Debater é "
        "permitido, faltar com respeito não.\n"
        "**3. Use os canais corretamente.**\n"
        "Cada canal possui um propósito. Ajude a manter o servidor organizado.\n"
        "**4. Não faça spam.**\n"
        "Evite flood, mensagens repetitivas, divulgações sem autorização ou "
        "qualquer conteúdo que atrapalhe a conversa.\n"
        "**5. Conteúdo impróprio.**\n"
        "Não compartilhe conteúdos ilegais, gore, pornografia ou qualquer "
        "material que viole as Diretrizes da Comunidade do Discord.\n"
        "**6. Respeite a equipe.**\n"
        "Caso algum moderador peça para encerrar um assunto ou chame sua "
        "atenção, colabore. Se discordar de alguma decisão, converse com a "
        "equipe em particular.\n"
        "**7. Não pentelhe a Murcega (nem a comunidade).**\n"
        "Brincadeiras fazem parte, mas saiba a hora de parar. Insistir, provocar "
        "de propósito, pressionar por atenção ou ficar repetindo o mesmo assunto "
        "depois que a resposta já foi dada não é legal. O bom senso vale para "
        "todo mundo.\n"
        "**8. Divulgações somente com autorização.**\n"
        "Qualquer divulgação de servidores, lives, redes sociais, projetos ou "
        "qualquer outro conteúdo deve ser autorizada previamente pela **Murcega** "
        "ou por um membro da equipe de moderação.\n"
        "════════════════════\n"

        "✦ *Cargos*\n"
        "Cada membro do Covil possui um cargo que representa seu papel dentro da "
        "comunidade.\n"
        "🦇 **A STREAMER**\n"
        "A Murcega, criadora do conteúdo e dona do Covil.\n"
        "⚜ **ADMINISTRAÇÃO**\n"
        "Responsáveis pela configuração, organização e manutenção das lives e do "
        "servidor.\n"
        "🩸 **MODERAÇÃO**\n"
        "Equipe encarregada de manter a ordem da comunidade e garantir o "
        "cumprimento das regras.\n"
        "💜 **SUBS**\n"
        "Membros inscritos na Twitch que recebem benefícios exclusivos no "
        "servidor.\n"
        "🦇 **MOGUERÇOS**\n"
        "Todos os demais membros da comunidade. São o coração do Covil e fazem "
        "este lugar existir.\n"
        "════════════════════\n"

        "✦ *Links*\n"
        "Caso queira entrar em contato comigo, acompanhar meu trabalho em outras "
        "plataformas ou acessar minhas redes sociais, basta clicar no botão "
        "abaixo.\n"
        "〔**Minhas Redes**〕(https://bio.site/murcega)"
    )

    embed = discord.Embed(
        description=texto,
        color=0x490206
    )

    embed.set_image(
        url="attachment://cuzinho.png"
    )

    log("Embed de regras criada.")

    return embed

# =========================================================
# BOTÃO DE LINK (MINHAS REDES)
# =========================================================

class ViewLinksRegras(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            discord.ui.Button(
                label="Minhas Redes",
                emoji="🖤",
                url="https://bio.site/murcega",
                style=discord.ButtonStyle.link
            )
        )

# =========================================================
# ENVIO DO GUIA DE REGRAS
# =========================================================

async def enviar_regras(canal):

    if not os.path.exists(IMAGEM_REGRAS):

        log("ERRO: Imagem de regras não encontrada.")
        log(f"Caminho procurado: {IMAGEM_REGRAS}")

        return False

    log("Imagem de regras localizada.")

    try:

        arquivo = discord.File(
            IMAGEM_REGRAS,
            filename="cuzinho.png"
        )

        embed = criar_embed_regras()

        view = ViewLinksRegras()

        await canal.send(
            embed=embed,
            file=arquivo,
            view=view
        )

        log(f"Guia de regras enviado no canal: {canal.name}")

        return True

    except Exception as erro:

        log(f"ERRO AO ENVIAR REGRAS: {erro}")

        return False

# =========================================================
# SISTEMA DE AVISO DE LIVE (TWITCH)
# =========================================================

async def obter_token_twitch(session):

    global twitch_access_token

    try:

        url = "https://id.twitch.tv/oauth2/token"

        params = {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }

        async with session.post(url, params=params) as resposta:

            if resposta.status != 200:

                log(f"ERRO AO OBTER TOKEN DA TWITCH: HTTP {resposta.status}")
                return None

            dados = await resposta.json()

            twitch_access_token = dados.get("access_token")

            log("Token da Twitch obtido com sucesso.")

            return twitch_access_token

    except Exception as erro:

        log(f"ERRO AO OBTER TOKEN DA TWITCH: {erro}")

        return None


async def obter_stream_twitch(session):

    global twitch_access_token

    if twitch_access_token is None:

        await obter_token_twitch(session)

        if twitch_access_token is None:
            return None

    headers = {
        "Client-Id": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {twitch_access_token}"
    }

    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USER_LOGIN.lower()}"

    try:

        async with session.get(url, headers=headers) as resposta:

            # TOKEN EXPIRADO
            if resposta.status == 401:

                log("Token da Twitch expirado, renovando...")

                twitch_access_token = None

                novo_token = await obter_token_twitch(session)

                if novo_token is None:
                    return None

                headers["Authorization"] = f"Bearer {novo_token}"

                async with session.get(url, headers=headers) as resposta2:

                    if resposta2.status != 200:

                        log(f"ERRO AO CONSULTAR STREAM: HTTP {resposta2.status}")
                        return None

                    dados = await resposta2.json()

            elif resposta.status != 200:

                log(f"ERRO AO CONSULTAR STREAM: HTTP {resposta.status}")
                return None

            else:

                dados = await resposta.json()

            streams = dados.get("data", [])

            if not streams:
                return None

            return streams[0]

    except Exception as erro:

        log(f"ERRO AO CONSULTAR STREAM DA TWITCH: {erro}")

        return None


async def obter_box_art_twitch(session, game_id):

    if not game_id:
        return None

    headers = {
        "Client-Id": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {twitch_access_token}"
    }

    url = f"https://api.twitch.tv/helix/games?id={game_id}"

    try:

        async with session.get(url, headers=headers) as resposta:

            if resposta.status != 200:

                log(f"ERRO AO CONSULTAR JOGO: HTTP {resposta.status}")
                return None

            dados = await resposta.json()

            jogos = dados.get("data", [])

            if not jogos:
                return None

            template = jogos[0].get("box_art_url")

            if not template:
                return None

            return template.replace("{width}", "285").replace("{height}", "380")

    except Exception as erro:

        log(f"ERRO AO CONSULTAR BOX ART: {erro}")

        return None


def formatar_duracao(inicio_iso):

    try:

        inicio = datetime.strptime(inicio_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        agora = datetime.now(timezone.utc)

        delta = agora - inicio

        segundos = int(delta.total_seconds())

        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segs = segundos % 60

        return f"{horas}h{minutos}m{segs}s"

    except Exception as erro:

        log(f"ERRO AO FORMATAR DURAÇÃO: {erro}")

        return "N/A"


class ViewAssistirLive(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            discord.ui.Button(
                label="Assistir na Twitch",
                emoji="🔴",
                url=f"https://twitch.tv/{TWITCH_USER_LOGIN}",
                style=discord.ButtonStyle.link
            )
        )


def criar_embed_live(stream, box_art_url):

    nome_exibicao = stream.get("user_name", TWITCH_USER_LOGIN)
    titulo = stream.get("title", "Sem título")
    jogo = stream.get("game_name", "Sem categoria")
    viewers = stream.get("viewer_count", 0)
    started_at = stream.get("started_at")

    duracao = formatar_duracao(started_at) if started_at else "N/A"

    link_canal = f"https://twitch.tv/{TWITCH_USER_LOGIN}"

    embed = discord.Embed(
        description=f"🔴 **[{nome_exibicao}]({link_canal}) está ao vivo!**\n{titulo}",
        color=0x9146FF,
        url=link_canal
    )

    embed.add_field(name="Game", value=jogo, inline=True)
    embed.add_field(name="Views", value=str(viewers), inline=True)
    embed.add_field(name="Duration", value=duracao, inline=True)

    if box_art_url:

        embed.set_thumbnail(url=box_art_url)

    thumbnail_stream = stream.get("thumbnail_url")

    if thumbnail_stream:

        thumbnail_final = (
            thumbnail_stream
            .replace("{width}", "640")
            .replace("{height}", "360")
        )

        # QUEBRA CACHE PARA A IMAGEM SEMPRE ATUALIZAR
        thumbnail_final = f"{thumbnail_final}?t={int(datetime.now().timestamp())}"

        embed.set_image(url=thumbnail_final)

    embed.set_footer(text="Twitch • Ao vivo agora")

    if started_at:

        try:

            embed.timestamp = datetime.strptime(
                started_at, "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=timezone.utc)

        except Exception:

            pass

    return embed


@tasks.loop(seconds=INTERVALO_VERIFICACAO_LIVE)
async def verificar_live_twitch():

    global live_esta_ativa, live_stream_id_atual, live_mensagem_atual, live_ultima_atualizacao

    try:

        async with aiohttp.ClientSession() as session:

            stream = await obter_stream_twitch(session)

            # OFFLINE
            if stream is None:

                log(f"[LIVE CHECK] {TWITCH_USER_LOGIN} está OFFLINE.")

                if live_esta_ativa:

                    log(f"Live de {TWITCH_USER_LOGIN} terminou. Último aviso será mantido (não será apagado).")

                live_esta_ativa = False
                live_stream_id_atual = None
                live_mensagem_atual = None
                live_ultima_atualizacao = None

                return

            stream_id = stream.get("id")

            log(
                f"[LIVE CHECK] {TWITCH_USER_LOGIN} está ONLINE "
                f"(viewers: {stream.get('viewer_count')}, jogo: {stream.get('game_name')})."
            )

            canal = bot.get_channel(ID_CANAL_LIVE)

            if canal is None:

                log("ERRO: Canal de aviso de live não encontrado.")
                return

            agora = datetime.now(timezone.utc)

            # ---------------------------------------------------
            # CASO 1: LIVE NOVA (ainda não tinha aviso ativo)
            # ---------------------------------------------------
            if not live_esta_ativa or stream_id != live_stream_id_atual:

                log("=" * 60)
                log("NOVA LIVE DETECTADA")
                log(f"Streamer: {stream.get('user_name')}")
                log(f"Título: {stream.get('title')}")
                log(f"Jogo: {stream.get('game_name')}")
                log(f"Viewers: {stream.get('viewer_count')}")
                log("=" * 60)

                box_art_url = await obter_box_art_twitch(session, stream.get("game_id"))

                embed = criar_embed_live(stream, box_art_url)

                nova_mensagem = await canal.send(
                    content=f"@everyone 🔴 **{stream.get('user_name')}** está ao vivo na Twitch!",
                    embed=embed,
                    view=ViewAssistirLive()
                )

                log("Aviso de live enviado com sucesso.")

                live_esta_ativa = True
                live_stream_id_atual = stream_id
                live_mensagem_atual = nova_mensagem
                live_ultima_atualizacao = agora

                return

            # ---------------------------------------------------
            # CASO 2: LIVE JÁ ATIVA - VERIFICA SE PASSOU 30 MIN
            # ---------------------------------------------------
            tempo_desde_ultima_atualizacao = (
                (agora - live_ultima_atualizacao).total_seconds()
                if live_ultima_atualizacao else INTERVALO_ATUALIZACAO_LIVE
            )

            if tempo_desde_ultima_atualizacao < INTERVALO_ATUALIZACAO_LIVE:

                # AINDA NÃO É HORA DE ATUALIZAR
                return

            log(f"Atualizando aviso de live (views, duração e imagem) após {int(tempo_desde_ultima_atualizacao)}s.")

            box_art_url = await obter_box_art_twitch(session, stream.get("game_id"))

            embed = criar_embed_live(stream, box_art_url)

            nova_mensagem = await canal.send(
                content=f"🔴 **{stream.get('user_name')}** continua ao vivo na Twitch!",
                embed=embed,
                view=ViewAssistirLive()
            )

            # APAGA O AVISO ANTERIOR (só o intermediário, nunca o que marca o fim da live)
            if live_mensagem_atual is not None:

                try:

                    await live_mensagem_atual.delete()

                    log("Aviso anterior apagado com sucesso.")

                except Exception as erro:

                    log(f"ERRO AO APAGAR AVISO ANTERIOR: {erro}")

            live_mensagem_atual = nova_mensagem
            live_ultima_atualizacao = agora

            log("Aviso de live atualizado com sucesso.")

    except Exception as erro:

        log(f"ERRO NO LOOP DE VERIFICAÇÃO DE LIVE: {erro}")


@verificar_live_twitch.before_loop
async def antes_de_verificar_live():

    await bot.wait_until_ready()

    log("Loop de verificação de live pronto para iniciar.")

async def enviar_teste_live(canal):

    log("Enviando teste do aviso de live...")

    try:

        async with aiohttp.ClientSession() as session:

            stream = await obter_stream_twitch(session)

            # STREAMER ONLINE -> USA DADOS REAIS
            if stream is not None:

                log(f"[LIVE CHECK] {TWITCH_USER_LOGIN} está ONLINE. Usando dados reais no teste.")

                box_art_url = await obter_box_art_twitch(session, stream.get("game_id"))

                embed = criar_embed_live(stream, box_art_url)

                await canal.send(
                    content=f"🧪 **[TESTE]** {TWITCH_USER_LOGIN} está **ONLINE** agora:",
                    embed=embed,
                    view=ViewAssistirLive()
                )

                return True

            # STREAMER OFFLINE -> USA DADOS DE EXEMPLO
            log(f"[LIVE CHECK] {TWITCH_USER_LOGIN} está OFFLINE. Usando dados de exemplo no teste.")

            stream_exemplo = {
                "id": "0000000000",
                "user_name": "Murcega08",
                "title": "【+18】 Acabei de acordar || !comandos !pix",
                "game_name": "Hunt: Showdown",
                "game_id": "493057",
                "viewer_count": 3,
                "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "thumbnail_url": "https://static-cdn.jtvnw.net/previews-ttv/live_user_murcega08-{width}x{height}.jpg"
            }

            box_art_url = await obter_box_art_twitch(session, stream_exemplo["game_id"])

            embed = criar_embed_live(stream_exemplo, box_art_url)

            await canal.send(
                content=f"🧪 **[TESTE]** {TWITCH_USER_LOGIN} está **OFFLINE** agora. Exemplo de como o aviso vai aparecer:",
                embed=embed,
                view=ViewAssistirLive()
            )

            return True

    except Exception as erro:

        log(f"ERRO AO ENVIAR TESTE DE LIVE: {erro}")

        return False

# =========================================================
# BOT ONLINE
# =========================================================

@bot.event
async def on_ready():

    log("=" * 60)
    log("BOT ONLINE")
    log(f"Nome: {bot.user}")
    log(f"ID: {bot.user.id}")
    log("=" * 60)

    # LISTA SERVIDORES
    for guild in bot.guilds:

        log(f"Servidor conectado: {guild.name}")
        log(f"ID do servidor: {guild.id}")
        log(f"Membros: {guild.member_count}")

    # CANAL TESTE
    canal_teste = bot.get_channel(CANAL_TESTE)

    if canal_teste is None:

        log("ERRO: Canal de teste não encontrado.")

    else:

        log(f"Canal teste encontrado: {canal_teste.name}")

        # ---------------------------------------------------
        # TESTE: BOAS-VINDAS
        # ---------------------------------------------------

        if not os.path.exists(IMAGEM_BOAS):

            log("ERRO: Imagem de boas-vindas não encontrada.")
            log(f"Caminho procurado: {IMAGEM_BOAS}")

        else:

            log("Imagem de boas-vindas localizada com sucesso.")

            try:

                log("Carregando imagem da embed de boas-vindas...")

                arquivo = discord.File(
                    IMAGEM_BOAS,
                    filename="IMAGEMboas.png"
                )

                log("Imagem carregada.")

                embed = criar_embed(
                    "@Murceguinho",
                    bot.user.display_avatar.url
                )

                log("Embed de boas-vindas criada.")

                await canal_teste.send(
                    embed=embed,
                    file=arquivo
                )

                log("Mensagem de teste (boas-vindas) enviada com sucesso.")

            except Exception as erro:

                log(f"ERRO AO ENVIAR TESTE DE BOAS-VINDAS: {erro}")

        # ---------------------------------------------------
        # TESTE: REGRAS
        # ---------------------------------------------------

        log("Enviando teste do guia de regras...")

        sucesso_teste_regras = await enviar_regras(canal_teste)

        if sucesso_teste_regras:

            log("Mensagem de teste (regras) enviada com sucesso.")

        else:

            log("ERRO AO ENVIAR TESTE DE REGRAS.")

        # ---------------------------------------------------
        # TESTE: LIVE (TWITCH)
        # ---------------------------------------------------

        sucesso_teste_live = await enviar_teste_live(canal_teste)

        if sucesso_teste_live:

            log("Mensagem de teste (live) enviada com sucesso.")

        else:

            log("ERRO AO ENVIAR TESTE DE LIVE.")

    # CANAL DE REGRAS (ENVIO REAL DO GUIA)
    canal_regras = bot.get_channel(ID_CANAL_REGRAS)

    if canal_regras is None:

        log("ERRO: Canal de regras não encontrado.")

    else:

        log(f"Canal de regras encontrado: {canal_regras.name}")
        log("Enviando guia de regras no canal oficial...")

        sucesso_regras = await enviar_regras(canal_regras)

        if sucesso_regras:

            log("Guia de regras publicado com sucesso no canal oficial.")

        else:

            log("ERRO AO PUBLICAR GUIA DE REGRAS NO CANAL OFICIAL.")

    # INICIA MONITOR DE LIVE DA TWITCH
    if not verificar_live_twitch.is_running():

        verificar_live_twitch.start()

        log("Loop de verificação de live da Twitch iniciado.")

# =========================================================
# NOVO MEMBRO
# =========================================================

@bot.event
async def on_member_join(member):

    log("=" * 60)
    log("NOVO MEMBRO DETECTADO")
    log(f"Nome: {member}")
    log(f"ID: {member.id}")
    log(f"Servidor: {member.guild.name}")
    log(f"Avatar URL: {member.display_avatar.url}")
    log("=" * 60)

    # ---------------------------------------------------
    # CARGO AUTOMÁTICO
    # ---------------------------------------------------

    try:

        cargo = member.guild.get_role(ID_CARGO_AUTOMATICO)

        if cargo is None:

            log("ERRO: Cargo automático não encontrado no servidor.")

        else:

            await member.add_roles(cargo, reason="Cargo automático ao entrar no servidor.")

            log(f"Cargo '{cargo.name}' atribuído automaticamente a {member}.")

    except discord.Forbidden:

        log("ERRO: Bot sem permissão para atribuir o cargo automático (verifique MANAGE_ROLES e a posição do cargo do bot na hierarquia).")

    except Exception as erro:

        log(f"ERRO AO ATRIBUIR CARGO AUTOMÁTICO: {erro}")

    try:

        canal = bot.get_channel(CANAL_BOAS_VINDAS)

        if canal is None:

            log("ERRO: Canal de boas-vindas não encontrado.")
            return

        log(f"Canal encontrado: {canal.name}")

        # VERIFICA PERMISSÕES
        perms = canal.permissions_for(member.guild.me)

        log(f"VIEW_CHANNEL: {perms.view_channel}")
        log(f"SEND_MESSAGES: {perms.send_messages}")
        log(f"ATTACH_FILES: {perms.attach_files}")
        log(f"EMBED_LINKS: {perms.embed_links}")

        # SEM PERMISSÃO
        if not perms.view_channel:
            log("ERRO: Sem VIEW_CHANNEL")
            return

        if not perms.send_messages:
            log("ERRO: Sem SEND_MESSAGES")
            return

        if not perms.attach_files:
            log("ERRO: Sem ATTACH_FILES")
            return

        if not perms.embed_links:
            log("ERRO: Sem EMBED_LINKS")
            return

        # IMAGEM
        if not os.path.exists(IMAGEM_BOAS):

            log("ERRO: Imagem não encontrada.")
            log(f"Caminho: {IMAGEM_BOAS}")

            return

        log("Imagem localizada.")

        # CARREGA ARQUIVO
        arquivo = discord.File(
            IMAGEM_BOAS,
            filename="IMAGEMboas.png"
        )

        log("Arquivo carregado.")

        # EMBED
        embed = criar_embed(
            member.mention,
            member.display_avatar.url
        )

        log("Embed criada.")

        # ENVIO
        await canal.send(
            embed=embed,
            file=arquivo
        )

        log("BOAS-VINDAS ENVIADA COM SUCESSO.")

    except Exception as erro:

        log("ERRO NO EVENTO on_member_join")
        log(str(erro))

# =========================================================
# MONITOR DE MENSAGENS
# =========================================================

@bot.event
async def on_message(message):

    # IGNORA BOTS
    if message.author.bot:
        return

    log(
        f"MENSAGEM | "
        f"Autor: {message.author} | "
        f"Canal: {message.channel.name} | "
        f"Texto: {message.content}"
    )

    # SOMENTE NO CANAL PROTEGIDO
    if message.channel.id == CANAL_PROTEGIDO:

        conteudo = message.content.lower()

        for palavra in palavras_proibidas:

            if palavra in conteudo:

                log("=" * 60)
                log("PALAVRA PROIBIDA DETECTADA")
                log(f"Usuário: {message.author}")
                log(f"ID: {message.author.id}")
                log(f"Canal: {message.channel.name}")
                log(f"Palavra detectada: {palavra}")
                log(f"Mensagem original: {message.content}")
                log("=" * 60)

                # APAGA MSG
                try:

                    await message.delete()

                    log("Mensagem apagada.")

                except Exception as erro:

                    log(f"ERRO AO APAGAR MSG: {erro}")

                usuario_id = message.author.id

                # CRIA CONTADOR
                if usuario_id not in advertencias:

                    advertencias[usuario_id] = 0

                    log("Usuário adicionado no sistema de advertências.")

                # ADVERTÊNCIA
                advertencias[usuario_id] += 1

                avisos = advertencias[usuario_id]

                log(f"Advertências atuais: {avisos}")

                # PRIMEIRA
                if avisos == 1:

                    await message.channel.send(
                        f"⚠️ {message.author.mention} recebeu uma advertência por linguagem ofensiva.",
                        delete_after=10
                    )

                    log("Advertência enviada.")

                # SEGUNDA = BAN
                elif avisos >= 2:

                    try:

                        await message.guild.ban(
                            message.author,
                            reason="2 advertências por linguagem ofensiva."
                        )

                        await message.channel.send(
                            f"🔨 {message.author} foi banido por reincidência.",
                            delete_after=10
                        )

                        log("Usuário banido com sucesso.")

                    except Exception as erro:

                        log(f"ERRO AO BANIR USUÁRIO: {erro}")

                return

    await bot.process_commands(message)

# =========================================================
# ERROS GERAIS
# =========================================================

@bot.event
async def on_error(event, *args, **kwargs):

    log("=" * 60)
    log(f"ERRO GLOBAL DETECTADO")
    log(f"Evento: {event}")
    log("=" * 60)

# =========================================================
# INICIAR BOT
# =========================================================

log("INICIANDO BOT...")

if not TOKEN:

    log("ERRO FATAL: DISCORD_TOKEN não encontrado. Verifique se o arquivo .env existe e está preenchido.")
    sys.exit(1)

if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:

    log("AVISO: TWITCH_CLIENT_ID ou TWITCH_CLIENT_SECRET não encontrados no .env. O aviso de live não vai funcionar.")

bot.run(TOKEN)
