"""Made-up sample data for previewing the IS Annual Letter: one contract per product.

Column names are the field names of the Jasper report AL_IS (rptAnnualLetter) and its
subreport sub_rep_poistnik_IS (rptPOnZ), so the real Excel exports can replace these files.
"""
from datetime import datetime
from io import BytesIO

import openpyxl

# (Allocation_…, ApprecLast12m_…, Value_…) column suffixes of each fund
FUNDS = {
    'Guaranteed': ('Guaranteed', 'Guaranteed', 'Guaranteed'),
    'ETF': ('ETF', 'ETF', 'ETF'),
    'Gold': ('Gold', 'Gold', 'Gold'),
    'Entrep': ('Entrep', 'Entrep', 'Entrep'),
    'Mortgage': ('MortgageIFund', 'Mortgage', 'Mortgage'),
    'FamilyOffice': ('FamilyIFund', 'FamOffice', 'FamOffice'),
    'WorldBrands': ('WorldIFund', 'Wbrands', 'Wbrands'),
    'Digital': ('DigitalAssetsIFund', 'Digital', 'Digital'),
    'FixedIncome': ('FixedIncomIFund', 'FixedIncomIFund', 'FixedIncomIFund'),
    'GlobalSelect': ('GlobalSelectIFund', 'GlobalSelectIFund', 'GlobalSelectIFund'),
    'Sustainability': ('SustainabilityIFund', 'SustainabilityIFund', 'SustainabilityIFund'),
}

MAIN_COLUMNS = (
    ['Contract_number', 'ProductName', 'Currency', 'Closing_date', 'PH_Gender', 'PH_TitleBefore', 'PH_FirstName',
     'PH_LastName', 'PH_TitleAfter', 'PH_Street', 'PH_Zip', 'PH_City', 'ValidFrom', 'PH_TechnicalBeginn',
     'IncreasedPremium', 'RegularPremium', 'Periodicity', 'Saldo_incl_LoyaltyBonus', 'InvestmentBalance',
     'NOVIS_LoyaltyBonus', 'NOVIS_SurvivalBonus', 'Special_Bonus']
    + [f'pay{i}_{part}' for i in range(1, 13) for part in ('ValueDate', 'Amount')]
    + [f'Allocation_{a}' for a, _, _ in FUNDS.values()]
    + [f'ApprecLast12m_{p}' for _, p, _ in FUNDS.values()]
    + [f'Value_{v}' for _, _, v in FUNDS.values()]
    + ['Password', 'AttachmentName']
)

DETAIL_COLUMNS = ['IdNum', 'PH_Flag', 'Rnk', 'Code', 'Symbol', 'FirstName', 'Lastname', 'BirthDate', 'ValidFrom',
                  'Death-Cover', 'Death-Cover-Decreasing', 'Duration-Death-Cover-Decreasing', 'Critical-illness',
                  'Operations', 'Hospitalization', 'Death-by-Accident', 'Accident-by-Permconsq', 'TreatmentPeriod',
                  'Disability-Cover', 'Disability-Rent']


def _contract(number, product, holder, regular, funds, **extra):
    row = {
        'Contract_number': number, 'ProductName': product, 'Currency': 'EUR', 'Closing_date': datetime(2025, 5, 31),
        'PH_Street': 'Laugavegur 100', 'PH_Zip': '101', 'PH_City': 'Reykjavík',
        'ValidFrom': datetime(2019, 3, 1), 'PH_TechnicalBeginn': datetime(2019, 3, 1),
        'IncreasedPremium': 0, 'RegularPremium': regular, 'Periodicity': 'Monthly',
        'Saldo_incl_LoyaltyBonus': 12345.67, 'InvestmentBalance': 11987.12, 'NOVIS_LoyaltyBonus': 358.55,
        'NOVIS_SurvivalBonus': 'N', 'Special_Bonus': 0, 'Password': '', 'AttachmentName': f'AL_IS_{number}',
    }
    row.update(zip(('PH_Gender', 'PH_TitleBefore', 'PH_FirstName', 'PH_LastName', 'PH_TitleAfter'), holder))
    for month in range(12):
        row[f'pay{month + 1}_ValueDate'] = datetime(2024 + (month + 5) // 12, (month + 5) % 12 + 1, 15)
        row[f'pay{month + 1}_Amount'] = regular
    for name, (allocation, apprec, value) in FUNDS.items():
        share = funds.get(name, 0)
        row[f'Allocation_{allocation}'] = share
        row[f'ApprecLast12m_{apprec}'] = round(share / 7 - 1.5, 2) if share else 0
        row[f'Value_{value}'] = round(11987.12 * share / 100, 2)
    row.update(extra)
    return row


MAIN_ROWS = [
    _contract('9900000001', 'NOVIS Wealth Insuring', ('F', '', 'Guðrún', 'Jónsdóttir', ''), 150,
              {'Guaranteed': 20, 'ETF': 15, 'Gold': 10, 'Entrep': 10, 'Mortgage': 10, 'FamilyOffice': 5,
               'WorldBrands': 10, 'Digital': 5, 'FixedIncome': 5, 'GlobalSelect': 5, 'Sustainability': 5},
              IncreasedPremium=5000, NOVIS_SurvivalBonus='Y', Special_Bonus=120.4, pay3_Amount=150.5),
    _contract('9900000002', 'NOVIS „Life Savings Plan”', ('M', 'Dr.', 'Jón', 'Jónsson', ''), 100,
              {'FixedIncome': 40, 'GlobalSelect': 35, 'Sustainability': 25}),
    _contract('9900000003', 'NOVIS „Flexible Savings Plan”', ('C', '', '', 'Dæmi ehf.', ''), 250,
              {'FixedIncome': 50, 'GlobalSelect': 30, 'Sustainability': 20}),
    _contract('9900000004', 'NOVIS Life Protector', ('F', '', 'Anna', 'Sigurðardóttir', ''), 45.9, {}),
]

_PERSONS = {
    '9900000001': [('Guðrún', 'Jónsdóttir'), ('Jón', 'Guðmundsson'), ('Sigríður', 'Jónsdóttir'), ('Ólafur', 'Jónsson'),
                   ('Helga', 'Jónsdóttir'), ('Einar', 'Jónsson'), ('Katrín', 'Jónsdóttir')],
    '9900000002': [('Jón', 'Jónsson'), ('María', 'Pálsdóttir')],
    '9900000003': [('Björn', 'Björnsson')],
    '9900000004': [('Anna', 'Sigurðardóttir'), ('Gunnar', 'Ólafsson'), ('Elín', 'Gunnarsdóttir')],
}

DETAIL_ROWS = [
    {'IdNum': number, 'PH_Flag': 'Y' if rank == 1 else 'N', 'Rnk': rank, 'Code': 'EUR', 'Symbol': 'EUR',
     'FirstName': first, 'Lastname': last, 'BirthDate': datetime(1960 + 5 * rank, rank, 10 + rank),
     'ValidFrom': datetime(2019, 3, 1), 'Death-Cover': 50000 - 5000 * rank, 'Critical-illness': 20000,
     'Disability-Cover': 30000, 'Death-by-Accident': 10000}
    for number, persons in _PERSONS.items()
    for rank, (first, last) in enumerate(persons, start=1)
]


def to_xlsx(columns, rows):
    """Excel file (bytes) with a header row and one row per dict."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(columns)
    for row in rows:
        ws.append([row.get(column) for column in columns])
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
