import random

import simpy


RANDOM_SEED = 42
TEMPO_ESPERA = 2      # Minutos de espera de um cliente
EXPONENCIAL_LAMBDA = 0.5 # VALOR DO LAMBA DA FUNCAO EXPONENCIAL PARA CRIACAO DE FREGUES      
TEMPO_SIM = 20     # TEMPO DA SIMULACAO EM MINUTOS

class Escalonador(object):
    def __init__(self, env, tempo_espera):
        self.env = env
        self.escalonador = simpy.Resource(env)
        self.tempo_espera = tempo_espera
        self.atendidos = 0

    def wash(self, fregues):
        yield self.env.timeout(TEMPO_ESPERA)
        self.atendidos += 1
        print self.atendidos


def fregues(env, nome, ec):
    print('%s entra na fila em %.2f.' % (nome, env.now))
    with ec.escalonador.request() as request:
        yield request
        print('%s comeca servico %.2f.' % (nome, env.now))
        yield env.process(ec.wash(nome))
        print('%s termina servico em %.2f.' % (nome, env.now))


def setup(env, tempo_espera, exponencial_lamdba):
    escalonador = Escalonador(env, tempo_espera)

    i = 0

    while True:
        t = random.expovariate(exponencial_lamdba)
        yield env.timeout(t)
        i += 1
        env.process(fregues(env, 'Fregues %d' % i, escalonador))

# Setup and start the simulation
print('Escalonador')
random.seed(RANDOM_SEED)  # This helps reproducing the results
env = simpy.Environment()
env.process(setup(env, TEMPO_ESPERA, EXPONENCIAL_LAMBDA))
env.run(until=TEMPO_SIM)