from ivc_project.settings import GOOGLE_RECAPTCHA_SECRET_KEY
import requests


# gets request as parameter and returns true or false, true if it's valid and false if it's not
def is_recaptcha_valid(request):
    """ Begin reCAPTCHA validation """
    recaptcha_response = request.POST.get('g-recaptcha-response')
    data = {
        'secret': GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    request_data = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = request_data.json()
    return result['success']
