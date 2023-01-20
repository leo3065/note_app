import tkinter as tk


def constrain(value, lower, upper):
    return min(max(value, lower), upper)


class TextboxFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        if not 'borderwidth' in kwargs:
            kwargs['borderwidth'] = 2
        if not 'relief' in kwargs:
            kwargs['relief'] = tk.RAISED
        super().__init__(master, **kwargs)
        
        self.rowconfigure(0, minsize=8)
        self.setup_interface()
        
        self.after(1, self.snap_in_range)
        
    def snap_in_range(self):
        self.place_configure(
            x=constrain(self.winfo_x(), 0, self.master.winfo_width()-self.winfo_width()),
            y=constrain(self.winfo_y(), 0, self.master.winfo_height()-self.winfo_height())
        )
        
    def setup_interface(self):
        textbox = self.textbox = tk.Text(
            self, font=('Consolas', 12), height=4, width=24, wrap=tk.NONE)
        textbox.grid(row=1, column=0, sticky=tk.N+tk.S+tk.W+tk.E)
        h_scroll = self.h_scroll = tk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=textbox.xview)
        h_scroll.grid(row=2, column=0, sticky=tk.W+tk.E)
        v_scroll = self.v_scroll = tk.Scrollbar(
            self, orient=tk.VERTICAL, command=textbox.yview)
        v_scroll.grid(row=1, column=1, sticky=tk.N+tk.S)
        
        textbox['xscrollcommand'] = h_scroll.set
        textbox['yscrollcommand'] = v_scroll.set
        
        textbox.bind('<Button-1>', lambda e: self.lift())
        
        self.bind('<Button-1>', self.drag_start_callback)
        self.bind('<Button1-Motion>', self.drag_callback)
        self.bind('<ButtonRelease-1>', self.drag_end_callback)
        self.bind('<ButtonRelease-3>', self.delete_callback)
        
    def drag_start_callback(self, event):
        if event.widget is not self:
            return
        self.update_idletasks()
        
        self.lift()
        self.origin_mouse_pos = event.x_root, event.y_root
        self.origin_self_pos = self.winfo_x(), self.winfo_y()
        
    def drag_callback(self, event):
        if event.widget is not self:
            return
        self.update_idletasks()
        
        origin_mouse_x, origin_mouse_y = self.origin_mouse_pos
        origin_x, origin_y = self.origin_self_pos
        mouse_x = event.x_root
        mouse_y = event.y_root
        delta_x = mouse_x - origin_mouse_x
        delta_y = mouse_y - origin_mouse_y
        
        self.place_configure(
            x=constrain(origin_x+delta_x, 0, self.master.winfo_width()-self.winfo_width()),
            y=constrain(origin_y+delta_y, 0, self.master.winfo_height()-self.winfo_height())
        )
    
    def drag_end_callback(self, event):
        if event.widget is not self:
            return
        self.winfo_toplevel().event_generate('<<Child_updated>>')
    
    def delete_callback(self, event):
        if event.widget is not self:
            return
        top_level = self.winfo_toplevel()
        self.destroy()
        top_level.event_generate('<<Child_updated>>')


class TkApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_interface()
        self.focus()
    
    def setup_interface(self):
        self.title('Test')
        self.geometry('640x480')
        self.minsize(640, 480)
        
        self.bind('<Button-3>', self.add_textbox_callback)
        self.bind('<<Child_updated>>', self.update_minsize)
        
        self.event_add('<<Save>>', '<Control-s>')
        self.bind('<<Save>>', lambda e: print(self.serialize_content()))
        
    def add_textbox_callback(self, event):
        if event.widget is not self:
            return
        xpos, ypos = event.x, event.y
        frame = TextboxFrame(self)
        frame.place(in_=self, x=xpos, y=ypos)
    
    def update_minsize(self, event):
        self.update_idletasks()
        
        min_width = 640
        min_height = 480
        for w in self.winfo_children():
            if isinstance(w, TextboxFrame):
                min_width = max(min_width, w.winfo_x()+w.winfo_width())
                min_height = max(min_height, w.winfo_y()+w.winfo_height())
        self.minsize(min_width, min_height)
    
    def serialize_content(self):
        self.update_idletasks()
        
        data = []
        for w in self.winfo_children():
            if isinstance(w, TextboxFrame):
                data.append(dict(
                    x=w.winfo_x(), y=w.winfo_y(), 
                    # The start of the text to the end of the text, stripping the final newline
                    text=w.textbox.get('1.0', 'end-1c')
                    ))
        return data

    def save_callback(self, event):
        pass


if __name__ == '__main__':
    TkApp().mainloop()