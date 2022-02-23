import matplotlib.pyplot as plt

def getGraphTest():
    """
        Графический вывод результатов
        замеров производительности.
    """

    fig = plt.figure(figsize=(10, 7))
    plot = fig.add_subplot()

    points = [count for count in range(1000, 2100, 100)]
    results = [61, 48, 41, 35, 32, 27, 23, 21, 19, 17, 15]

    plot.plot(points, results)
    plt.grid()
    plt.title("Зависимость производительности от числа точек сетки")
    plt.ylabel("Производительность, к/c")
    plt.xlabel("Число точек сетки, шт")

    plt.show()

if __name__ == "__main__":
    getGraphTest()
