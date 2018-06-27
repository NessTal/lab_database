import remi.gui as gui
from remi import start, App


class Window3(App):
    def __init__(self, *args):
        super(Window3, self).__init__(*args)

    def main(self):
        self.info_dict = dict()
        window3_container = gui.VBox()
        self.search_by = ['ID', 'e-mail', 'Name']
        self.handedness = ['Right', 'Left']
        self.gender = ['Female', 'Male']

        # Append to container
        window3_container.append(self.search_by_container())
        window3_container.append(self.participant_info())

        return window3_container

    def search_by_container(self):
        """create search by drop down, input and button"""
        search_by_container = gui.HBox(width='60%', height='20%')
        self.search_by_dd = gui.DropDown(width='30%')
        self.search_by_dd.add_child(0, gui.DropDownItem('Search By'))
        for idx, exp in enumerate(self.search_by):
            self.search_by_dd.add_child(idx + 1, gui.DropDownItem(exp))
        self.search_input = gui.Input()
        self.search_button = gui.Button('Search')
        # Append to container
        search_by_container.append(self.search_by_dd)
        search_by_container.append(self.search_input)
        search_by_container.append(self.search_button)

        return search_by_container

    def participant_info(self):
        """Show or edit participants' info"""
        info_container = gui.VBox()
        # Create participants' info table and add titles
        participant_table = gui.Table()
        row = gui.TableRow()
        table_title = gui.TableTitle()
        table_title.add_child(str(id(table_title)), 'Field')
        row.add_child(str(id(table_title)), table_title)
        table_title = gui.TableTitle()
        table_title.add_child(str(id(table_title)), 'Info')
        row.add_child(str(id(table_title)), table_title)
        participant_table.add_child(str(id(row)), row)

        # Create and add the relevant rows to the table
        id_row = self.add_row('ID', 'input')
        participant_table.add_child(str(id(id_row)), id_row)
        first_name_row = self.add_row('First Name', 'input')
        participant_table.add_child(str(id(first_name_row)), first_name_row)
        last_name_row = self.add_row('Last Name', 'input')
        participant_table.add_child(str(id(last_name_row)), last_name_row)
        email_row = self.add_row('e-mail', 'input')
        participant_table.add_child(str(id(email_row)), email_row)
        gender_row = self.add_row('Gender', 'drop_down')
        participant_table.add_child(str(id(gender_row)), gender_row)
        year_of_birth_row = self.add_row('Year of Birth', 'spinbox')
        participant_table.add_child(str(id(year_of_birth_row)), year_of_birth_row)
        handedness_row = self.add_row('Handedness', 'drop_down')
        participant_table.add_child(str(id(handedness_row)), handedness_row)
        reading_span_row = self.add_row('Reading Span', 'spinbox')
        participant_table.add_child(str(id(reading_span_row)), reading_span_row)
        comments_row = self.add_row('Comments', 'input')
        participant_table.add_child(str(id(comments_row)), comments_row)

        # add handedness options
        self.info_dict['Handedness'].add_child(0, gui.DropDownItem('Handedness'))
        for idx, exp in enumerate(self.handedness):
            self.info_dict['Handedness'].add_child(idx + 1, gui.DropDownItem(exp))
        # add gender options
        self.info_dict['Gender'].add_child(0, gui.DropDownItem('Gender'))
        for idx, exp in enumerate(self.gender):
            self.info_dict['Gender'].add_child(idx + 1, gui.DropDownItem(exp))

        # create experiment details table and add titles
        experiment_table = gui.Table()
        row = gui.TableRow()
        table_title = gui.TableTitle()
        table_title.add_child(str(id(table_title)), 'Field')
        row.add_child(str(id(table_title)), table_title)
        table_title = gui.TableTitle()
        table_title.add_child(str(id(table_title)), 'Info')
        row.add_child(str(id(table_title)), table_title)
        experiment_table.add_child(str(id(row)), row)

        # create and add rows for the experiments table
        subject_row = self.add_row('ID', 'input')
        participant_table.add_child(str(id(subject_row)), subject_row)
        experiment_row = self.add_row('Experiment', 'drop_down')
        participant_table.add_child(str(id(experiment_row)), experiment_row)

        # Create labels
        participant_label = gui.Label('Participant')
        experiment_label = gui.Label('Experiment')

        # Add widgets to the container
        info_container.append(participant_label)
        info_container.append(participant_table)
        info_container.append(experiment_label)
        info_container.append(experiment_table)
        return info_container

    def add_row(self, label, box_type):
        """create a row with a table and box type"""
        types_dict = {'input': gui.TextInput,
                      'date': gui.Date,
                      'spinbox': gui.SpinBox,
                      'drop_down': gui.DropDown}
        row = gui.TableRow()
        item = gui.TableItem()
        label = label
        item.add_child(str(id(item)), label)
        row.add_child(str(id(item)), item)
        item = gui.TableItem()
        box = types_dict[box_type]()
        self.info_dict[label] = box
        if box_type == 'spinbox':
            box.set_value(0)
        item.add_child(str(id(item)), box)
        row.add_child(str(id(item)), item)
        return row


if __name__ == '__main__':
    start(Window3)
