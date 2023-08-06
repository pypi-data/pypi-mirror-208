"""
Functions to process Spitschan 2016 (Outdoor illumination ...)
spectrum data files.

Reference:
Spitschan, M., Aguirre, G., Brainard, D. et al.
Variation of outdoor illumination as a function of solar elevation and light pollution.
Sci Rep 6, 26756 (2016). https://doi.org/10.1038/srep26756
"""

import os
import pandas as pd
import numpy as np
from dreye.api.units.convert import irr2flux
from dreye import DREYE_DIR


_WL_FILE = 'srep26756-s1.csv'
_RURAL_FILE = 'srep26756-s2.csv'
_CITY_FILE = 'srep26756-s3.csv'
SPITSCHAN2016_DATA = {
    'rural': {
        'filepath': os.path.join(DREYE_DIR, 'datasets', 'spitschan2016', _RURAL_FILE),
        'wl_filepath': os.path.join(DREYE_DIR, 'datasets', 'spitschan2016', _WL_FILE)
    },
    'city': {
        'filepath': os.path.join(DREYE_DIR, 'datasets', 'spitschan2016', _CITY_FILE),
        'wl_filepath': os.path.join(DREYE_DIR, 'datasets', 'spitschan2016', _WL_FILE)
    }
}
SPITSCHAN2016_FILE = os.path.join(
    DREYE_DIR, 'datasets', 'spitschan2016', 'spitschan2016.feather'
)


def load_dataset(as_wide=False, label_cols='data_id'):
    """
    Load Spitschan dataset of various spectra for different times of day as a dataframe.

    Parameters
    ----------
    as_wide : bool, optional
        Whether to return the dataframe as a wide-format dataframe.
    label_cols : str or list-like, optional
        The column `pandas.MultiIndex`, if `as_wide` is True.

    Returns
    -------
    df : `pandas.DataFrame`
        A long-format `pandas.DataFrame` with the following columns:
            * `date_number`
            * `solar_elevation`
            * `lunar_elevation`
            * `fraction_moon_illuminated`
            * `timestamp`
            * `hour`
            * `month`
            * `data_id`
            * `wavelengths`
            * `spectralirradiance`
            * `microspectralphotonflux`
            * `location`
        The columns attribute is a `pandas.MultiIndex` in wide-format.

    References
    ----------
    .. [1] Spitschan, M., Aguirre, G.K., Brainard, D.H., Sweeney, A.M. (2016)
       Variation of outdoor illumination as a function of solar elevation and light pollution.
       Sci Rep 6, 26756.
    """
    if os.path.exists(SPITSCHAN2016_FILE):
        df = pd.read_feather(SPITSCHAN2016_FILE)
    else:
        df = pd.DataFrame()
        for location, kwargs in SPITSCHAN2016_DATA.items():
            df_ = process_spitschan(**kwargs)
            df_['location'] = location
            if len(df) > 0:
                df_['data_id'] += (df['data_id'].max() + 1)
            df = df.append(df_, ignore_index=True)

    df.loc[:, 'microspectralphotonflux'] = df['microspectralphotonflux'].fillna(0)
    df.loc[df['microspectralphotonflux'] < 0, 'microspectralphotonflux'] = 0
    df.loc[:, 'spectralirradiance'] = df['spectralirradiance'].fillna(0)
    df.loc[df['spectralirradiance'] < 0, 'spectralirradiance'] = 0

    if as_wide:
        return pd.pivot_table(
            df,
            'microspectralphotonflux',
            'wavelengths',
            label_cols
        ).fillna(0)

    return df


def _process_spitschan(filepath, wl_filepath):
    """
    Process Spitschan2016 file and return metadata and data
    """
    wls = pd.read_csv(wl_filepath, header=None, names=['wavelengths'])
    df = pd.read_csv(filepath).iloc[:, :-1]
    # format metadata
    metadata = df.iloc[:4]
    metadata.index = [
        'date_number', 'solar_elevation',
        'lunar_elevation', 'fraction_moon_illuminated'
    ]
    metadata = metadata.T
    metadata['timestamp'] = pd.to_datetime(metadata.index)
    metadata['hour'] = metadata['timestamp'].dt.hour
    metadata['month'] = metadata['timestamp'].dt.month
    metadata.index = np.arange(metadata.shape[0])
    metadata['data_id'] = metadata.index
    # reformat data
    data = df.iloc[4:]
    data.index = wls['wavelengths']
    data.columns = np.arange(data.shape[1])
    data = data.T
    return metadata, data


def process_spitschan(filepath, wl_filepath):
    """
    Process Spitschan2016 file and return a long dataframe
    """
    metadata, data = _process_spitschan(filepath, wl_filepath)
    # create long format pandas dataframe
    data.index = pd.MultiIndex.from_frame(metadata)
    data = data.stack()
    data.name = 'spectralirradiance'
    data = data.reset_index()
    data['microspectralphotonflux'] = irr2flux(
        data['spectralirradiance'], data['wavelengths']
    ) * 10 ** 6
    return data
