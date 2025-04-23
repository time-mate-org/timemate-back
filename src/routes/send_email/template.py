def get_html_template(title, content, email_type): return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; margin-top: 20px;">
    <tr>
      <td align="center" style="background-color: #007bff; padding: 20px; color: #ffffff;">
        <h1 style="margin: 0; font-size: 20px;">{title}</h1>
      </td>
    </tr>
    <tr>
      <td style="padding: 20px;">
        <small style="font-size: 10px; margin: 10px 0;">Categoria: {email_type}</small>
        <p style="font-size: 16px; margin: 20px 0; padding: 3rem 0;">{content}</p>
      </td>
    </tr>
    <tr>
      <td align="center" style="padding: 5rem 0; background-color: #f4f4f4;">
        <p style="font-size: 14px; color: #007bff;">Timemate - seu app de agendamentos.</p>
      </td>
    </tr>
  </table>
</body>
</html>
"""
