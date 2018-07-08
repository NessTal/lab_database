import remi.gui as gui
from remi import start, App
#from back_end import *
from main import *
from filt_switch import *
from apscheduler.schedulers.blocking import BlockingScheduler
import multiprocessing
import csv

class LabApp(App):
    def __init__(self, *args):
        self.exp_names = unique_experiments()
        self.range_subject = {'hebrew_age':'Hebrew exposure age','year_of_birth':'Year of birth','reading_span':'Reading span'}
        self.dropdown_subject = {'gender':['Gender','Male','Female'], 'dominant_hand':['Dominant hand','Right','Left']}
        self.textinput_subject = {'other_languages':'Other languages'}
        self.checkbox_subject = {'send_mails': 'Agreed to receive emails'}
        self.textinput_search = {'sub_ID': 'ID',
                                 'first': 'First name',
                                 'last': 'Last name',
                                 'mail': 'e-mail',
                                 'other_languages': 'Other languages',
                                 'sub_notes': 'Comments'}
        self.date_subject = dict()
        self.range_experiment = dict()
        self.dropdown_experiment = {'exp_name': ['Experiments', 'Add New'] + self.exp_names}
        self.textinput_experiment = {'sub_code': 'Subject number',
                                     'exp_list': 'List',
                                     'exp_notes': 'Comments'}
        self.checkbox_experiment = {'participated': 'Participated'}
        self.date_experiment = {'date': 'Date'}
        self.order_filters = ['hebrew_age', 'other_languages', 'year_of_birth','gender','dominant_hand','reading_span','send_mails']
        self.order_subject = ['sub_ID', 'first', 'last', 'mail', 'gender', 'year_of_birth', 'dominant_hand',
                              'hebrew_age', 'other_languages', 'reading_span','send_mails',
                              'sub_notes']
        self.order_experiment = ['exp_name', 'participated', 'sub_code', 'date', 'exp_list', 'exp_notes']
        self.row_titles_search = {'first': 'First name', 'last': 'Last name', 'sub_ID': 'ID',
                                  'year_of_birth': 'Year of birth', 'dominant_hand': 'Dominant hand', 'mail': 'e-mail',
                                  'sub_notes': 'Comments', 'send_mails': 'Agreed to receive emails',
                                  'reading_span': 'Reading span', 'gender': 'Gender',
                                  'hebrew_age': 'Hebrew exposure age', 'other_languages': 'Other languages',
                                  'sub_code': 'Subject number', 'exp_name': 'Experiment', 'date': 'Date',
                                  'participated': 'Participated', 'exp_notes': 'Comments', 'exp_list': 'List'}

        # lists containing the filter's widgets, for the function filter() to get their values:
        self.filter_bio_widgets = {}
        self.filter_exp_yes_widgets = []
        self.filter_exp_no_widgets = []
        self.filter_export_file_name = []
        self.bio_widgets_for_display = {}
        self.new_field_widgets = []

        self.dialog = gui.GenericDialog(width='470', height='150')
        self.filter_results = pd.DataFrame()

        # attributes for the Edit tab
        self.info_dict = dict()
        self.search_by = ['ID', 'e-mail', 'Full Name']
        self.exp_info_dict = dict()
        self.search_widgets = dict()

        super(LabApp, self).__init__(*args)


    def main(self):
        """
        calls for the three big containers and creates tabs
        """
        self.new_fields_to_dicts()
        container = gui.TabBox()
        container.add_tab(self.filters_tab(), 'Fillter', 'Fillter')
        container.add_tab(self.edit_widget(), 'Add or Edit Subjects', 'Add or Edit Subjects')
        container.add_tab(self.new_field_tab(), 'Add New Fields', 'Add New Fields')
        return container

    """
    Filters tab
    """
    def filters_tab(self):
        """
        creates the filters tab which contains two part - filters and table (for the results).
        """
        filters_tab = gui.VBox(width = '100%') # the entire tab
        self.filters_box = gui.HBox(width = 800)  # the upper part
        self.filters_box.style['margin-top'] = '20px'
        filters_tab.append(self.filters_box)
        self.filter_table = gui.TableWidget(0,0)
        self.filter_table.style['margin-bottom'] = '100px'
        filters_tab.append(self.filter_table)
        self.filters_box.append(self.exp_filters())
        self.filters_box.append(self.subject_filters())
        return filters_tab

    def subject_filters(self):
        """
        creates filters for the subject's information.
        also calls for 'filters_tab_buttons' and appends the buttons box.
        """
        # create range filters:
        for filter, text in self.range_subject.items():
            box = gui.HBox(width = 350, height = 50)
            box.style['padding-left'] = '10px'
            box.style['padding-right'] = '10px'
            fil_label = gui.Label(text,width = 300)
            fil_from = gui.TextInput(hint='from',height=18)
            fil_to = gui.TextInput(hint='to',height=18)
            box.append(fil_label)
            box.append(fil_from)
            box.append(fil_to)
            self.filter_bio_widgets[filter] = [fil_from, fil_to]
            self.bio_widgets_for_display[filter] = box

        # create dropdown list filters:
        for filter, values in self.dropdown_subject.items():
            fil = gui.DropDown(height=20)
            for idx, val in enumerate(values):
                fil.add_child(idx,gui.DropDownItem(val))
            box = gui.HBox(width = 350, height = 50)
            box.style['padding-left'] = '10px'
            box.style['padding-right'] = '10px'
            box.append(fil)
            self.filter_bio_widgets[filter] = fil
            self.bio_widgets_for_display[filter] = box

        # create text input filters:
        for filter, text in self.textinput_subject.items():
            fil = gui.TextInput(hint=text,height=18)
            box = gui.HBox(width = 350, height = 50)
            box.style['padding-left'] = '10px'
            box.style['padding-right'] = '10px'
            box.append(fil)
            self.filter_bio_widgets[filter] = fil
            self.bio_widgets_for_display[filter] = box

        # create checkbox filters:
        for filter, text in self.checkbox_subject.items():
            fil = gui.CheckBoxLabel(text,height=18)
            box = gui.HBox(width = 350, height = 50)
            box.style['padding-left'] = '10px'
            box.style['padding-right'] = '10px'
            box.append(fil)
            self.filter_bio_widgets[filter] = fil
            self.bio_widgets_for_display[filter] = box

        # position filters:
        subject_filters = gui.Table()
        for idx, filter in enumerate(self.order_filters):
            row = gui.TableRow()
            item = gui.TableItem()
            item.add_child(0,self.bio_widgets_for_display[filter])
            row.add_child(0,item)
            subject_filters.add_child(idx,row)

        # add buttons:
        row = gui.TableRow()
        item = gui.TableItem()
        item.add_child(0,self.filters_tab_buttons())
        row.add_child(0,item)
        subject_filters.add_child(len(self.order_filters)+1,row)

        return subject_filters


    def filters_tab_buttons(self):
        """
        create the buttons for the filters tab.
        """
        buttons_box = gui.VBox(width = 350)
        buttons_box.style['padding-left'] = '10px'
        buttons_box.style['padding-right'] = '10px'
        buttons_box_1 = gui.HBox()
        buttons_box_1.style['margin-top'] = '10px'
        buttons_box_1.style['margin-bottom'] = '10px'
        filter_button = gui.Button('Filter', width = 70)
        filter_button.set_on_click_listener(self.filter_listener)
        buttons_box_1.append(filter_button)
        exp_list_button = gui.Button('Experiment list', width = 120)
        exp_list_button.style['margin-left'] = '10px'
        exp_list_button.style['margin-right'] = '10px'
        exp_list_button.set_on_click_listener(self.exp_list_listener)
        buttons_box_1.append(exp_list_button)
        clear_button = gui.Button('Clear', width = 70)
        clear_button.set_on_click_listener(self.clear_filters)
        buttons_box_1.append(clear_button)
        buttons_box.append(buttons_box_1)

        email_button = gui.Button('Send E-Mails', width = 140)
        email_button.set_on_click_listener(self.send_email_listener)
        buttons_box.append(email_button)

        export_box = gui.HBox(width = 350, height= 50)
        export_button = gui.Button('Export to Excel', width = 140)
        export_button.set_on_click_listener(self.export_to_excel_listener)
        export_file_name_input = gui.TextInput(hint='file name', width = 195, height=22)
        export_box.append(export_button)
        export_box.append(export_file_name_input)
        self.filter_export_file_name = export_file_name_input
        buttons_box.append(export_box)

        return buttons_box


    def exp_filters(self):
        """
        creates a table with "include" and "exclude" checkboxes for each experiment.
        """
        exp_filters = gui.HBox()
        for idx, exp in enumerate(self.exp_names):
            if (idx % 15) == 0: # starts an new table after each 15 experiments. todo: make all tables be of the same length (by adding empty rows)
                exp_table = gui.Table()
                exp_table.style['margin-right'] = '10px'
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


    def filter_listener(self, *args):
        self.filter(exp_list = 0)

    def exp_list_listener(self, *args):
        self.filter(exp_list = 1)

    def filter(self, exp_list=0, *args):
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

        if exp_list == 1 and len(selected_exp_yes) != 1:
            self.show_dialog("Please choose a single experiment to get the experiment's list.")
            self.filter_table.empty()
        else:

            # bio filters:
            # range filters:
            for filter in self.range_subject.keys():
                from_val = self.filter_bio_widgets[filter][0].get_value()
                to_val = self.filter_bio_widgets[filter][1].get_value()
                if from_val != '' :
                    if to_val != '' :
                        selected_filters[filter] = [int(from_val), int(to_val)]
                    else:
                        selected_filters[filter] = [int(from_val), max_range_value]
                else:
                    if to_val != '' :
                        selected_filters[filter] = [0, int(to_val)]

            # drop down filters:
            for filter, text in self.dropdown_subject.items():
                val = self.filter_bio_widgets[filter].get_value()
                if (val != None) and (val != text[0]):
                    selected_filters[filter] = val

            # text input filters:
            for filter in self.textinput_subject.keys():
                val = self.filter_bio_widgets[filter].get_value()
                if val != '':
                    selected_filters[filter] = val

            # chackbox filters:
            for filter in self.checkbox_subject.keys():
                val = self.filter_bio_widgets[filter].get_value()
                if val == True:
                    selected_filters[filter] = val

            # send selected filters (dict) to filt and receive a data frame with the filtered results:
            print(selected_filters)
            self.filter_results = filt(filt_dict = selected_filters, exp_list = exp_list)
            results_list_of_tuples = []
            results_list_of_tuples.append(tuple(self.filter_results.columns.str.capitalize().str.replace('_',' ')))
            self.filter_table.style['margin-top'] = '30px'
            for idx, row in self.filter_results.iterrows():
                results_list_of_tuples.append(tuple(row))
            self.filter_table.empty()
            self.filter_table.append_from_list(results_list_of_tuples,fill_title=True)
            for key,item in self.filter_table.get_child('0').children.items():
                self.filter_table.get_child('0').get_child(key).style['padding-left'] = '5px'
                self.filter_table.get_child('0').get_child(key).style['padding-right'] = '5px'
                self.filter_table.get_child('0').get_child(key).style['padding-top'] = '3px'
                self.filter_table.get_child('0').get_child(key).style['padding-bottom'] = '3px'


    def clear_filters(self,*args):
        self.filters_box.empty()
        self.filter_bio_widgets = {}
        self.filter_exp_yes_widgets = []
        self.filter_exp_no_widgets = []
        self.filter_export_file_name = []
        self.bio_widgets_for_display = {}
        self.filters_box.append(self.exp_filters())
        self.filters_box.append(self.subject_filters())


    def export_to_excel_listener(self, *args):
        file_name = self.filter_export_file_name.get_value()
        file = export_path+file_name+'.csv'
        self.filter_results.to_csv(file, index=False)
        self.show_dialog(f'Exported to: {file}')

    def send_email_listener(self,*args):
        if self.filter_results.empty == True:
            self.show_dialog('No recipients selected. Use the filter to select the relevant subjects.')
        else:
            self.dialog = gui.GenericDialog(message='',width=400)
            self.dialog.style['margin-top'] = '30px'
            self.dialog.style['padding'] = '30px'
            self.dialog.empty()
            box = gui.VBox()
            mail_subject = gui.TextInput(hint= 'Subject')
            mail_subject.style['padding-top'] = '3px'
            mail_subject.style['padding-bottom'] = '3px'
            mail_subject.style['margin-bottom'] = '15px'
            mail_content = gui.TextInput(single_line= False, hint= 'Content', height=450)
            mail_subject.style['padding-top'] = '3px'
            mail_content.style['margin-bottom'] = '15px'
            send_button = gui.Button('Send', width= 60)
            send_button.set_on_click_listener(self.send_emails)
            send_button.style['margin-left'] = '30px'
            cancel_button = gui.Button('Cancel', width= 60)
            cancel_button.set_on_click_listener(self.ok_or_cancel_listener)
            send_cancel_box = gui.HBox()
            send_cancel_box.append(cancel_button)
            send_cancel_box.append(send_button)
            box.append(mail_subject)
            box.append(mail_content)
            box.append(send_cancel_box)
            self.mail_widgets = [mail_subject,mail_content]
            self.dialog.append(box)
            self.dialog.show(self)

    def send_emails(self,*args):
        exp_mail(self.filter_results['mail'].tolist(),subject=self.mail_widgets[0].get_value(),contents=self.mail_widgets[1].get_value())
        self.dialog.hide()
        self.show_dialog('E-mails were sent!')
        print(self.filter_results['mail'].tolist())
        print(self.mail_widgets[0].get_value())
        print(self.mail_widgets[1].get_value())

    """
    Edit tab
    """

    def edit_widget(self):
        window3_container = gui.VBox()
        # Append to container
        window3_container.append(self.search_by_container())
        window3_container.append(self.participant_info())
        window3_container.append(self.import_from_excel())
        return window3_container  # edit_widget

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

        widgets_and_inputs = [
            (self.textinput_search, 'input'),
            (self.dropdown_subject, 'drop_down'),
            (self.range_subject, 'spinbox'),
            (self.date_subject, 'date'),
            (self.checkbox_subject, 'checkbox')
        ]
        # create the widgets and add them to a dictionary
        for widget in widgets_and_inputs:
            widget_dictionary = widget[0]
            widget_type = widget[1]
            for label in widget_dictionary:
                self.add_search_widget(label, widget_type, widget_dictionary, self.info_dict)

        # add the participants' table rows
        for row_title in self.order_subject:
            row = self.add_row(row_title, self.info_dict)
            participant_table.add_child(str(id(row)), row)

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

        exp_widgets_and_inputs = [
            (self.textinput_experiment, 'input'),
            (self.dropdown_experiment, 'drop_down'),
            (self.range_experiment, 'spinbox'),
            (self.date_experiment, 'date'),
            (self.checkbox_experiment, 'checkbox')
        ]
        # create the widgets and add them to a dictionary
        for widget in exp_widgets_and_inputs:
            widget_dictionary = widget[0]
            widget_type = widget[1]
            for label in widget_dictionary:
                self.add_search_widget(label, widget_type, widget_dictionary, self.exp_info_dict)

        # add the experiments table rows
        for row_title in self.order_experiment:
            row = self.add_row(row_title, self.exp_info_dict)
            experiment_table.add_child(str(id(row)), row)

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

    def add_search_widget(self, label, box_type, widget_dictionary, output_dictionary):
        """create a widget for the participants table"""
        types_dict = {'input': gui.TextInput,
                      'date': gui.Date,
                      'spinbox': gui.SpinBox,
                      'drop_down': gui.DropDown,
                      'checkbox': gui.CheckBox}
        box = types_dict[box_type]()  # create a widget
        if box_type == 'spinbox':
            box.set_value('-1')  # todo: '-1' is a temp value to avoid bugs. This should eventually be: ''.
        elif box_type == 'drop_down':
            for idx, item in enumerate(widget_dictionary[label]):
                box.add_child(idx + 1, gui.DropDownItem(item))
        output_dictionary[label] = box  # Store the widget in a dictionary

    def add_row(self, label, widget_dictionary):
        """create a row containing a label and a widget"""
        row_title = self.row_titles_search[label]
        row = gui.TableRow()
        item = gui.TableItem()
        item.add_child(str(id(item)), row_title)
        row.add_child(str(id(item)), item)
        item = gui.TableItem()
        box = widget_dictionary[label]
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
            subj_data = get_if_exists(search_value)
            # if the user does not exist, add the field we searched to the table so a new user could be created
            if type(subj_data) != pd.DataFrame:
                self.show_dialog('No subject found, you can add a new subject below')
                self.info_dict[field].set_value(str(search_value))  # todo: it doesn't work for full name
                # todo: clear all fields (other than the searched field)
            # else, add the subject's fields to the table
            else:
                self.add_subject(subj_data)

    def add_subject(self, data):
        """add a subject's details"""
        # access the relevant widgets and set the values in the DataFrame
        for label in self.info_dict:
            self.info_dict[label].set_value(str(data[label].values[0]))

    def update_subject_click(self, widget):
        """updates a subject's info when the Update Info button is clicked"""
        subject_info = dict()
        if self.info_dict['sub_ID'].get_value() == '':
            self.show_dialog('Please enter the ID')
        elif self.validate_int(self.info_dict['sub_ID'].get_value(), 'ID'):
            for label in self.info_dict:
                subject_info[label] = self.info_dict[label].get_value()
            subject_info['exp_name'] = 'no_exp'  # todo: this is temporary, delete later
        # else:
        #     if self.validate_int(self.info_dict['sub_ID'].get_value(), 'ID'):
        #         sub_id = int(self.info_dict['ID'].get_value())
        #     else:
        #         sub_id = 0
        #     first = self.info_dict['First Name'].get_value()
        #     last = self.info_dict['Last Name'].get_value()
        #     mail = self.info_dict['e-mail'].get_value()
        #     gender = self.info_dict['Gender'].get_value()
        #     # make sure this value is an integer. todo: turn this into a function
        #     if self.validate_int(self.info_dict['Year of Birth'].get_value(), 'Year of Birth'):
        #         year_of_birth = int(self.info_dict['Year of Birth'].get_value())
        #     else:
        #         year_of_birth = 0
        #     dominant_hand = self.info_dict['Handedness'].get_value()
        #     if self.validate_int(self.info_dict['Reading Span'].get_value(), 'Reading Span'):
        #         reading_span = int(self.info_dict['Reading Span'].get_value())
        #     else:
        #         reading_span = 0
        #     notes = self.info_dict['Comments'].get_value()
        #     if self.validate_int(self.info_dict['Hebrew Age'].get_value(), 'Hebrew Age'):
        #         hebrew_age = int(self.info_dict['Hebrew Age'].get_value())
        #     else:
        #         hebrew_age = 0
        #     other_languages = self.info_dict['Other Languages'].get_value()
        #
        #     subject_info = {
        #         'sub_ID': sub_id,
        #         'first': first,
        #         'last': last,
        #         'mail': mail,
        #         'gender': gender,
        #         'year_of_birth': year_of_birth,
        #         'dominant_hand': dominant_hand,
        #         'reading_span': reading_span,
        #         'notes': notes,
        #         'hebrew_age': hebrew_age,
        #         'other_languages': other_languages,
        #         'exp_name': 'no_exp'
        #     }
            add_or_update(subject_info)
            self.refresh_exp_lists()
            self.show_dialog('The participant was updated')

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


    def import_from_excel(self):
        import_box = gui.HBox(width = 300, height = 80)
        import_file = gui.TextInput(hint='File name', width = 140, height = 18)
        import_button = gui.Button('Import from excel', width = 140)
        import_button.set_on_click_listener(self.import_from_excel_listener)
        import_box.append(import_button)
        import_box.append(import_file)
        self.import_file_name = import_file
        return import_box

    def import_from_excel_listener(self,*args):
        file_name = self.import_file_name.get_value()
        file = import_path+file_name+'.csv'
        import_from_excel(file)
        self.refresh_exp_lists()
        self.show_dialog(f'Imported from: {file}')

    def refresh_exp_lists(self, *args):
        self.exp_names = unique_experiments()
        self.filter_exp_yes_widgets = []
        self.filter_exp_no_widgets = []
        self.clear_filters()


    """
    Add new fields tab
    """
    def new_field_tab(self):
        """
        creates the Add New fields tab.
        """
        new_field_tab = gui.VBox()
        new_field_tab.style['padding-top'] = '20px'
        new_field_tab.style['padding-bottom'] = '40px'
        field_name_box = gui.HBox()
        field_name_box.style['margin'] = '10px'
        field_name = gui.TextInput(width=370)
        self.new_field_widgets.append(field_name)
        field_name_box.append(gui.Label('Field name:', width=130))
        field_name_box.append(field_name)
        new_field_tab.append(field_name_box)

        to_which_table_box = gui.HBox()
        to_which_table_box.style['margin'] = '10px'
        to_which_table = gui.DropDown(width=370)
        to_which_table.append(gui.DropDownItem('Select'))
        to_which_table.append(gui.DropDownItem('a general "property" of a subject (e.g. reading span)'))
        to_which_table.append(gui.DropDownItem('a value in a specific experiment (e.g. experimental list)'))
        self.new_field_widgets.append(to_which_table)
        to_which_table_box.append(gui.Label('A value would be:',width=130))
        to_which_table_box.append(to_which_table)
        new_field_tab.append(to_which_table_box)

        field_type_box = gui.HBox()
        field_type_box.style['margin'] = '10px'
        field_type = gui.DropDown(width=370)
        field_type.append(gui.DropDownItem('Select'))
        field_type.append(gui.DropDownItem('Numerical, with range filtering'))
        field_type.append(gui.DropDownItem('Text/number, with a fixed set of options (scroll list)'))
        field_type.append(gui.DropDownItem('Boolean (checkbox - yes/no)'))
        field_type.append(gui.DropDownItem('Date'))
        field_type.append(gui.DropDownItem('Free text/number'))
        self.new_field_widgets.append(field_type)
        field_type_box.append(gui.Label('Field type:',width=130))
        field_type_box.append(field_type)
        new_field_tab.append(field_type_box)

        add_field_button = gui.Button('Add field')
        add_field_button.style['margin-top'] = '20px'
        add_field_button.style['padding-right'] = '10px'
        add_field_button.style['padding-left'] = '10px'
        add_field_button.set_on_click_listener(self.add_field_listener)
        new_field_tab.append(add_field_button)
        return new_field_tab

    def add_field_listener(self,*args):
        """
        checks if an options set is needed (for dropdown fields).
        """
        if self.new_field_widgets[0].get_value() == '' or self.new_field_widgets[1].get_value() == None or self.new_field_widgets[2].get_value() == None:
            self.show_dialog('Please fill out all the details.')
        elif pd.Series(self.new_field_widgets[0].get_value()).str.lower().str.replace(' ','_').values[0] in tables.table_experiment.columns.values:
            self.show_dialog("A field with this name alreade exists. Consider using the existing field (preferable!), or change the new field's name.")
        else:
            if self.new_field_widgets[2].get_value() == 'Text/number, with a fixed set of options (scroll list)':
                self.dialog.empty()
                box = gui.VBox()
                box.style['padding'] = '15px'
                box.append(gui.Label('Please list all possible values, separated by a comma'))
                options_set = gui.TextInput(hint='option 1, option 2, option 3, ...')
                options_set.style['margin'] = '15px'
                self.new_field_widgets.append(options_set)
                box.append(options_set)
                buttons_box = gui.HBox()
                cancel_button = gui.Button('Cancel', width=60)
                cancel_button.style['margin-right'] = '20px'
                cancel_button.set_on_click_listener(self.ok_or_cancel_listener)
                buttons_box.append(cancel_button)
                ok_button = gui.Button('OK', width=60)
                ok_button.set_on_click_listener(self.add_field)
                buttons_box.append(ok_button)
                box.append(buttons_box)
                self.dialog.append(box)
                self.dialog.show(self)
            else:
                self.add_field()


    def add_field(self,*args):
        """
        adds the new field to added_fields.csv and calls add_new_field (from back_end) to add the field to the DB.
        """
        if self.new_field_widgets[2].get_value() == 'Text/number, with a fixed set of options (scroll list)' and self.new_field_widgets[3].get_value() == '':
            self.dialog.hide()
            self.show_dialog('No options list was provided. Please choose a different field type or provide an options list.')
        else:
            row = []
            for widget in self.new_field_widgets:
                row.append(widget.get_value())

            row[0] = pd.Series(row[0]).str.lower().str.replace(' ','_').values[0]

            if row[1] == 'a value in a specific experiment (e.g. experimental list)':
                row[1] = 'Experiment'
            else:
                row[1] = 'Subject'

            if row[2] == 'Numerical, with range filtering':
                row[2] = 'integer'
            elif row[2] == 'Boolean (checkbox - yes/no)':
                row[2] = 'boolean'
            elif row[2] == 'Date':
                row[2] = 'date'
            else:
                row[2] = 'text'

            add_new_field(table_name=row[1],field_name=row[0],field_type=row[2])

            with open('added_fields.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(row)

            self.new_fields_to_dicts()
            self.clear_filters()
            tables.table_subjects = get_table_subjects()
            tables.table_experiment = get_table_experiment()
            self.show_dialog('The new field was added to the DB.')

    """
    General functions
    """
    def show_dialog(self, message: str):
        self.dialog.empty()
        text = gui.Label(message)
        text.style['text-align'] = 'center'
        text.style['margin-top'] = '30px'
        text.style['margin-bottom'] = '30px'
        self.dialog.append(text)
        ok = gui.Button('OK', width= 70)
        ok.style['margin-left'] = '200px'
        ok.set_on_click_listener(self.ok_or_cancel_listener)
        self.dialog.append(ok)
        self.dialog.show(self)

    def ok_or_cancel_listener(self,*args):
        self.dialog.hide()
        if len(self.new_field_widgets) > 3:
            self.new_field_widgets = self.new_field_widgets[:3]

    def new_fields_to_dicts(self,*args):
        add_new_fields_to_tables()

        dict = {'Subject':{'integer':self.range_subject, 'boolean':self.checkbox_subject,
                           'date':self.date_subject,'text':[self.dropdown_subject, self.textinput_subject]},
                'Experiment':{'integer':self.range_experiment, 'boolean':self.checkbox_experiment,
                              'date':self.date_experiment,'text':[self.dropdown_experiment, self.textinput_experiment]}}
        df = pd.read_csv('added_fields.csv')
        for idx, row in df.iterrows():
            field_name = row['field_name']
            field_name_for_display = row.str.capitalize().str.replace('_',' ')['field_name']
            table_name = row['table_name']
            field_type = row['field_type']

            if field_type == 'text':
                if type(row['options_set']) == str:
                    options_set = row.str.replace(', ',',')['options_set']
                    options_set = options_set.split(',')
                    options_set = [field_name_for_display] + options_set
                    dict[table_name][field_type][0][field_name] = options_set
                    switch_dict[field_name] = 'other'
                else:
                    dict[table_name][field_type][1][field_name] = field_name_for_display
                    switch_dict[field_name] = 'textinput'
            else:
                dict[table_name][field_type][field_name] = field_name_for_display
                if field_type == 'integer':
                    switch_dict[field_name] = 'range'
                else:
                    switch_dict[field_name] = 'other'

            if not field_name in col_order_experiment:
                if table_name == 'Experiment':
                    self.order_experiment.append(field_name)
                    experiment_fields.append(field_name)
                    col_order_experiment.append(field_name)
                else:
                    self.order_filters.append(field_name)
                    self.order_subject.append(field_name)
                    subject_fields.append(field_name)
                    col_order_subjects.append(field_name)
                    col_order_experiment.append(field_name)


def start_gui():
    start(LabApp, address='0.0.0.0', port=8081,multiple_instance=True,start_browser=True)


def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(mail_reminders, 'cron', hour=reminder_time)
    scheduler.start()



start_gui()

"""
if __name__ == '__main__':
    p1 = multiprocessing.Process(name='p1', target=start_gui)
    p2 = multiprocessing.Process(name='p2', target=start_scheduler)
    p1.start()
    p2.start()
"""
