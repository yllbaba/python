import matplotlib.pyplot as plt

def plot_points(data):
    plt.bar(data["name"], data["points"])
    plt.xticks(rotation=45)
    plt.title("Total Points per Player")
    plt.show()