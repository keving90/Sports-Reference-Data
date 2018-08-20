from tkinter import *  # Standard binding to Tk.
from tkinter.filedialog import askdirectory
from football_db.football_db_scraper import FbDbScraper
from pro_football_ref.pro_football_ref_scraper import ProFbRefScraper
import os


class NflScraperGui(Tk):
    """Main class for the NFL scraper GUI."""
    def __init__(self, *args, **kwargs):
        super(NflScraperGui, self).__init__()

        # Specify the root window's title.
        self.title("NFL Data Scraper")

        # Create and initialize the main container.
        container = Frame(self)
        container.grid(row=0, column=0)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create main menu frame and place in main container.
        frame = MainMenuFrame(container, self)
        frame.grid(row=0, column=0, sticky='nsew')


class MainMenuFrame(Frame):
    def __init__(self, parent, controller):
        super(MainMenuFrame, self).__init__(parent)

        # Main menu's top frame.
        main_frame = Frame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10)

        # Data Source
        # -----------

        # Frame containing source label and radio buttons.
        data_source_frame = Frame(main_frame)
        data_source_frame.grid(row=0, column=0, sticky='w')

        # Label prompting user to choose a data source.
        label = Label(data_source_frame, text='Choose a data source:')
        label.grid(row=0, column=0, sticky='w', padx=(0, 5))

        # Source radio button variable.
        self.data_source_var = IntVar(data_source_frame)
        self.data_source_var.set(0)

        # Source radio buttons.
        # Football Database radio button.
        fbdb_radio_button = Radiobutton(data_source_frame, text='Football Database',
                                        variable=self.data_source_var,
                                        value='0',
                                        command=self.set_fbdb_table_types)

        fbdb_radio_button.grid(row=0, column=1, sticky='w')

        # Pro Football Reference radio button.
        pro_ref_radio_button = Radiobutton(data_source_frame,
                                           text='Pro Football Reference',
                                           variable=self.data_source_var,
                                           value='1',
                                           command=self.set_pro_ref_table_types)

        pro_ref_radio_button.grid(row=0, column=2, sticky='w')

        # File name
        # ---------

        # File name's string frame, variable, label, and text field.
        file_name_frame = Frame(main_frame)
        file_name_frame.grid(row=1, column=0)
        self.file_name_var = StringVar()
        self.file_name_var.set('')
        file_name_label = Label(file_name_frame, text='File name (blank uses default name):')
        file_name_label.grid(row=0, column=0, sticky='w')
        file_name_entry = Entry(file_name_frame, textvariable=self.file_name_var)
        file_name_entry.grid(row=0, column=1, sticky='w', padx=(0, 10))

        # Frame containing Set Save Location and Scrape Data buttons.
        save_and_scrape_frame = Frame(main_frame)
        save_and_scrape_frame.grid(row=2, column=0)

        # Data file's save directory location.
        self.directory = None
        # self.directory = '~/Desktop'

        # Set Save Location and Scrape Data buttons
        # -----------------------------------------

        # Set Save Location button opens folder browser to select CSV file's save location.
        self.save_location_button = Button(save_and_scrape_frame, text='Set Save Location', command=self.get_save_location)
        self.save_location_button.grid(row=0, column=0, padx=50)

        # Scrape Data button.
        self.scrape_data_button = Button(save_and_scrape_frame, text='Scrape Data', command=self.scrape_data)
        self.scrape_data_button.grid(row=0, column=1, padx=50)

        # Option menus
        # ------------

        # Option menu variables for when the Football Database source is selected.
        # This data source is selected by default.
        # fbdb_tables = ['all_purpose', 'passing', 'rushing', 'receiving', 'scoring', 'fumbles', 'kick_returns',
        #                'punt_returns', 'kicking', 'scrimmage', 'fantasy_offense']
        fbdb_tables = ['Passing', 'Rushing', 'Receiving', 'Scoring', 'Fumbles', 'Kick Returns', 'Punt Returns',
                       'Kicking', 'Scrimmage Yards', 'All Purpose Yards', 'Fantasy Offense']

        # List of NFL seasons whose data can be scraped.
        # These years range from the beginning of the Super Bowl Era to present day.
        years = [year for year in range(2017, 1939, -1)]

        # Frame containing drop-down option menus.
        option_menu_frame = Frame(main_frame)
        option_menu_frame.grid(row=3, column=0)

        # Table type option menu variable.
        self.option_menu_var = StringVar(option_menu_frame)
        self.option_menu_var.set('Passing')

        # Start year variable.
        self.start_year_option_var = StringVar(option_menu_frame)
        self.start_year_option_var.set(str(years[0]))

        # End year variable.
        self.end_year_option_var = StringVar(option_menu_frame)
        self.end_year_option_var.set(str(years[0]))

        # Table type label and option menu.
        self.scrape_label = Label(option_menu_frame, text='Table to scrape from:')
        self.scrape_label.grid(row=0, column=0, sticky='e')
        self.table_types_menu = OptionMenu(option_menu_frame, self.option_menu_var, *fbdb_tables,
                                           command=self.option_menu_var.set)
        self.table_types_menu.grid(row=0, column=1, sticky='w')
        self.table_types_menu.config(width=16)

        # Start year label and option menu.
        self.start_year_label = Label(option_menu_frame, text='First year to scrape from:')
        self.start_year_label.grid(row=1, column=0, sticky='w')
        self.start_year_menu = OptionMenu(option_menu_frame, self.start_year_option_var, *years,
                                          command=self.start_year_option_var.set)
        self.start_year_menu.grid(row=1, column=1, sticky='w')
        self.start_year_menu.config(width=16)

        # End Year label and option menu.
        self.end_year_label = Label(option_menu_frame, text='Last year to scrape from:')
        self.end_year_label.grid(row=2, column=0, sticky='w')
        self.end_year_menu = OptionMenu(option_menu_frame, self.end_year_option_var, *years,
                                        command=self.end_year_option_var.set)
        self.end_year_menu.grid(row=2, column=1, sticky='w')
        self.end_year_menu.config(width=16)

        # Fantasy Settings button
        # -----------------------

        # Fantasy Settings button (not contained in its own frame).
        self.scrape_data_button = Button(main_frame, text='Fantasy Settings', command=self.view_fantasy_settings)
        self.scrape_data_button.grid(row=4, column=0)

        # Dictionary containing the default fantasy settings.
        # Used to initialize the Fantasy Settings window.
        default_fantasy_settings = {
            'pass_yards': '0.04',
            'pass_td': '4',
            'interceptions': '-1',
            'rush_yards': '0.10',
            'rush_td': '6',
            'rec_yards': '0.10',
            'receptions': '0',
            'rec_td': '6',
            'two_pt_conversions': '2',
            'fumbles_lost': '-2',
            'offensive_fumble_return_td': '6',
            'return_yards': '0.04',
            'return_td': '6',
            'pat_made': '1',
            '0-19_made': '3',
            '20-29_made': '3',
            '30-39_made': '3',
            '40-49_made': '4',
            '50_plus_made': '5'
        }

        # Create a dictionary of StringVar's for custom fantasy setting text entries and give them initial values
        # based on the default settings.
        self.fantasy_settings = {}
        for cat, value in default_fantasy_settings.items():
            self.fantasy_settings[cat] = StringVar()
            self.fantasy_settings[cat].set(value)

    def set_fbdb_table_types(self):
        """Gives the self.table_types_menu OptionMenu the relevant Football Database table types."""
        # Relevant table types.
        fbdb_tables = ['Passing', 'Rushing', 'Receiving', 'Scoring', 'Fumbles', 'Kick Returns', 'Punt Returns',
                       'Kicking', 'Scrimmage Yards', 'All Purpose Yards', 'Fantasy Offense']

        # Clear the current OptionMenu choices.
        self.table_types_menu.children['menu'].delete(0, 'end')

        # Add new OptionMenu choices.
        for table in fbdb_tables:
            self.table_types_menu.children['menu'].add_command(label=table,
                                                               command=lambda t=table: self.option_menu_var.set(t))

        # Set the default OptionMenu table selection.
        self.option_menu_var.set('Passing')

        # Enable the fantasy settings button.
        # self.scrape_data_button.state(['!disabled'])
        self.scrape_data_button['state'] = 'normal'

    def set_pro_ref_table_types(self):
        """Gives the self.table_types_menu OptionMenu the relevant Pro Football Reference table types."""
        # Relevant table types.
        pro_ref_tables = ['Passing', 'Rushing', 'Receiving', 'Scoring', 'Kicking', 'Returns', 'Defense', 'Fantasy']

        # Clear the current OptionMenu choices.
        self.table_types_menu.children['menu'].delete(0, 'end')

        # Add new OptionMenu choices.
        for table in pro_ref_tables:
            self.table_types_menu.children['menu'].add_command(label=table,
                                                               command=lambda t=table: self.option_menu_var.set(t))

        # Set the default OptionMenu table selection.
        self.option_menu_var.set('Passing')

        # Disable the fantasy settings button.
        self.scrape_data_button['state'] = 'disabled'

    def view_fantasy_settings(self):
        """
        Opens the fantasy settings window so users can set their own customized fantasy settings for offensive
        plays.
        """
        # Create a new window.
        top = Toplevel()
        top.title('Fantasy Settings')

        frame = Frame(top, padx=10, pady=10)
        frame.grid(row=0, column=0)

        # Title label.
        title_label = Label(frame, text='Custom Fantasy Settings', font='Helvetica 18 bold')
        title_label.grid(row=0, column=0, columnspan=2)

        # Label instructing user how to set their own custom fantasy settings.
        instructions_label = Label(frame, text='Enter a point value for the fantasy category.\n'
                                               'Values will be saved automatically.')
        instructions_label.grid(row=1, column=0, columnspan=2, pady=10)

        # Title labels for the column of fantasy categories and column of text entries.
        category_title_label = Label(frame, text='Offensive Category', font='Helvetica 14 bold')
        category_title_label.grid(row=2, column=0, sticky='e', padx=10)
        entry_title_label = Label(frame, text='Point Value', font='Helvetica 14 bold')
        entry_title_label.grid(row=2, column=1, sticky='w')

        # Dictionary used to initialize each fantasy category's text entry decription.
        label_messages = {
            'pass_yards': 'Points per pass yard:',
            'pass_td': 'Passing touchdowns:',
            'interceptions': 'Interceptions:',
            'rush_yards': 'Points per rush yard:',
            'rush_td': 'Rushing Touchdowns:',
            'rec_yards': 'Points per receiving yard:',
            'receptions': 'Receptions:',
            'rec_td': 'Reception touchdowns:',
            'two_pt_conversions': 'Two point conversions:',
            'fumbles_lost': 'Fumbles lost:',
            'offensive_fumble_return_td': 'Offensive fumble return touchdown:',
            'return_yards': 'Points per return yard:',
            'return_td': 'Return touchdowns:',
            'pat_made': 'Point after touchdown:',
            '0-19_made': '0-19 yards field goal:',
            '20-29_made': '20-29 yards field goal:',
            '30-39_made': '30-39 yards field goal:',
            '40-49_made': '40-49 yards field goal:',
            '50_plus_made': '50 or more yards field goal:'
        }

        # Create each text entry box and create a label to describe each text entry.
        # Fill the text entry with the relevant category's point value.
        for row_num, (cat, message) in enumerate(label_messages.items(), 3):
            label = Label(frame, text=message)
            label.grid(row=row_num, column=0, sticky='e', padx=10)
            entry = Entry(frame, textvariable=self.fantasy_settings[cat])
            entry.grid(row=row_num, column=1, sticky='w')

    def get_save_location(self):
        """Prompts user to choose directory to save data files in."""
        self.directory = askdirectory()

    def display_invalid_filename_msg(self):
        """Displays error message to user when the data file's name contains invalid characters."""
        top = Toplevel()
        top.title("File Extension Error")
        message_label = Label(top, text='The following characters are not allowed\n'
                                        + '''in your file name: \ / . < > ? * ' : " |''')
        message_label.grid(row=0, column=0, padx=10, pady=10)
        button = Button(top, text="Okay", command=top.destroy)
        button.grid(row=1, column=0, pady=(0, 10))

    def display_save_directory_error_msg(self):
        """Displays error message to user when a save directory for the data file has not been chosen."""
        # Window prompting user to choose a directory to save the data file in.
        top = Toplevel()
        top.title("Save Directory Error")
        message_label = Label(top, text='Please choose a directory to save\n'
                                        'your data file in by clicking on\n'
                                        'the "Set Save Location" button.')
        message_label.grid(row=0, column=0, padx=10, pady=10)
        button = Button(top, text="Okay", command=top.destroy)
        button.grid(row=1, column=0, pady=(0, 10))

    def get_file_name(self, table_name):
        """
        Returns the data file's name from the text entry box if provided. Otherwise, returns a default file name.
        Returns None if the file name has invalid characters.
        """
        # User did not name the file, so use the default file name.
        if self.file_name_var.get() == '':
            file_name = (table_name
                         + '-'
                         + self.start_year_option_var.get()
                         + '-' + self.end_year_option_var.get()
                         + '.csv')
        # Use the custom file name provided by user.
        else:
            # Invalid character not allowed in file name.
            invalid_chars = '''\/.<>?*':"|'''
            if any((c in self.file_name_var.get()) for c in invalid_chars):
                return None
            else:
                # Custom file name is valid.
                file_name = self.file_name_var.get() + '.csv'

        return file_name

    def scrape_from_football_db(self, table_name):
        """Scrapes data from footballdb.com using the FbDbScraper class."""
        football_db_obj = FbDbScraper()
        # User is scraping an individual stat category.
        if table_name != 'fantasy_offense':
            df = football_db_obj.get_specific_df(start_year=self.start_year_option_var.get(),
                                                 end_year=self.end_year_option_var.get(),
                                                 table_type=table_name)
        # User is scraping comprehensive data with fantasy points calculations.
        else:
            # Initialize the FbDbScraper object's dictionary based on the GUI's custom fantasy settings input
            # by the user.
            for key in football_db_obj.fantasy_settings.keys():
                # Custom fantasy setting based on stat type's dict key.
                custom_setting = self.fantasy_settings[key].get()

                # Convert StringVar in Custom Fantasy Settings text entries to necessary data type.
                if isinstance(football_db_obj.fantasy_settings[key], int):
                    football_db_obj.fantasy_settings[key] = int(custom_setting)
                elif isinstance(football_db_obj.fantasy_settings[key], float):
                    football_db_obj.fantasy_settings[key] = float(custom_setting)

            # Create the data frame.
            df = football_db_obj.get_fantasy_df(start_year=self.start_year_option_var.get(),
                                                end_year=self.end_year_option_var.get())

        return df

    def scrape_from_pro_football_reference(self, table_name):
        """Scrapes data from pro-football-reference.com using the ProFbRefScraper class."""
        pro_football_ref_obj = ProFbRefScraper()
        df = pro_football_ref_obj.get_data(start_year=self.start_year_option_var.get(),
                                           end_year=self.end_year_option_var.get(),
                                           table_type=table_name)

        return df

    def scrape_data(self):
        """Scrapes the data, stores it in a data frame, and saves it as a CSV file."""
        table_names = {
            'Passing': 'passing',
            'Rushing': 'rushing',
            'Receiving': 'receiving',
            'Scoring': 'scoring',
            'Fumbles': 'fumbles',
            'Kick Returns': 'kick_returns',
            'Punt Returns': 'punt_returns',
            'Kicking': 'kicking',
            'Scrimmage Yards': 'scrimmage',
            'All Purpose Yards': 'all_purpose',
            'Fantasy Offense': 'fantasy_offense',
            'Returns': 'returns',
            'Defense': 'defense',
            'Fantasy': 'fantasy'
        }
        # Save directory chosen.
        if self.directory is not None:
            df = None

            # Table type names in the option menu are different from the ones used to scrape the data.
            # Get the corresponding table type name for data scraping methods.
            table_name = table_names[self.option_menu_var.get()]

            # Get the file name provided by the user, and check for invalid characters in it.
            file_name = self.get_file_name(table_name)

            if file_name is None:
                # Invalid character found in custom file name.
                self.display_invalid_filename_msg()
                return

            # Scraping data from Football Database.
            if self.data_source_var.get() == 0:
                df = self.scrape_from_football_db(table_name)
            # Scraping data from Pro Football Reference.
            else:
                df = self.scrape_from_pro_football_reference(table_name)

            # Save scraped data to a csv file.
            df.to_csv(os.path.join(self.directory, file_name))

        # User hasn't chosen a save directory. Display "Save Directory Error" window.
        else:
            # Window prompting user to choose a directory to save the data file in.
            self.display_save_directory_error_msg()

    """
    TODO:
    
    CHECK STRING INPUT FOR FANTASY SETTINGS NUMBERS
    
    
    DONE:
    
    SET FANTASY SETTINGS DICT FOR FOOTBALL DATABASE OBJECT
    
    SHOULD BE ABLE TO NAME THE FILE
    Fix tables names in drop-down menu.
    
    Initialize fantasy settings to default in __init__.
    Provide fantasy settings fields in top level frame.
    User can press 'save' button, which will give instance variables new values.
    
    It looks like a save button is not needed.
    
    Initialize variables inside __init__
        Declare as StringVar()
        Use set() to give initial value
        
    To create label/entry combo:
        use dict
        key = category
        value = label message 
    """


if __name__ == '__main__':
    app = NflScraperGui()
    app.mainloop()
