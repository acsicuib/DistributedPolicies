import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from collections import defaultdict
import numpy as np

experiments = [
    ("P1_s3", "Rome", "scenarios/TaxiRome/", "policy/", [[41.878037, 12.4462643], [41.919234, 12.5149603]], "policy1.pl")
]


for ncase, name, experiment_path, policy_folder, projection, policy_file in experiments:
    pathcommon = experiment_path+"results_%s_20201121/"%ncase
    actions = pathcommon+"action_stats.txt"
    mov = pathcommon+"movements.csv"
    res = pathcommon+"Results_Rome_0.csv"
    detailedMoves = pathcommon+"moves_stats.txt"


    ## GLOBAL ACTIONS
    dfa = pd.read_csv(actions)

    df = pd.read_csv(mov)
    dm = df.groupby("time").count()

    mv = {}
    pos = 0
    for idx, time in enumerate(dm.index):
        while pos < len(dfa.time) and time > dfa.time.iloc[pos]:
            pos += 1
        mv[pos] = dm.taxi.iloc[idx]

    mv[0] = 0

    del dfa["time"]
    dfa = dfa.rename(columns={"none": "inhibited action"})
    dfa.index += 1
    # df[:7].plot.bar(stacked=True,ax=ax,cmap=cmap)
    color = ['blue', 'orange', 'green', 'red', "black"]

    fig, ax = plt.subplots(figsize=(20, 12))

    dfa.plot.bar(stacked=True, ax=ax, width=0.9, color=color)

    plt.title('Total number of actions by type along the movements', fontsize=38)
    plt.xlabel(r"Mario activations", fontsize=30)
    plt.ylabel(r"Number of instances", fontsize=30)

    plt.legend(loc='upper left', fontsize=18, ncol=5,handleheight=2.4, labelspacing=0.05)
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))

    ax.grid(linestyle='-', axis='y', linewidth='0.5', )
    ax.grid('on', which='minor', axis="y", linewidth='0.5')

    for tick in ax.get_xticklabels():
        tick.set_rotation(0)

    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'gray'
    ax2.set_ylabel('Number of handovers', color=color, fontsize=30)  # we already handled the x-label with ax1
    ax2.plot(list(mv.keys()), list(mv.values()), '-ok', color=color,
             markersize=10, linewidth=4,
             markerfacecolor='white',
             markeredgecolor='gray',
             markeredgewidth=2)

    ax2.tick_params(axis='y', labelcolor=color)

    fig.savefig(pathcommon+"actions_%s.pdf"%ncase, dpi=400)

    ### FOR EACH APP

    # =============================================================================
    # Analysing the type of actions FOR EACH APP of each users
    # =============================================================================
    df = pd.read_csv(mov)

    # Getting users
    users_raw = df.groupby("taxi")["DES"].apply(list)  # DES=ID, len(DES)=Number of changes
    usersCode = {}  # key: DES, value: (taxiCode,user_changes)
    usersMovs = {}
    for p in range(len(users_raw)):
        usersCode[users_raw[p][0]] = users_raw.index[p]
        usersMovs[users_raw[p][0]] = len(users_raw[p])

    dfc = pd.read_csv(res)
    # Getting the app of each user
    users_app = {}
    for sample in dfc.iterrows():
        users_app[sample[1]["DES.src"]] = sample[1]["app"]
        if len(users_app) == len(usersCode):
            break

    dfapp = pd.DataFrame([users_app, usersCode, usersMovs]).T
    dfapp.columns = ["app", "code", "movs"]

    ## apps 1,2,3 => Rate request senstivie
    ## apps 4,5,6 => Latency sensitive
    mapapps = {1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1}
    dfapp["type"] = dfapp.app.map(mapapps)
    ### Geting the movements for each group of app
    dfmov = pd.read_csv(mov)  # all movements
    # get mov from users Type0
    codes = dfapp[dfapp.type == 0].code.values
    dfmov0 = dfmov[dfmov.taxi.isin(codes)]
    dfmov0 = dfmov0.groupby("time").count()

    # get mov from users Type1
    codes = dfapp[dfapp.type == 1].code.values
    dfmov1 = dfmov[dfmov.taxi.isin(codes)]
    dfmov1 = dfmov1.groupby("time").count()

    ### Geting the operations for each group of app
    dem = pd.read_csv(detailedMoves)
    df0 = dem.loc[dem.app < 4]
    df1 = dem.loc[dem.app > 3]

    df0 = df0.groupby(["time", "action"]).agg({"action": "count"})
    df0.columns = ["freq"]
    df0.reset_index(level=["time", "action"], inplace=True)
    df0 = df0.pivot_table('freq', ['time'], 'action')
    df0 = df0.fillna(0)

    mv = {}
    pos = 0
    for idx, time in enumerate(dfmov0.index):
        while pos < len(df0.index) and time > df0.index[pos]:
            pos += 1
        mv[pos] = dfmov0.taxi.iloc[idx]

    mv[0] = 0

    dfa = df0
    dfa.index = pd.RangeIndex(start=1, stop=len(dfa) + 1, step=1)
    if "none" not in dfa.columns:
        dfa["none"] = np.zeros(len(dfa))
    dfa = dfa[["undeploy", "nop", "migrate", "replicate", "none"]]
    dfa = dfa.rename(columns={"none": "inhibited action"})
    color = ['blue', 'orange', 'green', 'red', "black"]

    fig, ax = plt.subplots(figsize=(20, 12))
    dfa.plot.bar(stacked=True, ax=ax, width=0.9, color=color)
    plt.title('Total number of actions (RRS Apps)', fontsize=38)
    plt.xlabel(r"Mario Activations", fontsize=30)
    plt.ylabel(r"Number of instances", fontsize=30)
    plt.legend(loc='upper left', fontsize=18, ncol=5, handleheight=2.4, labelspacing=0.05)
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    ax.grid(linestyle='-', axis='y', linewidth='0.5', )
    ax.grid('on', which='minor', axis="y", linewidth='0.5')
    for tick in ax.get_xticklabels():
        tick.set_rotation(0)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'gray'
    ax2.set_ylabel('Number of handovers', color=color, fontsize=30)  # we already handled the x-label with ax1
    ax2.plot(list(mv.keys()), list(mv.values()), '-ok', color=color,
             markersize=10, linewidth=4,
             markerfacecolor='white',
             markeredgecolor='gray',
             markeredgewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.savefig(pathcommon + "actions_%s_G1.pdf" % ncase, dpi=400)

    break
    # =============================================================================
    # Analysing the type of actions FOR EACH APP of each users
    # =============================================================================
    df = pd.read_csv(mov)

    # Getting users
    users_raw = df.groupby("taxi")["DES"].apply(list)  # DES=ID, len(DES)=Number of changes
    usersCode = {}  # key: DES, value: (taxiCode,user_changes)
    usersMovs = {}
    for p in range(len(users_raw)):
        usersCode[users_raw[p][0]] = users_raw.index[p]
        usersMovs[users_raw[p][0]] = len(users_raw[p])

    dfc = pd.read_csv(res)
    # Getting the app of each user
    users_app = {}
    for sample in dfc.iterrows():
        users_app[sample[1]["DES.src"]] = sample[1]["app"]
        if len(users_app) == len(usersCode):
            break

    dfapp = pd.DataFrame([users_app, usersCode, usersMovs]).T
    dfapp.columns = ["app", "code", "movs"]

    ## apps 1,2,3 => Rate request senstivie
    ## apps 4,5,6 => Latency sensitive
    mapapps = {1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1}
    dfapp["type"] = dfapp.app.map(mapapps)

    print("Total Movements of users for each app")
    print("\t type=0 are 1,2,3 apps ")
    print(dfapp.groupby("type").movs.agg([sum]))

    ### Geting the movements for each group of app
    dfmov = pd.read_csv(mov)  # all movements
    # get mov from users Type0
    codes = dfapp[dfapp.type == 0].code.values
    dfmov0 = dfmov[dfmov.taxi.isin(codes)]
    dfmov0 = dfmov0.groupby("time").count()

    # get mov from users Type1
    codes = dfapp[dfapp.type == 1].code.values
    dfmov1 = dfmov[dfmov.taxi.isin(codes)]
    dfmov1 = dfmov1.groupby("time").count()

    ### Geting the operations for each group of app
    dem = pd.read_csv(detailedMoves)
    df0 = dem.loc[dem.app < 4]
    df1 = dem.loc[dem.app > 3]

    df0 = df0.groupby(["time", "action"]).agg({"action": "count"})
    df0.columns = ["freq"]
    df0.reset_index(level=["time", "action"], inplace=True)
    df0 = df0.pivot_table('freq', ['time'], 'action')
    df0 = df0.fillna(0)

    mv = {}
    pos = 0
    for idx, time in enumerate(dfmov0.index):
        while pos < len(df0.index) and time > df0.index[pos]:
            pos += 1
        mv[pos] = dfmov0.taxi.iloc[idx]

    mv[0] = 0

    dfa = df0
    dfa.index = pd.RangeIndex(start=1, stop=len(dfa) + 1, step=1)
    if "none" not in dfa.columns:
        dfa["none"] = np.zeros(len(dfa))
    dfa = dfa[["undeploy", "nop", "migrate", "replicate", "none"]]
    dfa = dfa.rename(columns={"none": "inhibited action"})
    color = ['blue', 'orange', 'green', 'red', "black"]

    fig, ax = plt.subplots(figsize=(20, 12))
    dfa.plot.bar(stacked=True, ax=ax, width=0.9, color=color)
    plt.title('Total number of actions (Apps Group 1)', fontsize=38)
    plt.xlabel(r"Execution steps", fontsize=30)
    plt.ylabel(r"Number of instances", fontsize=30)
    plt.legend(loc='upper left', fontsize=18)  # policy_getcloser # policy_getclosers_I_II_III
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.grid(linestyle='-', axis='y', linewidth='0.5', )
    ax.grid('on', which='minor', axis="y", linewidth='0.5')
    for tick in ax.get_xticklabels():
        tick.set_rotation(0)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'gray'
    ax2.set_ylabel('Number of users changes', color=color, fontsize=30)  # we already handled the x-label with ax1
    ax2.plot(mv.keys(), mv.values(), '-ok', color=color,
             markersize=10, linewidth=4,
             markerfacecolor='white',
             markeredgecolor='gray',
             markeredgewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)
    fig.savefig(pathcommon+"actions_%s_G1.pdf"%ncase, dpi=400)

    df1 = df1.groupby(["time", "action"]).agg({"action": "count"})
    df1.columns = ["freq"]
    df1.reset_index(level=["time", "action"], inplace=True)
    df1 = df1.pivot_table('freq', ['time'], 'action')
    df1 = df1.fillna(0)

    mv = {}
    pos = 0
    for idx, time in enumerate(dfmov1.index):
        while pos < len(df1.index) and time > df1.index[pos]:
            pos += 1
        mv[pos] = dfmov1.taxi.iloc[idx]

    mv[0] = 0

    dfa = df1
    dfa.index = pd.RangeIndex(start=1, stop=len(dfa) + 1, step=1)
    if "none" not in dfa.columns:
        dfa["none"] = np.zeros(len(dfa))
    dfa = dfa[["undeploy", "nop", "migrate", "replicate", "none"]]
    dfa = dfa.rename(columns={"none": "inhibited action"})
    color = ['blue', 'orange', 'green', 'red', "black"]
    fig, ax = plt.subplots(figsize=(20, 12))
    dfa.plot.bar(stacked=True, ax=ax, width=0.9, color=color)
    plt.title('Total number of actions (Apps Group 2)', fontsize=38)
    plt.xlabel(r"Execution steps", fontsize=30)
    plt.ylabel(r"Number of instances", fontsize=30)
    plt.legend(loc='upper left', fontsize=18)  # policy_getcloser # policy_getclosers_I_II_III
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.grid(linestyle='-', axis='y', linewidth='0.5', )
    ax.grid('on', which='minor', axis="y", linewidth='0.5')
    for tick in ax.get_xticklabels():
        tick.set_rotation(0)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'gray'
    ax2.set_ylabel('Number of users changes', color=color, fontsize=30)  # we already handled the x-label with ax1
    ax2.plot(mv.keys(), mv.values(), '-ok', color=color,
             markersize=10, linewidth=4,
             markerfacecolor='white',
             markeredgecolor='gray',
             markeredgewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)
    fig.savefig(pathcommon+"actions_%s_G2.pdf"%ncase, dpi=400)

print("Done")