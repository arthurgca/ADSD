import random
import simpy

def inputExponencial():
    parametro =  input("Informe o lambda: ")
    return parametro, 'lambda'

def inputUniforme():
    parametros = raw_input("Informe o a e b separados por virgula: ")
    parametros = parametros.split(",")
    return parametros, "'a' e 'b'"

def inputNormal():
    parametros = raw_input("Informe o a media e o desvio padrao separados por virgula: ")
    parametros = parametros.split(",")
    return parametros, 'media e desvio padrao'

valido = False

while(not valido):
    try:
        switcher = {
            "exponencial": inputExponencial,
            "uniforme": inputUniforme,
            "normal": inputNormal,
        }

        distribuicao = raw_input("Qual a distribuicao escolhida? (exponencial, uniforme, normal): ")
        parametros, parametros_string = switcher[distribuicao]()

        TEMPO_SERVICO = input("Tempo de servico medio por fregues em minutos: ")
        TEMPO_SIM = input("Tempo total da simulacao em minutos: ")
        NUM_REPETICOES = input("Numero de repeticoes: ")
        valido = True
    except Exception as e:
        print "Erro na leitura de dados, recomece."

for repeticao in range(0,NUM_REPETICOES):
    RANDOM_SEED = random.random()

    print "\n------------------------------------------\n"
    ESTATISTICAS = {}
    ESTATISTICAS["quantidade_recebidos"] = 0
    ESTATISTICAS["quantidade_atendidos"] = 0
    ESTATISTICAS["EM_ESPERA"] = []
    ESTATISTICAS["TEMPOS_ATENDIMENTOS"] = []

    class Escalonador(object):
        def __init__(self, env, tempo_servico):
            self.env = env
            self.escalonador = simpy.Resource(env)
            self.tempo_servico = tempo_servico
            self.atendidos = 0

        def atende(self, fregues):

            yield self.env.timeout(TEMPO_SERVICO)
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


    def setup(env, tempo_servico, distribuicao, parametros):
        escalonador = Escalonador(env, tempo_servico)

        i = 0

        while True:
            #Para uniforme: random.uniform(a, b)
            #Para normal: random.normalvariate(mu, sigma)
            if (distribuicao == "exponencial"):
                t = random.expovariate(parametros)
            elif (distribuicao == "uniforme"):
                parametros = map(int, parametros)
                t = random.uniform(parametros[0], parametros[1])
            elif (distribuicao == "normal"):
                parametros = map(int, parametros)
                t = random.normalvariate(parametros[0], parametros[1])

            #Espera tempo da distribuicao
            yield env.timeout(t)

            #Cria novo fregues e adiciona na fila
            i += 1
            env.process(fregues(env, 'Fregues %d' % i, escalonador))

    #Cria tudo
    print('Escalonador')
    random.seed(RANDOM_SEED) 
    env = simpy.Environment()
    env.process(setup(env, TEMPO_SERVICO, distribuicao, parametros))
    env.run(until=TEMPO_SIM)

    print "\n------------------------------------------\n"
    print "Distribuicao: %s" % distribuicao
    print "Parametros %s: %s" % (parametros_string, parametros)
    print "Duracao da Simulacao: %d minutos" % TEMPO_SIM
    print "Requisicoes Recebidas: %d fregueses recebidos" % ESTATISTICAS["quantidade_recebidos"]
    print "Requisicoes Atendidas: %d fregueses atendidos" % ESTATISTICAS["quantidade_atendidos"]
    print "Tempo medio de atendimento: %.2f minutos" % (sum(ESTATISTICAS["TEMPOS_ATENDIMENTOS"])  / float(len(ESTATISTICAS["TEMPOS_ATENDIMENTOS"])))
    print "Quantidade media de elementos em espera: %.2f fregueses" % (sum(ESTATISTICAS["EM_ESPERA"])  / float(len(ESTATISTICAS["EM_ESPERA"])))