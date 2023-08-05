from dataclasses import dataclass
from typing import Optional
trade_conditions_dict = {
'1':'Acquisition',
'2':'Average Price Trade',
'3':'Automatic Execution',
'4':'Bunched Trade',
'5':'Bunched Sold Trade',
'6':'CAP Election',
'7':'Cash Sale',
'8':'Closing Prints',
'9':'Cross Trade',
'10':'Derivatively Priced',
'11':'Distribution',
'12':'Form T/Extended Hours',
'13':'Extended Hours (Sold Out Of Sequence)',
'14':'Intermarket Sweep',
'15':'Market Center Official Close',
'16':'Market Center Official Open',
'17':'Market Center Opening Trade',
'18':'Market Center Reopening Trade',
'19':'Market Center Closing Trade',
'20':'Next Day',
'21':'Price Variation Trade',
'22':'Prior Reference Price',
'23':'Rule 155 Trade (AMEX)',
'24':'Rule 127 (NYSE Only)',
'25':'Opening Prints',
'27':'Stopped Stock (Regular Trade)',
'28':'Re-Opening Prints',
'29':'Seller',
'30':'Sold Last',
'31':'Sold Last and Stopped Stock',
'32':'Sold (Out Of Sequence)',
'33':'Sold (Out of Sequence) and Stopped Stock',
'34':'Split Trade',
'35':'Stock Option',
'36':'Yellow Flag Regular Trade',
'37':'Odd Lot Trade',
'38':'Corrected Consolidated Close (per listing market)',
'41':'Trade Thru Exempt',
'52':'Contingent Trade',
'53':'Qualified Contingent Trade',
'55':'Opening Reopening Trade Detail',
'57':'Short Sale Restriction Activated',
'58':'Short Sale Restriction Continued',
'59':'Short Sale Restriction Deactivated',
'60':'Short Sale Restriction In Effect',
'62':'Financial Status - Bankrupt',
'63':'Financial Status - Deficient',
'64':'Financial Status - Delinquent',
'65':'Financial Status - Bankrupt and Deficient',
'66':'Financial Status - Bankrupt and Delinquent',
'67':'Financial Status - Deficient and Delinquent',
'68':'Financial Status - Deficient, Delinquent, and Bankrupt',
'69':'Financial Status - Liquidation',
'70':'Financial Status - Creations Suspended',
'71':'Financial Status - Redemptions Suspended'}

EQUITY_QUOTE_CONDITIONS = { 
'1':'Regular Two-Sided Open',
'2':'Regular One-Sided Open',
'3':'Slow Ask',
'4':'Slow Bid',
'5':'Slow Bid and Ask',
'6':'Slow Due LRP Bid',
'7':'Slow Due LRP Ask',
'9':'Slow Due Set Slow List Bid Ask',
'10':'Manual Ask Automated Bid',
'11':'Manual Bid Automated Ask',
'12':'Manual Bid and Ask',
'13':'Opening',
'14':'Closing',
'15':'Closed',
'16':'Resume',
'17':'Fast Trading',
'18':'Trading Range Indication',
'19':'Market Maker Quotes Closed',
'20':'Non-Firm',
'21':'News Dissemination',
'22':'Order Influx',
'23':'Order Imbalance',
'26':'Additional Information',
'27':'News Pending',
'28':'Additional Information Due To Related Security',
'29':'Due To Related Security',
'30':'In View Of Common',
'30':'Equipment Changeover',
'32':'No Open No Resume',
'40':'On Demand Auction',
'41':'Cash Only Settlement',
'42':'Next Day Settlement',
'43':'LULD Trading Pause',
'71':'Slow Due LRP Bid and Ask',
'82':'SIP Generated',
'84':'Crossed Market',
'85':'Locked Market',
'94':'CQS Generated',}






@dataclass
class Dividend:
    cash_amount: float
    declaration_date: str
    dividend_type: str
    ex_dividend_date: str
    frequency: int
    pay_date: str
    record_date: str
    ticker: str
    currency: Optional[str] = None
    




