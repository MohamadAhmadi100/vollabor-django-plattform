from io import BytesIO 
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  
import os

def html_to_pdf(template_src,context_dict,name):        
        template = get_template(template_src)
        html  = template.render(context_dict)
        result = BytesIO()
        path = 'media/virtualevent/contracts/'
        isdir = os.path.isdir(path)
        if isdir:
            pass
        else:
            os.mkdir(path)
        with open(f'{path}{name}.pdf', 'wb+') as output:
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), output) 
        if not pdf.err:
            return f'virtualevent/contracts/{name}.pdf'
        return None
          



