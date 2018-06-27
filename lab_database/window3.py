import remi.gui as gui
from remi import start, App


search_by = ['ID','e-mail', 'Name']


class Window3(App):
    def __init__(self, *args):
        super(Window3, self).__init__(*args)

    def main(self):
        search_by_container = gui.HBox(width='70%', height='20%')
        # Search by drop down
        self.search_by_dd = gui.DropDown(width='30%')
        self.search_by_dd.add_child(0, gui.DropDownItem('Search By'))
        for idx, exp in enumerate(search_by):
            self.search_by_dd.add_child(idx + 1, gui.DropDownItem(exp))
        # search input
        self.search_input = gui.Input()
        # Append to container
        search_by_container.append(self.search_by_dd)
        search_by_container.append(self.search_input)
        return search_by_container


if __name__ == '__main__':
    start(Window3)
