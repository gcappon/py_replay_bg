---
sidebar: heading
---

# Analyzing replay results

ReplayBG provides the possibility, to analyze in a painless way the results of `rbg.replay()`. To this aim,
ReplayBG integrates the [AGATA](https://github.com/gcappon/py_agata) software for analyzing the simulated glucose and
CGM profiles, a dedicated routines for the meal/insulin events.

This is done using the `Analyzer` class importable from `py_replay_bg.analyzer`. 

In the following, we show how to do that in the case of single portions of data and portions of data spanning 
more than one day (i.e., intervals).

## Analyzing replay results from single portions of data

To analyze replay results from single portions of data use the `Analyzer.analyze_replay_results()` static
method, which is formerly defined as:
```python 
    @staticmethod
    def analyze_replay_results(
            replay_results: Dict,
            data: pd.DataFrame = None,
    ) -> Dict
```

### Input parameters
- `replay_results`: the dictionary returned by or saved with the `rbg.replay()` method
- `data`, optional, default: `None`: The `data` parameter passed to `rbg.replay()` . If present, the method will also
compare the glucose fit vs the data.

### Output parameter
- `analysis`: A dictionary containing the results of the analysis with fields `median`, `ci5th`, `ci25th`, `ci75th`,
`ci95th`, i.e., dictionaries containing the analysis results computed from the median, 5-th percentile, 25-th 
percentile, 75-th percentile, and 95-th percentiles of the simulated profiles, respectively. 
Remember that, if the adopted identification method is MAP or `n_replay=1`, the values contained in `median`, `ci5th`, `ci25th`, `ci75th`,
`ci95th` coincide. Each dictionary contains:
  - `glucose` and `cgm`: two dictionaries containing the analysis results computed with AGATA from the simulated `glucose` and `cgm` profiles with fields:
    - `variability`: a dictionary containing the following fields (corresponding to glucose variability indices):
      - `mean_glucose`: the average glucose (mg/dl)
      - `median_glucose`: the median of glucose (mg/dl) 
      - `std_glucose`: the glucose standard deviation (mg/dl)
      - `cv_glucose`: the glucose coefficient of variation (%)
      - `range_glucose`: the spanned glucose range (mg/dl)
      - `iqr_glucose`: the glucose interquartile range (mg/dl)
      - `auc_glucose`: the area under the glucose curve (mg^2/dl^2)
      - `gmi`: the glucose management indicator (-)
      - `cogi`: the continuous glucose monitoring index (-)
      - `conga`: the CONGA index (-)
      - `j_index`: the J-index (-)
      - `mage_plus_index`: the positive MAGE index (mg/dl)
      - `mage_minus_index`: the negative MAGE index (mg/dl)
      - `mage_index`: the overall MAGE index (mg/dl)
      - `ef_index`: the EF index (-)
      - `modd`: the mean of daily difference (mg/dl)
      - `sddm_index`: the standard deviation of daily means (mg/dl)
      - `sdw_index`: the within standard deviation (mg/dl)
      - `std_glucose_roc`: the standard deviation of glucose rat of change (mg/dl/min)
      - `cvga`: the CVGA index (mg^2/dl^2)
    - `time_in_ranges`: a dictionary containing the following fields (corresponding to time in range indices):
      - `time_in_target`: the time in target (%)
      - `time_in_hypoglycemia`: the time in hypoglycemia (%)
      - `time_in_l1_hypoglycemia`: the time in level 1 hypoglycemia (%)
      - `time_in_l2_hypoglycemia`: the time in level 2 hypoglycemia (%)
      - `time_in_hyperglycemia`: the time in hyperglycemia (%)
      - `time_in_l1_hyperglycemia`: the time in level 1 hyperglycemia (%)
      - `time_in_l2_hyperglycemia`: the time in level 2 hyperglycemia (%)
    - `risk`: a dictionary containing the following fields (corresponding to glucose risk indices):
      - `adrr`: the average daily risk (-)
      - `lbgi`: the low blood glucose index (-)
      - `hbgi`: the high blood glucose index (-)
      - `bgri`: the blood glucose risk index (-)
      - `gri`: the glucose risk indicator (-)
    - `glycemic_transformation`: a dictionary containing the following fields (corresponding to glucose variability 
    indices which adopt a "scale transformation"):
      - `grade_score`: the overall GRADE score (-)
      - `grade_hypo_score`: the hypo GRADE score (-)
      - `grade_hyper_score`: the hyper GRADE score (-)
      - `grade_eu_score`: the euglycemia GRADE score (-)
      - `igc`: the index of glucose control (-)
      - `hypo_index`: the hypo index (-) 
      - `hyper_index`: the hyper index (-)
      - `mr_index`: the MR index (-)
    - `events`: a dictionary containing the following fields (corresponding to glucose adverse events):
      - `hypoglycemic_events`: a dictionary of dictionaries `hypo`, `l1`, and `l2` containing the results of the analysis
      of hypoglycemic, level 1 hypoglycemic, and level 2 hypoglycemic events, respectively. Each dictionary has fields:
          - `time_start`: a np.ndarray containing the timestamp when each event starts
          - `time_end`: a np.ndarray containing the timestamp when each event ends
          - `duration`: a np.ndarray containing the duration of each event (min)
          - `mean_duration`: the average duration of the events (min)
          - `events_per_week`: the frequency per week of the events (#/week)
      - `hyperglycemic_events`: a dictionary of dictionaries `hyper`, `l1`, and `l2` containing the results of the analysis
      of hyperglycemic, level 1 hyperglycemic, and level 2 hyperglycemic events, respectively. Each dictionary has fields:
          - `time_start`: a np.ndarray containing the timestamp when each event starts
          - `time_end`: a np.ndarray containing the timestamp when each event ends
          - `duration`: a np.ndarray containing the duration of each event (min)
          - `mean_duration`: the average duration of the events (min)
          - `events_per_week`: the frequency per week of the events (#/week)
      - `events`: a dictionary containing the following fields (corresponding to glucose adverse events):
      - `extended_hypoglycemic_events`: a dictionary containing the results of the analysis
      of extended hypoglycemic events with fields:
          - `time_start`: a np.ndarray containing the timestamp when each event starts
          - `time_end`: a np.ndarray containing the timestamp when each event ends
          - `duration`: a np.ndarray containing the duration of each event (min)
          - `mean_duration`: the average duration of the events (min)
          - `events_per_week`: the frequency per week of the events (#/week)
    - `data_quality`: a dictionary containing the following fields (corresponding to data quality):
      - `number_of_days_of_observation`: the length of the profile (days)
      - `missing_glucose_percentage`: the percentage of missing glucose data (%)
  - `events`: a dictionary containing the analysis of the simulated meal/insulin events:
    - `total_insulin`: the total amount of injected insulin (U)
    - `total_basal_insulin`: the total amount of injected basal insulin (U)
    - `total_bolus_insulin`: the total amount of injected bolus insulin (U)
    - `total_correction_bolus_insulin`: the total amount of injected correction bolus  insulin (U)
    - `total_cho`: the total amount of ingested meals (g)
    - `total_hypotreatments`: the total amount of ingested hypotreatements (g)
    - `total_meal_announcements`: the total amount of announced meals (g)
    - `correction_bolus_insulin_number`: the number of correction bolus events (#)
    - `hypotreatment_number`: the number of hypotreatment events (#)
    - `exercise_session_number`: the number of exercise sessions (#). NOT YET IMPLEMENTED

### Example 

```python
# Load previously saved results, e.g., ...
with open(os.path.join(results_folder_location, 'results', 'workspaces', 'results.pkl'), 'rb') as file:
    replay_results = pickle.load(file)

# Analyze them
analysis = Analyzer.analyze_replay_results(replay_results)
```

The full code can be found in `/example/code/analysis_example.py`.

## Analyzing replay results from portions of data spanning more than one day (i.e., intervals)

To analyze replay results from single portions of data use the `Analyzer.analyze_replay_results_interval()` static
method, which is formerly defined as:
```python 
    @staticmethod
    def analyze_replay_results_interval(
            replay_results_interval: list,
            data_interval: list = None,
    ) -> Dict
```

### Input parameters
- `replay_results_interval`: a list of dictionaries returned by or saved with the `rbg.replay()` method
- `data_interval`, optional, default: `None`: The list of `data` passed to `rbg.replay()` . If present, the method will also
compare the glucose fit vs the data.

### Output parameter
- `analysis`: A dictionary containing the results of the analysis with fields `median`, `ci5th`, `ci25th`, `ci75th`,
`ci95th`, i.e., dictionaries containing the analysis results computed from the median, 5-th percentile, 25-th 
percentile, 75-th percentile, and 95-th percentiles of the simulated profiles, respectively. 
Remember that, if the adopted identification method is MAP or `n_replay=1`, the values contained in `median`, `ci5th`, `ci25th`, `ci75th`,
`ci95th` coincide. Each dictionary contains:
  - `glucose` and `cgm`: two dictionaries containing the analysis results computed with AGATA from the simulated `glucose` and `cgm` profiles with fields:
    - `variability`: a dictionary containing the following fields (corresponding to glucose variability indices):
      - `mean_glucose`: the average glucose (mg/dl)
      - `median_glucose`: the median of glucose (mg/dl) 
      - `std_glucose`: the glucose standard deviation (mg/dl)
      - `cv_glucose`: the glucose coefficient of variation (%)
      - `range_glucose`: the spanned glucose range (mg/dl)
      - `iqr_glucose`: the glucose interquartile range (mg/dl)
      - `auc_glucose`: the area under the glucose curve (mg^2/dl^2)
      - `gmi`: the glucose management indicator (-)
      - `cogi`: the continuous glucose monitoring index (-)
      - `conga`: the CONGA index (-)
      - `j_index`: the J-index (-)
      - `mage_plus_index`: the positive MAGE index (mg/dl)
      - `mage_minus_index`: the negative MAGE index (mg/dl)
      - `mage_index`: the overall MAGE index (mg/dl)
      - `ef_index`: the EF index (-)
      - `modd`: the mean of daily difference (mg/dl)
      - `sddm_index`: the standard deviation of daily means (mg/dl)
      - `sdw_index`: the within standard deviation (mg/dl)
      - `std_glucose_roc`: the standard deviation of glucose rat of change (mg/dl/min)
      - `cvga`: the CVGA index (mg^2/dl^2)
    - `time_in_ranges`: a dictionary containing the following fields (corresponding to time in range indices):
      - `time_in_target`: the time in target (%)
      - `time_in_hypoglycemia`: the time in hypoglycemia (%)
      - `time_in_l1_hypoglycemia`: the time in level 1 hypoglycemia (%)
      - `time_in_l2_hypoglycemia`: the time in level 2 hypoglycemia (%)
      - `time_in_hyperglycemia`: the time in hyperglycemia (%)
      - `time_in_l1_hyperglycemia`: the time in level 1 hyperglycemia (%)
      - `time_in_l2_hyperglycemia`: the time in level 2 hyperglycemia (%)
    - `risk`: a dictionary containing the following fields (corresponding to glucose risk indices):
      - `adrr`: the average daily risk (-)
      - `lbgi`: the low blood glucose index (-)
      - `hbgi`: the high blood glucose index (-)
      - `bgri`: the blood glucose risk index (-)
      - `gri`: the glucose risk indicator (-)
    - `glycemic_transformation`: a dictionary containing the following fields (corresponding to glucose variability 
    indices which adopt a "scale transformation"):
      - `grade_score`: the overall GRADE score (-)
      - `grade_hypo_score`: the hypo GRADE score (-)
      - `grade_hyper_score`: the hyper GRADE score (-)
      - `grade_eu_score`: the euglycemia GRADE score (-)
      - `igc`: the index of glucose control (-)
      - `hypo_index`: the hypo index (-) 
      - `hyper_index`: the hyper index (-)
      - `mr_index`: the MR index (-)
    - `events`: a dictionary containing the following fields (corresponding to glucose adverse events):
      - `hypoglycemic_events`: a dictionary of dictionaries `hypo`, `l1`, and `l2` containing the results of the analysis
      of hypoglycemic, level 1 hypoglycemic, and level 2 hypoglycemic events, respectively. Each dictionary has fields:
          - `time_start`: a np.ndarray containing the timestamp when each event starts
          - `time_end`: a np.ndarray containing the timestamp when each event ends
          - `duration`: a np.ndarray containing the duration of each event (min)
          - `mean_duration`: the average duration of the events (min)
          - `events_per_week`: the frequency per week of the events (#/week)
      - `hyperglycemic_events`: a dictionary of dictionaries `hyper`, `l1`, and `l2` containing the results of the analysis
      of hyperglycemic, level 1 hyperglycemic, and level 2 hyperglycemic events, respectively. Each dictionary has fields:
          - `time_start`: a np.ndarray containing the timestamp when each event starts
          - `time_end`: a np.ndarray containing the timestamp when each event ends
          - `duration`: a np.ndarray containing the duration of each event (min)
          - `mean_duration`: the average duration of the events (min)
          - `events_per_week`: the frequency per week of the events (#/week)
      - `events`: a dictionary containing the following fields (corresponding to glucose adverse events):
      - `extended_hypoglycemic_events`: a dictionary containing the results of the analysis
      of extended hypoglycemic events with fields:
          - `time_start`: a np.ndarray containing the timestamp when each event starts
          - `time_end`: a np.ndarray containing the timestamp when each event ends
          - `duration`: a np.ndarray containing the duration of each event (min)
          - `mean_duration`: the average duration of the events (min)
          - `events_per_week`: the frequency per week of the events (#/week)
    - `data_quality`: a dictionary containing the following fields (corresponding to data quality):
      - `number_of_days_of_observation`: the length of the profile (days)
      - `missing_glucose_percentage`: the percentage of missing glucose data (%)
  - `events`: a dictionary containing the analysis of the simulated meal/insulin events:
    - `total_insulin`: the total amount of injected insulin (U)
    - `total_basal_insulin`: the total amount of injected basal insulin (U)
    - `total_bolus_insulin`: the total amount of injected bolus insulin (U)
    - `total_correction_bolus_insulin`: the total amount of injected correction bolus  insulin (U)
    - `total_cho`: the total amount of ingested meals (g)
    - `total_hypotreatments`: the total amount of ingested hypotreatements (g)
    - `total_meal_announcements`: the total amount of announced meals (g)
    - `correction_bolus_insulin_number`: the number of correction bolus events (#)
    - `hypotreatment_number`: the number of hypotreatment events (#)
    - `exercise_session_number`: the number of exercise sessions (#). NOT YET IMPLEMENTED

### Example 

```python
# Initialize results list
replay_results_interval = []

# Load previously saved results, e.g., ...
for day in range(start_day, end_day+1):
    with open(os.path.join(results_folder_location, 'results', 'workspaces', 'results_' + str(day) + '.pkl'), 'rb') as file:
        replay_results = pickle.load(file)
    replay_results_interval.append(replay_results)

# Analyze them
analysis = Analyzer.analyze_replay_results_interval(replay_results_interval=replay_results_interval)
```

The full code can be found in `/example/code/analysis_example_intervals.py`.