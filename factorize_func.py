import multiprocessing
# Виміряємо час виконання для синхронної версії
import time


def factorize(*numbers):
    results = []
    for num in numbers:
        factors = []
        for i in range(1, num + 1):
            if num % i == 0:
                factors.append(i)
        results.append(factors)
    return results


# Покращимо продуктивність використовуючи кілька ядер процесора для паралельних обчислень

def factorize_parallel(*numbers):
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())  # Використовуємо кілька ядер процесора
    results = pool.map(factorize_single, numbers)  # Викликаємо factorize_single паралельно для кожного числа
    pool.close()
    pool.join()
    return results


def factorize_single(num):
    factors = []
    for i in range(1, num + 1):
        if num % i == 0:
            factors.append(i)
    return factors


if __name__ == '__main__' or 'get_ipython' in globals():
    multiprocessing.freeze_support()

    start_time_sync = time.time()
    a, b, c, d = factorize(128, 255, 99999, 10651060)
    end_time_sync = time.time()
    print("Синхронна версія: ", end_time_sync - start_time_sync, "секунд")
    print(f'{a}, {b}, {c}, {d}')

    # Виміряємо час виконання для версії з використанням кількох ядер процесора
    start_time_parallel = time.time()
    a, b, c, d = factorize_parallel(128, 255, 99999, 10651060)
    end_time_parallel = time.time()
    print("Паралельна версія: ", end_time_parallel - start_time_parallel, "секунд")
    print(f'{a}, {b}, {c}, {d}')
