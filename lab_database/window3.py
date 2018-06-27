import remi.gui as gui
from remi import start, App


search_by = ['ID','e-mail', 'Name']


class Window3(App):
    def __init__(self, *args):
        super(Window3, self).__init__(*args)

    def main(self):
        window3_container = gui.VBox()

        # Append to container
        window3_container.append(self.search_by_container())

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
        table_title = gui.TableTitle()


if __name__ == '__main__':
    start(Window3)
