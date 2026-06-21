from concurrent.futures import ThreadPoolExecutor, as_completed

class ProParallelTranslator:

```
def __init__(self, translator, workers=4):
    self.translator = translator
    self.workers = workers

def translate_batch(self, items, callback=None):

    results = []
    total = len(items)
    done = 0

    with ThreadPoolExecutor(max_workers=self.workers) as executor:

        futures = {
            executor.submit(
                self.translator.translate,
                text
            ): text
            for text in items
        }

        for future in as_completed(futures):

            try:
                result = future.result()
            except Exception:
                result = futures[future]

            results.append(result)

            done += 1

            if callback:
                callback(done, total)

    return results
```
