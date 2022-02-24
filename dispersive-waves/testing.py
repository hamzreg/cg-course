import matplotlib.pyplot as plt
import pylab

def getGraphTest():
    """
        Графический вывод результатов
        замеров производительности.
    """

    fig = plt.figure(figsize=(10, 7))
    plot = fig.add_subplot()

    points = [count for count in range(800, 2100, 100)]
    results = [78, 74, 61, 48, 41, 35, 32, 27, 23, 21, 19, 17, 15]

    plot.plot(points, results)
    plt.grid()
    plt.title("Зависимость производительности от числа точек сетки")
    plt.ylabel("Производительность, к/c")
    plt.xlabel("Число точек сетки, шт.")

    plt.hlines(60, 0, 1008, color = "red", linestyle = "--")
    plt.vlines(1008, 0, 60, color = "red", linestyle = "--")

    pylab.xlim(740, 2060)
    pylab.ylim(0, 80)
    plt.text(1012, 1, "1008")

    plt.show()

if __name__ == "__main__":
    getGraphTest()
