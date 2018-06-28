import remi.gui as gui
from remi import start, App
from back_end import *

class LabApp(App):
    def __init__(self, *args):
        self.exp_names = ['A','B','C','A','B','C','A','B','C','A','B','C','A','B','C','A','B','C','A','B','C','A','B','C','A','B','C','A','B','C'] ######### to be somehow received from the database
        # lists containing the filter's widgets, for the function filter() to get their values:
        self.filter_bio_widgets = []
        self.filter_exp_yes_widgets = []
        self.filter_exp_no_widgets = []
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

    def filters_widget(self):
        """
        creates the filters container by calling for its three parts (two that create filters and one that creates the table).
        """
        filters_widget = gui.VBox(width = '100%', height = 1000) # the entire tab
        filters_box = gui.HBox(width = 800, height = 50)  # the upper part
        filters_box.append(self.exp_filters())
        filters_box.append(self.bio_filters())
        table_box = gui.TableWidget(0,0)    # the bottom part
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
        for row in results:
            results_list_of_tuples.append(tuple(row))
        print(results_list_of_tuples)
        # table_box.append_from_list(results_list_of_tuples,fill_title=True)
        return results

    def send_email(self):
        print('emails') ######### add noa's function


    def edit_widget(self): ########## add from talt
        edit_widget = gui.VBox(width = 500, height = 500)
        return edit_widget

    def create_widget(self): # to be added in the future
        create_widget = gui.VBox(width = 500, height = 500)
        return create_widget


start(LabApp, address='0.0.0.0', port=8081,multiple_instance=True,start_browser=True)
