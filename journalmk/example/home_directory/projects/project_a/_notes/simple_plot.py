import sys
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10 * np.pi)
plt.plot(x, np.sin(x) + np.exp(x / 10))

if sys.argv[-1].endswith(".pdf"):
    plt.savefig(sys.argv[-1])
else:
    plt.show()
