import pandas
import io
import datetime


def df_to_csv(df: pandas.DataFrame) -> bytes:
    """
    Convert the DataFrame to a strongly formatted CSV.
    :param df: pandas DataFrame compatible with Wizata standards.
    :return: bytes containing the full CSV file.
    """
    b_buf = io.BytesIO()

    df.to_csv(b_buf,
              date_format="%Y-%m-%d-%H-%M-%S-%f",
              sep=",",
              decimal=".",
              encoding="utf-8")

    b_buf.seek(0)
    return b_buf.read()


def df_from_csv(b_data: bytes) -> pandas.DataFrame:
    """
    Convert the bytes to a pandas.DataFrame.
    :param b_data: bytes representing a CSV file.
    :return: pandas DataFrame formatted.
    """
    b_buf = io.BytesIO(b_data)

    df = pandas.read_csv(b_buf,
                         sep=",",
                         decimal=".",
                         encoding="utf-8")

    # detect timestamp column
    if "timestamp" in df.columns:
        df = df.rename(columns={'timestamp': 'Timestamp'})
    if "Timestamp" not in df.columns:
        raise ValueError('Cannot read dataframe as no Timestamp columns exists.')

    # detect timestamp type
    if df['Timestamp'].dtypes == 'int64':
        df['Timestamp'] = pandas.to_datetime(df['Timestamp'], unit="ms")
    elif df['Timestamp'].dtypes == 'object':
        df['Timestamp'] = df['Timestamp'].apply(lambda _: datetime.datetime.strptime(_, "%Y-%m-%d-%H-%M-%S-%f"))

    df = df.set_index('Timestamp')
    df.rename_axis("sensorId", axis="columns", inplace=True)

    return df


def df_from_json(json):
    """
    Convert a dictionary dataframe using JSON convention into a panda Dataframe.

    Dataframe must contain a timestamp column and be compatible to float data types.

    :param json: JSON formatted dataframe.
    :return: panda Dataframe
    """
    df = pandas.DataFrame.from_dict(json, orient='columns')
    df = df.set_index('Timestamp')

    if df.index.dtype == 'int64':
        df.index = [datetime.datetime.fromtimestamp(i) for i in (df.index / 1000).astype(int)]
        df.index.name = 'Timestamp'
    if not isinstance(df.index, pandas.DatetimeIndex):
        raise TypeError("Unexpected type {0}".format(df.index))

    df.rename_axis("sensorId", axis="columns", inplace=True)
    return df


def df_to_json(df: pandas.DataFrame):
    """
    Convert a panda Dataframe to a JSON compatible dictionary.

    Dataframe must be compatible to Wizata format using Timestamp index and float data types.

    :param df: panda Dataframe to convert.
    :return: dictionary representing JSON compatible dataframe.
    """
    df_json = {
        "Timestamp": list(df.index)
    }
    for col in list(df.columns):
        if col != 'Timestamp':
            df_json[col] = list(df[col].values.astype(float))
        else:
            df_json[col] = list(df[col].values)
    return df_json
