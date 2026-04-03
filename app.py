from flask import Flask, render_template, request
import csv

app = Flask(__name__)

class No:
    def __init__(self, chave, valor_filme):
        self.chave = chave
        self.valores = [valor_filme] 
        self.proximo = None

class TabelaHash:
    def __init__(self, tamanho=127):
        self.tamanho = tamanho
        self.tabela = [None] * self.tamanho

    def _funcao_hash(self, chave):
        soma = 0
        for caractere in chave:
            soma += ord(caractere)
        return soma % self.tamanho
    
    def inserir(self, chave, valor_filme):
        indice = self._funcao_hash(chave)

        if self.tabela[indice] is None:
            self.tabela[indice] = No(chave, valor_filme)
        else:
            atual = self.tabela[indice]
            while True:
                if atual.chave == chave:
                    atual.valores.append(valor_filme)
                    break

                if atual.proximo is None:
                    atual.proximo = No(chave, valor_filme)
                    break
                atual = atual.proximo
            
    def buscar(self, chave):
        indice = self._funcao_hash(chave)
        atual = self.tabela[indice]

        while atual is not None:
            if atual.chave == chave:
                return atual.valores
            atual = atual.proximo

        return []
    
def busca_seq_nome(lista_filmes, pedaco_nome):
    resultados = []
    pedaco_nome = pedaco_nome.lower()
    for filme in lista_filmes:
        if pedaco_nome in filme['titulo'].lower():
            resultados.append(filme)
    return resultados

def busca_seq_ano(lista_filmes, ano):
    resultados = []
    for filme in lista_filmes:
        if filme['ano'] == ano:
            resultados.append(filme)
    return resultados
        
filmes_por_genero = TabelaHash(tamanho=127)
todos_os_filmes = []
generos_disponiveis = set()
anos_disponiveis = set()

def carregar_dados():
    try:
        with open('imdb_top_1000.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                filme = {
                    'titulo': row['Series_Title'],
                    'poster': row['Poster_Link'],
                    'ano': row['Released_Year'],
                    'nota': row['IMDB_Rating'],
                    'genero_str': row['Genre']
                }
                todos_os_filmes.append(filme)

                if filme['ano']:
                    anos_disponiveis.add(filme['ano'])

                generos = [g.strip().lower() for g in row['Genre'].split(',')]
                for genero in generos:
                    if genero:
                        filmes_por_genero.inserir(genero, filme)
                        generos_disponiveis.add(genero)

    except Exception as e:
        print(f"Erro ao ler o CSV: {e}")

carregar_dados()
lista_generos = sorted(list(generos_disponiveis))
lista_anos = sorted(list(anos_disponiveis), reverse=True)

@app.route('/')
def index():

    query_nome = request.args.get('nome', '').strip()
    query_genero = request.args.get('genero', '').strip().lower()
    query_ano = request.args.get('ano', '').strip()

    if query_genero:
        resultados = filmes_por_genero.buscar(query_genero)
    else:
        resultados = todos_os_filmes.copy()
    
    if query_nome:
        resultados = busca_seq_nome(resultados, query_nome)

    if query_ano:
        resultados = busca_seq_ano(resultados, query_ano)
    
    if not query_nome and not query_genero and not query_ano:
        resultados_exibicao = resultados

    else:
        resultados_exibicao = resultados

    return render_template('index.html',
                           filmes=resultados_exibicao, 
                           generos=lista_generos, 
                           anos=lista_anos,
                           busca_nome=query_nome,
                           busca_genero=query_genero,
                           busca_ano=query_ano)

if __name__ == '__main__':
    app.run(debug=True)