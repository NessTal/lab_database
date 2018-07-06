switch_dict = {'gender': 'other',
               'year_of_birth': 'range',
               'dominant_hand': 'other',
               'reading_span': 'range',
               'send_mails': 'other',
               'hebrew_age': 'range',
               'other_languages': 'textinput'}


class FiltSwitch:

    def __init__(self):
        self.switch_dict = {'range': self.__filt_range,
                            'textinput': self.__filt_textinput,
                            'other': self.__filt_other}

    def __filt_range(self, key, val, df):
        df = df.loc[list(df[key] >= val[0])]
        df = df.loc[list(df[key] <= val[1])]
        return df

    def __filt_textinput(selfself, key, val, df):
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

