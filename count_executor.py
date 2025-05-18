import time


def provide_countable(items, supplier) -> list:
    start = time.time_ns()
    results = []
    i = 0
    total = len(items)
    for item in items:
        try:
            results.append(supplier(item))
        except Exception as e:
            duration = int((time.time_ns() - start) / 1000000)
            print(f'Exception {e} during iteration {i}/{total} {duration}ms')
            return results
        i += 1
        duration = int((time.time_ns() - start) / 1000000)
        print(f'Executed {i}/{total} {duration}ms')
    return results
