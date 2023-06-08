import json
import tkinter as tk
import requests
from tkinterhtml import HtmlFrame
import os

currentSource = None


def main():
    window = tk.Tk()

    # Frame for holding the button stack on the left.
    button_frame = tk.Frame(window)
    button_frame.grid(row=1, column=0, sticky='nw')
    # relieflist = ["flat", "raised", "sunken",  "groove", "ridge"]

    # Image to add to button
    assetfolder_path = '/home/lennetwork/Documents/go_projects/centrol/python/assets'
    button_size = 24
    buttonImages = ('pluslogo.png', 'minuslogo.png')

    # Adding left side menu buttons
    path = os.path.join(assetfolder_path, buttonImages[0])
    button_add = create_button(
        button_frame, path, button_size, command=lambda: open_add_window(window, listbox_feed))

    path = os.path.join(assetfolder_path, buttonImages[1])
    button_remove = create_button(button_frame, path, button_size)

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

    # Attempt to get list of sources on launch
    sourcesJsonList = []
    while not sourcesJsonList:
        retrieve = getRSS(url)
        if retrieve is not None:
            sourcesJsonList += retrieve
        else:
            promptRequest(window)  # block until user clicks retry button

    # Seperate sources from list. Sources is not a list of json objects (dicts)
    sources = [json.loads(sourcesJsonList[x]['data'])
               for x in range(len(sourcesJsonList))]

    # Getting the name of the source. Source decides their title.
    for source in sources:
        sourceName = source['Channel']['Title']
        listbox_feed.insert(tk.END, sourceName)

    # Setting selection colors
    for i, item in enumerate(listbox_feed.get(0, tk.END)):
        listbox_feed.itemconfigure(i, background='#bdc2c9', foreground='black',
                                   selectbackground='#3b3c3d', selectforeground='white')

    listbox_feed.configure(
        relief=tk.RAISED, borderwidth=1, highlightthickness=1, exportselection=False)

    listbox_feed.bind('<<ListboxSelect>>', lambda event: listbox_feed_selected(
        event, listbox_feed, listbox_content, sources, text_description))

    #  This gets a list of Items. Each item contains a dictionary with the keys:
    # 'Title', 'Description', 'PubDate', 'Link'

    listbox_content.configure(
        relief=tk.RAISED, borderwidth=1, highlightthickness=1, exportselection=False)

    # Handle placing description in description box when title is selected
    # Bind function to ListboxSelect event
    listbox_content.bind('<<ListboxSelect>>', lambda event: listbox_content_selected(
        event, listbox_content=listbox_content, text_description=text_description, json=sources[currentSource]))

    window.mainloop()

# Blocking function for rerequesting


def promptRequest(master):
    new_window = tk.Toplevel(master)
    # new_window.lift()  # Make the window the top layer
    new_window.grab_set()  # Disable interaction with the main window
    # Set the main window as the parent of the popup window
    new_window.transient(master)
    new_window.geometry("300x150")

    # Create a label for the textbox
    label = tk.Label(new_window, text="Could not find sources. Try again?")
    label.pack()

    # Create a select button
    select_button = tk.Button(new_window, text="Retry request")
    select_button.pack()

    # Function to handle button click
    def select_button_click():
        new_window.destroy()

    # Set the button's command to the click function
    select_button.config(command=select_button_click)


# Creates left side menu button.
def create_button(frame: tk.Frame, imagePath, size: int, command=None) -> tk.Button:
    image = tk.PhotoImage(file=imagePath)
    button = tk.Button(frame, image=image, width=size,
                       height=size, command=command)

    # Store reference to image so it doesn't get obliviated by the garbage collecter
    button.image = image
    # The proper thing to do would be make a custom button class that inherits from tk.Button,
    # and encapsulates the image, but this is fine for now. Minimal mutation.
    button.pack(side='top')
    return button


# Function called when add button is clicked.
# Creates a popup window that takes link to RSS feed.
def open_add_window(master, listbox_feed: tk.Listbox):
    new_window = tk.Toplevel(master)
    # new_window.lift()  # Make the window the top layer
    new_window.grab_set()  # Disable interaction with the main window
    # new_window.modal = True  # Set the window as modal
    # Set the main window as the parent of the popup window
    new_window.transient(master)
    new_window.geometry("300x150")

    # Create a label for the textbox
    label = tk.Label(new_window, text="Enter RSS Feed URL:")
    label.pack()

    # Create a textbox
    textbox = tk.Entry(new_window)
    textbox.pack()

    # Create a select button
    select_button = tk.Button(new_window, text="Select")
    select_button.pack()

    # Function to handle button click
    def select_button_click():
        # Retrieve the text from the textbox
        url = textbox.get()
        # Add url to feed list
        listbox_feed.insert(tk.END, url)
        for i, _ in enumerate(listbox_feed.get(0, tk.END)):
            listbox_feed.itemconfigure(i, background='#bdc2c9', foreground='black',
                               selectbackground='#3b3c3d', selectforeground='white')
        # Close the popup window
        new_window.destroy()

    # Set the button's command to the click function
    select_button.config(command=select_button_click)


def listbox_content_selected(event, listbox_content: tk.Listbox, text_description: HtmlFrame, json: list):
    currentText = ''
    # Check is listbox is currently selected, only update if so
    if listbox_content.curselection():  # If it is, set currentText variable
        # Get index of selected item
        # We have to get [0] of the selection. tkinter returns selection as a tuple because it can be a range
        selected_index = int(listbox_content.curselection()[0])
        # Fetch the current item's description from the list of items
        currentText = json['Channel']['Item'][selected_index]['Description']
        text_description.set_content(makeHtml(currentText))

# The htmlFrame widget from tkinterhtml only renders html. Dumb.
# This function turns any text into html by throwing a div on it.


def makeHtml(nonHtml):
    return f'<div>{nonHtml}</div>'


def listbox_feed_selected(event, listbox_feed: tk.Listbox, listbox_content: tk.Listbox, sources: list, content_htmlframe: HtmlFrame):
    if listbox_feed.curselection():  # If it is, set currentText variable
        # Get index of selected item
        # We have to get [0] of the selection. tkinter returns selection as a tuple because it can be a range
        selected_index = int(listbox_feed.curselection()[0])
        global currentSource
        currentSource = selected_index  # update global variable
        try:
            currentContent = sources[selected_index]
            populateContent(listbox_content, currentContent['Channel']['Item'])
        except:
            content_htmlframe.set_content('')
            populateContent(listbox_content, [''])
        


def populateContent(listbox_content: tk.Listbox, itemJson):
    listbox_content.delete(0, tk.END)
    for i, item in enumerate(itemJson):
        listbox_content.insert(i, item['Title'])
        # alternate colors light grey and dark grey
        background = '#aeb2b8' if i % 2 == 0 else '#bdc2c9'
        listbox_content.itemconfigure(
            i, background=background, foreground='black', selectbackground='#3b3c3d', selectforeground='white')

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
