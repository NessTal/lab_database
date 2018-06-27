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
        filter_button = gui.Button('Filter')
        filter_button.set_on_click_listener(self.filter)
        filters_box.append(filter_button)
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
        exp_filters = gui.Table()
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
        for exp in exp_names:
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
        return exp_filters

    def filter(self, *args):
        selected_filters = []
        return selected_filters

    def edit_widget(self):
        edit_widget = gui.VBox(width = 500, height = 500)
        return edit_widget

    def create_widget(self):
        create_widget = gui.VBox(width = 500, height = 500)
        return create_widget


start(LabApp, address='0.0.0.0', port=8081,multiple_instance=True,start_browser=True)

