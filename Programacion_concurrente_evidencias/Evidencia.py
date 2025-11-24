import time
import threading
import multiprocessing as mp
import concurrent.futures
import random
from typing import List, Dict
import math

def simulate_io_task_modern(task_id: int, delay: float = 1.0) -> Dict:
    thread_name = threading.current_thread().name
    print(f"🧵 {thread_name}: Iniciando tarea {task_id} (delay={delay}s)")
    start_time = time.time()
    
    time.sleep(1.0)
    random_delay = random.uniform(0, 0.5)
    time.sleep(random_delay)  
    
    duration = time.time() - start_time
    
    result = {
        'task_id': task_id,
        'fixed_delay': 1.0,
        'random_delay': round(random_delay, 3),
        'total_duration': round(duration, 3),
        'status': 'completed'
    }
    
    print(f"✅ {thread_name}: Completado {task_id} en {duration:.2f}s")
    return result

def simulate_slow_task(task_id: int, delay: float = 2.0) -> dict:
    print(f"⏱️ Tarea {task_id}: Iniciando proceso de bloqueo...")
    start_time = time.time()
    
    time.sleep(1.0)
    random_delay = random.uniform(0, 0.5)
    time.sleep(random_delay)
    
    duration = time.time() - start_time
    print(f"✅ Tarea {task_id}: Completada en {duration:.3f}s (fijo: 1.0s, aleatorio: {random_delay:.3f}s)")
    
    return {
        'task_id': task_id,
        'fixed_delay': 1.0,
        'random_delay': round(random_delay, 3),
        'total_duration': round(duration, 3)
    }

def demonstrate_sequential_problems():
    print("\n" + "🐌" + "="*60)
    print("🐌 EXPERIMENTO 1.1: 20 tareas de manera SECUENCIAL")
    print("="*60)
    
    total_start = time.time()
    results = []
    
    for i in range(20):
        result = simulate_slow_task(i + 1)
        results.append(result)
    
    total_time = time.time() - total_start
    print(f"\n⏱️ TIEMPO TOTAL SECUENCIAL: {total_time:.2f} segundos")
    
    return results, total_time

def simulate_tasks_with_threadpool(tasks: List[int], max_workers: int = 10) -> List[Dict]:
    print("\n" + "🧵" + "="*60)
    print("🧵 EXPERIMENTO 1.2: 20 tareas con 10 workers")
    print("="*60)
    
    total_start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        print(f"📋 Enviando {len(tasks)} tareas al ThreadPool...")
        
        future_to_task = {
            executor.submit(simulate_io_task_modern, task): task
            for task in tasks
        }
        
        results = []
        
        for future in concurrent.futures.as_completed(future_to_task):
            task_id = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"❌ Error procesando tarea {task_id}: {e}")
    
    total_time = time.time() - total_start
    print(f"\n⏱️ TIEMPO TOTAL THREADPOOL: {total_time:.2f} segundos")
    
    return results, total_time

def find_primes_processpool(tasks: List[int], max_workers: int = 10) -> List[Dict]:
    print("\n" + "🔥" + "="*60)
    print("🔥 EXPERIMENTO 1.3: 20 tareas con 10 workers")
    print("="*60)
    
    total_start = time.time()
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        print(f"📋 Enviando {len(tasks)} tareas al ProcessPool...")
        
        future_to_task = {
            executor.submit(simulate_io_task_modern, task): task
            for task in tasks
        }
        
        results = []
        
        for future in concurrent.futures.as_completed(future_to_task):
            task_id = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"❌ Error procesando tarea {task_id}: {e}")
    
    total_time = time.time() - total_start
    print(f"\n⏱️ TIEMPO TOTAL PROCESSPOOL: {total_time:.2f} segundos")
    
    return results, total_time

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def find_primes_in_range(start: int, end: int, worker_id: int = 0) -> Dict:
    print(f"🧮 Worker {worker_id}: Calculando suma de factoriales de {start} a {end}")
    start_time = time.time()
    total_sum = 0
    for i in range(start, end + 1):
        fact = 1
        for j in range(2, i + 1):
            fact *= j
        total_sum += fact
    
    duration = time.time() - start_time
    print(f"✅ Worker {worker_id}: Suma completada en {duration:.2f}s - Rango {start}-{end}")
    
    return {
        'worker_id': worker_id,
        'start': start,
        'end': end,
        'sum': total_sum,
        'duration': duration
    }

def find_primes_sequential(ranges: List[tuple]) -> List[int]:
    print("\n" + "🐌" + "="*60)
    print(f"🐌 EXPERIMENTO 2.1: Suma de factoriales (SECUENCIAL)")
    print("="*60)
    
    total_start = time.time()
    all_sums = []
    
    for i, (start, end) in enumerate(ranges):
        result = find_primes_in_range(start, end, i+1)
        all_sums.append(result['sum'])
    
    total_time = time.time() - total_start
    total_sum = sum(all_sums)
    
    print(f"\n⏱️ TIEMPO TOTAL SECUENCIAL: {total_time:.2f} segundos")
    print(f"📊 Suma total de factoriales: {total_sum}")
    
    return total_sum, total_time

def find_primes_threading(ranges: List[tuple]) -> List[int]:
    print("\n" + "🧵" + "="*60)
    print(f"🧵 EXPERIMENTO 2.2: Suma de factoriales (4 workers)")
    print("="*60)
    
    total_start = time.time()
    all_sums = []
    lock = threading.Lock()
    threads = []
    
    def threaded_worker(start, end, worker_id):
        result = find_primes_in_range(start, end, worker_id)
        with lock:
            all_sums.append(result['sum'])
    
    for i, (start, end) in enumerate(ranges):
        thread = threading.Thread(
            target=threaded_worker,
            args=(start, end, i+1)
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    total_time = time.time() - total_start
    total_sum = sum(all_sums)
    
    print(f"\n⏱️ TIEMPO TOTAL THREADING: {total_time:.2f} segundos")
    print(f"📊 Suma total de factoriales: {total_sum}")
    
    return total_sum, total_time

def find_primes_multiprocessing_manual(ranges: List[tuple]) -> List[int]:
    print("\n" + "🔥" + "="*60)
    print(f"🔥 EXPERIMENTO 2.3: Suma de factoriales (MULTIPROCESSING - 4 workers)")
    print("="*60)
    
    total_start = time.time()
    processes = []
    manager = mp.Manager()
    shared_results = manager.list()
    
    for i, (start, end) in enumerate(ranges):
        process = mp.Process(
            target=multiprocessing_worker,
            args=(start, end, i+1, shared_results)
        )
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()
    
    total_sum = sum(shared_results)
    total_time = time.time() - total_start
    
    print(f"\n⏱️ TIEMPO TOTAL MULTIPROCESSING: {total_time:.2f} segundos")
    print(f"📊 Suma total de factoriales: {total_sum}")
    
    return total_sum, total_time

def multiprocessing_worker(start: int, end: int, worker_id: int, shared_results):
    result = find_primes_in_range(start, end, worker_id)
    shared_results.append(result['sum'])

def run_all_experiments():
    print("🎯" + "="*70)
    print("🎯 EJECUTANDO LOS 6 EXPERIMENTOS")
    print("="*70)
    
    results = {}
    
    print("\n🔬 EXPERIMENTO 1: Procesos de bloqueo con time.sleep()")
    print("="*50)
    
    print("\n" + "1.1" + "="*30)
    results_exp1_1, time1_1 = demonstrate_sequential_problems()
    results['exp1_1'] = time1_1
    
    print("\n" + "1.2" + "="*30)
    tasks = list(range(1, 21))
    results_exp1_2, time1_2 = simulate_tasks_with_threadpool(tasks, 10)
    results['exp1_2'] = time1_2
    
    print("\n" + "1.3" + "="*30)
    results_exp1_3, time1_3 = find_primes_processpool(tasks, 10)
    results['exp1_3'] = time1_3
    
    print("\n🔬 EXPERIMENTO 2: Suma de factoriales")
    print("="*50)
    
    n = 500
    
    chunk_size = n // 4
    ranges = [
        (1, chunk_size),
        (chunk_size + 1, chunk_size * 2),
        (chunk_size * 2 + 1, chunk_size * 3),
        (chunk_size * 3 + 1, n)
    ]
    
    print(f"📋 Rangos de trabajo: {ranges}")
    
    print("\n" + "2.1" + "="*30)
    sum2_1, time2_1 = find_primes_sequential(ranges)
    results['exp2_1'] = time2_1
    
    print("\n" + "2.2" + "="*30)
    sum2_2, time2_2 = find_primes_threading(ranges)
    results['exp2_2'] = time2_2
    
    print("\n" + "2.3" + "="*30)
    sum2_3, time2_3 = find_primes_multiprocessing_manual(ranges)
    results['exp2_3'] = time2_3
    
    #Resumen
    print("\n" + "📊" + "="*70)
    print("📊 RESUMEN FINAL DE TODOS LOS EXPERIMENTOS")
    print("="*70)
    
    print(f"\n🔬 EXPERIMENTO 1 (time.sleep):")
    print(f"   1.1 Secuencial:    {results['exp1_1']:.2f}s")
    print(f"   1.2 ThreadPool:    {results['exp1_2']:.2f}s (speedup: {results['exp1_1']/results['exp1_2']:.2f}x)")
    print(f"   1.3 ProcessPool:   {results['exp1_3']:.2f}s (speedup: {results['exp1_1']/results['exp1_3']:.2f}x)")
    
    print(f"\n🔬 EXPERIMENTO 2 (factoriales):")
    print(f"   2.1 Secuencial:    {results['exp2_1']:.2f}s")
    print(f"   2.2 Threading:     {results['exp2_2']:.2f}s (speedup: {results['exp2_1']/results['exp2_2']:.2f}x)")
    print(f"   2.3 Multiprocessing: {results['exp2_3']:.2f}s (speedup: {results['exp2_1']/results['exp2_3']:.2f}x)")
    
    return results

if __name__ == "__main__":
    print("🎯 INICIANDO EXPERIMENTOS DE CONCURRENCIA Y PARALELISMO")
    
    results = run_all_experiments()
    
    print("\n✅ TODOS LOS EXPERIMENTOS COMPLETADOS")
