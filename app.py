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
        
filmes_por_genero = TabelaHash(tamanho=127)
todos_os_filmes = []

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

                generos = [g.strip().lower() for g in row['Genre'].split(',')]

                for genero in generos:
                    filmes_por_genero.inserir(genero, filme)
    except Exception as e:
        print(f"Erro ao ler o CSV: {e}")

carregar_dados()

@app.route('/')
def index():
    query = request.args.get('busca', '').strip().lower()

    if query:
        resultados = filmes_por_genero.buscar(query)
    else:
        resultados = todos_os_filmes[:20]
    return render_template('index.html', filmes=resultados, busca=query)

if __name__ == '__main__':
    app.run(debug=True)