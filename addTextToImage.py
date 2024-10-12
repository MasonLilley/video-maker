from PIL import Image, ImageDraw, ImageFont
import textwrap

def addTextToTemplate(userString, titleString, outputPath="introImage.png",templatePath="resources/postTemplate.png"):
    templatePath = templatePath
    image = Image.open(templatePath)

    draw = ImageDraw.Draw(image)

    # Title Text #
    text = titleString
    fontSize = 40
    fontPath = "resources/roboto.ttf"
    font = ImageFont.truetype(fontPath, fontSize)
    text_x = 125
    text_y = 930

    # Top User Text #
    short_text = userString
    short_font_size = 30
    short_font = ImageFont.truetype(fontPath, short_font_size)
    short_text_x = 205
    short_text_y = 820

    wrapped_text = textwrap.fill(text, width=50)
    draw.text((text_x, text_y), wrapped_text, fill='black', font=font)
    draw.text((short_text_x, short_text_y), short_text, fill='black', font=short_font)

    output_path = "introImage.png"
    image.save(output_path)

    image.show()