# Resumo

**Pato vs. Torrada** é um clicker onde você é um patinho simples e precisa derrotar todas as torradas.
Compre mais patos para te ajudar e evolua-os!
Descubra todas as 10 torradas e vença elas até o nível 54!

# Como rodar o jogo no Visual Studio Code

Baixe como zip

Extraia o zip Pato-vs.-Torrada-main, você criará uma pasta, ela se chamará Pato-vs.-Torrada-main

Abra no VScode a pasta que contém todos os arquivos

Certifique-se que tem o Python instalado, com o pygame.exe no path

Instale a biblioteca pygame no Vscode através do comando
```
pip install pygame
```
Use o jogo.py para rodar o código

Pronto agora é só jogar!

# Informações sobre a gameplay

O jogo começa com um pato inicial que dá 1 de dano nas torradas.
A moeda do jogo é a Patocoin, que você ganha ao matar as torradas e usa pra comprar patos.

Patos disponíveis para comprar:
  - Pato Siamês: Adiciona 10 de DPS na primeira compra. A cada compra adiciona mais 10, mas aumenta o preço em 1.5.
  - Pato dobrado: Dobra o dano do seu clique (pato simples). A cada compra dobra o dano mas triplica o custo.
  - Pato musculoso: Adiciona um clique automático e escala com o dano de clique. A cada compra aumenta a frequência de cliques em -50 milissegundos, mas dobra de preço.
  - Pato realista: Duplica o DPS a cada compra, mas quadriplica o preço.
  - Pato burguês: Ainda não foi implementado no jogo. Mas seus efeitos seriam aumentar o dano, DPS e patocois temporariamente.

A cada nível que você sobe, as torradas ficam mais fortes, mas também dão mais patocoins. Nos níveis múltiplos de 5, a torrada é um boss, que você tem apenas 10 segundos para matar.
  - Se você conseguir vencê-lo dentro do tempo, avançará para o próximo nível.
  - Se não conseguir matar o boss dentro dos 10 segundos, a vida dele volta a ficar cheia.
    - Aqui você tem a opção de voltar os níveis anteriores e também trancar em um nível específico, para juntar dinheiro e conseguir mais patos para vencer o boss.
   
# Cheats

Aperte a tecla "p" para ganhar patocoins

# Ideias futuras:
- Torradas boss tem armadura contra DPS.
- Pato burguês chega de jatinho particular e adiciona buffs em todos os patos.

# Inspirações

**Pato vs. Torrada** foi inspirado em jogos clickers, mas tem como principal inspiração para seu modelo de gameplay, o jogo Clicker Heroes e Duck Pond!

Esse jogo foi feito 100% por mim.

[Vídeo explicando a programação e mostrando a gameplay](https://drive.google.com/file/d/1RXUL7ZQSNVrTUbzpCTccicB7_eti3Wk-/view?usp=sharing)
