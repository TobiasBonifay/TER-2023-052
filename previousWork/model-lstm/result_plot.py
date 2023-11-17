import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DIR_RESULT = "\result-data"
DATASET_FILE = 'data/dataset.csv'


def read_all_file():
    list_of_files = []
    for root, dirs, files in os.walk("result-data/"):
        for file in files:
            if os.path.splitext(file)[1] == ".csv":
                list_of_files.append(os.path.join(root, file))

    return list_of_files


def read_dataset_file():
    df = pd.read_csv(DATASET_FILE, sep=',')
    print(df.head())
    return df


def get_reduction(i):
    if i == 0:
        return "0_4"
    elif i == 1:
        return "0_5"
    elif i == 2:
        return "0_6"
    elif i == 3:
        return "0_7"
    elif i == 4:
        return "0_8"
    elif i == 5:
        return "0_9"
    else:
        return "NONE"


def file_to_df(file):
    df = pd.read_csv(file, sep=",")
    return df


def plot_all_result(list_files):
    df_dataset = read_dataset_file()
    for file in list_files:
        df = file_to_df(file)
        plot_df_pred(df, df_dataset, file)


def plot_df_pred(df, df_dataset, file):
    print(df.index.shape[0])
    for i in range(int(df.index.shape[0] / 6000) + 1):
        index = df.index.to_numpy()[i * 6000:(i + 1) * 6000] / 2

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        ax1.plot(index, df["response_time"].to_numpy()[i * index.shape[0]:(i + 1) * index.shape[0]], 'b-')
        ax2.plot(index, df_dataset['memproc'][i * index.shape[0]:(i + 1) * index.shape[0]], 'orange')
        ax2.plot(index, df_dataset['mem_vm'][i * index.shape[0]:(i + 1) * index.shape[0]], 'g-')
        ax2.plot(index, df_dataset['limit_cgroup'][i * index.shape[0]:(i + 1) * index.shape[0]] * 1e-3, 'r-')

        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Expected Response time (ms)', color='orange')
        ax2.set_ylabel('memory info')

        plt.legend(['memproc', 'mem_vm', 'limit_cgroup'])
        plt.title('Experience with reduction ' + str(get_reduction(i)).replace("_", ".") + '% of memory use by process')

        fig.savefig(
            "plot_result_bis/dataset_" + get_reduction(i).replace("_", ".") + "/" + file.split("/")[1].split(".")[
                0] + ".png")
        '''
        index = df.index.to_numpy()[i*6000:(i+1)*6000]/2
        plt.plot(index,df["response_time"].to_numpy()[i*6000:(i+1)*6000], label="predict response time")
        plt.xlabel("Time (s)")
        plt.ylabel("predict response time (ms)")
        plt.title(file.split("/")[1].split(".")[0])
        plt.savefig("plot_result/dataset_"+str(i)+"/"+file.split("/")[1].split(".")[0]+".png")
        plt.show()
        '''


if __name__ == "__main__":
    list_files = read_all_file()
    plot_all_result(list_files)
