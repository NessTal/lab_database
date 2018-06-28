class FiltSwitch:

    def __init__(self):
        self.switch_dict = {
            'gender': self.__filt_gender,
            'year_from': self.__filt_year_from,
            'year_to': self.__filt_year_to,
            'hand': self.__filt_hand,
            'rs_from': self.__filt_rs_from,
            'rs_to': self.__filt_rs_to,
            'send_mails': self.__filt_send_mails,
            'hebrew_age': self.__filt_hebrew_age,
            'other_languages': self.__filt_other_languages
        }

    def __filt_gender(self, val, df):
        return df.loc[df['gender'] == val]

    def __filt_year_from(self, val, df):
        return df.loc[df['year_of_birth'] >= val]

    def __filt_year_to(self, val, df):
        return df.loc[df['year_of_birth'] <= val]

    def __filt_hand(self, val, df):
        return df.loc[df['dominant_hand'] == val]

    def __filt_rs_from(self, val, df):
        return df.loc[df['reading_span'] >= val]

    def __filt_rs_to(self, val, df):
        return df.loc[df['reading_span'] <= val]

    def __filt_send_mails(self, val, df):
        return df.loc[df['send_mails'] == val]

    def __filt_hebrew_age(self, val, df):
        return df.loc[df['hebrew_age'] <= val]

    def __filt_other_languages(self, val, df):
        return df.loc[df['other_languages'] == val]


    def filter_by_key(self, key, val, df):
        if key != 'exp_include' and key != 'exp_exclude':
            df = self.switch_dict[key](val, df)
        return df


if __name__ == '__main__':
    sw = FiltSwitch()
    new_df = sw.filter_by_key(key, val, df)

