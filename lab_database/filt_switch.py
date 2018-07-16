import datetime as dt
import pandas as pd

switch_dict = {'gender': 'other',
               'date_of_birth': 'date',
               'dominant_hand': 'other',
               'reading_span': 'range',
               'send_mails': 'other',
               'hebrew_age': 'range',
               'other_languages': 'textinput',
               'experiment_name': 'textinput',
               'experimenter_name': 'textinput',
               'experimenter_mail': 'textinput',
               'duration': 'range',
               'lab': 'other'}


class FiltSwitch:

    def __init__(self):
        self.switch_dict = {'range': self.__filt_range,
                            'date': self.__filt_date,
                            'textinput': self.__filt_textinput,
                            'other': self.__filt_other}

    def __filt_range(self, key, val, df):
        if val[0] != 'None':
            df = df.loc[df[key] >= val[0]]
        if val[1] != 'None':
            df = df.loc[df[key] <= val[1]]
        return df

    def __filt_date(self, key, val, df):
        col = pd.to_datetime(df[key],format='%d-%m-%Y')
        from_list = val[0].split('-')
        to_list = val[1].split('-')
        if val[0] != 'None':
            df = df.loc[col >= dt.date(int(from_list[2]),int(from_list[1]),int(from_list[0]))]
        if val[1] != 'None':
            df = df.loc[col <= dt.date(int(to_list[2]),int(to_list[1]),int(to_list[0]))]
        return df

    def __filt_textinput(self, key, val, df):
        if val == 'None':
            df = df.loc[df[key].isna()]
        else:
            df = df.loc[df[key] == val]
        return df

    def __filt_other(self, key, val, df):
        return df.loc[df[key] == val]


    def filter_by_key(self, key, val, df):
        if key != 'exp_include' and key != 'exp_exclude':
            df = self.switch_dict[switch_dict[key]](key, val, df)
        return df


if __name__ == '__main__':
    sw = FiltSwitch()
    new_df = sw.filter_by_key(key, val, df)

