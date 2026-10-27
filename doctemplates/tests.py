from django.template import Template as DjangoTemplate, Context
from django.test import SimpleTestCase

from .templatetags.letter_filters import money


class MoneyFilterTests(SimpleTestCase):
    def test_formats_like_word(self):
        self.assertEqual(money('1906.81'), '1 906.81')
        self.assertEqual(money('1234567.5'), '1 234 567.50')
        self.assertEqual(money('15.5'), '15.50')
        self.assertEqual(money(0), '0.00')

    def test_non_numbers_are_returned_unchanged(self):
        self.assertEqual(money(''), '')
        self.assertEqual(money('n/a'), 'n/a')

    def test_available_in_templates_without_load(self):
        rendered = DjangoTemplate('{{ PremiumOwed|money }} evrur').render(Context({'PremiumOwed': '1906.81'}))
        self.assertEqual(rendered, '1 906.81 evrur')
