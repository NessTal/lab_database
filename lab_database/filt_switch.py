class FiltSwitch:

    def __init__(self):
        self.switch_dict = {
            'gender': self.__filt_other,
            'year_of_birth': self.__filt_range,
            'dominant_hand': self.__filt_other,
            'reading_span': self.__filt_range,
            'send_mails': self.__filt_other,
            'hebrew_age': self.__filt_range,
            'other_languages': self.__filt_textinput
        }

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
            df = self.switch_dict[key](key, val, df)
        return df


if __name__ == '__main__':
    sw = FiltSwitch()
    new_df = sw.filter_by_key(key, val, df)

