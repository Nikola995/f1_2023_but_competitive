import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

const_palette = {'Mercedes': 'silver',
                 'Aston Martin': 'green',
                 'Ferrari': 'red',
                 'Red Bull': 'blue',
                 'Alpine F1 Team': 'royalblue',
                 'McLaren': 'orange',
                 'Alfa Romeo': 'maroon',
                 'Haas F1 Team': 'black',
                 'Williams': 'dodgerblue',
                 'AlphaTauri': 'darkblue'}


driver_palette = {'Valtteri Bottas': ('Alfa Romeo', '-'),
                   'Guanyu Zhou': ('Alfa Romeo', '--'),
                   'Nyck de Vries': ('AlphaTauri', '--'),
                   'Daniel Ricciardo': ('AlphaTauri', '-.'),
                   'Yuki Tsunoda': ('AlphaTauri', '-'),
                   'Esteban Ocon': ('Alpine F1 Team', '-'),
                   'Pierre Gasly': ('Alpine F1 Team', '--'),
                   'Fernando Alonso': ('Aston Martin', '-'),
                   'Lance Stroll': ('Aston Martin', '--'),
                   'Charles Leclerc': ('Ferrari', '-'),
                   'Carlos Sainz': ('Ferrari', '--'),
                   'Kevin Magnussen': ('Haas F1 Team', '--'),
                   'Nico Hülkenberg': ('Haas F1 Team', '-'),
                   'Oscar Piastri': ('McLaren', '--'),
                   'Lando Norris': ('McLaren', '-'),
                   'Lewis Hamilton': ('Mercedes', '-'),
                   'George Russell': ('Mercedes', '--'),
                   'Sergio Pérez': ('Red Bull', '-'),
                   'Logan Sargeant': ('Williams', '--'),
                   'Alexander Albon': ('Williams', '-')}

def melt_constructors_df(data: pd.DataFrame) -> pd.DataFrame:
    const_timeline = data.copy()
    race_order = (data
                  .drop(['Constructor', 'Points'], axis=1)
                  .columns)
    const_timeline[race_order] = data[race_order].cumsum(axis=1)
    df = (const_timeline
          .drop(['Points'], axis=1)
          .melt(id_vars='Constructor',
                value_vars=race_order,
                var_name='Race',
                value_name='Points'))
    return df

def constructors_timeline_plot(data: pd.DataFrame) -> None:
    df = melt_constructors_df(data)
    plt.figure(figsize=(16, 10))
    p = sns.lineplot(data=df, x='Race', y='Points',
                    hue='Constructor', marker='o', palette=const_palette)
    plt.title("Constructors' Championship Timeline")
    plt.legend(loc='upper left')
    sns.despine(bottom=True)
    plt.show()


def melt_drivers_df(data: pd.DataFrame) -> pd.DataFrame:
    driver_timeline = data.copy()
    race_order = (data
                  .drop(['No', 'Driver', 'Points'], axis=1)
                  .columns)
    driver_timeline[race_order] = data[race_order].cumsum(axis=1)
    df = (driver_timeline
          .drop(['Points'], axis=1)
          .melt(id_vars='Driver',
                value_vars=race_order,
                var_name='Race',
                value_name='Points'))
    return df

def drivers_timeline_plot(data: pd.DataFrame) -> None:
    df = melt_drivers_df(data)
    plt.figure(figsize=(16, 10))
    ax = sns.lineplot(data=df, x='Race', y='Points',
                    hue='Driver', marker='o')
    handles, labels = ax.get_legend_handles_labels()
    for i, (line, handle, label) in enumerate(zip(ax.lines, handles, labels)):
        line.set_linestyle(driver_palette[label][1])
        handle.set_linestyle(line.get_linestyle())
        line.set_color(const_palette[driver_palette[label][0]])
        handle.set_color(line.get_color())
    plt.title("Drivers' Championship Timeline")
    plt.legend(loc='upper left')
    sns.despine(bottom=True)
    plt.show()