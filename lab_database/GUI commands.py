import remi.gui as gui
from remi import start, App

exps = ['A','B','C']
table = [(1,2,3,4), (5,6,7,8), (9,10,11,12)]

class LabApp(App):
    def __init__(self, *args):
        super(LabApp, self).__init__(*args)

    def main(self):
        container = gui.HBox(width = 500, height = 500)
        self.lbl = gui.Label('Hello world!')
        self.bt = gui.Button('Press me!')

        self.part1 = gui.VBox(width = 200, height = 200)
        self.bt1 = gui.Button('button1')
        self.part1.add_child(1,self.bt1)
        self.cb = gui.CheckBoxLabel(label="check box", checked=False)
        self.part1.add_child(2,self.cb)

        self.dd = gui.DropDown()
        self.dd.add_child(0,gui.DropDownItem('Choose Experiment'))
        for idx, exp in enumerate(exps):
            self.dd.add_child(idx + 1, gui.DropDownItem(exp))

        self.tw = gui.TableWidget(0,0,use_title=False,editable=True)
        self.tw.append_from_list(table,fill_title=True)

        # setting the listeners for the onclick events of buttons:
        self.bt.set_on_click_listener(self.on_button_pressed)
        self.cb.set_on_change_listener(self.on_checkbox_change)


        # appending widgets:
        container.append(self.lbl)
        container.append(self.bt)
        container.append(self.part1)
        container.append(self.dd)
        container.append(self.tw)

        # returning the root widget
        return container


    # listener functions
    def on_button_pressed(self, widget):
        self.lbl.set_text('Button pressed!')
        self.bt.set_text('Hi!')

    def on_checkbox_change(self, widget, *args):
#        cb_count += 1
#        mod_tup = cb_count % 2
#        if mod_tup[2] == 0:
        if self.cb.get_value() == 1:
            self.lbl.set_text('Checkbox checked!')
        else:
            self.lbl.set_text('Checkbox unchecked')

# starts the webserver
start(LabApp, address='0.0.0.0', port=8081,multiple_instance=True,start_browser=True)
