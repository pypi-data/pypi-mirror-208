# How to center table: add to header style this two attributes - margin-left: auto; margin-right: auto;
# сделать 2 красивых пресета 

class HTMLMessage:
    def __init__(self, body=""):
        self.body = body
        self.html = ""

    def __add_header(self):
        
        '''
        Adds the opening <html> and <body> tags to the HTML message. 
        Is called inside of the self.__update_message() method.

        Returns:
            None.
        '''
        self.html += "<html><body>"

    def __add_body(self):
        
        '''
        Adds the body of the message, including any existing HTML code, to the HTML message.
        Is called inside of the self.__update_message() method.

        Returns:
            None.
        '''
        self.html += "<p>" + self.body + "</p>"

    def __add_footer(self):
        
        '''
        Adds the closing </body> and </html> tags to the HTML message.
        Is called inside of the self.__update_message() method.

        Returns:
            None.
        '''
        
        self.html += "</body></html>"

    def __update_message(self):
        
        '''
        Creates complete HTML code of the message with any changes applied.
        Is calles inside of all methods which are used for the modifation of the message.
        
        Returns:
            None.
        '''
        
        self.html = ""
        self.__add_header()
        self.__add_body()
        self.__add_footer()

    def insert_html(self, html_code):
        
        '''
        Inserts HTML code into the message body.
        Args:
            html_code (str): The HTML code to be added to the message body.
        Example:
            msg = HTMLMessage()
            msg.insert_html("<h1>Hello, World!</h1>")
        '''
        
        self.body += html_code
        self.__update_message()

    def insert_text(self, text, new_line=False, style_dict={}):
        
        '''
        Inserts text into the message body.

        Args:
            text (str): The text to be inserted into the message body.
            new_line (bool, optional): Whether to insert a line break before the text. Defaults to False.
            style_dict (dict, optional): A dictionary containing CSS style properties and values for formatting the text. 
                Defaults to an empty dictionary.

        Example:
            msg = HTMLMessage()
            msg.insert_text("This is some text.")
            msg.insert_text("This is some bold text.", style_dict={"font-weight": "bold"})
            msg.insert_text("This is some italic text.", style_dict={"font-style": "italic"})
            msg.insert_text("This is some underlined text.", style_dict={"text-decoration": "underline"})
            msg.insert_text("This is some red text.", style_dict={"color": "red"})
            msg.insert_text("This is some large text.", style_dict={"font-size": "large"})

        '''
        
        if new_line:
            text = "<br>" + text
        
        if style_dict:
            text = f'<span style="{self.generate_css_style(style_dict)}">{text}</span>'

        self.body += text
        self.__update_message()
    
    def create_formated_text(self, text, new_line=False, style_dict={}):
        
        '''
        Creates formatted text without inserting it into the message body.

        Args:
            text (str): The text to be formatted.
            new_line (bool, optional): Whether to insert a line break before the text. Defaults to False.
            style_dict (dict, optional): A dictionary containing CSS style properties and values for formatting the text. 
                Defaults to an empty dictionary.

        Returns:
            str: The formatted text.

        Example:
            msg = HTMLMessage()
            formatted_text = msg.create_formated_text("This is some bold and red text.", style_dict={"font-weight": "bold", "color": "red"})
        '''
        
        if new_line:
            text = "<br>" + text
        
        if style_dict:
            text = f'<span style="{self.generate_css_style(style_dict)}">{text}</span>'
        
        return text
    
    def insert_hyperlink(self, text, url, new_line=False):
        
        '''
        Inserts a hyperlink into the message body.

        Args:
            text (str): The text to be displayed as the hyperlink.
            url (str): The URL that the hyperlink should point to.

        Example:
            msg = HTMLMessage()
            msg.insert_hyperlink("Click here to go to Google", "https://www.google.com")
        '''
        if new_line:
            br = '<br>'
        else:
            br=''
        
        hyperlink = f'<a href="{url}">{br}{text}</a>'
        self.body += hyperlink
        self.__update_message()

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
    
    def show_formatting_tips(self):
        
        from IPython.display import display as msg_display, HTML as msg_HTML
        
        html_tips = ''' 
        
        
        <h1>color:</h1> The color of the text can be specified using a color name (e.g. "red", "blue", "green"), a hexadecimal value (e.g. "#ff0000", "#0000ff", "#00ff00"), or an RGB value (e.g. "rgb(255, 0, 0)", "rgb(0, 0, 255)", "rgb(0, 255, 0)").
        <p style="color: blue;">{'color': 'blue'}</p>
        <p style="color: #00ff00;">{'color': '#00ff00'}</p>
        
        <h1>background-color:</h1> The background color of the text can be specified using the same values as the color property.
        <p style="background-color: lightblue;">{'background-color': 'lightblue'}</p>
        <p style="background-color: #ffcccc;">{'background-color': '#ffcccc'}</p>
        
        <h1>font-size:</h1> The size of the text can be specified in pixels (e.g. "12px"), points (e.g. "12pt"), em units (e.g. "1.2em"), or as a percentage of the parent element's font size (e.g. "120%").
        <p style="font-size: 14pt;">{'font-size': '14pt'}</p>
        <p style="font-size: 1.5em;">{'font-size': '1.5em'}</p>
        
        <h1>font-family:</h1> The font family of the text can be specified as a font name (e.g. "Arial", "Times New Roman"), a generic font family (e.g. "serif", "sans-serif", "monospace"), or a font stack that lists multiple font families in order of preference (e.g. "Helvetica, Arial, sans-serif").
        <p style="font-family: 'Times New Roman', serif;">{'font-family': 'Times New Roman, serif'}</p>
        <p style="font-family: 'Courier New', monospace;">{'font-family': 'Courier New, monospace'}</p>

        <h1>font-weight:</h1> The weight of the text can be specified as a number between 100 and 900, or as a keyword (e.g. "normal", "bold").
        <p style="font-weight: 900;">{'font-weight': '900'}</p>
        <p style="font-weight: normal;">{'font-weight': 'normal'}</p>
        
        <h1>font-style:</h1> The style of the text can be specified as a keyword (e.g. "normal", "italic", "oblique").
        <p style="font-style: oblique;">{'font-style': 'oblique'}</p>
        <p style="font-style: normal;">{'font-style': 'normal'}</p>
        
        <h1>text-decoration:</h1> The decoration of the text can be specified as a keyword (e.g. "none", "underline", "overline", "line-through").
        <p style="text-decoration: overline;">{'text-decoration': 'overline'}</p>
        <p style="text-decoration: line-through;">{'text-decoration': 'line-through'}</p>
        
        <h1>text-align:</h1> The alignment of the text can be specified as a keyword (e.g. "left", "right", "center", "justify"). Please note, that 'text-align' won't work without property 'display' set to 'block'.
        <div style="text-align: left; display: block;">{'text-align': 'left', 'display': 'block'}</div>
        <div style="text-align: center; display: block;">{'text-align': 'center', 'display': 'block'}</div>
        
        <h1>line-height:</h1> The height of a line of text can be specified as a number (e.g. "1.5"), or as a unitless value that is a multiplier of the font size (e.g. "1.5em", "150%").
        <p style="line-height: 2;">{'line-height': '2'}</p>
        <p style="line-height: 200%;">{'line-height': '200%'}</p>
        
        <h1>letter-spacing:</h1> The spacing between letters can be specified in pixels, em units, or as a percentage of the font size.
        <p style="letter-spacing: 0.1em;">{'letter-spacing': '0.1em'}</p>
        <p style="letter-spacing: -1px;">{'letter-spacing': '-1px'}</p>
        
        <h1>word-spacing:</h1> The spacing between words can be specified in pixels, em units, or as a percentage of the font size.
        <p style="word-spacing: 0.5em;">{'word-spacing': '0.5em'} some words for example</p>
        <p style="word-spacing: 10px;">{'word-spacing': '20px'} some words for example</p>
        
        <h1>text-transform:</h1> The capitalization of the text can be specified as a keyword (e.g. "none", "uppercase", "lowercase", "capitalize").
        <p style="text-transform: lowercase;">{'text-transform': 'lowercase'}</p>
        <p style="text-transform: capitalize;">{'text-transform': 'capitalize'}</p>
        
        <h1>vertical-align:</h1> The vertical alignment of the text can be specified as a keyword (e.g. "baseline", "middle", "top", "bottom").
        <p style="vertical-align: top;">{'vertical-align': 'top'}</p>
        <p style="vertical-align: bottom;">{'vertical-align': 'bottom'}</p>
        
        <h1>text-shadow:</h1> The shadow effect of the text can be specified as a series of values, including the horizontal and vertical offsets (in pixels or other units), the blur radius, and the color of the shadow (e.g. "2px 2px 2px #000000").
        <p style="text-shadow: 1px 1px 1px #ff0000;">{'text-shadow': '1px 1px 1px #ff0000'}</p>
        <p style="text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.5);">{'text-shadow': '3px 3px 5px rgba(0, 0, 0, 0.5)'}</p>        
        
        '''
        
        msg_display(msg_HTML(html_tips))
    
    def to_string(self):
        
        '''
        Converts the HTML message to a string. This method should be used to assign html code in string format to a variable, 
        which will be passed to email sender as html text of message. 

        Returns:
            str: The HTML message as a string, with newline characters removed.

        Example:
            msg = HTMLMessage()
            msg.insert_text("This is some text.")
            html_string = msg.to_string()
        '''
        
        return str(self.html).replace('\n', '')
    
    def display(self):
        
        '''
        Displays the HTML message in an IPython notebook.

        Note: Please note that message appearance may differ from what you see in Outlook if you use Dark Theme.

        Example:
            msg = HTMLMessage()
            msg.insert_text("This is some text.")
            msg.display()

        '''
        from IPython.display import display as msg_display, HTML as msg_HTML


        self.__update_message()
        msg_display(msg_HTML(str(self.html)))
        
    
    def __str__(self):
        self.__update_message()
        return self.html
