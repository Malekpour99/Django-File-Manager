{% extends "mail_templated/base.tpl" %}

{% block subject %}
Account Activation
{% endblock %}

{% block html %}
Please click on the provided link to activate your account:
<a href="{{ protocol }}://{{ domain }}{% url "accounts:activation" token=token %}">Activation Link</a>
<br />
If you didn't request an activation link just ignore this message.
and if you recieved this message again, make sure to contact us.
{% endblock %}
