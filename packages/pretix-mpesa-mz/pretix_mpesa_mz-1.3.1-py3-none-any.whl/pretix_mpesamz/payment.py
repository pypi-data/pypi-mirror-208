import json
from pprint import pprint
from collections import OrderedDict

from i18nfield.fields import I18nFormField, I18nTextarea
from i18nfield.strings import LazyI18nString

from pretix.base.models import OrderPayment, OrderRefund
from pretix.base.payment import BasePaymentProvider, PaymentException
from pretix.base.templatetags.rich_text import rich_text
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from django import forms

from random import randint
from pretix_mpesamz.mpesa_api import execute_mpesa_c2b
from pretix_mpesamz.mpesa_api import execute_mpesa_reversal


class MpesaPayment(BasePaymentProvider):
    identifier = 'mpesa'

    ########################################################
    #                   General Settings
    ########################################################
    @property
    def verbose_name(self):
        return str(self.settings.get('method_name', as_type=LazyI18nString) or _('M-Pesa'))

    @property
    def confirm_button_name(self):
        return _('Pagar via M-Pesa')

    @property
    def priority(self):
        return 100

    ########################################################
    #                Control Panel Settings
    ########################################################
    @property
    def information_text(self):
        return rich_text(self.settings.get('information_text', as_type=LazyI18nString))

    @property
    def payment_pending_text(self):
        return rich_text(self.settings.get('payment_pending_text', as_type=LazyI18nString))

    @property
    def payment_completed_text(self):
        return rich_text(self.settings.get('payment_completed_text', as_type=LazyI18nString))

    @property
    def settings_form_fields(self):
        service_provider_code_field = forms.CharField(
            label=_('Código de Provedor de Serviço M-Pesa'),
            help_text=_('Identificador da entidade fornecido pelo M-Pesa')
        )

        api_url_field = forms.CharField(
            label=_('API URL'),
            help_text=_('API URL fornecido pelo M-Pesa')
        )

        api_key_field = forms.CharField(
            label=_('API Key'),
            help_text=_('API Key fornecido pelo M-Pesa')
        )

        public_key_field = forms.CharField(
            label=_('Public Key'),
            help_text=_('Public Key fornecido pelo M-Pesa')
        )

        info_field = I18nFormField(
            label=_('Payment information text'),
            help_text=_('Shown to the user when selecting a payment method.'),
            widget=I18nTextarea,
        )
        pending_field = I18nFormField(
            label=_('Payment pending text'),
            help_text=_(
                'Shown to the user when viewing a pending payment order.'),
            widget=I18nTextarea,
        )
        completed_field = I18nFormField(
            label=_('Payment completed text'),
            help_text=_(
                'Shown to the user when viewing an order with completed payment.'),
            widget=I18nTextarea,
        )

        settingsList = [
            ('service_provider_code', service_provider_code_field),
            ('api_url', api_url_field),
            ('api_key', api_key_field),
            ('public_key', public_key_field),
            ('information_text', info_field),
            ('payment_pending_text', pending_field),
            ('payment_completed_text', completed_field)
        ]

        return OrderedDict(list(super().settings_form_fields.items()) + settingsList)

    ########################################################
    #               Checkout process settings
    ########################################################
    def payment_is_valid_session(self, request):
        return all([
            request.session.get('payment_%s_msisdn' %
                                self.identifier, '') != ''
        ])

    def order_change_allowed(self, order):
        return True

    ########################################################
    #                   General Settings
    ########################################################

    @property
    def payment_form_fields(self):
        # Validate: ensure only valid numbers can be entered
        msisdn_field = ('msisdn',
                        forms.IntegerField(
                            label='Número (+258):',
                            required=True,
                            min_value=840000000,
                            max_value=859999999,
                            error_messages={
                                'invalid': 'Por favor, introduza um número 84 ou 85 válido'}
                        ))
        return OrderedDict([
            msisdn_field,
        ])

    def payment_form_render(self, request):

        form = self.payment_form(request)
        template = get_template('pretix_mpesamz/checkout_payment_form.html')
        ctx = {
            'request': request,
            'form': form,
            'information_text': self.information_text,
        }
        return template.render(ctx)

    def checkout_confirm_render(self, request):
        template = get_template('pretix_mpesamz/order.html')
        ctx = {
            'information_text': self.information_text,
            'msisdn': request.session.get('payment_%s_msisdn' % self.identifier)
        }
        return template.render(ctx)

    def execute_payment(self, request, payment):
        msisdn = request.session.get('payment_%s_msisdn' % self.identifier, '')

        try:
            config = {
                'api_url': self.settings.get('api_url'),
                'api_key': self.settings.get('api_key'),
                'public_key': self.settings.get('public_key')
            }

            payment_data = {
                'msisdn': "258" + str(msisdn),
                'reference': payment.order.event.slug.replace('-', ''),
                'third_party_reference': payment.order.code,
                'amount': str(int(float(payment.amount))),
                'service_provider_code': self.settings.get('service_provider_code')
            }

            result = execute_mpesa_c2b(config, payment_data)
            pprint(result)

            if result['output_ResponseCode'] == 'INS-0':
                success_payload = json.dumps({
                    'success': True,
                    'code': result['output_ResponseCode'],
                    'msisdn': msisdn,
                    'conversation': result['output_ConversationID'],
                    'description': result['output_ResponseDesc'],
                    'transaction': result['output_TransactionID']
                })
                # Displayed in control panel but not on API order response
                payment.info = success_payload

                payment.save(update_fields=['info'])
                payment.confirm()
            else:
                error_payload = json.dumps({
                    'success': False,
                    'code': result['output_ResponseCode'],
                    'msisdn': msisdn,
                    'conversation': result['output_ConversationID'],
                    'description': result['output_ResponseDesc'],
                    'transaction': result['output_TransactionID']
                })

                # Displayed in control panel but not on API order response
                payment.info = error_payload

                payment.save(update_fields=['info'])
                payment.fail()

            return
        except Exception as e:
            print(repr(e))

    def payment_prepare(self, request, payment):
        msisdn = request.session.get('payment_%s_msisdn' % self.identifier, '')

        try:
            config = {
                'api_key': self.settings.get('api_key'),
                'public_key': self.settings.get('public_key')
            }

            payment_data = {
                'msisdn': "258" + str(msisdn),
                'reference': 'TKT' + str(randint(0, 10000)),
                'third_party_reference': payment.order.code + str(randint(1, 10)),
                'amount': str(int(float(payment.amount))),
                'service_provider_code': self.settings.get('service_provider_code')
            }

            result = execute_mpesa_c2b(config, payment_data)
            # pprint(result)

            if result['output_ResponseCode'] == 'INS-0':
                success_payload = json.dumps({
                    'success': True,
                    'code': result['output_ResponseCode'],
                    'msisdn': msisdn,
                    'conversation': result['output_ConversationID'],
                    'description': result['output_ResponseDesc'],
                    'transaction': result['output_TransactionID']
                })
                # Displayed in control panel but not on API order response
                payment.info = success_payload

                payment.save(update_fields=['info'])
                payment.confirm()
            else:
                error_payload = json.dumps({
                    'success': False,
                    'code': result['output_ResponseCode'],
                    'msisdn': msisdn,
                    'conversation': result['output_ConversationID'],
                    'description': result['output_ResponseDesc'],
                    'transaction': result['output_TransactionID']
                })

                # Displayed in control panel but not on API order response
                payment.info = error_payload

                payment.save(update_fields=['info'])
                payment.fail()

            return
        except Exception as e:
            print(repr(e))

    def payment_pending_render(self, request, payment) -> str:
        template = get_template('pretix_mpesamz/payment_pending.html')
        if payment.info is not None and 'conversation' in payment.info:
            payment_info = json.loads(payment.info)
        else:
            return _("No payment information available.")

        if payment_info['code'] == "INS-6":
            reason = "PIN incorreto"
        elif payment_info['code'] == "INS-9":
            reason = "demora na comunicação entre a aplicação e o M-Pesa"
        elif payment_info['code'] == "INS-10":
            reason = "transação duplicada"
        else:
            reason = payment_info['description']

        ctx = {
            'reason': reason,
            'msisdn': request.session.get('payment_%s_msisdn' % self.identifier, '')
        }
        return template.render(ctx)

    def order_completed_render(self, request, order) -> str:
        template = get_template('pretix_mpesamz/order.html')
        if order.payment_info:
            payment_info = json.loads(order.payment_info)
        else:
            return _("No payment information available.")
        ctx = {
            'information_text': self.payment_completed_text,
            'msisdn': self.msisdn
        }
        return template.render(ctx)

    ########################################################
    #                 Refund payment for Order
    ########################################################
    def payment_refund_supported(self, payment: OrderPayment):
        return True

    def payment_partial_refund_supported(self, payment: OrderPayment):
        return False

    def execute_refund(self, refund: OrderRefund):
        try:
            # pprint(vars(refund.payment))
            payment_info = json.loads(refund.payment.info)
            config = {
                'api_url': self.settings.get('api_url'),
                'api_key': self.settings.get('api_key'),
                'public_key': self.settings.get('public_key')
            }

            payment_data = {
                'transaction': payment_info['transaction'],
                'third_party_reference': refund.order.code,
                'amount': str(refund.amount),
                'service_provider_code': self.settings.get('service_provider_code')
            }

            result = execute_mpesa_reversal(config, payment_data)

            pprint(result)

            if result['output_ResponseCode'] == 'INS-0':
                success_payload = json.dumps({
                    'success': True,
                    'code': result['output_ResponseCode'],
                    'conversation': result['output_ConversationID'],
                    'description': result['output_ResponseDesc'],
                    'transaction': result['output_TransactionID']
                })
                # Displayed in control panel but not on API order response
                refund.payment.info = success_payload
                refund.info = success_payload
                refund.done()
            else:
                error_payload = json.dumps({
                    'success': False,
                    'code': result['output_ResponseCode'],
                    'conversation': result['output_ConversationID'],
                    'description': result['output_ResponseDesc'],
                    'transaction': result['output_TransactionID']
                })
                refund.payment.info = error_payload
                refund.info = error_payload

                raise PaymentException(error_payload['description'])

        except Exception as e:
            print(repr(e))
            raise PaymentException('M-Pesa refund could not be completed')

    def refund_control_render(self, request, refund) -> str:
        template = get_template('pretix_mpesamz/refund_control.html')

        if refund.info is not None and 'transaction' in refund.info:
            refund_info = json.loads(refund.info)
        else:
            return _("Devolução via M-Pesa sem sucesso.")

        ctx = {
            'description': refund_info['description'],
            'code': refund_info['code'],
            'transaction': refund_info['transaction']
        }
        return template.render(ctx)

    ########################################################
    #                   Called to display Order
    #                   info in Control Panel
    ########################################################

    def payment_control_render(self, request, payment) -> str:
        template = get_template('pretix_mpesamz/control.html')

        if payment.info is not None and 'conversation' in payment.info:
            payment_info = json.loads(payment.info)
        else:
            return _("Pagamento via M-Pesa sem sucesso.")

        ctx = {
            'conversationID': payment_info['conversation'],
            'msisdn': payment_info['msisdn'],
            'description': payment_info['description'],
            'code': payment_info['code'],
            'transaction': payment_info['transaction']
        }
        return template.render(ctx)
