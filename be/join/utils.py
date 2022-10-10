def convert_entered_to_given_email(entered_email):
    if '@gmail.com' in entered_email.lower():  # in case email is gmail, soroushmehraban and
        # soroush.mehraban should be the same
        gmail_username = entered_email.lower().split("@gmail.com")[0]
        gmail_username_sections = gmail_username.split(".")
        gmail_username = "".join(gmail_username_sections)
        given_email = f"{gmail_username}@gmail.com".lower()
    else:
        given_email = entered_email.lower()

    return given_email