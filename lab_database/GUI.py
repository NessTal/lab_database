import remi.gui as gui
from remi import start, App
# from back_end import *
from main import *
from filt_switch import *
from apscheduler.schedulers.blocking import BlockingScheduler
import multiprocessing
import csv
import numpy as np


class LabApp(App):
    def __init__(self, *args):
        self.exp_names = unique_experiments()
        self.range_subject = {'hebrew_age': 'Hebrew exposure age', 'reading_span': 'Reading span'}
        self.dropdown_subject = {'gender': ['Gender', 'Male', 'Female'],
                                 'dominant_hand': ['Dominant hand', 'Right', 'Left']}
        self.checkbox_subject = {'send_mails': 'Agreed to receive emails'}
        self.date_subject = {'date_of_birth': 'Date of birth'}
        self.textinput_subject = {'other_languages': 'Other languages'}
        self.textinput_subject_no_filter = {'subject_ID': 'ID',
                                            'first_name': 'First name',
                                            'last_name': 'Last name',
                                            'mail': 'e-mail',
                                            'subject_notes': 'Comments'}
        self.range_session = {}
        self.dropdown_session = {'experiment_name': ['Experiments'] + self.exp_names}
        self.textinput_session = {'participant_number': 'Subject number',
                                  'exp_list': 'List', 'session_notes': 'Comments',
                                  'scheduled_time': 'Scheduled time'}
        self.checkbox_session = {'participated': 'Participated', 'credit': 'Credit'}
        self.date_session = {'date': 'Date'}
        self.range_experiment = {'duration': 'Duration'}
        self.dropdown_experiment = {'lab': ['Lab', 'SPL (Aya)', 'CaLL (Einat)'], 'location': ['Location', 'ווב חדר 202', 'קרטר']}
        self.textinput_experiment = {'experiment_name': 'Experiment name','experimenter_name': 'Experimenter',
                                     'experimenter_mail': 'E-mail address', 'description': 'Description'}
        self.checkbox_experiment = {}
        self.date_experiment = {}

        self.order_filters = ['hebrew_age', 'other_languages', 'date_of_birth','gender','dominant_hand', 'reading_span',
                              'send_mails']
        self.order_subject = ['subject_ID', 'first_name', 'last_name', 'mail', 'gender', 'date_of_birth',
                              'dominant_hand', 'hebrew_age', 'other_languages', 'reading_span', 'send_mails',
                              'subject_notes']
        self.order_session = ['experiment_name', 'participated', 'participant_number', 'date', 'exp_list', 'session_notes']
        self.order_experiment = ['experiment_name','experimenter_name','experimenter_mail','lab','duration','location','description']

        self.row_titles_search = {'first_name': 'First name', 'last_name': 'Last name', 'subject_ID': 'ID',
                                  'date_of_birth': 'Date of birth', 'dominant_hand': 'Dominant hand', 'mail': 'e-mail',
                                  'subject_notes': 'Comments', 'send_mails': 'Agreed to receive emails',
                                  'reading_span': 'Reading span', 'gender': 'Gender',
                                  'hebrew_age': 'Hebrew exposure age', 'other_languages': 'Other languages',
                                  'participant_number': 'Subject number', 'experiment_name': 'Experiment', 'date': 'Date',
                                  'participated': 'Participated', 'session_notes': 'Comments', 'exp_list': 'List',
                                  'credit': 'Credit', 'scheduled_time':'Scheduled time'}

        # lists containing the filter's widgets, for the function filter() to get their values:
        self.filter_sub_widgets = {}
        self.filter_exp_yes_widgets = []
        self.filter_exp_no_widgets = []
        self.filter_export_file_name = []
        self.bio_widgets_for_display = {}
        self.new_field_widgets = []
        self.filter_experiment_widgets = {}
        self.filter_experiment_widgets_for_display = {}

        self.edit_experiment_widgets = {}
        self.edit_experiment_boxes_for_display = {}
        self.optional_fields_widgets = {}
        self.key_words_widgets = {}
        self.filter_key_words_widgets = {}

        self.key_words_table = gui.ListView()
        self.filter_key_words_table = gui.ListView()

        self.dialog = gui.GenericDialog(width='470', height='150')
        self.filter_results = pd.DataFrame()
        self.filter_experiments_results = pd.DataFrame()

        # attributes for the Edit subject tab
        self.info_dict = dict()
        self.search_by = ['ID', 'e-mail', 'Full Name']
        self.exp_info_dict = dict()
        self.search_widgets = dict()

        super(LabApp, self).__init__(*args)

    def main(self):
        """
        calls for the four big containers and creates tabs
        """
        self.new_fields_to_dicts()
        container = gui.TabBox()
        container.add_tab(self.filters_tab(), 'Filters', 'Filters')
        container.add_tab(self.edit_subjects_tab(), 'Add or Edit Subjects', 'Add or Edit Subjects')
        container.add_tab(self.experiments_tab(), 'Experiments', 'Experiments')
        container.add_tab(self.edit_experiments_tab(), 'Add or Edit Experiments', 'Add or Edit Experiments')
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
        for filter, text in self.range_subject.items():
            self.create_range_filter(filter,text,self.filter_sub_widgets,self.bio_widgets_for_display)

        for filter, text in self.date_subject.items():
            self.create_date_filter(filter,text,self.filter_sub_widgets,self.bio_widgets_for_display)

        for filter, values in self.dropdown_subject.items():
            self.create_dropdown_filter(filter,values,self.filter_sub_widgets,self.bio_widgets_for_display)

        for filter, text in self.textinput_subject.items():
            self.create_textinput_filter(filter,text,self.filter_sub_widgets,self.bio_widgets_for_display)

        for filter, text in self.checkbox_subject.items():
            self.create_checkbox_filter(filter,text,self.filter_sub_widgets,self.bio_widgets_for_display)


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


    def create_range_filter(self,filter, text, widgets_dict, widgets_for_display_dict):
        box = gui.HBox(width = 350, height = 50)
        box.style['padding-left'] = '10px'
        box.style['padding-right'] = '10px'
        fil_label = gui.Label(text,width = 300)
        fil_from = gui.TextInput(hint='from',height=18)
        fil_to = gui.TextInput(hint='to',height=18)
        box.append(fil_label)
        box.append(fil_from)
        box.append(fil_to)
        widgets_dict[filter] = [fil_from, fil_to]
        widgets_for_display_dict[filter] = box

    def create_date_filter(self,filter,text,widgets_dict,widgets_for_display_dict):
        box = gui.HBox(width = 350, height = 50)
        box.style['padding-left'] = '10px'
        box.style['padding-right'] = '10px'
        fil_label = gui.Label(text,width = 300)

        fil_from = gui.HBox()
        from_dd = gui.TextInput(hint='dd')
        from_mm = gui.TextInput(hint='mm')
        from_yyyy = gui.TextInput(hint='yyyy')
        fil_from.append(from_dd)
        fil_from.append(from_mm)
        fil_from.append(from_yyyy)

        fil_lable_to = gui.Label('to')
        fil_lable_to.style['margin-right'] = '2px'
        fil_lable_to.style['margin-left'] = '2px'

        fil_to = gui.HBox()
        to_dd = gui.TextInput(hint='dd')
        to_mm = gui.TextInput(hint='mm')
        to_yyyy = gui.TextInput(hint='yyyy')
        fil_to.append(to_dd)
        fil_to.append(to_mm)
        fil_to.append(to_yyyy)

        box.append(fil_label)
        box.append(fil_from)
        box.append(fil_lable_to)
        box.append(fil_to)

        widgets_dict[filter] = [[from_dd,from_mm,from_yyyy],[to_dd,to_mm,to_yyyy]]
        widgets_for_display_dict[filter] = box

    def create_dropdown_filter(self,filter,values,widgets_dict,widgets_for_display_dict):
        fil = gui.DropDown(height=20)
        for idx, val in enumerate(values):
            fil.add_child(idx,gui.DropDownItem(val))
        box = gui.HBox(width = 350, height = 50)
        box.style['padding-left'] = '10px'
        box.style['padding-right'] = '10px'
        box.append(fil)
        widgets_dict[filter] = fil
        widgets_for_display_dict[filter] = box

    def create_textinput_filter(self,filter,text,widgets_dict,widgets_for_display_dict):
        fil = gui.TextInput(hint=text,height=18)
        box = gui.HBox(width = 350, height = 50)
        box.style['padding-left'] = '10px'
        box.style['padding-right'] = '10px'
        box.append(fil)
        widgets_dict[filter] = fil
        widgets_for_display_dict[filter] = box

    def create_checkbox_filter(self,filter,text,widgets_dict,widgets_for_display_dict):
        fil = gui.CheckBoxLabel(text,height=18)
        box = gui.HBox(width = 350, height = 50)
        box.style['padding-left'] = '10px'
        box.style['padding-right'] = '10px'
        box.append(fil)
        widgets_dict[filter] = fil
        widgets_for_display_dict[filter] = box


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
        export_file_name_input = gui.TextInput(hint='file name', width = 195)
        export_file_name_input.style['padding'] = '4px'
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
                from_val = self.filter_sub_widgets[filter][0].get_value()
                to_val = self.filter_sub_widgets[filter][1].get_value()
                if (from_val != '') or (to_val != ''):
                    if from_val == '':
                        selected_filters[filter] = ['None', int(to_val)]
                    elif to_val == '':
                        selected_filters[filter] = [int(from_val), 'None']
                    else:
                        selected_filters[filter] = [int(from_val), int(to_val)]

            # date filters:
            for filter in self.date_subject.keys():
                widgets_from = self.filter_sub_widgets[filter][0]
                widgets_to = self.filter_sub_widgets[filter][1]
                if (widgets_from[0].get_value() != '') and (widgets_from[1].get_value() != '') and (widgets_from[2].get_value() != ''):
                    from_val = widgets_from[0].get_value()+'-'+widgets_from[1].get_value()+'-'+widgets_from[2].get_value()
                else:
                    from_val = 'None'
                if (widgets_to[0].get_value() != '') and (widgets_to[1].get_value() != '') and (widgets_to[2].get_value() != ''):
                    to_val = widgets_to[0].get_value()+'-'+widgets_to[1].get_value()+'-'+widgets_to[2].get_value()
                else:
                    to_val = 'None'
                if (from_val != 'None') or (to_val != 'None'):
                    selected_filters[filter] = [from_val,to_val]




            # drop down filters:
            for filter, text in self.dropdown_subject.items():
                val = self.filter_sub_widgets[filter].get_value()
                if (val != None) and (val != text[0]):
                    selected_filters[filter] = val

            # text input filters:
            for filter in self.textinput_subject.keys():
                val = self.filter_sub_widgets[filter].get_value()
                if val != '':
                    selected_filters[filter] = val

            # checkbox filters:
            for filter in self.checkbox_subject.keys():
                val = self.filter_sub_widgets[filter].get_value()
                if val == True:
                    selected_filters[filter] = val

            # send selected filters (dict) to filt and receive a data frame with the filtered results:
            print(f'selected filters: {selected_filters}')
            self.filter_results = filt(filt_dict = selected_filters, exp_list = exp_list)
            results_list_of_tuples = []
            titles = list(self.filter_results.columns.str.capitalize().str.replace('_',' '))
            titles[titles.index('Subject id')] = 'Subject ID'
            results_list_of_tuples.append(tuple(titles))
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
        self.filter_sub_widgets = {}
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
        print(f'emails: {self.filter_results["mail"].tolist()}')
        print(self.mail_widgets[0].get_value())
        print(self.mail_widgets[1].get_value())

    """
    Edit subjects tab
    """

    def edit_subjects_tab(self):
        edit_subjects_tab = gui.VBox()
        # Append to container
        edit_subjects_tab.append(self.search_by_container())
        self.window3_for_clear = gui.VBox()
        self.experiment_for_clear = gui.VBox()
        self.experiment_for_clear.append(self.experiment_info())
        self.window3_for_clear.append(self.participant_info())
        self.window3_for_clear.append(self.experiment_for_clear)
        edit_subjects_tab.append(self.window3_for_clear)
        edit_subjects_tab.append(self.participant_info_buttons())
        edit_subjects_tab.append(self.import_from_excel())
        return edit_subjects_tab

    def search_by_container(self):
        """create search by drop down, input and button"""
        search_by_container = gui.HBox(width='60%', height='20%')
        search_field_container = gui.HBox(width='30%', height='20%')
        search_by_label = gui.Label('Search By:')
        self.search_by_dd = gui.DropDown(width='60%')
        for idx, item in enumerate(self.search_by):
            self.search_by_dd.add_child(idx, gui.DropDownItem(item))
        self.search_by_dd.set_value('ID')
        self.search_widgets['search by field'] = self.search_by_dd
        self.search_input = gui.Input()
        self.search_widgets['search by value'] = self.search_input
        self.search_button = gui.Button('Search')
        self.search_button.style['padding'] = '5px'

        # Append to container
        search_field_container.append(search_by_label)
        search_field_container.append(self.search_by_dd)
        search_by_container.append(search_field_container)
        search_by_container.append(self.search_input)
        search_by_container.append(self.search_button)

        self.search_button.set_on_click_listener(self.search_button_click)

        return search_by_container

    def participant_info(self):
        """Show or edit participants' info"""
        participant_container = gui.VBox()

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
            (self.textinput_subject, 'input'),
            (self.textinput_subject_no_filter, 'input'),
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

        # create labels:
        participant_label = gui.Label('Participant')
        participant_label.style['margin-top'] = '5px'
        # Add widgets to the container
        participant_container.append(participant_label)
        participant_container.append(participant_table)

        return participant_container

    def experiment_info(self):
        """show or edit an experiment's info"""
        experiment_container = gui.VBox()
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
            (self.textinput_session, 'input'),
            (self.dropdown_session, 'drop_down'),
            (self.range_session, 'spinbox'),
            (self.date_session, 'date'),
            (self.checkbox_session, 'checkbox')
        ]
        # create the widgets and add them to a dictionary
        for widget in exp_widgets_and_inputs:
            widget_dictionary = widget[0]
            widget_type = widget[1]
            for label in widget_dictionary:
                self.add_search_widget(label, widget_type, widget_dictionary, self.exp_info_dict)

        # add the experiments table rows
        for row_title in self.order_session:
            row = self.add_row(row_title, self.exp_info_dict)
            experiment_table.add_child(str(id(row)), row)

        # Create labels
        experiment_label = gui.Label('Experiment')
        experiment_label.style['margin-top'] = '5px'

        self.optional_fields_session_table = gui.Table()
        # Add widgets to the container:
        experiment_container.append(experiment_label)
        experiment_container.append(experiment_table)
        experiment_container.append(self.optional_fields_session_table)

        self.exp_info_dict['experiment_name'].set_on_change_listener(self.exp_dropdown_change)
        return experiment_container

    def participant_info_buttons(self):
        """contains participant info, experiment info and the relevant buttons"""
        info_container = gui.VBox()
        # Create update and clear buttons
        self.update_info = gui.Button('Update Info')
        self.update_info.style['padding'] = '5px'
        clear_info = gui.Button('Clear')
        clear_info.style['padding'] = '5px'
        clear_info.style['margin-right'] = '5px'
        clear_info.set_on_click_listener(self.clear_window3)
        buttons_box = gui.HBox()
        buttons_box.style['margin-top'] = '5px'
        buttons_box.append(clear_info)
        buttons_box.append(self.update_info)

        # Add widgets to the container
        info_container.append(buttons_box)

        self.update_info.set_on_click_listener(self.update_subject_click)
        return info_container

    def add_search_widget(self, label, box_type, widget_dictionary, output_dictionary):
        """create a widget for the participants table"""
        types_dict = {'input': gui.TextInput,
                      'date': self.date_field,
                      'spinbox': gui.SpinBox,
                      'drop_down': gui.DropDown,
                      'checkbox': gui.CheckBox}
        if self.row_titles_search[label] == 'Comments':
            box = gui.TextInput(single_line=False)
        else:
            box = types_dict[box_type]()  # create a widget
        if box_type == 'spinbox':
            box.set_value('')
        elif box_type == 'drop_down':
            for idx, item in enumerate(widget_dictionary[label]):
                box.add_child(idx + 1, gui.DropDownItem(item))
        output_dictionary[label] = box  # Store the widget in a dictionary

    def date_field(self):
        date_box = gui.HBox(width=150)
        day = gui.TextInput(hint='dd', width='30%')
        month = gui.TextInput(hint='mm', width='30%')
        year = gui.TextInput(hint='yyyy', width='40%')
        date_box.append(day, key='day')
        date_box.append(month, key='month')
        date_box.append(year, key='year')
        return date_box

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
        search_field_to_label = {'ID': 'subject_ID', 'e-mail': 'mail'}
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
            print(f'get_if_exists result: {subj_data}')
            # if the user does not exist, add the field we searched to the table so a new user could be created
            if type(subj_data) != pd.DataFrame:
                if subj_data == 'Too many!':
                    self.show_dialog('More than one participant was found. Please search by ID.')
                else:
                    self.show_dialog('No subject found, you can add a new subject below')
                    self.clear_window3()
                    try:
                        label = search_field_to_label[field]
                        self.info_dict[label].set_value(str(search_value))
                    except KeyError:
                        if ' ' in search_value:
                            first_name, last_name = search_value.split(' ', 1)
                            self.info_dict['first_name'].set_value(first_name)
                            self.info_dict['last_name'].set_value(last_name)
                        else:
                            self.info_dict['first_name'].set_value(search_value)
            # else, add the subject's fields to the table
            else:
                self.clear_window3()
                self.add_subject_data(subj_data, self.info_dict)

    def add_subject_data(self, subj_data: pd.DataFrame, widget_dict: dict):
        """add a subject's details"""
        # access the relevant widgets and set the values in the DataFrame
        for label in widget_dict:
            widget = widget_dict[label]
            value = subj_data[label].values[0]
            # if the widget contains a date, split and set each value in its field
            if type(widget) is gui.HBox:
                day, month, year = value.split('-')
                widget.children['day'].set_value(day)
                widget.children['month'].set_value(month)
                widget.children['year'].set_value(year)
            else:
                if type(widget) in [gui.TextInput, gui.DropDown]:
                    if value is None:
                        value = ''
                    value = str(value)
                widget.set_value(value)

    def update_subject_click(self, widget):
        """updates a subject's info when the Update Info button is clicked"""
        subject_info = dict()  # output dict
        experiment_name = self.exp_info_dict['experiment_name'].get_value()
        # validate that there is an ID, and that it only contains numbers
        if self.info_dict['subject_ID'].get_value() == '':
            self.show_dialog('Please enter the ID')
        elif self.validate_int(self.info_dict['subject_ID'].get_value(), 'ID'):
            # enter the participant's values to the output dictionary
            subject_info = self.update_info_dictionary(subject_info, self.info_dict)
            # if an experiment was chosen, update the experiment fields as well
            if experiment_name is not None and experiment_name not in ['Experiments', 'Add New']:
                # todo: handle KeyError ('participant_number'), reset experiments only
                subject_info = self.update_info_dictionary(subject_info, self.exp_info_dict)

            if self.validate_range_fields(self.range_subject, subject_info):
                print(f'to add_or_update: {subject_info}')
                add_or_update(subject_info)
                self.refresh_exp_lists()
                self.show_dialog('The participant was updated')

    def update_info_dictionary(self, info_dictionary, widget_dictionary: dict)->dict:
        """
        receives a widget dictionary and participant's info dict
        returns a dictionary with non-empty values
        """
        for label in widget_dictionary:
            widget = widget_dictionary[label]
            if type(widget) is gui.HBox:
                value = ''
                date = [widget.children['day'].get_value(),
                        widget.children['month'].get_value(),
                        widget.children['year'].get_value()]
                if value not in date:
                    value = '-'.join(date)
            else:
                value = widget_dictionary[label].get_value()
            # if the field's value exists and isn't empty, add it to the dictionary
            if value not in [None, '', 'None', 'nan']:
                info_dictionary[label] = value
        return info_dictionary

    def validate_range_fields(self, range_dict: dict, participant_info: dict)->bool:
        for label in range_dict:
            if label in participant_info:
                row_title = self.row_titles_search[label]
                if not self.validate_int(participant_info[label], row_title):
                    return False
        return True

    def exp_dropdown_change(self, *args):
        exp_name = self.exp_info_dict['experiment_name'].get_value()
        self.clear_experiment()
        self.optional_fields_session_table.empty()
        if exp_name not in [None, 'Experiments']:
            optional_fields = filt_experiments({'experiment_name': exp_name})['fields'].values[0].split(', ')
            if len(optional_fields) > 0:
                for field in optional_fields:
                    row = self.add_row(field, self.exp_info_dict)
                    self.optional_fields_session_table.add_child(str(id(row)), row)

            subj_id = self.info_dict['subject_ID'].get_value()
            if subj_id == '':
                self.show_dialog("Please search for a participant first.")
            # elif self.validate_int(subj_id, 'ID'):
            #    try:
            else:
                print(f'to get_if_exist: {subj_id}, {exp_name}')
                subj_data = get_if_exists(int(subj_id), exp_name)
                print(f'from get_if_exists: {subj_data}')
                self.add_subject_data(subj_data, self.exp_info_dict)
            #    except KeyError:
            #        self.clear_experiment()
            #        self.exp_info_dict['experiment_name'].set_value(exp_name)
                # todo: check if there is data for this experiment+user and clear exp fields if not

    def validate_int(self, num, field: str, debug=False)->bool:
        """validates that the input can be modified to int"""
        try:
            x = float(num)
            return True
        except ValueError:
            if not debug:
                self.show_dialog(f'The field "{field}" can only contain numbers')
                return False
            else:
                raise ValueError  # for testing

    def import_from_excel(self):
        import_box = gui.HBox(width=300, height=80)
        import_file = gui.TextInput(hint='File name', width=140)
        import_file.style['padding'] = '4px'
        import_button = gui.Button('Import from excel', width=140)
        import_button.set_on_click_listener(self.import_from_excel_listener)
        import_box.append(import_button)
        import_box.append(import_file)
        self.import_file_name = import_file
        return import_box

    def clear_window3(self, *args):
        self.window3_for_clear.empty()
        self.window3_for_clear.append(self.participant_info())
        self.clear_experiment()
        self.window3_for_clear.append(self.experiment_for_clear)

    def clear_experiment(self):
        """clears all experiment fields"""
        self.experiment_for_clear.empty()
        self.experiment_for_clear.append(self.experiment_info())

    def import_from_excel_listener(self, *args):
        file_name = self.import_file_name.get_value()
        file = import_path+file_name+'.csv'
        date_fields = list(self.date_subject.keys()) + list(self.date_session.keys())
        import_from_excel(file, date_fields)
        self.refresh_exp_lists()
        self.clear_window3()
        self.show_dialog(f'Imported from: {file}')

    def refresh_exp_lists(self, *args):
        self.exp_names = unique_experiments()
        self.filter_exp_yes_widgets = []
        self.filter_exp_no_widgets = []
        self.clear_filters()

    """
    Experiments tab
    """
    def experiments_tab(self):
        experiments_tab = gui.VBox()

        experiment_filters = gui.HBox()
        self.experiment_filters_left = gui.Table()
        self.experiment_filters_left.style['margin'] = '60px'
        experiment_filters.append(self.experiment_filters_left)
        self.build_experiment_filters_left()
        experiment_filters.append(self.key_words('filter'))
        experiments_tab.append(experiment_filters)

        self.filtered_experiments_table = gui.TableWidget(0,0)
        self.filtered_experiments_table.style['margin-bottom'] = '50px'
        experiments_tab.append(self.filtered_experiments_table)
        return experiments_tab


    def build_experiment_filters_left(self):
        for filter, text in self.range_experiment.items():
            self.create_range_filter(filter,text,self.filter_experiment_widgets, self.filter_experiment_widgets_for_display)

        for filter, text in self.date_experiment.items():
            self.create_date_filter(filter,text,self.filter_experiment_widgets, self.filter_experiment_widgets_for_display)

        for filter, values in self.dropdown_experiment.items():
            self.create_dropdown_filter(filter,values,self.filter_experiment_widgets, self.filter_experiment_widgets_for_display)

        for filter, text in self.textinput_experiment.items():
            if filter != 'description':
                self.create_textinput_filter(filter,text,self.filter_experiment_widgets, self.filter_experiment_widgets_for_display)

        for filter, text in self.checkbox_experiment.items():
            self.create_checkbox_filter(filter,text,self.filter_experiment_widgets, self.filter_experiment_widgets_for_display)


        # position filters:
        for idx, filter in enumerate(self.order_experiment[:-1]):
            row = gui.TableRow()
            item = gui.TableItem()
            item.add_child(0,self.filter_experiment_widgets_for_display[filter])
            row.add_child(0,item)
            self.experiment_filters_left.add_child(idx,row)

        # add buttons:
        clear_filters_experiment = gui.Button('Clear')
        clear_filters_experiment.set_on_click_listener(self.clear_experiments_filters)
        clear_filters_experiment.style['padding-left'] = '10px'
        clear_filters_experiment.style['padding-right'] = '10px'

        filter_experiment = gui.Button('Filter')
        filter_experiment.set_on_click_listener(self.filter_experiments)
        filter_experiment.style['padding-left'] = '10px'
        filter_experiment.style['padding-right'] = '10px'

        buttons_box = gui.HBox(height=50)
        buttons_box.style['padding-bottom'] = '10px'
        buttons_box.append(clear_filters_experiment)
        buttons_box.append(filter_experiment)

        row = gui.TableRow()
        item = gui.TableItem()
        item.add_child(0,buttons_box)
        row.add_child(0,item)
        self.experiment_filters_left.add_child(len(self.order_experiment),row)


    def filter_experiments(self,*args):
        selected_filters = {}
        key_words = []
        for key_word, widget in self.filter_key_words_widgets.items():
            if widget.get_value() == True:
                key_words.append(key_word)
        if len(key_words) > 0:
            selected_filters['key_words'] = key_words

        # range filters:
        for filter in self.range_experiment.keys():
            from_val = self.filter_experiment_widgets[filter][0].get_value()
            to_val = self.filter_experiment_widgets[filter][1].get_value()
            if (from_val != '') or (to_val != ''):
                if from_val == '':
                    selected_filters[filter] = ['None', int(to_val)]
                elif to_val == '':
                    selected_filters[filter] = [int(from_val), 'None']
                else:
                    selected_filters[filter] = [int(from_val), int(to_val)]

        # date filters:
        for filter in self.date_experiment.keys():
            widgets_from = self.filter_sub_widgets[filter][0]
            widgets_to = self.filter_sub_widgets[filter][1]
            from_val = widgets_from[0].get_value()+'-'+widgets_from[1].get_value()+'-'+widgets_from[2].get_value()
            to_val = widgets_to[0].get_value()+'-'+widgets_to[1].get_value()+'-'+widgets_to[2].get_value()
            if (from_val != 'None') or (to_val != 'None'):
                selected_filters[filter] = [from_val,to_val]

        # drop down filters:
        for filter, text in self.dropdown_experiment.items():
            val = self.filter_experiment_widgets[filter].get_value()
            if (val != None) and (val != text[0]):
                selected_filters[filter] = val

        # text input filters:
        for filter in self.textinput_experiment.keys():
            if filter != 'description':
                val = self.filter_experiment_widgets[filter].get_value()
                if val != '':
                    selected_filters[filter] = val

        # checkbox filters:
        for filter in self.checkbox_experiment.keys():
            val = self.filter_experiment_widgets[filter].get_value()
            if val == True:
                selected_filters[filter] = val

        # send selected filters (dict) to filt and receive a data frame with the filtered results:
        print(f'selected experiment filters: {selected_filters}')
        self.filter_experiments_results = filt_experiments(selected_filters)
        results_list_of_tuples = []
        titles = list(self.filter_experiments_results.columns.str.capitalize().str.replace('_',' '))
        results_list_of_tuples.append(tuple(titles))
        self.filtered_experiments_table.style['margin-top'] = '30px'
        for idx, row in self.filter_experiments_results.iterrows():
            results_list_of_tuples.append(tuple(row))
        self.filtered_experiments_table.empty()
        self.filtered_experiments_table.append_from_list(results_list_of_tuples,fill_title=True)
        for key,item in self.filtered_experiments_table.get_child('0').children.items():
            self.filtered_experiments_table.get_child('0').get_child(key).style['padding-left'] = '5px'
            self.filtered_experiments_table.get_child('0').get_child(key).style['padding-right'] = '5px'
            self.filtered_experiments_table.get_child('0').get_child(key).style['padding-top'] = '3px'
            self.filtered_experiments_table.get_child('0').get_child(key).style['padding-bottom'] = '3px'


    def clear_experiments_filters(self,*args):
        self.experiment_filters_left.empty()
        self.build_experiment_filters_left()
        self.filter_key_words_table.empty()
        self.build_key_words_table('filter')



    """
    Edit experiments tab
    """
    def edit_experiments_tab(self):
        """
        creates the Add New fields tab.
        """
        edit_experiments_tab = gui.HBox()
        edit_experiments_tab.append(self.edit_experiments_left())
        edit_experiments_tab.append(self.optional_fields())
        edit_experiments_tab.append(self.key_words('edit'))
        return edit_experiments_tab


    def edit_experiments_left(self):
        edit_experiments_left = gui.VBox()
        edit_experiments_left.style['margin-bottom'] = '50px'
        edit_experiments_left.style['margin-left'] = '220px'

        search_experiment_box = gui.HBox(width=450, height=40)
        search_experiment_box.style['margin-top'] = '20px'
        search_experiment_label = gui.Label('Experiment name',width=200)
        search_experiment_label.style['text-align'] = 'left'
        search_experiment_input = gui.TextInput(height=18)
        self.edit_experiment_widgets['search'] = search_experiment_input
        search_experiment_button = gui.Button('Search',width=100)
        search_experiment_button.style['margin-left'] = '10px'
        search_experiment_button.set_on_click_listener(self.search_experiment)
        search_experiment_box.append(search_experiment_label)
        search_experiment_box.append(search_experiment_input)
        search_experiment_box.append(search_experiment_button)
        edit_experiments_left.append(search_experiment_box)

        self.edit_experiment_table = gui.Table()
        self.edit_experiment_table.style['margin'] = '20px'
        self.build_edit_experiment_table()
        edit_experiments_left.append(self.edit_experiment_table)

        buttons_box = gui.HBox()
        update_experiment_button = gui.Button('Update experiment')
        update_experiment_button.style['padding-right'] = '10px'
        update_experiment_button.style['padding-left'] = '10px'
        update_experiment_button.style['margin-left'] = '20px'
        update_experiment_button.set_on_click_listener(self.update_experiment)
        clear_button = gui.Button('Clear')
        clear_button.style['padding-right'] = '10px'
        clear_button.style['padding-left'] = '10px'
        clear_button.set_on_click_listener(self.clear_edit_experiment)
        buttons_box.append(clear_button)
        buttons_box.append(update_experiment_button)
        edit_experiments_left.append(buttons_box)
        return edit_experiments_left


    def search_experiment(self, *args):
        exp = get_experiment(self.edit_experiment_widgets['search'].get_value())
        if len(exp) == 0:
            self.show_dialog('No experiment found, you can add a new experiment below')
            self.clear_edit_experiment()
            self.edit_experiment_widgets['experiment_name'].set_text(self.edit_experiment_widgets['search'].get_value())
        else:
            exp_dict = exp.to_dict(orient='list')
            self.edit_experiment_widgets['experiment_name'].set_text(exp_dict.pop('experiment_name')[0])
            for key, val in exp_dict.items():
                val = val[0]
                if (key == 'fields') or (key == 'key_words'):
                    self.set_checkboxes_values(key, val)
                else:
                    if val != None:
                        if key in ['duration','reading_span']:
                            self.edit_experiment_widgets[key].set_value(int(val))
                        else:
                            self.edit_experiment_widgets[key].set_value(val)


    def set_checkboxes_values(self,key, selected):
        keys_dict = {'fields':[self.optional_fields_table, self.build_optional_fields_table,self.optional_fields_widgets],
                     'key_words': [self.key_words_table, self.build_key_words_table, self.key_words_widgets]}
        keys_dict[key][0].empty()
        if key == 'key_words':
            keys_dict[key][1]('edit')
        else:
            keys_dict[key][1]()
        if selected != None:
            selected = selected.split(', ')
            for item in selected:
                keys_dict[key][2][item].set_value(True)


    def build_edit_experiment_table(self):
        # create text input fields:
        for filter, text in self.textinput_experiment.items():
            box = gui.HBox(width = 350, height = 40)
            box.style['padding-left'] = '10px'
            box.style['padding-right'] = '10px'
            fil_label = gui.Label(text, width= 170)
            fil_label.style['text-align'] = 'left'
            box.append(fil_label)
            if filter == 'experiment_name':
                fil_input = gui.Label('')
                fil_input_box = gui.HBox(width=338, height=22)
                fil_input_box.style['background-color'] = 'rgb(217,236,253)'
                fil_input_box.style['padding'] = '2px'
                fil_input_box.append(fil_input)
                box.append(fil_input_box)
            else:
                fil_input = gui.TextInput(height=18)
                box.append(fil_input)
            self.edit_experiment_widgets[filter] = fil_input
            self.edit_experiment_boxes_for_display[filter] = box

        # create range fields:
        for filter, text in self.range_experiment.items():
            box = gui.HBox(width = 350, height = 40)
            box.style['padding-left'] = '10px'
            box.style['padding-right'] = '10px'
            fil_label = gui.Label(text, width= 170)
            fil_label.style['text-align'] = 'left'
            fil_input = gui.SpinBox(height=18)
            fil_input.set_value('')
            box.append(fil_label)
            box.append(fil_input)
            self.edit_experiment_widgets[filter] = fil_input
            self.edit_experiment_boxes_for_display[filter] = box

        # create date fields:
        for filter, text in self.date_experiment.items():
            box = gui.HBox(width = 350, height = 40)
            box.style['padding-left'] = '10px'
            box.style['padding-right'] = '10px'
            fil_label = gui.Label(text, width= 170)
            fil_label.style['text-align'] = 'left'
            fil_input = gui.Date()
            fil_input.set_value(None)
            box.append(fil_label)
            box.append(fil_input)
            self.edit_experiment_widgets[filter] = fil_input
            self.edit_experiment_boxes_for_display[filter] = box

        # create dropdown list fields:
        for filter, values in self.dropdown_experiment.items():
            box = gui.HBox(width = 350, height = 40)
            box.style['padding-left'] = '10px'
            box.style['padding-right'] = '10px'
            fil_label = gui.Label(values[0], width= 170)
            fil_label.style['text-align'] = 'left'
            fil_input = gui.DropDown(height=20)
            fil_input.add_child(0,gui.DropDownItem(''))
            for idx, val in enumerate(values[1:]):
                fil_input.add_child(idx+1,gui.DropDownItem(val))
            box.append(fil_label)
            box.append(fil_input)
            self.edit_experiment_widgets[filter] = fil_input
            self.edit_experiment_boxes_for_display[filter] = box

        # create checkbox fields:
        for filter, text in self.checkbox_experiment.items():
            box = gui.HBox(width = 350, height = 40)
            fil = gui.CheckBoxLabel(text,height=18)
            box.style['padding-left'] = '10px'
            box.style['padding-right'] = '10px'
            box.append(fil)
            self.edit_experiment_widgets[filter] = fil
            self.edit_experiment_boxes_for_display[filter] = box

        # position fields:
        for idx, field in enumerate(self.order_experiment):
            row = gui.TableRow()
            item = gui.TableItem()
            item.add_child(0,self.edit_experiment_boxes_for_display[field])
            row.add_child(0,item)
            self.edit_experiment_table.add_child(idx,row)


    def clear_edit_experiment(self, *args):
        self.edit_experiment_table.empty()
        self.build_edit_experiment_table()
        self.key_words_table.empty()
        self.build_key_words_table('edit')
        self.optional_fields_table.empty()
        self.build_optional_fields_table()


    def update_experiment(self, *args):
        dict = {}
        dict['experiment_name'] = self.edit_experiment_widgets['experiment_name'].get_text()
        for key,val in self.edit_experiment_widgets.items():
            if (key != 'search') and (key != 'experiment_name'):
                dict[key] = val.get_value()
        dict['fields'] = self.checkboxes_values_to_string('fields')
        dict['key_words'] = self.checkboxes_values_to_string('key_words')
        add_or_update_experiment(dict)
        if dict['experiment_name'] not in self.exp_names:
            self.exp_info_dict['experiment_name'].add_child(-1, gui.DropDownItem(dict['experiment_name']))
            self.refresh_exp_lists()
        self.show_dialog('The experiment was updated')


    def checkboxes_values_to_string(self,key1):
        keys_dict = {'fields':self.optional_fields_widgets,
                     'key_words': self.key_words_widgets}
        selected = []
        for key, val in keys_dict[key1].items():
            if val.get_value() == True:
                selected.append(key)
        selected = ', '.join(selected)
        return selected


    def optional_fields(self):
        optional_fields = gui.VBox(height=500)
        lable = gui.Label('Select optional fields:')
        lable.style['margin-top'] = '25px'
        lable.style['margin-bottom'] = '15px'
        optional_fields.append(lable)
        self.optional_fields_table = gui.ListView()
        optional_fields.append(self.optional_fields_table)
        self.build_optional_fields_table()
        add_field_button = gui.Button('Add new field')
        add_field_button.style['margin-top'] = '20px'
        add_field_button.style['margin-bottom'] = '20px'
        add_field_button.style['padding-right'] = '10px'
        add_field_button.style['padding-left'] = '10px'
        add_field_button.set_on_click_listener(self.show_new_field_dialog)
        optional_fields.append(add_field_button)
        return optional_fields


    def build_optional_fields_table(self, *args):
        for opt_field in session_optional_fields:
            box = gui.HBox()
            label = gui.Label(opt_field.capitalize().replace('_',' '),width=150)
            label.style['text-align'] = 'left'
            label.style['margin'] = '3px'
            checkbox = gui.CheckBox()
            checkbox.style['margin'] = '3px'
            box.append(checkbox)
            box.append(label)
            self.optional_fields_widgets[opt_field] = checkbox
            item = gui.TableItem()
            item.append(box)
            row = gui.TableRow()
            row.append(item)
            self.optional_fields_table.append(row)


    def key_words(self,tab):
        table_widget_dict = {'edit': self.key_words_table, 'filter': self.filter_key_words_table}
        if tab == 'edit':
            key_words = gui.VBox(height=500)
        else:
            key_words = gui.VBox(height=400)
        key_words.style['margin-bottom'] = '40px'
        key_words.style['margin-right'] = '220px'
        lable = gui.Label('Select key words:')
        lable.style['margin-top'] = '25px'
        lable.style['margin-bottom'] = '15px'
        key_words.append(lable)
        key_words.append(table_widget_dict[tab])
        self.build_key_words_table(tab)
        if tab == 'edit':
            add_key_word_button = gui.Button('Add new key word')
            add_key_word_button.style['margin-top'] = '20px'
            add_key_word_button.style['margin-bottom'] = '20px'
            add_key_word_button.style['padding-right'] = '10px'
            add_key_word_button.style['padding-left'] = '10px'
            add_key_word_button.set_on_click_listener(self.show_new_key_word_dialog)
            key_words.append(add_key_word_button)
        return key_words


    def build_key_words_table(self,tab):
        widgets_holder_dict = {'edit': [self.key_words_widgets, self.key_words_table],
                               'filter': [self.filter_key_words_widgets, self.filter_key_words_table]}
        df = pd.read_csv('key_words.csv',header=None)
        for idx, key_word in df.iterrows():
            key_word = key_word.values[0]
            box = gui.HBox()
            label = gui.Label(key_word, width= 150)
            label.style['text-align'] = 'left'
            label.style['margin'] = '3px'
            checkbox = gui.CheckBox()
            checkbox.style['margin'] = '3px'
            box.append(checkbox)
            box.append(label)
            widgets_holder_dict[tab][0][key_word] = checkbox
            item = gui.TableItem()
            item.append(box)
            row = gui.TableRow()
            row.append(item)
            widgets_holder_dict[tab][1].append(row)


    def show_new_key_word_dialog(self, *args):
        self.dialog =gui.GenericDialog(width='470', height='150')
        self.dialog.empty()
        box = gui.VBox()
        box.style['padding'] = '15px'
        box.append(gui.Label('Please enter the new key word'))
        self.new_key_word_widget = gui.TextInput(hint='Key word')
        self.new_key_word_widget.style['margin'] = '15px'
        self.new_key_word_widget.style['padding-top'] = '3px'
        self.new_key_word_widget.style['padding-bottom'] = '3px'
        self.new_key_word_widget.style['padding-right'] = '7px'
        self.new_key_word_widget.style['padding-left'] = '7px'
        box.append(self.new_key_word_widget)
        buttons_box = gui.HBox()
        cancel_button = gui.Button('Cancel', width=60)
        cancel_button.style['margin-right'] = '20px'
        cancel_button.set_on_click_listener(self.ok_or_cancel_listener)
        buttons_box.append(cancel_button)
        ok_button = gui.Button('OK', width=60)
        ok_button.set_on_click_listener(self.add_key_word)
        buttons_box.append(ok_button)
        box.append(buttons_box)
        self.dialog.append(box)
        self.dialog.show(self)


    def add_key_word(self, *args):
        with open('key_words.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([self.new_key_word_widget.get_value()])
        self.key_words_table.empty()
        self.build_key_words_table('edit')
        self.filter_key_words_table.empty()
        self.build_key_words_table('filter')
        self.dialog.hide()


    def show_new_field_dialog(self, *args):
        self.new_field_widgets = []
        self.dialog = gui.GenericDialog()
        self.dialog.empty()
        new_field_tab = gui.VBox()
        new_field_tab.style['padding-top'] = '20px'
        new_field_tab.style['padding-bottom'] = '40px'
        field_name_box = gui.HBox()
        field_name_box.style['margin'] = '10px'
        field_name = gui.TextInput(width=366)
        field_name.style['padding'] = '2px'
        self.new_field_widgets.append(field_name)
        field_name_box.append(gui.Label('Field name:', width=130))
        field_name_box.append(field_name)
        new_field_tab.append(field_name_box)

        to_which_table_box = gui.HBox()
        to_which_table_box.style['margin'] = '10px'
        to_which_table = gui.DropDown(width=370)
        to_which_table.style['padding'] = '2px'
        to_which_table.append(gui.DropDownItem('Select'))
        to_which_table.append(gui.DropDownItem('a general "property" of a subject (e.g. dominant hand)'))
        to_which_table.append(gui.DropDownItem('a general "property" of an experiment (e.g. duration)'))
        to_which_table.append(gui.DropDownItem('a value for the participant in the specific experiment (e.g. experimental list)'))
        self.new_field_widgets.append(to_which_table)
        to_which_table_box.append(gui.Label('A value would be:',width=130))
        to_which_table_box.append(to_which_table)
        new_field_tab.append(to_which_table_box)

        field_type_box = gui.HBox()
        field_type_box.style['margin'] = '10px'
        field_type = gui.DropDown(width=370)
        field_type.style['padding'] = '2px'
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

        buttons_box = gui.HBox()
        buttons_box.style['margin-top'] = '5px'
        add_field_button = gui.Button('Add field')
        add_field_button.style['margin-left'] = '20px'
        add_field_button.style['padding-right'] = '10px'
        add_field_button.style['padding-left'] = '10px'
        add_field_button.set_on_click_listener(self.show_options_set_dialog)
        cancel_button = gui.Button('Cancel')
        cancel_button.style['padding-right'] = '10px'
        cancel_button.style['padding-left'] = '10px'
        cancel_button.set_on_click_listener(self.ok_or_cancel_listener)
        buttons_box.append(cancel_button)
        buttons_box.append(add_field_button)
        new_field_tab.append(buttons_box)
        self.dialog.append(new_field_tab)
        self.dialog.show(self)

    def show_options_set_dialog(self,*args):
        """
        checks if an options set is needed (for dropdown fields).
        """
        self.dialog.hide()
        if self.new_field_widgets[0].get_value() == '' or self.new_field_widgets[1].get_value() == None or self.new_field_widgets[2].get_value() == None:
            self.show_dialog('Please fill out all the details.')
        elif pd.Series(self.new_field_widgets[0].get_value()).str.lower().str.replace(' ','_').values[0] in tables.table_sessions.columns.values:
            self.show_dialog("A field with this name already exists. Consider using the existing field (preferable!), or change the new field's name.")
        elif pd.Series(self.new_field_widgets[0].get_value()).str.lower().str.replace(' ','_').values[0] in tables.table_experiments.columns.values:
            self.show_dialog("A field with this name already exists. Consider using the existing field (preferable!), or change the new field's name.")
        else:
            if self.new_field_widgets[2].get_value() == 'Text/number, with a fixed set of options (scroll list)':
                self.dialog = gui.GenericDialog(width='470', height='150')
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
        if self.new_field_widgets[2].get_value() == 'Text/number, with a fixed set of options (scroll list)':
            self.dialog.hide()
        if self.new_field_widgets[2].get_value() == 'Text/number, with a fixed set of options (scroll list)' and self.new_field_widgets[3].get_value() == '':
            self.show_dialog('No options list was provided. Please choose a different field type or provide an options list.')
        else:
            row = []
            for widget in self.new_field_widgets:
                row.append(widget.get_value())

            row[0] = pd.Series(row[0]).str.lower().str.replace(' ','_').values[0]

            if row[1] == 'a general "property" of a subject (e.g. dominant hand)':
                row[1] = 'Subject'
            elif row[1] == 'a general "property" of an experiment (e.g. duration)':
                row[1] = 'Experiment'
            else:
                row[1] = 'Session'

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
            self.clear_window3()
            self.clear_experiments_filters()
            self.clear_edit_experiment()
            self.show_dialog('The new field was added to the DB.')

    """
    General functions
    """
    def show_dialog(self, message: str):
        self.dialog = gui.GenericDialog(width='470', height='150')
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
        dict_to_dicts = {'Subject':{'integer':self.range_subject, 'boolean':self.checkbox_subject,
                           'date':self.date_subject,'text':[self.dropdown_subject, self.textinput_subject]},
                         'Experiment':{'integer':self.range_experiment, 'boolean':self.checkbox_experiment,
                                       'date':self.date_experiment,'text':[self.dropdown_experiment, self.textinput_experiment]},
                         'Session':{'integer':self.range_session, 'boolean':self.checkbox_session,
                              'date':self.date_session,'text':[self.dropdown_session, self.textinput_session]}}
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
                    dict_to_dicts[table_name][field_type][0][field_name] = options_set
                    if table_name != 'Session':
                        switch_dict[field_name] = 'other'
                else:
                    dict_to_dicts[table_name][field_type][1][field_name] = field_name_for_display
                    if table_name != 'Session':
                        switch_dict[field_name] = 'textinput'
            else:
                dict_to_dicts[table_name][field_type][field_name] = field_name_for_display
                if table_name != 'Session':
                    if field_type == 'integer':
                        switch_dict[field_name] = 'range'
                    elif field_type == 'date':
                        switch_dict[field_name] = 'date'
                    else:
                        switch_dict[field_name] = 'other'

            if table_name == 'Session':
                if field_name not in self.order_session:
                    self.order_session.insert(-1, field_name)
            elif table_name == 'Experiment':
                if field_name not in self.order_experiment:
                    self.order_experiment.insert(-1, field_name)
            else:
                if field_name not in self.order_subject:
                    self.order_filters.insert(-1, field_name)
                    self.order_subject.insert(-1, field_name)
            self.row_titles_search[field_name] = field_name_for_display


def start_gui():
    start(LabApp, address='0.0.0.0', port=8081,multiple_instance=True,start_browser=True)


def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(mail_reminders, 'cron', hour=reminder_time)
    scheduler.start()


# start_gui()

if __name__ == '__main__':
    p1 = multiprocessing.Process(name='p1', target=start_gui)
    p2 = multiprocessing.Process(name='p2', target=start_scheduler)
    p1.start()
    p2.start()
