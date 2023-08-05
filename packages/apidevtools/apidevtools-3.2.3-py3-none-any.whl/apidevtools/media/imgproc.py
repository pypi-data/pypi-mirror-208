import io
import PIL.Image
from PIL import ImageDraw as _ImageDraw, ImageFont as _ImageFont
import numpy as _np
import pathlib as _pathlib
import os as _os


# make the package entirely async
# try to replace numpy with pure python
# fix fonts


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

#
# class Font:
#     @staticmethod
#     def system() -> list[str]:
#         """
#         Get a list of system fonts
#         :return:
#         """
#         if _os.name != 'nt':
#             raise OSError('System fonts are available only for Windows. Please wait for an update.')
#         paths = _pathlib.PurePath(_pathlib.Path.home().drive, _os.sep, 'windows', 'fonts')
#         return [str(path.absolute()) for path in list(_pathlib.Path(paths).glob('*.ttf'))]
#
#     @staticmethod
#     def font(ttf_name: str) -> str:
#         """
#         Find a system font by its name, if not found returns ARIALNB by default
#         :param ttf_name:
#         :return:
#         """
#         # try the similarity approach https://www.geeksforgeeks.org/python-word-similarity-using-spacy/
#         ttf = list(filter(lambda filepath: _os.path.basename(filepath).split('.')[0] == ttf_name, Font.system()))
#         return ttf[0] if len(ttf) else Font.font('ARIALNB')


def generate(
        # text: str = Image.text, size: int = 512, fonttf=Font.font('ARIALNB'),
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
        from site import getsitepackages

        fonttf = _os.path.join(getsitepackages()[1], 'apidevtools', 'media', 'ARIALNB.TTF')

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
