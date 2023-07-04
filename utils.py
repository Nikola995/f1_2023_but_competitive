import ergast_py
from ergast_py.models.result import Result
from typing import Tuple
import pandas as pd
from datetime import time

e = ergast_py.Ergast()
scoring_system_race = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
                       6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
scoring_system_sprint = {1: 8, 2: 7, 3: 6, 4: 5,
                         5: 4, 6: 3, 7: 2, 8: 1}
fastest_lap_points = 1


def race_results(remove_drivers: list = [], round: int = 1,
                 season: int = 2023) -> Tuple[pd.DataFrame, Result]:
    round = e.season(season).round(round).get_result()
    results_new = list(filter(lambda x:
                              x.driver.code not in remove_drivers,
                              round.results))
    # Update points from new positions
    for result, new_pos in zip(results_new,
                               range(1, len(results_new) + 1)):
        result.position = new_pos
        result.position_text = str(
            new_pos) if result.position_text.isdigit() else 'DNF'
        result.points = scoring_system_race.get(new_pos, 0)
        # Set max value if fastest lap is missing
        if not result.fastest_lap.time:
            result.fastest_lap.time = time.max
    # Update fastest lap from new positions
    fastest_lap = min(results_new, key=lambda x: x.fastest_lap.time)
    if fastest_lap.position <= 10:
        results_new[fastest_lap.position - 1].points += fastest_lap_points
    # Extract features into pd.DataFrame
    race_results_list = []
    for result in results_new:
        info = (result.position_text,
                result.driver.permanent_number,
                f'{result.driver.given_name} {result.driver.family_name}',
                result.constructor.name,
                result.laps,
                result.points
                )
        race_results_list.append(info)
    race_results = (pd.DataFrame
                    .from_records(race_results_list,
                                  columns=['Pos', 'No', 'Driver',
                                           'Constructor', 'Laps',
                                           'Points'])
                    )
    return race_results.set_index('Pos'), fastest_lap


def print_fastest_lap(fastest_lap: Result) -> None:
    print(f'Fastest lap: {fastest_lap.driver.given_name} '
          f'{fastest_lap.driver.family_name} ({fastest_lap.constructor.name})'
          f' - {fastest_lap.fastest_lap.time.strftime("%M:%S.%f").strip("0")}'
          f' (lap {fastest_lap.fastest_lap.lap})')


def sprint_results(remove_drivers: list = [], round: int = 1,
                   season: int = 2023) -> pd.DataFrame:
    try:
        sprint = e.season(season).round(round).get_sprint()
    except Exception:
        return pd.DataFrame()
    results_new = list(filter(lambda x:
                              x.driver.code not in remove_drivers,
                              sprint.sprint_results))
    # Update points from new positions
    for result, new_pos in zip(results_new,
                               range(1, len(results_new) + 1)):
        result.position = new_pos
        result.position_text = str(
            new_pos) if result.position_text.isdigit() else 'DNF'
        result.points = scoring_system_sprint.get(new_pos, 0)
    # Extract features into pd.DataFrame
    sprint_results_list = []
    for result in results_new:
        info = (result.position_text,
                result.driver.permanent_number,
                f'{result.driver.given_name} {result.driver.family_name}',
                result.constructor.name,
                result.laps,
                result.points
                )
        sprint_results_list.append(info)
    sprint_results = (pd.DataFrame
                      .from_records(sprint_results_list,
                                    columns=['Pos', 'No', 'Driver',
                                             'Constructor', 'Laps',
                                             'Points'])
                      )
    return sprint_results.set_index('Pos')


def circuit_location_code(round: int = 1, season: int = 2023) -> str:
    location = e.season(season).round(round).get_circuit().location
    if location.country == 'USA':
        match location.locality:
            case 'Miami':
                code = 'MIA'
            case 'Austin':
                code = 'TEX'
            case 'Las Vegas':
                code = 'VEG'
    elif location.country == 'Austria':
        code = 'AUT'
    else:
        code = location.country[:3]
    return code.upper()


def drivers_standings_base(remove_drivers: list = [],
                           season: int = 2023) -> pd.DataFrame:
    drivers_original = e.season(2023).get_drivers()
    drivers_filtered = list(filter(lambda x: x.code not in remove_drivers,
                                   drivers_original))
    drivers_standings_base = (pd.DataFrame
                              .from_records(
                                  [(d.permanent_number,
                                    f'{d.given_name} {d.family_name}')
                                   for d in drivers_filtered],
                                  columns=('No', 'Driver')))
    return drivers_standings_base


def drivers_standings(remove_drivers: list = [], round: int = 1,
                      season: int = 2023) -> pd.DataFrame:
    ds_df = drivers_standings_base(remove_drivers, season)
    ds_base_columns = ds_df.columns
    for round_curr in range(1, round + 1):
        loc_code = circuit_location_code(round_curr, season)
        sprint_res = sprint_results(remove_drivers, round_curr, season)
        if not sprint_res.empty:
            ds_df = ds_df.merge((sprint_res[['Driver', 'Points']]
                                 .rename(columns={'Points': f'{loc_code}_SPR'})),
                                how='left',
                                on='Driver')
        race_res, _ = race_results(remove_drivers, round_curr, season)
        ds_df = ds_df.merge((race_res[['Driver', 'Points']]
                             .rename(columns={'Points': loc_code})),
                            how='left',
                            on='Driver')
    ds_df['Points'] = (ds_df
                       .drop(ds_base_columns, axis=1)
                       .sum(axis=1))
    ds_df = ds_df.sort_values(by='Points', ascending=False, ignore_index=True)
    ds_df.index = ds_df.index + 1
    return ds_df


def constructors_standings_base(remove_cons: list = [],
                                season: int = 2023) -> pd.DataFrame:
    cons_original = e.season(2023).get_constructors()
    cons_filtered = list(filter(lambda x:x.constructor_id not in remove_cons,
                                cons_original))
    constructors_standings_base = (pd.DataFrame
                                   .from_records(
                                     [{'Constructor': c.name}
                                      for c in cons_filtered]))
    return constructors_standings_base


def get_points_by_constructor(results: pd.DataFrame) -> pd.DataFrame:
    return (results
            .groupby(['Constructor'])
            ['Points']
            .sum()
            .to_frame()
            .reset_index())


def constructors_standings(remove_cons: list = [], remove_drivers: list = [],
                           round: int = 1, season: int = 2023) -> pd.DataFrame:
    cs_df = constructors_standings_base(remove_cons, season)
    cd_base_columns = cs_df.columns
    for round_curr in range(1, round + 1):
        loc_code = circuit_location_code(round_curr, season)
        sprint_res = sprint_results(remove_drivers, round_curr, season)
        if not sprint_res.empty:
            cs_sprint = get_points_by_constructor(sprint_res)
            cs_df = cs_df.merge((cs_sprint
                                 .rename(columns={'Points': f'{loc_code}_SPR'})),
                                how='left',
                                on='Constructor')
        race_res, _ = race_results(remove_drivers, round_curr, season)
        cs_race = get_points_by_constructor(race_res)
        cs_df = cs_df.merge((cs_race
                             .rename(columns={'Points': loc_code})),
                            how='left',
                            on='Constructor')
    cs_df['Points'] = (cs_df
                       .drop(cd_base_columns, axis=1)
                       .sum(axis=1))
    cs_df = cs_df.sort_values(by='Points', ascending=False, ignore_index=True)
    cs_df.index = cs_df.index + 1
    return cs_df
