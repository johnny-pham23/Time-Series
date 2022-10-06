# This gist was created for the Kaggle dataset "Hourly Energy Consumption" which can be found at https://www.kaggle.com/robikscube/hourly-energy-consumption
# Taking a look at the datasets, one can see that they are sorted by they are sorted by: year asc -> month desc -> day desc -> hour asc
# There are also missing/duplicate values, which lead to offset by up to a day
# This method sorts them properly and deals with missing/duplicate values using the averages (of the energy consumption)
# Returns the processed dataframe
import pandas as pd
def process_missing_and_duplicate_timestamps(filepath, verbose=True):
    df = pd.read_csv(filepath)
    df.sort_values('Datetime', inplace=True)
    df.reset_index(drop=True, inplace=True)

    indices_to_remove = []
    series_to_add = []
    hour_counter = 1
    prev_date = ''

    if verbose:
        print(filepath)

    for index, row in df.iterrows():
        date_str = row['Datetime']

        year_str = date_str[0:4]
        month_str = date_str[5:7]
        day_str = date_str[8:10]
        hour_str = date_str[11:13]
        tail_str = date_str[14:]

        def date_to_str():
            return '-'.join([year_str, month_str, day_str]) + ' ' + ':'.join([hour_str, tail_str])
        def date_with_hour(hour):
            hour = '0' + str(hour) if hour < 10 else str(hour)
            return '-'.join([year_str, month_str, day_str]) + ' ' + ':'.join([hour, tail_str])

        if hour_counter != int(hour_str):
            if prev_date == date_to_str():
                # Duplicate datetime, we'll calculate the average and keep only one
                average = int((df.iat[index, 1]+df.iat[index-1, 1])/2)  # Get the average
                df.iat[index, 1] = average
                indices_to_remove.append(index-1)  # Dropping here will offset the index, so we do it after the for-loop
                if verbose:
                    print('Duplicate ' + date_to_str() + ' with average ' + str(average))
            elif hour_counter < 23:
                # Missing datetime, we'll add it using the average of the previous and next for the consumption (MWs)
                average = int((df.iat[index, 1]+df.iat[index-1, 1])/2)

                # Adding here will offset the index, so we do it after the for-loop
                series_to_add.append(pd.Series([date_with_hour(hour_counter), average], index=df.columns))
                if verbose:
                    print('Missing ' + date_with_hour(hour_counter) + ' with average ' + str(average))
            else:
                # Didn't find any such cases in the Hourly Energy Consumption (PJM) (Kaggle) dataset
                # Leaving it for other datasets
                print(date_to_str() + ' and hour_counter ' + str(hour_counter) + " with previous: " + prev_date)

            # Adjust for the missing/duplicate value
            if prev_date < date_to_str():
                hour_counter = (hour_counter + 1) % 24
            else:
                hour_counter = (hour_counter - 1) if hour_counter - 1 > 0 else 0

        # Increment the hour
        hour_counter = (hour_counter + 1) % 24
        prev_date = date_str

    df.drop(indices_to_remove, inplace=True)
    df = df.append(series_to_add)

    # New rows are added at the end, sort them and also recalculate the indices
    df.sort_values('Datetime', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df