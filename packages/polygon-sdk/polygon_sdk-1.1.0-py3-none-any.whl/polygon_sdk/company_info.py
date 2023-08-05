class CompanyInformation:
    def __init__(self, results):
        self.ticker = results.get('ticker')
        self.name = results.get('name')
        self.market = results.get('market')
        self.primary_exchange = results.get('primary_exchange')
        self.type = results.get('type', 'N/A')
        self.active = results.get('active', 'N/A')
        self.cik = results.get('cik', 'N/A')
        self.market_cap = results.get('market_cap', 0)

        address = results.get('address')
        if address:
            self.address = address
            self.street = address.get('street', 'N/A')
            self.phone_number = address.get('phone_number', 'No Phone Number')
            self.postal_code = address.get('postal_code', 'No Postal Code')
            self.state = address.get('state', 'N/A')
            self.city = address.get('city', 'N/A')
        else:
            self.address = 'N/A'
            self.street = 'N/A'
            self.phone_number = 'N/A'
            self.postal_code = 'N/A'
            self.state = 'N/A'
            self.city = 'N/A'
        
        self.sic_code = results.get('sic_code', 'N/A')
        self.sic_description = results.get('sic_description', 'N/A')
        self.description = results.get('description', 'N/A')
        self.homepage_url = results.get('homepage_url', 'N/A')
        self.total_employees = results.get('total_employees', 'N/A')
        self.branding = results.get('branding', None)
        self.weighted_shares_outstanding = results.get('weighted_shares_outstanding', 0)
        self.list_date = results.get('list_date', 'N/A')
        self.share_class_shares_outstanding = results.get('share_class_shares_outstanding', 0)