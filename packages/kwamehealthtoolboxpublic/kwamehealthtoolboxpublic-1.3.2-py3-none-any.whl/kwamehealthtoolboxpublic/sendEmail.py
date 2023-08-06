import smtplib
import email.utils
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email import charset
import logging

log = logging.getLogger()
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.INFO)

HTML_HEADER = """
    <link href="https://fonts.googleapis.com/css?family=Dongle:400,500,600,700,800" rel="stylesheet">
    <style>
      /* -------------------------------------
          GLOBAL RESETS
      ------------------------------------- */

      /*All the styling goes here*/

      img {
        border: none;
        -ms-interpolation-mode: bicubic;
        max-width: 100%; 
      }

      body {
        background-color: #f6f6f6;
        font-family: sans-serif;
        -webkit-font-smoothing: antialiased;
        font-size: 14px;
        line-height: 1.4;
        margin: 0;
        padding: 0;
        -ms-text-size-adjust: 100%;
        -webkit-text-size-adjust: 100%; 
      }

      table {
        border-collapse: separate;
        mso-table-lspace: 0pt;
        mso-table-rspace: 0pt;
        width: 100%; }
        table td {
          font-family: sans-serif;
          font-size: 14px;
          vertical-align: top; 
      }

      /* -------------------------------------
          BODY & CONTAINER
      ------------------------------------- */

      .body {
        background-color: #f6f6f6;
        width: 100%; 
      }

      /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
      .container {
        display: block;
        margin: 0 auto !important;
        /* makes it centered */
        max-width: 580px;
        padding: 10px;
        width: 580px; 
      }

      .content {
        box-sizing: border-box;
        display: block;
        margin: 0 auto;
        max-width: 580px;
        padding: 10px; 
      }

      /* -------------------------------------
          HEADER, FOOTER, MAIN
      ------------------------------------- */
      .main {
        background: #ffffff;
        border-radius: 3px;
        width: 100%; 
      }

      .main-green {
        background: #66ff00;
        border-radius: 3px;
        width: 100%; 
      }

      .main-red {
        background: red;
        border-radius: 3px;
        width: 100%; 
      }

      .main-orange {
        background: orange;
        border-radius: 3px;
        width: 100%; 
      }

      .wrapper {
        box-sizing: border-box;
        padding: 20px; 
      }

      .content-block {
        padding-bottom: 10px;
        padding-top: 10px;
      }

      .footer {
        clear: both;
        margin-top: 10px;
        text-align: center;
        width: 100%; 
      }
        .footer td,
        .footer p,
        .footer span,
        .footer a {
          color: #999999;
          font-size: 12px;
          text-align: center; 
      }

      /* -------------------------------------
          TYPOGRAPHY
      ------------------------------------- */
      h1,
      h2,
      h3,
      h4 {
        color: #000000;
        font-family: sans-serif;
        font-weight: 400;
        line-height: 1.4;
        margin: 0;
        margin-bottom: 30px; 
      }

      h1 {
        font-size: 35px;
        font-weight: 300;
        text-align: center;
        text-transform: capitalize; 
      }

      p,
      ul,
      ol {
        font-family: sans-serif;
        font-size: 14px;
        font-weight: normal;
        margin: 0;
        margin-bottom: 15px; 
      }
        p li,
        ul li,
        ol li {
          list-style-position: inside;
          margin-left: 5px; 
      }

      a {
        color: #3498db;
        text-decoration: underline; 
      }

      /* -------------------------------------
          BUTTONS
      ------------------------------------- */
      .btn {
        box-sizing: border-box;
        width: 100%; }
        .btn > tbody > tr > td {
          padding-bottom: 15px; }
        .btn table {
          width: auto; 
      }
        .btn table td {
          background-color: #ffffff;
          border-radius: 5px;
          text-align: center; 
      }
        .btn a {
          background-color: #ffffff;
          border: solid 1px #3498db;
          border-radius: 5px;
          box-sizing: border-box;
          color: #3498db;
          cursor: pointer;
          display: inline-block;
          font-size: 14px;
          font-weight: bold;
          margin: 0;
          padding: 12px 25px;
          text-decoration: none;
          text-transform: capitalize; 
      }

      .btn-primary table td {
        background-color: #3498db; 
      }

      .btn-primary a {
        background-color: #3498db;
        border-color: #3498db;
        color: #ffffff; 
      }

      .btn-success table td {
        background-color: #66ff00; 
      }

      .btn-success a {
        background-color: #66ff00;
        border-color: #66ff00;
        color: #ffffff; 
      }

      /* -------------------------------------
          OTHER STYLES THAT MIGHT BE USEFUL
      ------------------------------------- */
      .last {
        margin-bottom: 0; 
      }

      .first {
        margin-top: 0; 
      }

      .align-center {
        text-align: center; 
      }

      .align-right {
        text-align: right; 
      }

      .align-left {
        text-align: left; 
      }

      .clear {
        clear: both; 
      }

      .mt0 {
        margin-top: 0; 
      }

      .mb0 {
        margin-bottom: 0; 
      }

      .preheader {
        color: transparent;
        display: none;
        height: 0;
        max-height: 0;
        max-width: 0;
        opacity: 0;
        overflow: hidden;
        mso-hide: all;
        visibility: hidden;
        width: 0; 
      }

      .powered-by a {
        text-decoration: none; 
      }

      hr {
        border: 0;
        border-bottom: 1px solid #f6f6f6;
        margin: 20px 0; 
      }

      /* -------------------------------------
          RESPONSIVE AND MOBILE FRIENDLY STYLES
      ------------------------------------- */
      @media only screen and (max-width: 620px) {
        table[class=body] h1 {
          font-size: 28px !important;
          margin-bottom: 10px !important; 
        }
        table[class=body] p,
        table[class=body] ul,
        table[class=body] ol,
        table[class=body] td,
        table[class=body] span,
        table[class=body] a {
          font-size: 16px !important; 
        }
        table[class=body] .wrapper,
        table[class=body] .article {
          padding: 10px !important; 
        }
        table[class=body] .content {
          padding: 0 !important; 
        }
        table[class=body] .container {
          padding: 0 !important;
          width: 100% !important; 
        }
        table[class=body] .main {
          border-left-width: 0 !important;
          border-radius: 0 !important;
          border-right-width: 0 !important; 
        }
        table[class=body] .btn table {
          width: 100% !important; 
        }
        table[class=body] .btn a {
          width: 100% !important; 
        }
        table[class=body] .img-responsive {
          height: auto !important;
          max-width: 100% !important;
          width: auto !important; 
        }
      }

      /* -------------------------------------
          PRESERVE THESE STYLES IN THE HEAD
      ------------------------------------- */
      @media all {
        .ExternalClass {
          width: 100%; 
        }
        .ExternalClass,
        .ExternalClass p,
        .ExternalClass span,
        .ExternalClass font,
        .ExternalClass td,
        .ExternalClass div {
          line-height: 100%; 
        }
        .apple-link a {
          color: inherit !important;
          font-family: inherit !important;
          font-size: inherit !important;
          font-weight: inherit !important;
          line-height: inherit !important;
          text-decoration: none !important; 
        }
        .btn-primary table td:hover {
          background-color: #34495e !important; 
        }
        .btn-primary a:hover {
          background-color: #34495e !important;
          border-color: #34495e !important; 
        } 
        .btn-success table td:hover {
          background-color: #008000 !important; 
        }
        .btn-success a:hover {
          background-color: #008000 !important;
          border-color: #008000 !important; 
        }         
      }
  h1,h2,h3,h4,h5,h6{
    font-family: "Dongle", sans-serif;
    color: #000000;
    margin-top: 0;
  }

  body{
    font-family: "Dongle", sans-serif;
    font-weight: 400;
    font-size: 40px;
  }

  .big-words {
    color: #4d4d4d;
  }
    </style>
  </head>"""

def sendCustomEmail(emailType, subject, data, email, ccEmails, config):
    website_url = config.websiteURL
    support_email = config.supportEmail
    company_name = config.companyName
    fromName = config.fromName
    service_name = fromName
    service_url = config.serviceURL
    company_address = config.address
    company_logo_url = config.companyLogoURL
    company_banner_url = config.companyBannerURL

    EMAIL_FROM = config.emailFrom
    EMAIL_TO = email
    password = config.password
    doNotReplyEmail = config.doNotReplyEmail

    if emailType == "NOTIFICATION":
        subject = service_name+" Notification"
        subjectMain = subject
        EMAIL_BODY = data
        EMAIL_BODY += """<br><br>Contact us at """+str(support_email)+""" for any assistance</p>"""

    elif emailType == "ERROR_NOTIFICATION":
        subject = """<div style="color:red;">"""+service_name+""" Error Notification</div>"""
        subjectMain = service_name+" Error Notification"
        EMAIL_BODY = """<div style="color:red;">"""+data+"""</div>"""
        EMAIL_BODY += """<br><br>Contact us at """+str(support_email)+""" for any assistance</p>"""

    elif emailType == "NOTIFICATION_PATIENT_ADDED":
        subjectMain = subject
        EMAIL_BODY = data
        EMAIL_BODY += """<br><br>Contact us at """+str(support_email)+""" for any assistance</p>"""

    elif emailType == "LETTER":
        subject = service_name+" "+data[0]
        subjectMain = subject
        EMAIL_BODY = data[1]
        EMAIL_BODY += """<br><br>Contact us at """+str(support_email)+""" for any assistance</p>"""

    elif emailType == "referralLetter":
        subject = service_name+" Letter (Referrer): "+data[0]
        subjectMain = subject
        EMAIL_BODY = data[1]
        EMAIL_BODY += """<br><br>Contact us at """+str(support_email)+""" for any assistance</p>"""

    elif emailType == "ACCOUNT-ADDED":
        subject = service_name+": Account Added"
        subjectMain = subject
        EMAIL_BODY = """
            <p>Welcome """ + str(data["firstName"]) + """. You have been added to the """+str(service_name)+""" Dashboard</strong></p>
            <p>Please click the button below to activate your account</p>
            <p>Your login credentials to use after activation:</p>
            <p><strong>Username:</strong> """ + str(data["username"]) + """</p>
            <p><strong>Password:</strong> """ + str(data["password"]) + """</p>
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="btn btn-primary">
                <tbody>
                    <tr>
                        <td align="center">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                <tbody>
                                    <tr>
                                        <td>
                                            <a href=\"""" + str(service_url) + """/activation/"""+str(data["active"])+"""/"""+str(EMAIL_TO)+"""\" target="_blank">Activate now
                                            </a>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>
            <p>If you did not create an account you can safely ignore this email or contact us at """+str(support_email)+"""</p>
        """
        EMAIL_BODY += """<br><br>Contact us at """+str(support_email)+""" for any assistance</p>"""

    else:
        first_name = data[0]
        active = data[1]
        subject = "Welcome "+str(first_name)+"...Start Your First Campaign with MusaEMR!"
        subjectMain = subject
        EMAIL_BODY = """
            <p>Welcome """ + str(first_name) + """</strong></p>
            <p>Please click the button below to login to your account</p>
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="btn btn-primary">
                <tbody>
                    <tr>
                        <td align="center">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                <tbody>
                                    <tr>
                                        <td>
                                            <a href=\"""" + str(service_url) + """/activation/"""+str(active)+"""/"""+str(EMAIL_TO)+"""\" target="_blank">Activate now
                                            </a>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>
            <p>If you did not create an account you can safely ignore this email or contact us at """+str(support_email)+"""</p>
        """

    EMAIL_CONTENT = """
    <!doctype html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>""" + str(service_name) + """</title>
        """ + str(HTML_HEADER) + """
    <body class="">
        <!--<span class="preheader">""" + str(subject) + """</span>-->
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
                <tr>
                    <td>&nbsp;</td>

                    <td class="container">
                        <div class="content">

                            <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                <tbody>
                                    <tr>
                                        <td align="center">
                                            <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                                <tbody>
                                                    <tr>
                                                        <td align="center"> <img src=\""""+str(company_logo_url)+"""\" width="15%"></td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                            
                            <table role="presentation" style="border-radius: 3px;">
                                <!-- START MAIN CONTENT AREA -->
                                <tr>
                                    <td class="wrapper" style="border-radius: 3px;">
                                        <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                            <tr align="center">
                                                <td>
                                                    <h1 style="color: #0c2c44"><strong>""" + str(subject) + """</strong></h1>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            <!-- START CENTERED WHITE CONTAINER -->
                            <table role="presentation" class="main">
                            <!-- START MAIN CONTENT AREA -->

                                <tr>
                                    <td class="wrapper">
                                        <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td>
                                                    """ + str(EMAIL_BODY) + """
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>

                                <!-- END MAIN CONTENT AREA -->
                            </table>
                            <!-- END CENTERED WHITE CONTAINER -->

                            <!-- START FOOTER -->
                            <div class="footer">
                                <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="background-color: #0c2c44;color: white">
                                    <tr>
                                        <td class="content-block powered-by" style="background-color: #0c2c44;color: white">
                                            <a href=\"""" + str(website_url) + """\" style="color: white">""" + str(company_name) + """</a>
                                            """+company_address+"""
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            <!-- END FOOTER -->

                        </div>
                    </td>
                    <td>&nbsp;</td>
                </tr>
            </table>
    </body>
    </html>
    """
    msg_html_content = MIMEText(EMAIL_CONTENT, "html", "utf-8")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = Header(subjectMain, "utf-8").encode()
    msg["From"] = str(fromName+" "+doNotReplyEmail) #this can change name from e.g. do-not-reply
    msg["To"] = EMAIL_TO
    msg['CC'] = ",".join(ccEmails)
    msg.attach(msg_html_content)

    if emailType == "LETTER" or emailType == "referralLetter":
        fileBytes = data[2]
        part = MIMEApplication(
            fileBytes,
            Name=data[3]
        )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % data[3]
        msg.attach(part)

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    server.login(EMAIL_FROM, password)
    server.sendmail(EMAIL_FROM, [EMAIL_TO]+ccEmails, msg.as_string())
    server.quit()
    return "OK"
