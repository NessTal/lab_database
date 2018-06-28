class FiltSwitch:

    def __init__(self):
        self.switch_dict = {
            'gender': self.__filt_gender,
            'hand': self.__filt_dominant_hand,
        }

    def __filt_gender(self, val, df):
        return df.loc[df['gender'] == val]

    def __filt_dominant_hand(self, val, df):
        pass

    def filter_by_key(self, key, val, df):
        return self.switch_dict[key](val, df)


if __name__ == '__main__':
    sw = FiltSwitch()
    new_df = sw.filter_by_key(key, val, df)
