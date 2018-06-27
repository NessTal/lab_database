import remi.gui as gui
from remi import start, App

# delete when database exists:
exp_names = ['A','B','C']

class LabApp(App):
    def __init__(self, *args):
        super(LabApp, self).__init__(*args)

    def main(self):
        container = gui.TabBox()
        container.add_tab(self.filters_widget(), 'Fillter', 'Fillter')
        container.add_tab(self.edit_widget(), 'Add or Edit Subject', 'Add or Edit Subject')
        container.add_tab(self.create_widget(), 'Add Experiment or Field', 'Add Experiment or Field')
        return container

    def filters_widget(self):
        filters_widget = gui.VBox(width = 1000, height = 1000) # the entire tab
        filters_box = gui.HBox(width = 1000, height = 300)  # the upper part
        filters_box.append(self.bio_filters())
        filters_box.append(self.exp_filters())
        table_box = gui.TableWidget(0,0)    # the bottom part
        filters_widget.append(filters_box)
        filters_widget.append(table_box)
        return filters_widget

    def bio_filters(self):
        bio_filters = gui.VBox(width = 500, height = 300)
        gender = gui.DropDown()
        gender.add_child(0,gui.DropDownItem('Gender'))
        gender.add_child(1,gui.DropDownItem('Male'))
        gender.add_child(2,gui.DropDownItem('Female'))
        bio_filters.append(gender)
        return bio_filters

    def exp_filters(self):
        exp_filters = gui.HBox(width = 500, height = 300)
        exp_f_yes = gui.VBox(width=250, height=300)
        exp_f_no = gui.VBox(width=250, height=300)
        exp_f_yes_title = gui.Label('Include')
        exp_f_no_title = gui.Label('Exclude')
        exp_f_yes.append(exp_f_yes_title)
        exp_f_no.append(exp_f_no_title)
        for exp in exp_names:
            exp_f_yes.append(gui.CheckBox())
            exp_f_no.append(gui.CheckBoxLabel(label=exp))
        exp_filters.append(exp_f_yes)
        exp_filters.append(exp_f_no)
        return exp_filters

    def edit_widget(self):
        edit_widget = gui.VBox(width = 500, height = 500)
        return edit_widget

    def create_widget(self):
        create_widget = gui.VBox(width = 500, height = 500)
        return create_widget


start(LabApp, address='0.0.0.0', port=8081,multiple_instance=True,start_browser=True)

