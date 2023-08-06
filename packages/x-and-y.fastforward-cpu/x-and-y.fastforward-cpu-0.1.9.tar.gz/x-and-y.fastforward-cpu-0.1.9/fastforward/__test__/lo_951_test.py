import unittest
from fastforward.model_for_encoding import ModelForEncoding
from numpy import ndarray
from threading import Barrier
import concurrent.futures
import pytest


@pytest.mark.skip(reason="only testable with proper models")
class LO951Test(unittest.TestCase):

    model = ModelForEncoding(
        f"/home/bnjm/IdeaProjects/semantic-search/models/sentence-transformers_paraphrase-multilingual-MiniLM-L12-v2/int8/")
    threads = 10
    barrier = Barrier(threads + 1)
    cdl = Barrier(threads)
    futures = []

    def test_encoding_fails(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as pool:
            for x in range(0, self.threads):
                future = pool.submit(self.run_encoding)
                self.futures = self.futures + [future]
            self.barrier.wait()
            for f in self.futures:
                r = future.result()
                self.assertEqual(len(r), 384)

    def run_encoding(self):
        self.barrier.wait()
        result: ndarray = self.model("""
      CPython implementation detail: In CPython, due to the Global Interpreter Lock, only one thread can execute Python code at once (even though certain performance-oriented libraries might overcome this limitation). If you want your application to make better use of the computational resources of multi-core machines, you are advised to use multiprocessing or concurrent.futures.ProcessPoolExecutor. However, threading is still an appropriate model if you want to run multiple I/O-bound tasks simultaneously.
       """)
        return result.tolist()
