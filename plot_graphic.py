import numpy as np 
import scipy.linalg as la 
import matplotlib.pyplot as plt 
import scipy.optimize as opt 

f = lambda x:x**2+1
x = np.linspace(-2,2,500)
sol = opt.minimize_scalar(f,bounds=(1,1000),method='bounded')
plt.plot(x,f(x))
print(sol)
plt.scatter([sol.x],[sol.fun],label='solucao')
plt.legend()
plt.show()
