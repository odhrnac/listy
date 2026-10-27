from io import BytesIO
from types import SimpleNamespace

from django.template import Template as DjangoTemplate, Context
from django.test import SimpleTestCase

from readers import read_excel
from .sample_data import with_aliases, linked_rows, build_context
from .starter_templates import read_starter_file
from .starter_templates import is_annual_letter_samples as samples
from .templatetags.letter_filters import money, excel_date


class MoneyFilterTests(SimpleTestCase):
    def test_formats_like_word(self):
        self.assertEqual(money('1906.81'), '1 906.81')
        self.assertEqual(money('1234567.5'), '1 234 567.50')
        self.assertEqual(money('15.5'), '15.50')
        self.assertEqual(money(0), '0.00')

    def test_decimals(self):
        self.assertEqual(money('1906.81', 0), '1 907')
        self.assertEqual(money('150.0', 'auto'), '150')
        self.assertEqual(money('150.5', 'auto'), '150.50')

    def test_non_numbers_are_returned_unchanged(self):
        self.assertEqual(money(''), '')
        self.assertEqual(money('n/a'), 'n/a')

    def test_available_in_templates_without_load(self):
        rendered = DjangoTemplate('{{ PremiumOwed|money }} evrur').render(Context({'PremiumOwed': '1906.81'}))
        self.assertEqual(rendered, '1 906.81 evrur')


class ExcelDateFilterTests(SimpleTestCase):
    def test_formats_excel_dates(self):
        self.assertEqual(excel_date('2021-05-31 00:00:00'), '31.05.2021')
        self.assertEqual(excel_date('2021-05-31'), '31.05.2021')
        self.assertEqual(excel_date('31.05.2021'), '31.05.2021')

    def test_non_dates_are_returned_unchanged(self):
        self.assertEqual(excel_date(''), '')
        self.assertEqual(excel_date('soon'), 'soon')


class SampleDataTests(SimpleTestCase):
    def test_aliases_for_columns_with_dashes(self):
        row = with_aliases({'Death-Cover': '100', 'IdNum': '1'})
        self.assertEqual(row['Death_Cover'], '100')
        self.assertEqual(row['Death-Cover'], '100')

    def test_linked_rows_match_numbers_written_differently(self):
        detail = [{'IdNum': '1718070440.0', 'Rnk': '1'}, {'IdNum': '999', 'Rnk': '1'}]
        rows = linked_rows({'Contract_number': '1718070440'}, detail, 'Contract_number', 'IdNum')
        self.assertEqual(len(rows), 1)

    def test_build_context_puts_linked_rows_under_detail_name(self):
        template = SimpleNamespace(detail_excel='x.xlsx', detail_name='insured', main_key='Nr', detail_key='Nr')
        context = build_context(template, {'Nr': '5'}, [{'Nr': '5'}, {'Nr': '6'}])
        self.assertEqual(context['insured'], [{'Nr': '5'}])


class AnnualLetterTemplateTests(SimpleTestCase):
    """Render the IS Annual Letter starter template with its sample Excels, as the preview does."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.main_rows = read_excel(BytesIO(samples.to_xlsx(samples.MAIN_COLUMNS, samples.MAIN_ROWS)))
        cls.detail_rows = read_excel(BytesIO(samples.to_xlsx(samples.DETAIL_COLUMNS, samples.DETAIL_ROWS)))
        cls.body = DjangoTemplate(read_starter_file('is_annual_letter', 'body.html'))
        cls.template = SimpleNamespace(detail_excel='x.xlsx', detail_name='insured',
                                       main_key='Contract_number', detail_key='IdNum')

    def render(self, product):
        row = next(r for r in self.main_rows if product in r['ProductName'])
        context = build_context(self.template, row, self.detail_rows)
        context['letter_date'] = '01.06.2025'
        return self.body.render(Context(context))

    def test_wealth_insuring(self):
        html = self.render('Wealth Insuring')
        self.assertIn('NOVIS „Wealth Insuring”', html)
        self.assertIn('NOVIS Survival Bonus:', html)
        self.assertIn('NOVIS Digital Assets Insurance Fund', html)
        self.assertIn('Accident insurance (accident, extended accident and accidental death):', html)
        self.assertEqual(html.count('class="al-person"'), 7)
        self.assertIn('150.50 EUR', html)  # payment with cents keeps them
        self.assertIn('<td>150 EUR</td>', html)  # whole payments drop .00

    def test_life_savings_plan(self):
        html = self.render('Life Savings Plan')
        self.assertIn('Permanent disability insurance', html)
        self.assertNotIn('NOVIS Gold Insurance Fund', html)
        self.assertIn('Dear Dr. Jón Jónsson,', html)

    def test_flexible_savings_plan(self):
        html = self.render('Flexible Savings Plan')
        self.assertNotIn('Critical illnesses insurance:', html)
        self.assertIn('Dear Dæmi ehf.,', html)

    def test_life_protector(self):
        html = self.render('Life Protector')
        self.assertNotIn('>YOUR INSURANCE ACCOUNT<', html)
        self.assertNotIn('Evaluation of NOVIS insurance funds', html)
        self.assertNotIn('Once a month:', html)
        self.assertIn('45.90 EUR', html)  # regular premium with decimals only for Life Protector
        self.assertIn('Critical illnesses insurance:', html)
