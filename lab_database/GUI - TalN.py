import remi.gui as gui
from remi import start, App


class LabApp(App):
    def __init__(self, *args):
        self.exp_names = ['A','B','C'] ######### to be somehow received from the database
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
        container.add_tab(self.create_widget(), 'Add Experiment or Field', 'Add Experiment or Field')
        return container

    def filters_widget(self):
        """
        creates the filters container by calling for its three parts (two that create filters and one that creates the table).
        a "Filter" button is also created here, which has a listener function.
        """
        filters_widget = gui.VBox(width = 1000, height = 1000) # the entire tab
        filters_box = gui.HBox(width = 1000, height = 300)  # the upper part
        filters_box.append(self.bio_filters())
        filters_box.append(self.exp_filters())
        filter_button = gui.Button('Filter')
        filter_button.set_on_click_listener(self.filter)
        filters_box.append(filter_button)
        table_box = gui.TableWidget(0,0)    # the bottom part
        filters_widget.append(filters_box)
        filters_widget.append(table_box)
        return filters_widget

    def bio_filters(self):
        """
        creates filters for the subject's biographic information.
        """
        bio_filters = gui.VBox(width = 500, height = 300)

        gender = gui.DropDown()
        gender.add_child(0,gui.DropDownItem('Gender'))
        gender.add_child(1,gui.DropDownItem('Male'))
        gender.add_child(2,gui.DropDownItem('Female'))
        bio_filters.append(gender)
        self.filter_bio_widgets.append(gender)

        years = gui.HBox(width = 500, height = 100)
        years_label = gui.Label('Year of birth')
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

        rs = gui.HBox(width = 500, height = 100)
        rs_label = gui.Label('Reading Span')
        rs_from = gui.TextInput(hint='from')
        rs_to = gui.TextInput(hint='to')
        rs.append(rs_label)
        rs.append(rs_from)
        rs.append(rs_to)
        bio_filters.append(rs)
        self.filter_bio_widgets.append(rs_from)
        self.filter_bio_widgets.append(rs_to)
        return bio_filters

    def exp_filters(self):
        """
        creates an "include" and "exclude" checkbox for each experiment.
        """
        exp_filters = gui.Table()
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
        exp_filters.add_child(str(id(row)), row)
        # creating a row for each experiment:
        for exp in self.exp_names:
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
            exp_filters.add_child(str(id(row)), row)
            self.filter_exp_yes_widgets.append(cb_yes)
            self.filter_exp_no_widgets.append(cb_no)
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

        #bio filters:
        if (self.filter_bio_widgets[0].get_value() != None) and (self.filter_bio_widgets[0].get_value() != 'Gender'):
            selected_filters['gender'] = self.filter_bio_widgets[0].get_value()
        if self.filter_bio_widgets[1].get_value() != '':
            selected_filters['year_from'] = self.filter_bio_widgets[1].get_value()
            selected_filters['year_to'] = self.filter_bio_widgets[2].get_value()
        if (self.filter_bio_widgets[3].get_value() != None) and (self.filter_bio_widgets[3].get_value() != 'Dominant hand' ):
            selected_filters['hand'] = self.filter_bio_widgets[3].get_value()
        if self.filter_bio_widgets[4].get_value() != '':
            selected_filters['rs_from'] = self.filter_bio_widgets[4].get_value()
            selected_filters['rs_to'] = self.filter_bio_widgets[5].get_value()
        print(selected_filters)
        return selected_filters

    def edit_widget(self): ########## add from talt
        edit_widget = gui.VBox(width = 500, height = 500)
        return edit_widget

    def create_widget(self): ########## needs to be created
        create_widget = gui.VBox(width = 500, height = 500)
        return create_widget


start(LabApp, address='0.0.0.0', port=8081,multiple_instance=True,start_browser=True)

