
"""
Gerencia a gravação de dados numa tabela no banco.
"""

# TODO: ajustar tratamento de erro para tratamento próprio

import blipy.erro as erro
from blipy.profiling import ProfilingPerformance
from blipy.enum_tipo_col_bd import TpColBD as tp


class TabelaSaida(ProfilingPerformance):
    """
    Tabela a ser gravada no banco de dados.
    """

    # tratamento de erro
    # este atributo é um atributo de classe, portanto pode ser alterado pora
    # todas as instâncias dessa classe, se se quiser um tipo de tratamento de
    # erro diferente de imprimir mensagem no console.
    # Para alterá-lo, usar sintaxe "TabelaSaida.e = <novo valor>"
    e = erro.console

    def __init__(self, 
        nome, colunas, conexao_bd, qtd_insercoes_simultaneas=10_000):
        """
        Args:
            nome                     : nome da tabela no banco
            colunas                  : dict com objetos do classe Coluna
                                       representando as colunas do banco
            conexao_bd               : conexão com o banco de dados
            qtd_insercoes_simultaneas: quantos registros vão ser submetidos de
                                       uma só vez para inserção,
                                       simultaneamente, no banco de dados, a
                                       fim de melhorar a performance
        """

        self.__nome         = nome
        self.__conexao_bd   = conexao_bd
        self.col            = colunas

        self._profiling_on = False

        # atributos para permitir inserir vários registros de uma só vez no
        # banco, melhorando substancialmente a performance da carga
        self.__qtd_insercoes_simultaneas = qtd_insercoes_simultaneas
        self.__qtd_registros_na_fila = 0
        self.__registros_para_insercao = []

    def __del__(self):
        # salva o último bloco de registros em memória no banco de dados, se
        # houver registros remanescentes
        if self.__qtd_registros_na_fila > 0:
            self.__salva_registros_no_banco()

    @property
    def qtd_insercoes_simultaneas(self):
        return self.__qtd_insercoes_simultaneas
    @qtd_insercoes_simultaneas.setter
    def qtd_insercoes_simultaneas(self, qtd_insercoes_simultaneas):
        self.__qtd_insercoes_simultaneas = qtd_insercoes_simultaneas

    def __salva_registros_no_banco(self):
        # monta statement de insert no formato
        # insert into tabela (col1, col2, ...) values (:1, :2, ...)
        cols = ""
        for coluna in self.col:
            cols += self.col[coluna].nome + ", "
        cols = cols[:len(cols)-2]

        insert_stmt =   "insert into " + self.__nome +  \
                        " (" + cols + ") values ("

        i = 1
        for col in self.col:
            insert_stmt += ":" + str(i) + ","
            i += 1

        insert_stmt = insert_stmt[:len(insert_stmt)-1]
        insert_stmt += ")"

        # insere de uma só vez todos os registros que estão armazenados na
        # memória
        self.__conexao_bd.insere_varios_registros(
                insert_stmt, 
                self.__registros_para_insercao)

        self.__qtd_registros_na_fila = 0
        self.__registros_para_insercao = []

    # TODO: criar parâmetro para estratégia de gravacao (limpa e grava tudo, insert, update etc.)
    def grava_registro(self):
        """
        Grava os dados da tabela no banco.

        Um erro de banco disparará uma exceção.
        """

        # TODO: implementar os outros estratégias além do insert: insert_update, update_insert, update

        if self._profiling_on:
            self._inicia_timer()

        # monta o registro a ser inserido no banco como uma tupla do python
        aux = []
        for coluna in self.col:
            if  self.col[coluna].valor is None or   \
                str(self.col[coluna].valor) == "nan":

                aux.append(None)
            else:
                # TODO: tratar demais tipos possíveis do banco (como bool)
                if self.col[coluna].tipo == tp.STRING:
                    # se a conexão for feita via jdbc, o tipo será
                    # java.lang.String e esse cast será necessário. Se a conexão
                    # não for jdbc, este cast não faz nada
                    aux.append(str(self.col[coluna].valor))

                elif self.col[coluna].tipo == tp.INT     or  \
                     self.col[coluna].tipo == tp.NUMBER  or  \
                     self.col[coluna].tipo == tp.DATE:

                    aux.append(self.col[coluna].valor)

                else:
                    self.e._(   "Tipo de dado inválido para a coluna " \
                                + self.col[coluna].nome + " da tabela " + \
                                self.__nome + ".")
                    if self._profiling_on:
                        self._finaliza_timer()
                    # TODO: disparar uma exceção específica pro master job saber se continua ou não (?)
                    raise RuntimeError
        registro = tuple(i for i in aux)

        if self.__qtd_registros_na_fila < self.__qtd_insercoes_simultaneas:
            # vai guardanado registros na memória para depois inseri-los de uma
            # só vez
            self.__registros_para_insercao.append(registro)
            self.__qtd_registros_na_fila += 1

        if self.__qtd_registros_na_fila == self.__qtd_insercoes_simultaneas:
            # salva os registros da memória no banco de dados a cada vez que se
            # atinge o parâmetro de quantidade de inserções simultâneas. O
            # último bloco remanescente de registros em memória, se houver,
            # será salvo no destrutor desse objeto 
            self.__salva_registros_no_banco()

        if self._profiling_on:
            self._finaliza_timer()

    def habilita_profiling_performance(self, path_csv=""):
        """
        Habilita o registro de performance para essa classe em si e para todas
        as colunas que compõem a tabela.
        """
        
        # habilita profiling pra todas as colunas que compõem a tabela
        for key in list(self.col):
            self.col[key].habilita_profiling_performance(path_csv)

        self._profiling_on = True

class Coluna(ProfilingPerformance):
    """
    Uma coluna de uma tabela do banco de dados.
    """

# TODO: parâmetro 'tipo' seria interessante se fosse pra fazer um cast automático do resultado da ft para o valor da coluna
    def __init__(self, nome, tipo, func_transf):
        """
        Args:
            nome        : nome da coluna no banco de dados
            tipo        : tipo da coluna no banco de dados. É um elemento do 
                          enum tipo_col_bd
            func_transf : função de transformação que será aplicada para obter
                          o valor da coluna. Se for None, valor da coluna no 
                          banco de dados será NULL
        """
        self.nome           = nome
        self.tipo           = tipo
        self.__func_transf  = func_transf
        self.valor          = None

        # tratamento de erro
        # este atributo é público, portanto pode ser alterado por quem usa 
        # esta classe se quiser um tipo de tratamento de erro diferente de 
        # imprimir mensagem no console
        self.e = erro.console

        self._profiling_on = False

    def calcula_valor(self, entradas=None):
        """
        Calcula o valor da coluna de acordo com sua função de transformação.
        Se a função de transformação for None, valor será NULL (None).

        Arg:
            entradas    : tupla de valores a ser passado para a função de
                          transformação
        """

        if self._profiling_on:
            self._inicia_timer()

        if self.__func_transf is None:
            self.valor = None
        else:
            try:
                self.valor = self.__func_transf.transforma(entradas)
            except Exception as err:
                self.e._(
                    f"Erro ao calcular o valor da coluna {self.nome}." + 
                    "\n" + str(err))
                if self._profiling_on:
                    self._finaliza_timer()
                raise RuntimeError

        if self._profiling_on:
            self._finaliza_timer()

