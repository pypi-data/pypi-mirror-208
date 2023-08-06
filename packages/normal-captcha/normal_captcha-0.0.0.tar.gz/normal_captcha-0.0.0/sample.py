from nomal_captcha.main import NormalCaptcha

text = (
    NormalCaptcha(
        './<imageName>',
        'path\\to\\tesseract.exe')
    .process()
)
print(text)