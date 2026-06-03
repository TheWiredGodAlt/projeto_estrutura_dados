import time
import psutil
import os

class PerformanceMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())

    def measure_time_and_memory(self, func, *args, **kwargs):
        """
        Mede o tempo de execução (em segundos) e o consumo de memória (em MB)
        de uma determinada função.

        Args:
            func: A função a ser medida.
            *args: Argumentos posicionais da função.
            **kwargs: Argumentos nomeados da função.

        Returns:
            tuple: (resultado_da_funcao, tempo_execucao, memoria_consumida)
        """
        # Marca o início da medição
        start_time = time.perf_counter()
        start_memory = self.process.memory_info().rss / (1024 * 1024)  # Em MB

        # Executa a função
        result = func(*args, **kwargs)

        # Marca o fim da medição
        end_time = time.perf_counter()
        end_memory = self.process.memory_info().rss / (1024 * 1024)

        execution_time = end_time - start_time
        memory_used = max(0, end_memory - start_memory)  # Evita valores negativos

        return result, execution_time, memory_used