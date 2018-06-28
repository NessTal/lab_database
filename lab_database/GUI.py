import remi.gui as gui
from remi import start, App
from back_end import *

class LabApp(App):
    def __init__(self, *args):
        self.exp_names = ['A','B','Exp1','Exp2','B','C','A','B','C','A','B','C','A','B','C','A','B','C','A','B','C','A','B','C','A','B','C','A','B','C'] ######### to be somehow received from the database
        # lists containing the filter's widgets, for the function filter() to get their values:
        self.filter_bio_widgets = []
        self.filter_exp_yes_widgets = []
        self.filter_exp_no_widgets = []
        self.filter_table = []
        self.info_dict = dict()
        self.search_by = ['ID', 'e-mail', 'Full Name']
        self.handedness = ['Right', 'Left']
        self.gender = ['Female', 'Male']
        self.search_widgets = dict()
        super(LabApp, self).__init__(*args)

    def main(self):
        """
        calls for the three big containers and creates tabs
        """
        container = gui.TabBox()
        container.add_tab(self.filters_widget(), 'Fillter', 'Fillter')
        container.add_tab(self.edit_widget(), 'Add or Edit Subject', 'Add or Edit Subject')
        container.add_tab(self.create_widget(), 'Add Fields', 'Add Fields')
        return container

    """
    Filters tab
    """

    def filters_widget(self):
        """
        creates the filters container by calling for its three parts (two that create filters and one that creates the table).
        """
        filters_widget = gui.VBox(width = '100%', height = 1000) # the entire tab
        filters_box = gui.HBox(width = 800, height = 50)  # the upper part
        filters_box.append(self.exp_filters())
        filters_box.append(self.bio_filters())
        table_box = gui.TableWidget(0,0)    # the bottom part
        self.filter_table = table_box
        filters_widget.append(filters_box)
        filters_widget.append(table_box)
        return filters_widget

    def bio_filters(self):
        """
        creates filters for the subject's biographic information.
        the "Filter" and "Send an E-Mail" buttons are also created here (but their listener functions are for all filtering, including exp).
        """
        bio_filters = gui.VBox(width = 300, height = 450)

        languages = gui.HBox(width = 300, height = 100)
        hebrew_age = gui.TextInput(hint='Hebrew exposure age')
        languages.append(hebrew_age)
        other_languages = gui.TextInput(hint='other languages')
        languages.append(other_languages)
        bio_filters.append(languages)
        self.filter_bio_widgets.append(hebrew_age)
        self.filter_bio_widgets.append(other_languages)

        gender = gui.DropDown()
        gender.add_child(0,gui.DropDownItem('Gender'))
        gender.add_child(1,gui.DropDownItem('Male'))
        gender.add_child(2,gui.DropDownItem('Female'))
        bio_filters.append(gender)
        self.filter_bio_widgets.append(gender)

        years = gui.HBox(width = 300, height = 100)
        years_label = gui.Label('Year of birth',width = 300)
        years_from = gui.TextInput(hint='from')
        years_to = gui.TextInput(hint='to')
        years.append(years_label)
        years.append(years_from)
        years.append(years_to)
        bio_filters.append(years)
        self.filter_bio_widgets.append(years_from)
        self.filter_bio_widgets.append(years_to)

        hand = gui.DropDown()
        hand.add_child(0,gui.DropDownItem('Dominant hand'))
        hand.add_child(1,gui.DropDownItem('Right'))
        hand.add_child(2,gui.DropDownItem('Left'))
        bio_filters.append(hand)
        self.filter_bio_widgets.append(hand)

        rs = gui.HBox(width = 300, height = 100)
        rs_label = gui.Label('Reading Span',width = 300)
        rs_from = gui.TextInput(hint='from')
        rs_to = gui.TextInput(hint='to')
        rs.append(rs_label)
        rs.append(rs_from)
        rs.append(rs_to)
        bio_filters.append(rs)
        self.filter_bio_widgets.append(rs_from)
        self.filter_bio_widgets.append(rs_to)

        send_mails = gui.CheckBoxLabel('Agreed to receive emails')
        bio_filters.append(send_mails)
        self.filter_bio_widgets.append(send_mails)

#        gap = gui.HBox(height=150)
#        bio_filters.append(send_mails)

        # Filter and email buttons with listener:
        buttons_box = gui.HBox(width = 300, height=100)
        filter_button = gui.Button('Filter', width = 80)
        filter_button.set_on_click_listener(self.filter)
        buttons_box.append(filter_button)
        email_button = gui.Button('Send an E-Mail', width = 150)
        email_button.set_on_click_listener(self.send_email)
        buttons_box.append(email_button)
        bio_filters.append(buttons_box)



        return bio_filters

    def exp_filters(self):
        """
        creates an "include" and "exclude" checkbox for each experiment.
        """
        exp_filters = gui.HBox()
        for idx, exp in enumerate(self.exp_names):
            if (idx % 15) == 0:
                exp_table = gui.Table()
                # creating the titles:
                row = gui.TableRow()
                item = gui.TableTitle()
                item.add_child(str(id(item)),'Include')
                row.add_child(str(id(item)),item)
                item = gui.TableTitle()
                item.add_child(str(id(item)),'Exclude')
                row.add_child(str(id(item)),item)
                item = gui.TableTitle()
                item.add_child(str(id(item)),'Experiment')
                row.add_child(str(id(item)),item)
                exp_table.add_child(str(id(row)), row)
            # creating a row for each experiment:
            row = gui.TableRow()
            item = gui.TableItem()
            cb_yes = gui.CheckBox()
            item.add_child(str(id(item)),cb_yes)
            row.add_child(str(id(item)),item)
            item = gui.TableItem()
            cb_no = gui.CheckBox()
            item.add_child(str(id(item)),cb_no)
            row.add_child(str(id(item)),item)
            item = gui.TableItem()
            exp_name = gui.Label(exp)
            item.add_child(str(id(item)),exp_name)
            row.add_child(str(id(item)),item)
            exp_table.add_child(str(id(row)), row)
            self.filter_exp_yes_widgets.append(cb_yes)
            self.filter_exp_no_widgets.append(cb_no)
            if (idx % 15) == 0:
                exp_filters.append(exp_table)
        return exp_filters

    def filter(self, *args):
        """
        passes the requested filters to a function that queries the database, receives the relevant data
        and displays it in the table part of the Filter tab.
        sends a dict with field as a key and the desired filter an value (for exp filter this would be a list).
        """
        # reset selected filters dict:
        selected_filters = {}
        # check which filters were selected:
        # exp filters:
        selected_exp_yes = []
        selected_exp_no = []
        for idx, exp in enumerate(self.exp_names):
            if self.filter_exp_yes_widgets[idx].get_value() == 1:
                selected_exp_yes.append(self.exp_names[idx])
            elif self.filter_exp_no_widgets[idx].get_value() == 1:
                selected_exp_no.append(self.exp_names[idx])
        if selected_exp_yes != []:
            selected_filters['exp_include'] = selected_exp_yes
        if selected_exp_no != []:
            selected_filters['exp_exclude'] = selected_exp_no

        #bio filters: 0-1: languages, 2: gender, 3-4: years, 5: hand, 6-7: rs
        if (self.filter_bio_widgets[0].get_value() != ''):
            selected_filters['hebrew_age'] = int(self.filter_bio_widgets[0].get_value())
        if (self.filter_bio_widgets[1].get_value() != ''):
            selected_filters['other_languages'] = self.filter_bio_widgets[1].get_value()
        if (self.filter_bio_widgets[2].get_value() != None) and (self.filter_bio_widgets[2].get_value() != 'Gender'):
            selected_filters['gender'] = self.filter_bio_widgets[2].get_value()
        if self.filter_bio_widgets[3].get_value() != '':
            selected_filters['year_from'] = int(self.filter_bio_widgets[3].get_value())
        if self.filter_bio_widgets[4].get_value() != '':
            selected_filters['year_to'] = int(self.filter_bio_widgets[4].get_value())
        if (self.filter_bio_widgets[5].get_value() != None) and (self.filter_bio_widgets[5].get_value() != 'Dominant hand' ):
            selected_filters['hand'] = self.filter_bio_widgets[5].get_value()
        if self.filter_bio_widgets[6].get_value() != '':
            selected_filters['rs_from'] = int(self.filter_bio_widgets[6].get_value())
        if self.filter_bio_widgets[7].get_value() != '':
            selected_filters['rs_to'] = int(self.filter_bio_widgets[7].get_value())
        if self.filter_bio_widgets[8].get_value() == '1':
            selected_filters['send_mails'] = int(self.filter_bio_widgets[8].get_value())
        results = filt(filt_dict = selected_filters)
        results_list_of_tuples = []
        results_list_of_tuples.append(tuple(results.columns.values))
        for idx, row in results.iterrows():
            results_list_of_tuples.append(tuple(row))
        print(results_list_of_tuples)
        self.filter_table.append_from_list(results_list_of_tuples,fill_title=True)
        return results

    def send_email(self):
        print('emails') ######### add noa's function

    """
    Edit tab
    """

    def edit_widget(self):
        window3_container = gui.VBox()
        # Append to container
        window3_container.append(self.search_by_container())
        window3_container.append(self.participant_info())
        return window3_container # edit_widget

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

            subject_info={'sub_ID': sub_id,
                          'first': first,
                          'last': last,
                          'mail': mail,
                          'gender': gender,
                          'year_of_birth': year_of_birth,
                          'dominant_hand': dominant_hand,
                          'reading_span': reading_span,
                          'notes': notes,
                          'hebrew_age': hebrew_age,
                          'other_languages': other_languages,
                          'name': 'no_exp'}
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
        self.error_dialog = gui.GenericDialog(message=message, width='30%', height='15%')
        self.error_dialog.show(self)


    """
    Create tab
    """
    def create_widget(self): # to be added in the future
        create_widget = gui.VBox(width = 500, height = 500)
        return create_widget


start(LabApp, address='0.0.0.0', port=8081,multiple_instance=True,start_browser=True)