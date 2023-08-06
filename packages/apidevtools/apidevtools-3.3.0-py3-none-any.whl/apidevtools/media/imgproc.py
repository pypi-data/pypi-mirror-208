import io
import PIL.Image
from PIL import ImageDraw as _ImageDraw, ImageFont as _ImageFont
import numpy as _np


def convert(image: bytes | io.BytesIO | PIL.Image.Image) -> PIL.Image.Image:
    """
    Create PIL.Image.Image from bytes or io.BytesIO.
    Also accepts PIL.Image.Image to simplify usage in and Image classes.
    :param image:
    :return:
    """
    if not isinstance(image, PIL.Image.Image):
        if isinstance(image, Image):
            image = image.bytesio
        elif isinstance(image, bytes):
            image = io.BytesIO(image)
        return PIL.Image.open(image)
    return image


class Image:
    image: PIL.Image.Image
    text = 'N/S'

    def __init__(self, image: bytes | io.BytesIO | PIL.Image.Image, text: str = text):
        self.image = convert(image)
        self.text = text

    @property
    def bytes(self) -> bytes:
        return self.bytesio.getvalue()

    @property
    def bytesio(self) -> io.BytesIO:
        output = io.BytesIO()
        self.image.save(output, 'PNG')
        return output

    async def url(self) -> str | None:
        from . import telegraph

        return await telegraph.upload(self.bytesio)


def generate(
        text: str = Image.text, size: int = 512, fonttf=None,
        bg_color: tuple[int, int, int] = (0, 0, 0), font_color: tuple[int, int, int] = (255, 255, 255)
) -> Image:
    """
    Generate image from apidevtools.image.Image. Supposed to be used as for instance: user
    By default has "N/A" white text on the black background.
    :param text:
    :param size:
    :param fonttf:
    :param bg_color:
    :param font_color:
    :return:
    """
    if not fonttf:
        from os import path

        fonttf = path.join(path.dirname(__file__), 'ARIALNB.TTF')

    font = _ImageFont.truetype(font=fonttf, size=int(size * 0.6))
    img = PIL.Image.new(mode='RGB', size=(size, size), color=bg_color)
    draw = _ImageDraw.Draw(img)
    _, _, width, height = draw.textbbox((0, 0), text, font=font)
    draw.text(xy=((size - width) / 2, (size - height) / 3), text=text, font=font, fill=font_color)
    return Image(img, text)


def crop(image: bytes | io.BytesIO | PIL.Image.Image | Image) -> Image:
    """
    Crop any image to circle form.
    :param image:
    :return:
    """
    img = convert(image)
    size = min(img.size)
    alpha = PIL.Image.new('L', img.size, 0)
    _ImageDraw.Draw(alpha).pieslice(((0, 0), (size, size)), 0, 360, fill=255)
    img = PIL.Image.fromarray(_np.dstack((_np.array(img), _np.array(alpha))))
    img = img.crop((0, 0, size, size))
    return Image(img)


def default(text: str = Image.text) -> Image:
    """
    Quick way to create am image from some text.
    :param text:
    :return:
    """
    return crop(generate(text))
