from PIL import Image, ImageDraw, ImageFont
import textwrap

def addTextToTemplate(userString, titleString, outputPath="introImage.png",templatePath="resources/postTemplate.png"):
    templatePath = templatePath
    image = Image.open(templatePath)

    draw = ImageDraw.Draw(image)

    # Title Text #
    text = titleString
    fontSize = 35
    fontPath = "resources/roboto.ttf"
    font = ImageFont.truetype(fontPath, fontSize)
    text_x = 120
    text_y = 920

    # Top User Text #
    short_text = "TheRedditNarrator"
    short_font_size = 30
    short_font = ImageFont.truetype(fontPath, short_font_size)
    short_text_x = 230
    short_text_y = 825

    # Verified Favicon #
    verifiedImage = Image.open("resources/verified.png")
    verifiedImage = verifiedImage.resize((30,30))
    verified_x = 195
    verified_y = 828
    image.paste(verifiedImage, (verified_x, verified_y), verifiedImage)

    wrapped_text = textwrap.fill(text, width=50)
    draw.text((text_x, text_y), wrapped_text, fill='black', font=font)
    draw.text((short_text_x, short_text_y), short_text, fill='black', font=short_font)

    image.save(outputPath)

    image.show()

# addTextToTemplate("u/Puzzleheaded_Hour966", "Am I in the wrong for kicking my brother and his new wife out of my house after they tried to “redecorate” my dead daughter’s room while I was at work?")