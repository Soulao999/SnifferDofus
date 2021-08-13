import databaseManager
import matplotlib.pyplot as plt
import datetime

def timechartFromGID(GID: int) -> None:
    fig, axs = plt.subplots(3)
    dbManager = databaseManager.DatabaseManager()
    records = dbManager.getAllRecordsFromGID(GID)
    x = [datetime.datetime.strptime(record[7][:-7],"%Y-%m-%d %H:%M:%S") for record in records]
    y1 = [record[3] for record in records]
    y10 = [record[4] for record in records]
    y100 = [record[5] for record in records]
    axs[0].plot(x,y1,'rx',x,y1,'k')
    axs[1].plot(x,y10,'rx',x,y10,'k')
    axs[2].plot(x,y100,'rx',x,y100,'k')
    # for ax in axs:
    #     ax.legend(loc="upper left")
    plt.show()



if __name__ == "__main__":
    timechartFromGID(11110)