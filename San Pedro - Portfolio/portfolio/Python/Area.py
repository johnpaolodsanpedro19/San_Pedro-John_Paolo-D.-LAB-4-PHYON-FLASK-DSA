import os
import re
import smtplib
import ssl
from email.message import EmailMessage

from flask import Blueprint, current_app, render_template, request, session
from .linked_list import SinglyLinkedList
from .stack import Stack, infix_to_postfix

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/profile')
def profile():
    return render_template('profile.html')

@bp.route('/works', methods=['GET', 'POST'])
def works():
    result = None
    input_string = ''
    error = None
    if request.method == 'POST':
        input_string = request.form.get('inputString', '')
        if input_string:
            result = input_string.upper()
        else:
            error = 'Enter some text to convert.'
    return render_template('touppercase.html', result=result, input_string=input_string, error=error)

@bp.route('/works/area/circle', methods=['GET', 'POST'])
def acircle():
    result = None
    radius = ''
    error = None
    if request.method == 'POST':
        radius = request.form.get('radius', '')
        try:
            radius_value = float(radius)
            if radius_value <= 0:
                error = 'Radius must be greater than zero.'
            else:
                result = 3.14159 * radius_value ** 2
        except ValueError:
            error = 'Enter a valid number for the radius.'
    return render_template('circle.html', result=result, radius=radius, error=error)

@bp.route('/works/area/triangle', methods=['GET', 'POST'])
def triangle():
    result = None
    base = ''
    height = ''
    error = None
    if request.method == 'POST':
        base = request.form.get('base', '')
        height = request.form.get('height', '')
        try:
            base_value = float(base)
            height_value = float(height)
            if base_value <= 0 or height_value <= 0:
                error = 'Base and height must be greater than zero.'
            else:
                result = base_value * height_value / 2
        except ValueError:
            error = 'Enter valid numbers for the base and height.'
    return render_template(
        'triangle.html',
        result=result,
        base=base,
        height=height,
        error=error,
    )

@bp.route('/works/linked-list', methods=['GET', 'POST'])
def linked_list():
    linked = SinglyLinkedList(session.get('linked_list_values', []))
    status = None
    status_type = None
    input_value = ''
    input_target = ''

    if request.method == 'POST':
        operation = request.form.get('operation', '')
        value = request.form.get('value', '').strip()
        target = request.form.get('target', '').strip()
        input_value = value
        input_target = target

        if operation in ('insert_beginning', 'insert_end', 'insert_after') and len(value) > 40:
            status = 'Values must be 40 characters or fewer.'
            status_type = 'error'
        elif operation in ('insert_beginning', 'insert_end') and not value:
            status = 'Enter a value to add to the list.'
            status_type = 'error'
        elif operation in ('insert_beginning', 'insert_end') and len(linked.to_list()) >= 10:
            status = 'The list is limited to 10 nodes.'
            status_type = 'error'
        elif operation == 'insert_beginning':
            linked.insert_at_beginning(value)
            status = f'Added “{value}” at the beginning.'
            status_type = 'success'
        elif operation == 'insert_end':
            linked.insert_at_end(value)
            status = f'Added “{value}” at the end.'
            status_type = 'success'
        elif operation == 'insert_after':
            if not target or not value:
                status = 'Enter both the existing node value and the new value.'
                status_type = 'error'
            elif len(target) > 40 or len(value) > 40:
                status = 'Values must be 40 characters or fewer.'
                status_type = 'error'
            elif len(linked.to_list()) >= 10:
                status = 'The list is limited to 10 nodes.'
                status_type = 'error'
            elif linked.insert_after(target, value) is None:
                status = f'Could not find “{target}” in the list.'
                status_type = 'error'
            else:
                status = f'Inserted “{value}” after “{target}”.'
                status_type = 'success'
        elif operation == 'search':
            if not target:
                status = 'Enter a target value to search for.'
                status_type = 'error'
            elif target in linked.to_list():
                status = f'Found “{target}” in the list.'
                status_type = 'success'
            else:
                status = f'Could not find “{target}” in the list.'
                status_type = 'error'
        elif operation == 'print':
            status = f'List: {" → ".join(linked.to_list()) if linked.to_list() else "head → None · tail → None"}'
            status_type = 'success'
        elif operation == 'clear':
            linked = SinglyLinkedList()
            input_value = ''
            input_target = ''
            status = 'The list is empty. head and tail are None.'
            status_type = 'success'
        elif operation == 'remove_beginning':
            removed = linked.remove_beginning()
            if removed is None:
                status = 'The list is empty; there is no first node to remove.'
                status_type = 'error'
            else:
                status = f'Removed “{removed}” from the beginning.'
                status_type = 'success'
        elif operation == 'remove_end':
            removed = linked.remove_at_end()
            if removed is None:
                status = 'The list is empty; there is no last node to remove.'
                status_type = 'error'
            else:
                status = f'Removed “{removed}” from the end.'
                status_type = 'success'
        elif operation == 'remove_value':
            if not value:
                status = 'Enter the value of the node to remove.'
                status_type = 'error'
            else:
                removed = linked.remove_at(value)
                if removed is None:
                    status = f'Could not find “{value}” in the list.'
                    status_type = 'error'
                else:
                    status = f'Removed “{removed}” from the list.'
                    status_type = 'success'
        else:
            status = 'Choose a valid linked-list operation.'
            status_type = 'error'

        session['linked_list_values'] = linked.to_list()

    return render_template(
        'linked_list.html',
        values=linked.to_list(),
        status=status,
        status_type=status_type,
        input_value=input_value,
        input_target=input_target,
    )

@bp.route('/works/stack', methods=['GET', 'POST'])
def stack():
    stack_data = Stack(session.get('stack_values', []))
    status = None
    status_type = None
    top_value = stack_data.peek()
    expression = ''
    stack_input = ''
    postfix = None

    if request.method == 'POST':
        operation = request.form.get('operation', '')
        value = request.form.get('value', '').strip()
        stack_input = value

        if operation == 'convert':
            expression = request.form.get('expression', '').strip()
            if len(expression) > 200:
                status = 'Expressions must be 200 characters or fewer.'
                status_type = 'error'
            else:
                try:
                    postfix, _ = infix_to_postfix(expression)
                except ValueError as error:
                    status = str(error)
                    status_type = 'error'
                else:
                    status = 'Expression converted to postfix.'
                    status_type = 'success'
        elif operation == 'push':
            if not value:
                status = 'Enter a value to push onto the stack.'
                status_type = 'error'
            elif len(value) > 40:
                status = 'Values must be 40 characters or fewer.'
                status_type = 'error'
            elif len(stack_data.to_list()) >= 10:
                status = 'The stack is limited to 10 items.'
                status_type = 'error'
            else:
                stack_data.push(value)
                stack_input = ''
                status = f'Pushed “{value}” onto the stack.'
                status_type = 'success'
        elif operation == 'pop':
            popped = stack_data.pop()
            if popped is None:
                status = 'The stack is empty; there is nothing to pop.'
                status_type = 'error'
            else:
                status = f'Popped “{popped}” from the stack.'
                status_type = 'success'
        elif operation == 'clear':
            stack_data = Stack()
            stack_input = ''
            status = 'Stack is empty. top is None.'
            status_type = 'success'
        elif operation == 'peek':
            top_value = stack_data.peek()
            if top_value is None:
                status = 'The stack is empty; there is no top item.'
                status_type = 'error'
            else:
                status = f'The top item is “{top_value}”.'
                status_type = 'success'
        elif operation == 'print':
            values = stack_data.to_list()
            status = f'Stack: {" → ".join(values) if values else "top → None"}'
            status_type = 'success'
        else:
            status = 'Choose a valid stack operation.'
            status_type = 'error'

        session['stack_values'] = stack_data.to_list()
        top_value = stack_data.peek()

    return render_template(
        'stack.html',
        values=stack_data.to_list(),
        top_value=top_value,
        status=status,
        status_type=status_type,
        expression=expression,
        stack_input=stack_input,
        postfix=postfix,
    )

# @bp.route('/areaOfcirle', methods=['GET', 'POST'])
# def areaOfcirle():
#     result = None
#     name=request.get('name','')
#     print(name)
#     if request.method == 'POST':
#         input_string = request.form.get('inputradius', '')
#         result = int(input_string) * int(input_string) * 3.14
#     return render_template('areaCircle.html', result=result)

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    status = None
    status_type = None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        sender_email = request.form.get('sender_email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not all((name, sender_email, subject, message)):
            status = 'Please fill in every field.'
            status_type = 'error'
        elif len(name) > 120 or len(sender_email) > 254 or len(subject) > 200 or len(message) > 10000:
            status = 'One or more fields are too long. Please shorten your message and try again.'
            status_type = 'error'
        elif not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', sender_email):
            status = 'Please enter a valid email address so I can reply.'
            status_type = 'error'
        elif '\r' in subject or '\n' in subject:
            status = 'Please enter a subject on a single line.'
            status_type = 'error'
        else:
            smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
            smtp_username = os.environ.get('SMTP_USERNAME')
            smtp_password = os.environ.get('SMTP_PASSWORD')
            smtp_port_value = os.environ.get('SMTP_PORT', '587')

            if not all((smtp_username, smtp_password)):
                status = 'This Flask server does not have email settings. Stop it, then start the app with .\\run_with_email.ps1 from the project folder.'
                status_type = 'error'
                current_app.logger.error('Contact email unavailable: SMTP_USERNAME or SMTP_PASSWORD is not configured.')
            else:
                try:
                    smtp_port = int(smtp_port_value)
                except ValueError:
                    current_app.logger.error('Contact email unavailable: SMTP_PORT must be an integer.')
                    status = 'Your message could not be sent right now. Please try again later.'
                    status_type = 'error'
                else:
                    if not 1 <= smtp_port <= 65535:
                        current_app.logger.error('Contact email unavailable: SMTP_PORT is outside the valid range.')
                        status = 'Your message could not be sent right now. Please try again later.'
                        status_type = 'error'
                    else:
                        email = EmailMessage()
                        email['Subject'] = subject
                        email['From'] = smtp_username
                        email['To'] = 'johnpaolosanpedro19@gmail.com'
                        email['Reply-To'] = sender_email
                        email.set_content(f'From: {name}\nReply email: {sender_email}\n\n{message}')

                        try:
                            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                                server.starttls(context=ssl.create_default_context())
                                server.login(smtp_username, smtp_password)
                                server.send_message(email)
                        except (OSError, smtplib.SMTPException):
                            current_app.logger.exception('Failed to send contact form email.')
                            status = 'Your message could not be sent right now. Please try again later.'
                            status_type = 'error'
                        else:
                            status = 'Thanks! Your message was sent successfully.'
                            status_type = 'success'

    return render_template('contact.html', status=status, status_type=status_type)
