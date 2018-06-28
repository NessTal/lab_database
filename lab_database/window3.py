import remi.gui as gui
from remi import start, App
import pandas as pd
import peewee
from back_end import *


class Window3(App):
    def __init__(self, *args):
        super(Window3, self).__init__(*args)

    def main(self):
        self.info_dict = dict()
        window3_container = gui.VBox()
        self.search_by = ['ID', 'e-mail', 'Full Name']
        self.handedness = ['Right', 'Left']
        self.gender = ['Female', 'Male']
        self.search_widgets = dict()

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
        self.search_widgets['search by field'] = self.search_by_dd
        self.search_input = gui.Input()
        self.search_widgets['search by value'] = self.search_input
        self.search_button = gui.Button('Search')
        # Append to container
        search_by_container.append(self.search_by_dd)
        search_by_container.append(self.search_input)
        search_by_container.append(self.search_button)

        self.search_button.set_on_click_listener(self.search_button_click)

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
        # todo: add the new fields
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
        hebrew_age_row = self.add_row('Hebrew Age', 'spinbox')
        participant_table.add_child(str(id(hebrew_age_row)), hebrew_age_row)
        other_languages_row = self.add_row('Other Languages', 'input')
        participant_table.add_child(str(id(other_languages_row)), other_languages_row)
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
        experiment_row = self.add_row('Experiment', 'drop_down')
        experiment_table.add_child(str(id(experiment_row)), experiment_row)
        date_row = self.add_row('Date', 'date')
        experiment_table.add_child(str(id(date_row)), date_row)
        subject_number_row = self.add_row('Subject Number', 'input')
        experiment_table.add_child(str(id(subject_number_row)), subject_number_row)
        # exp_comments_row = self.add_row('Comments', 'input')
        # experiment_table.add_child(str(id(exp_comments_row)), exp_comments_row)
        list_row = self.add_row('List', 'input')
        experiment_table.add_child(str(id(list_row)), list_row)

        # Create labels
        participant_label = gui.Label('Participant')
        experiment_label = gui.Label('Experiment')

        # Create update button
        self.update_info = gui.Button('Update Info')

        # Add widgets to the container
        info_container.append(participant_label)
        info_container.append(participant_table)
        info_container.append(experiment_label)
        info_container.append(experiment_table)
        info_container.append(self.update_info)

        self.update_info.set_on_click_listener(self.update_subject_click)
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
        self.info_dict[label] = box  # add the widgets to a dict
        if box_type == 'spinbox':
            box.set_value(0)
        item.add_child(str(id(item)), box)
        row.add_child(str(id(item)), item)
        return row

    def search_button_click(self, widget):
        """search a user based on name/email/ID"""
        # Verify that the search fields are not empty, alert the user with dialog box
        # todo : test input
        field = self.search_widgets['search by field'].get_value()
        search_value = self.search_widgets['search by value'].get_value()
        if field not in self.search_by:
            self.show_dialog('Please select a field')
        elif search_value == '':
            self.show_dialog('Please enter your input')
        # verify that ID is an int
        # todo: check if other ID validation is required (we currently have some partial data, e.g. 4-digits IDs)
        elif field == 'ID' and not self.validate_int(search_value, 'ID'):
            pass
        else:
            if field == 'ID':
                search_value = int(search_value)
            subj_data = find_subject(search_value)
            subj_data = subj_data[0]
            # if the user does not exist, add the field we searched to the table so a new user could be created
            if subj_data.empty:
                print(subj_data)  # todo: delete this later
                self.show_dialog('No subject found, you can add a new subject below')
                self.info_dict[field].set_value(search_value)
            # else, add the subject's fields to the table
            else:
                self.add_subject(subj_data)

    def add_subject(self, data):
        """add a subject's details"""
        # access the relevant widgets and set the values in the DataFrame
        self.info_dict['ID'].set_value(str(data['sub_ID'][0]))
        self.info_dict['First Name'].set_value(data['first'][0])
        self.info_dict['Last Name'].set_value(data['last'][0])
        self.info_dict['e-mail'].set_value(data['mail'][0])
        self.info_dict['Gender'].set_value(data['gender'][0])
        self.info_dict['Year of Birth'].set_value(data['year_of_birth'][0])
        self.info_dict['Handedness'].set_value(data['dominant_hand'][0])
        self.info_dict['Reading Span'].set_value(int(data['reading_span'][0]))
        self.info_dict['Comments'].set_value(data['notes'][0])
        self.info_dict['Hebrew Age'].set_value(int(data['hebrew_age'][0]))
        self.info_dict['Other Languages'].set_value(data['other_languages'][0])

    def update_subject_click(self, widget):
        """updates a subject's info when the Update Info button is clicked"""
        if self.info_dict['ID'].get_value() == '':
            self.show_dialog('Please enter the ID')
        else:
            if self.validate_int(self.info_dict['ID'].get_value(), 'ID'):
                sub_id = int(self.info_dict['ID'].get_value())
            else:
                sub_id = 0
            first = self.info_dict['First Name'].get_value()
            last = self.info_dict['Last Name'].get_value()
            mail = self.info_dict['e-mail'].get_value()
            gender = self.info_dict['Gender'].get_value()
            # make sure this value is an integer. todo: turn this into a function
            if self.validate_int(self.info_dict['Year of Birth'].get_value(), 'Year of Birth'):
                year_of_birth = int(self.info_dict['Year of Birth'].get_value())
            else:
                year_of_birth = 0
            dominant_hand = self.info_dict['Handedness'].get_value()
            if self.validate_int(self.info_dict['Reading Span'].get_value(), 'Reading Span'):
                reading_span = int(self.info_dict['Reading Span'].get_value())
            else:
                reading_span = 0
            notes = self.info_dict['Comments'].get_value()
            if self.validate_int(self.info_dict['Hebrew Age'].get_value(), 'Hebrew Age'):
                hebrew_age = int(self.info_dict['Hebrew Age'].get_value())
            else:
                hebrew_age = 0
            other_languages = self.info_dict['Other Languages'].get_value()

            subject_info={'sub_id': sub_id,
                          'first': first,
                          'last': last,
                          'mail': mail,
                          'gender': gender,
                          'year_of_birth': year_of_birth,
                          'dominant_hand': dominant_hand,
                          'reading_span': reading_span,
                          'notes': notes,
                          'hebrew_age': hebrew_age,
                          'other_languages': other_languages}
            insert_experiment(subject_info)

    def validate_int(self, num, field: str, debug=False)->bool:
        """validates that the input can be modified to int"""
        try:
            x = int(num)
            return True
        except ValueError:
            if not debug:
                self.show_dialog(f'The field {field} can only contain numbers')
                return False
            else:
                raise ValueError # for testing

    def show_dialog(self, message: str):
        self.error_dialog = gui.GenericDialog(message=message)
        self.error_dialog.show(self)


if __name__ == '__main__':
    start(Window3)
