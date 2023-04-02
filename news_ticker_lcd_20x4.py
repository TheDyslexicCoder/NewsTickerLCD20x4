import requests
import json
import time
import smbus

# Initialize the I2C bus
bus = smbus.SMBus(1)
address = 0x27

def lcd_init():
    lcd_byte(0x33,LCD_CMD)
    lcd_byte(0x32,LCD_CMD)
    lcd_byte(0x06,LCD_CMD)
    lcd_byte(0x0C,LCD_CMD)
    lcd_byte(0x28,LCD_CMD)
    lcd_byte(0x01,LCD_CMD)
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

    bus.write_byte(address, bits_high)
    lcd_toggle_enable(bits_high)

    bus.write_byte(address, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    time.sleep(E_DELAY)
    bus.write_byte(address, (bits | 0b00000100))
    time.sleep(E_PULSE)
    bus.write_byte(address,(bits & ~0b00000100))
    time.sleep(E_DELAY)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")

    if line == 1:
        lcd_byte(LCD_LINE_1, LCD_CMD)
    elif line == 2:
        lcd_byte(LCD_LINE_2, LCD_CMD)
    elif line == 3:
        lcd_byte(LCD_LINE_3, LCD_CMD)
    elif line == 4:
        lcd_byte(LCD_LINE_4, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

LCD_WIDTH = 20
LCD_CHR = 1
LCD_CMD = 0

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
LCD_LINE_3 = 0x94
LCD_LINE_4 = 0xD4
LCD_BACKLIGHT = 0x08

E_PULSE = 0.0005
E_DELAY = 0.0005

# Function to create a marquee effect for the given text
def marquee_text(text, width):
    # If the text length is less than or equal to the display width, return the original text
    if len(text) <= width:
        return [text]

    result = []
    # Add extra spaces at the end of the text to create a smooth scrolling effect
    padded_text = text + " " * ((width // 2) + 1)

    # Generate a list of subtexts by sliding a window of 'width' characters over the padded text
    for i in range(len(text) + 1):
        result.append(padded_text[i:i+width])

    return result

# Function to fetch and display news headlines on the LCD screen
def display_news():
    while True:
        # Fetch news headlines from the API
        url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=<Your_API_Key_Here>"
        response = requests.get(url)
        data = json.loads(response.text)

        # Extract headlines from the API response
        headlines = []
        for article in data["articles"]:
            headline = article["title"]
            headlines.append(headline)

        # Initialize the LCD screen
        lcd_init()

        # Loop through each headline and display it on the LCD screen
        for i in range(len(headlines)):
            # Create a marquee effect for the headline
            marquee_headline = marquee_text(headlines[i], LCD_WIDTH)

            # Display the marquee headline on the LCD screen
            for sub_headline in marquee_headline:
                lcd_string(sub_headline, (i % 4) + 1)
                time.sleep(0.6)  # Adjust the sleep duration to control the scrolling speed

            time.sleep(2)  # Add a sleep duration after displaying each headline

        # Clear the LCD screen and wait for 30 seconds before fetching news again
        lcd_byte(0x01, LCD_CMD)
        time.sleep(30)

# Start the news display
display_news()
