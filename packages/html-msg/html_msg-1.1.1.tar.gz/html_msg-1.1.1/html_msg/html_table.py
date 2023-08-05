class HTMLTable:
    
    presets = {
        "Basic": {
        
            "table_style": "border: 1px solid; border-collapse: collapse; padding: 5pt 5pt 5pt;",
            "header_style": "border: 1px solid; border-collapse: collapse; padding: 5pt 5pt 5pt; font-weight: bold; text-align: center;",
        },
            
        "Tile":{
            
            "table_style": "border: solid #E0E0E0 1.0pt; border-radius: 10px; padding: 10pt 10pt 10pt; background-color: #F8F8F8;",
            "header_style": "border: solid #E0E0E0 1.0pt; border-radius: 10px; padding: 10pt 10pt 10pt; background-color: #F8F8F8; font-weight: bold;",
        },
        
        "Modern":
        {
            "table_style": "border-top: solid #E0E0E0 1.0pt; border-left: none; border-bottom: solid #E0E0E0 1.0pt; border-right: none; padding: 3.75pt 3.75pt 3.75pt; color: #1B5198; text-align: left;",
            "header_style": "border-top: none; border-left: none; border-bottom: solid #E0E0E0 1.0pt; border-right: none; padding: 3.75pt 3.75pt 3.75pt; text-align: center; color: #6C8999"
        },
        
        "Grey":{
            "table_style": "border: 1.5px solid #000000;text-align: center;border-collapse: collapse; padding: 5pt 5pt 5pt;color: black;",
            "header_style": "border: 1.5px solid #000000;text-align: center;border-collapse: collapse;background: linear-gradient(to bottom, #dbdbdb 0%, #d3d3d3 66%, #CFCFCF 100%);border-bottom: 1.5px solid #000000;color: black;padding: 10pt 10pt 10pt;margin-left: auto;margin-right: auto;"
        },
        
    }
    
    def __init__(self, rows=None, headers=None):
        
        if rows is None:
            self.rows = []
        else:
            self.rows = rows
        
        self.headers = headers
        self.cell_color_map = {}
        self.cell_style_map = {}
        self.font_family = 'Arial'
        self.font_size = '12px'
        self.font_color = 'black'
        self.table_style = self.presets["Basic"]["table_style"]
        self.header_style = self.presets["Basic"]["header_style"]
        self.html_table  = ''
    
    def __update_table(self):
        self.html_table = f'<table style="font-family: {self.font_family}; font-size: {self.font_size}; color: {self.font_color}; {self.table_style}">\n'
        self.__update_headers()
        self.__update_rows()
        self.html_table += '</table>'
    
    def __update_headers(self):
        # Add headers if they exist
        if self.headers:
            self.html_table += '<tr>'
            for header in self.headers:
                self.html_table += f'<th style="{self.header_style}">{header}</th>'
            self.html_table += '</tr>\n'
    
    def __update_rows(self):
        # Add rows
        for i, row in enumerate(self.rows):
            self.html_table += '<tr>'
            cell_style = ''
            
            for j, cell in enumerate(row):
                
                # Add cell color and cell style if they exist
                cell_style = ''
                
                if (i, j) in self.cell_style_map:
                    cell_style += f' {self.cell_style_map[(i, j)]};'
                
                if (i, j) in self.cell_color_map:
                    cell_style += f' background: {self.cell_color_map[(i, j)]};'
                
                self.html_table += f'<td style="{self.table_style}{cell_style}">{cell}</td>'
            
            self.html_table += '</tr>\n'
    
    def add_row(self, row):
        
        '''
        Appends a new row to the table.

        Args:
            row (list): list representing a new row.
            
        Example:
            table = HTMLTable()
            table.add_row(["value1", "value2", "value3"])
        '''
        
        self.rows.append(row)
    
    def set_headers(self, headers):
        
        '''
        Sets the headers of the table.

        Args:
            headers (list): list representing headers of the table.

        Example:
            table = HTMLTable()
            table.set_headers(["header1", "header2", "header3"])
        '''
        
        self.headers = headers
    
    def set_cell_color(self, row_index, col_index, color):
        
        '''
        Sets the background color of a specific cell.

        Args:
            row_index (int): the index of the row of the cell.
            col_index (int): the index of the column of the cell.
            color (str): a string representing the color.

        Example:
            table = HTMLTable()
            table.set_cell_color(0, 1, "red")
        '''
        
        if row_index < len(self.rows) and col_index < len(self.rows[row_index]):
            if color is None:
                if (row_index, col_index) in self.cell_style_map:
                    self.cell_color_map[(row_index, col_index)] = 'none'
            else:
                self.cell_color_map[(row_index, col_index)] = color
    
    def set_cell_style(self, row_index, col_index, style):
        
        '''
        Sets the style of a specific cell.

        Args:
            row_index (int): the index of the row of the cell.
            col_index (int): the index of the column of the cell.
            style (str): dictionary with style in the form {key: value} or a string representing the css style. 

        Example:
            table = HTMLTable()
            # all three lines below do the same thing
            table.set_cell_style(0,1, {'background': 'white', 'color': 'red', 'text-align': 'left'})
            table.set_cell_style(0,1, table.generate_css_style({'background': 'white', 'color': 'red', 'text-align': 'left'}))
            table.set_cell_style(0,1,'background: white;color: red;text-align: left;')
        '''
        
        if row_index < len(self.rows) and col_index < len(self.rows[row_index]):
            if style is None:
                if (row_index, col_index) in self.cell_style_map:
                    del self.cell_style_map[(row_index, col_index)]
            elif type(style) == dict:
                ctyle_css = self.generate_css_style(style)
                self.cell_style_map[(row_index, col_index)] = ctyle_css
            elif type(style) == str:
                self.cell_style_map[(row_index, col_index)] = style
            else:
                raise ValueError('Argument <style> must be dictionary or string.')
    
    def get_cell_content(self, row_index, col_index):
        
        '''
        Gets the content of a specific cell. 
        Might be used for conditional formating (if value in cell is equal to ..., then ...)

        Args:
            row_index (int): the index of the row of the cell.
            col_index (int): the index of the column of the cell.

        Returns:
            (str) the content of the specified cell.

        Example:
            table = HTMLTable()
            table.add_row(["value1", "value2", "value3"])
            table.get_cell_content(0, 1)  # returns "value2"
        '''
        
        if row_index < len(self.rows) and col_index < len(self.rows[row_index]):
            return self.rows[row_index][col_index]
    
    def set_table_style(self, style):
        
        '''
        Sets the CSS style of the table.
        
        Note: Please note that this method sets the style of rows. 
              In order to set the style of headers, use method 'set_header_style'

        Args:
            style (str): a dictionary or a string representing the CSS style.

        Example:
            table = HTMLTable()
            table.set_table_style("border-collapse: collapse; padding: 5pt 5pt 5pt;")
        '''
        if type(style) == dict:
            self.table_style = self.generate_css_style(style)
        elif type(style) == str:
            self.table_style = style
        else:
            raise ValueError(f'Parameter <style> must be either dictionary or string.')
    
    def set_header_style(self, style):
        
        '''
        Sets the CSS style of the table header.

        Args:
            style (dict or str): a dictionary or a string representing the CSS style.

        Example:
            table = HTMLTable()
            table.set_header_style("border: solid #E0E0E0 1.0pt; padding: 5pt 5pt 5pt;")
        '''
        if type(style) == dict:
            self.header_style = self.generate_css_style(style)
        elif type(style) == str:
            self.header_style = style
        else:
            raise ValueError(f'Parameter <style> must be either dictionary or string.')       
        
    
    def apply_design_preset(self, preset_name):
        
        '''
        Applies a pre-defined design preset to the table.

        Args:
            preset_name (str): a string representing the name of the preset.

        Example:
            table = HTMLTable()
            table.apply_design_preset("Minimalistic")
        '''
        
        self.set_table_style(self.presets[preset_name]["table_style"])
        self.set_header_style(self.presets[preset_name]["header_style"])
        self.__update_table()
    
    def generate_css_style(self, style_dict):
        
        '''
        Generates a string of CSS style properties and values from a dictionary.

        Args:
            style_dict (dict): A dictionary containing CSS style properties and values.

        Returns:
            str: A string of CSS style properties and values.

        Example:
            msg = HTMLMessage()
            style_dict = {"font-weight": "bold", "color": "red"}
            style = msg.generate_css_style(style_dict)
            # style will be "font-weight: bold;color: red;"
        '''
        
        style = ""
        for key, value in style_dict.items():
            style += f"{key}: {value};"
        return style
    
    def create_sample_table(self):
        
        '''
        This method creates an instance of the HTMLTable class with sample rows and headers for demonstration purposes.

        Args:
            None

        Returns:
            sample_table (HTMLTable): An instance of the HTMLTable class with sample rows and headers.

        Example:
            html_table = HTMLTable()
            sample_table = html_table.create_sample_table()
            
        '''
        
        sample_table = HTMLTable(rows=[
            ["John", "Doe", "example@example.com", "(123) 456-7890"],
            ["Jane", "Doe", "example@example.com", "(123) 456-7890"]
        ], headers=["First Name", "Last Name", "Email", "Phone Number"])
        
        return sample_table
    
    def show_table_design_presets(self):
        
        '''
        This method displays a sample table for each design preset available in the presets attribute of the HTMLTable class.
        
        Args:
            None.
        
        Returns:
            None.
        
        Example:
            table = HTMLTable()
            table.show_table_design_presets()
        '''
        
        # Display sample table for each preset
        for preset_name, preset in self.presets.items():
            print(f"\n{preset_name}:")
            sample_table = self.create_sample_table()
            sample_table.set_table_style(preset["table_style"])
            sample_table.set_header_style(preset["header_style"])
            sample_table.display()
    
    def create_table_from_pandas_df(self, df):
        
        '''
        Fills instance of HTMLTable with data from given Pandas dataframe. .

        Args:
            df (DataFrame): The Pandas DataFrame to create the table from.
        
        Returns:
            None.
        
        Note: This method might take a lot of computation time if large dataframe is provided, because data is processed rowwise. 
        
        Example:
            new_table = HTMLTable()
            new_table.create_table_from_pandas_df(sample_df)
        '''
        
        import pandas as pd
        
        df_headers = df.columns.values.tolist()
        self.set_headers(df_headers)
        df_rows = df.values.tolist()
        for row in df_rows:
            self.add_row(row)
        

    def create_html_hyperlink(self, link, text):
        
        '''
        Create an HTML hyperlink with the given link text and URL.
        This method might be used with the method "add_row" in order to insert link into the table.  

        Args:
            link_text (str): The text to be displayed as the hyperlink.
            url (str): The URL that the hyperlink should point to.

        Returns:
            str: An HTML string containing the hyperlink with the given link text and URL.
    
        Example:
            # Create a table with headers
            table = HTMLTable(rows=[], headers=['Title', 'Status', 'File link'])
            table.add_row(['Unit test 1', 'SUCCESS', table.create_html_hyperlink('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'result')])
        
        '''
        
        return f'<a href="{link}">{text}</a>'
        
    
    def display(self):
        
        '''
        Displays the HTML table in an IPython notebook.

        Note: Please note that table appearance may differ from what you see in Outlook if you use Dark Theme.

        Example:
            table = HTMLTable()
            table.create_sample_table()
            table.apply_design_preset("Minimalistic")
            table.display()
        '''
        from IPython.display import display, HTML

        self.__update_table()
        display(HTML(self.html_table))
        
    def to_string(self):
        
        '''
        Converts the HTML table to a string. 
        This method should be used to assign html code in a string format to the variable, 
        which will be passed to the method 'add_html' of an instance of HTMLMessage() class in order to insert the table into 
        message body. 

        Returns:
            str: The HTML Table as a string, with newline characters removed.

        Example:
            table = HTMLTable()
            table.create_sample_table()
            table.apply_design_preset("Minimalistic")
            table_str = table.to_string()
            msg = HTMLMessage()
            msg.add_html(table_str)
        '''
        
        return str(self.html_table).replace('\n', '')
    
    def __str__(self):
        self.__update_table()
        return self.html_table
    
    
