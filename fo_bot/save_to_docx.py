import re
import io

from docx import Document

from fo_bot.settings import DOCX_TEMPLATE_FILENAME


def _docx_replace_regex(doc_obj, regex, replace):
    for p in doc_obj.paragraphs:
        if regex.search(p.text):
            inline = p.runs
            # Loop added to work with runs (strings with same style)
            for i in range(len(inline)):
                if regex.search(inline[i].text):
                    text = regex.sub(replace, inline[i].text)
                    inline[i].text = text


def save_to_docx(**kwargs):
    doc = Document(DOCX_TEMPLATE_FILENAME)

    for key, value in kwargs.items():
        _docx_replace_regex(doc, re.compile(key), value)

    output = io.BytesIO()
    doc.save(output)

    return output


if __name__ == '__main__':
    output = save_to_docx(info='''А: Б
В: Г Д''',
                  p1='10')

    with open('demo.docx', 'wb') as f:
        f.write(output.getvalue())
    output.close()
