import matplotlib.pyplot as plt

class graphe:
    def __init__(self, titre: str, labelx: str, labely: str):
        plt.title(titre)
        plt.ylabel(labely)
        plt.xlabel(labelx)
    
    def afficher(self, liste_points: list):
        x = []
        y = []
        for i in liste_points:
            x.append(i[0])
            y.append(i[1])
        plt.plot(x,y)
        plt.show()

