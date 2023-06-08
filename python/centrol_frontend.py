import tkinter as tk
import requests
from tkinterhtml import HtmlFrame
import os


def main():
    window = tk.Tk()

    example_titles = ["this is a title", "iran is a country", "in shocking news: whitehouse isn't actually white",
                      "how many mics do we rip on the daily: The real answer", "Scientist discovers shocking truth: all items in universe fit into only 2 categories: potato, not potato"]
    # Button stack
    button_frame = tk.Frame(window)
    button_frame.grid(row=1, column=0, sticky='nw')
    # relieflist = ["flat", "raised", "sunken",  "groove", "ridge", ]

    # Image to add to button
    logo_addsource = tk.PhotoImage(file= '/home/lennetwork/Documents/go_projects/centrol/python/assets/pluslogo.png')
    button_addsource = tk.Button(button_frame, image=logo_addsource, height=24, width=24)
    button_addsource.pack(side='top')


    # Creating feed widgets
    label_feed = tk.Label(window, text="Feed list")
    listbox_feed = tk.Listbox(window, activestyle='underline')
    # Creating content widgets
    label_content = tk.Label(window, text="Content")
    listbox_content = tk.Listbox(window, activestyle='underline')
    # Create the display box for the descriptions
    # disabled state means it can't be typed in by users. state='normal' is normal.
    text_description = HtmlFrame(
        window, fontscale=1.0, vertical_scrollbar='auto', horizontal_scrollbar='auto')

    # Placing feed widgets
    label_feed.grid(row=0, column=1, sticky='ns')
    listbox_feed.grid(row=1, column=1, sticky='ns')
    # Placing content widgets
    label_content.grid(row=0, column=2, sticky='nsew')
    listbox_content.grid(row=1, column=2, sticky='nsew')
    # Placing description widget
    text_description.grid(row=2, column=0, sticky='nsew', columnspan=3)

    # Configure weights for rows and columns
    # feed column, no horizontal expansion
    window.columnconfigure(1, weight=0)
    # content column, expand horizontally with a minimum size
    window.columnconfigure(2, weight=1)

    # header row, no vertical expansion
    window.rowconfigure(0, weight=0)
    # content row, expand vertically
    window.rowconfigure(1, weight=1, minsize=300)
    # description row, yes vertical expansion, because we want that! Duh! Scrollbar thinks the window is very tall otherwise.
    window.rowconfigure(2, weight=1)

    # Window sizing
    window_width, window_height = 800, 600
    window_min_width, window_min_height = 192, 48
    window.geometry(f'{window_width}x{window_height}')
    window.minsize(width=window_min_width, height=window_min_height)

    # Get JSON using custom function
    url = 'http://localhost:8000/api/simp'
    json_rss = getRSS(url)

    # Getting the name of the source. Source decides their title.
    sourceName = json_rss['Channel']['Title']
    listbox_feed.insert(tk.END, sourceName)
    listbox_feed.itemconfigure(tk.END, background='#3b3c3d', foreground='white',
                               selectbackground='#3b3c3d', selectforeground='white')

    #  This gets a list of Items. Each item contains a dictionary with the keys:
    # 'Title', 'Description', 'PubDate', 'Link'
    items: list = json_rss['Channel']['Item']

    for i, item in enumerate(items):
        listbox_content.insert(i, item['Title'])
        # alternate colors light grey and dark grey
        background = '#aeb2b8' if i % 2 == 0 else '#bdc2c9'
        listbox_content.itemconfigure(
            i, background=background, foreground='black', selectbackground='#3b3c3d', selectforeground='white')

    listbox_content.configure(
        relief=tk.RAISED, borderwidth=1, highlightthickness=1)

    # Handle placing description in description box when title is selected
    # Bind function to ListboxSelect event
    listbox_content.bind('<<ListboxSelect>>', lambda event: listbox_content_selected(
        event, listbox_content=listbox_content, text_description=text_description, json=items))

    window.mainloop()


def listbox_content_selected(event, listbox_content: tk.Listbox, text_description: HtmlFrame, json: list):
    currentText = ''
    # Check is listbox is currently selected, only update if so
    if listbox_content.curselection():  # If it is, set currentText variable
        # Get index of selected item
        # We have to get [0] of the selection. tkinter returns selection as a tuple because it can be a range
        selected_index = int(listbox_content.curselection()[0])
        # Fetch the current item's description from the list of items
        currentText = json[selected_index]['Description']
        updateTextbox(text_description, currentText)


def updateTextbox(textbox: HtmlFrame, text: str):
    textbox.set_content(text)


# Function for requesting the JSON data of the RSS. Returns JSON object if successful, returns None is not successful.
def getRSS(url: str):
    response = requests.get(url)

    if response.status_code == 200:
        rss_json = response.json()
        return rss_json
    else:
        print('Error occurred while fetching RSS data:', response.status_code)
        return None


if __name__ == '__main__':
    main()
