import random
import simpy

ESTATISTICAS = {}
ESTATISTICAS["quantidade_recebidos"] =+ 0
ESTATISTICAS["EM_ESPERA"] = []
ESTATISTICAS["TEMPOS_ATENDIMENTOS"] = []

RANDOM_SEED = 43
TEMPO_ESPERA = 2      # Minutos de espera de um cliente
EXPONENCIAL_LAMBDA = 0.5 # VALOR DO LAMBA DA FUNCAO EXPONENCIAL PARA CRIACAO DE FREGUES      
TEMPO_SIM = 20     # TEMPO DA SIMULACAO EM MINUTOS

class Escalonador(object):
    def __init__(self, env, tempo_espera):
        self.env = env
        self.escalonador = simpy.Resource(env)
        self.tempo_espera = tempo_espera
        self.atendidos = 0

    def atende(self, fregues):

        yield self.env.timeout(TEMPO_ESPERA)
        self.atendidos += 1

        #GUARDA QUANTOS USUARIOS EM ESPERA FICARAM NAQUELE PASSO
        #GUARDA QUANTOS FORAM ATENDIDOS
        #GUARDA OS TEMPOS DE ATENDIMENTO FAZENDO A DIFERENCA ENTRE ENTRADA E TEMPO ATUAL
        ESTATISTICAS["EM_ESPERA"].append(ESTATISTICAS["quantidade_recebidos"] - self.atendidos)
        ESTATISTICAS["quantidade_atendidos"] = self.atendidos
        ESTATISTICAS["TEMPOS_ATENDIMENTOS"].append(self.env.now - ESTATISTICAS[fregues]["entrada"])


def fregues(env, nome, ec):
    print('%s entra na fila em %.2f.' % (nome, env.now))

    #GUARDA NOME DO FREGUES PARA PEGAR ENTRADA
    #ADICIONA MAIS UM NA QUANTIDADE DE SOLICITACOES RECEBIDAS
    ESTATISTICAS["quantidade_recebidos"] = ESTATISTICAS["quantidade_recebidos"] + 1
    ESTATISTICAS[nome] = {"entrada": env.now}

    with ec.escalonador.request() as request:
        yield request
        print('%s comeca servico %.2f.' % (nome, env.now))
        yield env.process(ec.atende(nome))
        print('%s termina servico em %.2f.' % (nome, env.now))


def setup(env, tempo_espera, exponencial_lamdba):
    escalonador = Escalonador(env, tempo_espera)

    i = 0

    while True:
        #Para uniforme: random.uniform(a, b)
        #Para normal: random.normalvariate(mu, sigma)
        t = random.expovariate(exponencial_lamdba)

        #Espera tempo da distribuicao
        yield env.timeout(t)

        #Cria novo fregues e adiciona na fila
        i += 1
        env.process(fregues(env, 'Fregues %d' % i, escalonador))

#Cria tudo
print('Escalonador')
random.seed(RANDOM_SEED) 
env = simpy.Environment()
env.process(setup(env, TEMPO_ESPERA, EXPONENCIAL_LAMBDA))
env.run(until=TEMPO_SIM)

print "\n------------------------------------------\n"
print "Duracao da Simulacao: %d minutos" % TEMPO_SIM
print "Requisicoes Recebidas: %d fregueses recebidos" % ESTATISTICAS["quantidade_recebidos"]
print "Requisicoes Atendidas: %d fregueses atendidos" % ESTATISTICAS["quantidade_atendidos"]
print "Tempo medio de atendimento: %.2f minutos" % (sum(ESTATISTICAS["TEMPOS_ATENDIMENTOS"])  / float(len(ESTATISTICAS["TEMPOS_ATENDIMENTOS"])))
print "Quantidade media de elementos em espera: %.2f fregueses" % (sum(ESTATISTICAS["EM_ESPERA"])  / float(len(ESTATISTICAS["EM_ESPERA"])))