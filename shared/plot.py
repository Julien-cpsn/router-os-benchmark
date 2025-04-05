import json
import matplotlib.pyplot as plt

if __name__ == "__main__":
    data_file = open('results/result_global.json', 'r')
    data = json.load(data_file)

    labels = []
    throughput_values = []
    jitter_values = []

    for key, results in data.items():
        labels.append(key)
        throughput_values.append([])
        jitter_values.append([])

        for run in results['runs']:
            throughput = run['throughput_mbps']
            jitter = run['jitter_ms']
            throughput_values[-1].append(throughput)
            jitter_values[-1].append(jitter)

    plt.boxplot(throughput_values, labels=labels)
    plt.title("Throughput")
    plt.ylabel("Mbps")
    plt.xlabel("Operating System")
    plt.savefig("results/throughput_mbps.png")

    plt.boxplot(jitter_values, labels=labels)
    plt.ylim(0.05, 0.001)
    plt.title("Jitter")
    plt.ylabel("ms")
    plt.xlabel("Operating System")
    plt.savefig("results/jitter_ms.png")