from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={},option_response=True):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err and option_response:#for pdf 
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    elif not pdf.err and not option_response:# for attachment in email
        return result.getvalue()
    return None