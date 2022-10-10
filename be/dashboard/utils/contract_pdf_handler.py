import os

from reportlab.pdfgen import canvas
from datetime import date
from textwrap import wrap

from dashboard.models import ProjectContractItem
from ivc_project.settings import MEDIA_ROOT, MEDIA_URL


def make_logo(pdf):
    pdf.drawInlineImage(f'{MEDIA_ROOT}/tecvico-logo.jpg', 210, 780, width=150, height=44)


def make_watermark(pdf):
    pdf.drawInlineImage(f'{MEDIA_ROOT}/tecvico-watermark.jpg', 0, 200, width=550, height=541)


def make_date(pdf):
    pdf.drawString(50, 770, "Date")
    pdf.drawString(450, 770, str(date.today()))


def make_contract_number(pdf):
    pdf.drawString(50, 750, 'Contract Number')
    pdf.drawString(450, 750, '1')


def make_title(pdf, document_title):
    pdf.drawCentredString(300, 710, document_title)


def make_parties(pdf):
    offset = 660

    # BETWEEN
    pdf.setFont('Helvetica', 14)
    pdf.drawString(50, offset, 'Between:')
    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(50, offset - 20, 'TECVICO Company')

    # AND
    pdf.setFont('Helvetica', 14)
    pdf.drawString(50, offset - 100, 'And:')
    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(50, offset - 120, '................................   Company')

    # OUR ADDRESS
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(310, offset, 'Address:')
    pdf.drawString(310, offset - 11, 'Vancouver, British Columbia, Canada V6L 1L7, CA')

    # OUR PHONE NUMBER
    pdf.drawString(310, offset - 40, 'Phone Number:')
    pdf.drawString(310, offset - 51, '+16047886129')

    # CLIENT ADDRESS
    pdf.drawString(310, offset - 100, 'Address:')
    pdf.drawString(310, offset - 111, '...............................................................................')

    # CLIENT PHONE NUMBER
    pdf.drawString(310, offset - 140, 'Phone Number:')
    pdf.drawString(310, offset - 151, '...............................................................................')


def make_general_text_on_second_page(pdf):
    offset = 760

    # FIRST PARAGRAPH
    t = pdf.beginText()
    t.setFont('Helvetica', 13)
    t.setTextOrigin(50, offset)
    t.textLines(wrap("The Client has agreed to Accept all the terms, subject to the following terms and conditions:",
                     90))
    pdf.drawText(t)

    # AGREEMENT
    t = pdf.beginText()
    t.setFont('Helvetica-Bold', 13)
    t.setTextOrigin(50, offset - 50)
    t.textLines(wrap("1.       Agreement",
                     90))
    pdf.drawText(t)

    t = pdf.beginText()
    t.setFont('Helvetica', 13)
    t.setTextOrigin(87, offset - 65)
    t.textLines(wrap('"Agreement" means an executive document between the client and TECVICO.',
                     80))
    pdf.drawText(t)

    # TECVICO REPRESENTATIVE
    t = pdf.beginText()
    t.setFont('Helvetica-Bold', 13)
    t.setTextOrigin(50, offset - 105)
    t.textLines(wrap("2.       TECVICO Representative",
                     90))
    pdf.drawText(t)

    t = pdf.beginText()
    t.setFont('Helvetica', 13)
    t.setTextOrigin(87, offset - 120)
    t.textLines(wrap('For the purposes of administration of this Agreement “TECVICO Representative” means: CTO of    '
                     'TECVICO “Mohammad Ghaemi”',
                     80))
    pdf.drawText(t)

    # SERVICES
    t = pdf.beginText()
    t.setFont('Helvetica-Bold', 13)
    t.setTextOrigin(50, offset - 175)
    t.textLines(wrap("3.       Services",
                     90))
    pdf.drawText(t)

    t = pdf.beginText()
    t.setFont('Helvetica', 13)
    t.setTextOrigin(87, offset - 200)
    t.textLines(wrap("3.1.    The TECVICO will carry out the services as following:",
                     90))
    pdf.drawText(t)

    return offset - 200


def make_services(pdf, our_services, offset):
    last_offset = offset - 25
    for index, service in enumerate(our_services, start=1):
        service_with_number = wrap(f"3.1.{index} {service.item}", 70)
        number_of_lines = len(service_with_number)
        if last_offset < 100 and number_of_lines > 3:
            make_new_page(pdf)
        t = pdf.beginText()
        t.setFont('Helvetica', 13)
        t.setTextOrigin(124, last_offset)

        t.textLines(service_with_number)
        pdf.drawText(t)

        last_offset -= number_of_lines * 20
        if last_offset < 50:
            last_offset = make_new_page(pdf)
    return last_offset


def make_new_page(pdf):
    pdf.showPage()
    make_logo(pdf)
    make_watermark(pdf)
    last_offset = 760
    return last_offset


def make_clients_obligations(pdf, clients_obligations, offset):
    last_offset = offset - 20
    if last_offset < 200:
        last_offset = make_new_page(pdf)

    # CLIENT'S OBLIGATIONS
    t = pdf.beginText()
    t.setFont('Helvetica-Bold', 13)
    t.setTextOrigin(50, last_offset)
    t.textLines(wrap("4.      Client’s obligations",
                     90))
    pdf.drawText(t)

    last_offset -= 20

    for index, obligation in enumerate(clients_obligations, start=1):
        service_with_number = wrap(f"4.{index} {obligation.item}", 70)
        number_of_lines = len(service_with_number)
        t = pdf.beginText()
        t.setFont('Helvetica', 13)
        t.setTextOrigin(87, last_offset)

        t.textLines(service_with_number)
        pdf.drawText(t)

        last_offset -= number_of_lines * 20
        if last_offset < 50 or (last_offset < 100 and number_of_lines > 3):
            make_new_page(pdf)
    return last_offset


def make_client_terms(pdf, client_terms, offset):
    last_offset = offset - 20
    if last_offset < 200:
        last_offset = make_new_page(pdf)

    # CLIENT TERMS
    t = pdf.beginText()
    t.setFont('Helvetica-Bold', 13)
    t.setTextOrigin(50, last_offset)
    t.textLines(wrap("5.      Client terms",
                     90))
    pdf.drawText(t)

    last_offset -= 20

    for index, term in enumerate(client_terms, start=1):
        service_with_number = wrap(f"5.{index} {term.item}", 70)
        number_of_lines = len(service_with_number)
        t = pdf.beginText()
        t.setFont('Helvetica', 13)
        t.setTextOrigin(87, last_offset)

        t.textLines(service_with_number)
        pdf.drawText(t)

        last_offset -= number_of_lines * 20
        if last_offset < 50 or (last_offset < 100 and number_of_lines > 3):
            make_new_page(pdf)
    return last_offset


def make_signature(pdf, offset):
    if offset < 10:
        offset = make_new_page(pdf)

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(50, offset, "Tecvico Signature")

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(400, offset, "Client Signature")


def locate_the_file_name(client_name):
    file_name = f'{MEDIA_ROOT}/contracts/contract_{client_name}.pdf'
    if os.path.exists(file_name):
        number = 2
        while True:
            file_name = f'{MEDIA_ROOT}/contracts/contract_{client_name}{number}.pdf'
            if not os.path.exists(file_name):
                break
            number += 1
    return file_name


def create_contract(client_name, project):
    file_name = locate_the_file_name(client_name)

    document_title = "Agreement of partnership services"
    pdf = canvas.Canvas(file_name)
    pdf.setTitle(document_title)

    make_logo(pdf)
    make_watermark(pdf)
    pdf.setFont('Helvetica', 12)
    make_date(pdf)
    make_contract_number(pdf)
    pdf.setFont('Helvetica-Bold', 18)
    make_title(pdf, document_title)
    make_parties(pdf)

    make_new_page(pdf)
    last_offset = make_general_text_on_second_page(pdf)

    our_services = ProjectContractItem.objects.filter(project=project, from_item="Tecvico", item_type='Optional', agree=True)

    last_offset = make_services(pdf, our_services, last_offset)
    clients_obligations = ProjectContractItem.objects.filter(project=project, from_item="Tecvico", item_type='Mandatory')

    last_offset = make_clients_obligations(pdf, clients_obligations, last_offset)
    client_terms = ProjectContractItem.objects.filter(project=project, from_item="Company", agree=True)

    last_offset = make_client_terms(pdf, client_terms, last_offset)
    make_signature(pdf, last_offset - 50)
    pdf.save()

    return True, file_name.replace(MEDIA_ROOT, "")
