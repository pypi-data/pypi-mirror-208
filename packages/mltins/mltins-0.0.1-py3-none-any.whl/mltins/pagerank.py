import numpy as np


class PageRank:
    def __init__(self, M, d, max_iter=100, tol=1e-6):
        self.M = M
        self.n = M.shape[0]
        self.d = d
        self.max_iter = max_iter
        self.tol = tol

    def compute(self):
        A = self.d * self.M + (1 - self.d) / self.n * np.ones((self.n, self.n))

        xt = np.random.random(self.n)
        for i in range(self.max_iter):
            yt1 = A @ xt
            xt1 = yt1 / np.max(yt1)

            if np.linalg.norm(xt1 - xt, ord=2) < self.tol:
                break
            else:
                xt = xt1

        return xt / np.linalg.norm(xt, ord=2)
