{% extends "mail_templated/base.tpl" %}

{% block subject %}
Account Reset Password
{% endblock %}

{% block html %}
You are recieving the following link since you have requested for a reset password link.
<br />
Please click on the provided link to reset your account's password:
<a href="{{ protocol }}://{{ domain }}{% url "accounts:reset-password-validate" token=token %}">Reset Password Link</a>
<br />
If you didn't request a reset password link just ignore this message.
and if you recieved this message again, make sure to contact us.
{% endblock %}
