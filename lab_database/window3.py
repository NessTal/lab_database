import remi.gui as gui
from remi import start, App


search_by = ['ID','e-mail', 'Name']


class Window3(App):
    def __init__(self, *args):
        super(Window3, self).__init__(*args)
        self.info_dict = dict()

    def main(self):
        window3_container = gui.VBox()

        # Append to container
        window3_container.append(self.search_by_container())
        window3_container.append(self.participant_info())

        return window3_container

    def search_by_container(self):
        """create search by drop down, input and button"""
        search_by_container = gui.HBox(width='60%', height='20%')
        self.search_by_dd = gui.DropDown(width='30%')
        self.search_by_dd.add_child(0, gui.DropDownItem('Search By'))
        for idx, exp in enumerate(search_by):
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
        # Create the table and add titles
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
        first_name_row = self.add_row('First Name', 'input')
        participant_table.add_child(str(id(first_name_row)), first_name_row)
        last_name_row = self.add_row('Last Name', 'input')
        participant_table.add_child(str(id(last_name_row)), last_name_row)
        id_row = self.add_row('ID', 'input')
        participant_table.add_child(str(id(id_row)), id_row)
        email_row = self.add_row('e-mail', 'input')
        participant_table.add_child(str(id(email_row)), email_row)
        year_of_birth_row = self.add_row('Year of Birth', 'slider')
        participant_table.add_child(str(id(year_of_birth_row)), year_of_birth_row)

        info_container.append(participant_table)
        return info_container

    def add_row(self, label, box_type):
        """create a row with a table and box type"""
        types_dict = {'input': gui.TextInput, 'date': gui.Date, 'slider': gui.SpinBox}
        row = gui.TableRow()
        item = gui.TableItem()
        label = label
        item.add_child(str(id(item)), label)
        row.add_child(str(id(item)), item)
        item = gui.TableItem()
        box = types_dict[box_type]()
        self.info_dict[label] = box
        item.add_child(str(id(item)), box)
        row.add_child(str(id(item)), item)
        return row


if __name__ == '__main__':
    start(Window3)
