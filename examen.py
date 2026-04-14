import matplotlib.pyplot as plt
nombres = ['Cole1', 'Cole2', 'Cole3', 'Cole4']
inferior = [3, 7, 5, 1]
normal = [10, 6, 1, 23]
superior = [7,2, 8, 9]
obesos = [2, 7, 6, 9]
ejeY = []
i = 0
while i <len(nombres):
 ejeY.append( superior[i] + obesos[i])
 i = i+1
fig, ax = plt.subplots()
ax.bar(nombres, ejeY, width=1, edgecolor="white", linewidth=0.7)
plt.show()

