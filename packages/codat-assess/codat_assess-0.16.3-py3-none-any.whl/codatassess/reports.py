"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

import requests as requests_http
from . import utils
from codatassess.models import operations, shared
from typing import Optional

class Reports:
    r"""Data integrity is important"""
    _client: requests_http.Session
    _security_client: requests_http.Session
    _server_url: str
    _language: str
    _sdk_version: str
    _gen_version: str

    def __init__(self, client: requests_http.Session, security_client: requests_http.Session, server_url: str, language: str, sdk_version: str, gen_version: str) -> None:
        self._client = client
        self._security_client = security_client
        self._server_url = server_url
        self._language = language
        self._sdk_version = sdk_version
        self._gen_version = gen_version
        
    
    def get_accounts_for_enhanced_balance_sheet(self, request: operations.GetAccountsForEnhancedBalanceSheetRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetAccountsForEnhancedBalanceSheetResponse:
        r"""Enhanced Balance Sheet Accounts
        The Enhanced Balance Sheet Accounts endpoint returns a list of categorized accounts that appear on a company’s Balance Sheet along with a balance per financial statement date.
        
        Codat suggests a category for each account automatically, but you can [change it](/docs/assess-categorizing-accounts-ecommerce-lending) to a more suitable one.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetAccountsForEnhancedBalanceSheetRequest, base_url, '/companies/{companyId}/reports/enhancedBalanceSheet/accounts', request)
        
        query_params = utils.get_query_params(operations.GetAccountsForEnhancedBalanceSheetRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetAccountsForEnhancedBalanceSheetResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.EnhancedReport])
                res.enhanced_report = out

        return res

    
    def get_accounts_for_enhanced_profit_and_loss(self, request: operations.GetAccountsForEnhancedProfitAndLossRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetAccountsForEnhancedProfitAndLossResponse:
        r"""Enhanced Profit and Loss Accounts
        The Enhanced Profit and Loss Accounts endpoint returns a list of categorized accounts that appear on a company’s Profit and Loss. It also includes a balance per the financial statement date.
        
        Codat suggests a category for each account automatically, but you can [change it](/docs/assess-categorizing-accounts-ecommerce-lending) to a more suitable one.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetAccountsForEnhancedProfitAndLossRequest, base_url, '/companies/{companyId}/reports/enhancedProfitAndLoss/accounts', request)
        
        query_params = utils.get_query_params(operations.GetAccountsForEnhancedProfitAndLossRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetAccountsForEnhancedProfitAndLossResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.EnhancedReport])
                res.enhanced_report = out

        return res

    
    def get_commerce_customer_retention_metrics(self, request: operations.GetCommerceCustomerRetentionMetricsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetCommerceCustomerRetentionMetricsResponse:
        r"""Get the customer retention metrics for a specific company.
        Gets the customer retention metrics for a specific company connection, over one or more periods of time.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetCommerceCustomerRetentionMetricsRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/commerceMetrics/customerRetention', request)
        
        query_params = utils.get_query_params(operations.GetCommerceCustomerRetentionMetricsRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetCommerceCustomerRetentionMetricsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Report])
                res.report = out

        return res

    
    def get_commerce_lifetime_value_metrics(self, request: operations.GetCommerceLifetimeValueMetricsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetCommerceLifetimeValueMetricsResponse:
        r"""Get the lifetime value metric for a specific company.
        Gets the lifetime value metric for a specific company connection, over one or more periods of time.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetCommerceLifetimeValueMetricsRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/commerceMetrics/lifetimeValue', request)
        
        query_params = utils.get_query_params(operations.GetCommerceLifetimeValueMetricsRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetCommerceLifetimeValueMetricsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Report])
                res.report = out

        return res

    
    def get_commerce_orders_metrics(self, request: operations.GetCommerceOrdersMetricsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetCommerceOrdersMetricsResponse:
        r"""Get order information for a specific company
        Gets the order information for a specific company connection, over one or more periods of time.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetCommerceOrdersMetricsRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/commerceMetrics/orders', request)
        
        query_params = utils.get_query_params(operations.GetCommerceOrdersMetricsRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetCommerceOrdersMetricsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Report])
                res.report = out

        return res

    
    def get_commerce_refunds_metrics(self, request: operations.GetCommerceRefundsMetricsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetCommerceRefundsMetricsResponse:
        r"""Get the refunds information for a specific company
        Gets the refunds information for a specific company connection, over one or more periods of time.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetCommerceRefundsMetricsRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/commerceMetrics/refunds', request)
        
        query_params = utils.get_query_params(operations.GetCommerceRefundsMetricsRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetCommerceRefundsMetricsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Report])
                res.report = out

        return res

    
    def get_commerce_revenue_metrics(self, request: operations.GetCommerceRevenueMetricsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetCommerceRevenueMetricsResponse:
        r"""Commerce Revenue Metrics
        Get the revenue and revenue growth for a specific company connection, over one or more periods of time.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetCommerceRevenueMetricsRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/commerceMetrics/revenue', request)
        
        query_params = utils.get_query_params(operations.GetCommerceRevenueMetricsRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetCommerceRevenueMetricsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Report])
                res.report = out

        return res

    
    def get_enhanced_balance_sheet(self, request: operations.GetEnhancedBalanceSheetRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetEnhancedBalanceSheetResponse:
        r"""Enhanced Balance Sheet
        Gets a fully categorized balance sheet statement for a given company, over one or more period(s).
        
        Deprecated: this method will be removed in a future release, please migrate away from it as soon as possible
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetEnhancedBalanceSheetRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/enhancedBalanceSheet', request)
        
        query_params = utils.get_query_params(operations.GetEnhancedBalanceSheetRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetEnhancedBalanceSheetResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Report])
                res.report = out

        return res

    
    def get_enhanced_cash_flow_transactions(self, request: operations.GetEnhancedCashFlowTransactionsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetEnhancedCashFlowTransactionsResponse:
        r"""Get enhanced cash flow report
        The Enhanced Cash Flow Transactions endpoint provides a fully categorized list of banking transactions for a company. Accounts and transaction data are obtained from the company's banking data sources.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetEnhancedCashFlowTransactionsRequest, base_url, '/companies/{companyId}/reports/enhancedCashFlow/transactions', request)
        
        query_params = utils.get_query_params(operations.GetEnhancedCashFlowTransactionsRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetEnhancedCashFlowTransactionsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.EnhancedCashFlowTransactions])
                res.enhanced_cash_flow_transactions = out

        return res

    
    def get_enhanced_financial_metrics(self, request: operations.GetEnhancedFinancialMetricsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetEnhancedFinancialMetricsResponse:
        r"""List financial metrics
        Gets all the available financial metrics for a given company, over one or more periods.
        
        Deprecated: this method will be removed in a future release, please migrate away from it as soon as possible
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetEnhancedFinancialMetricsRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/financialMetrics', request)
        
        query_params = utils.get_query_params(operations.GetEnhancedFinancialMetricsRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetEnhancedFinancialMetricsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.FinancialMetrics])
                res.financial_metrics = out

        return res

    
    def get_enhanced_invoices_report(self, request: operations.GetEnhancedInvoicesReportRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetEnhancedInvoicesReportResponse:
        r"""Enhanced Invoices Report
        Gets a list of invoices linked to the corresponding banking transaction
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetEnhancedInvoicesReportRequest, base_url, '/companies/{companyId}/reports/enhancedInvoices', request)
        
        query_params = utils.get_query_params(operations.GetEnhancedInvoicesReportRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetEnhancedInvoicesReportResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.EnhancedInvoicesReport])
                res.enhanced_invoices_report = out

        return res

    
    def get_enhanced_profit_and_loss(self, request: operations.GetEnhancedProfitAndLossRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetEnhancedProfitAndLossResponse:
        r"""Enhanced Profit and Loss
        Gets a fully categorized profit and loss statement for a given company, over one or more period(s).
        
        Deprecated: this method will be removed in a future release, please migrate away from it as soon as possible
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetEnhancedProfitAndLossRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/enhancedProfitAndLoss', request)
        
        query_params = utils.get_query_params(operations.GetEnhancedProfitAndLossRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetEnhancedProfitAndLossResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Report])
                res.report = out

        return res

    
    def get_recurring_revenue_metrics(self, request: operations.GetRecurringRevenueMetricsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetRecurringRevenueMetricsResponse:
        r"""Get key metrics for subscription revenue
        Gets key metrics for subscription revenue.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetRecurringRevenueMetricsRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/subscriptions/mrr', request)
        
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GetRecurringRevenueMetricsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Report])
                res.report = out

        return res

    
    def request_recurring_revenue_metrics(self, request: operations.RequestRecurringRevenueMetricsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.RequestRecurringRevenueMetricsResponse:
        r"""Request production of key subscription revenue metrics
        Request production of key subscription revenue metrics.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.RequestRecurringRevenueMetricsRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/subscriptions/process', request)
        
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('GET', url)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.RequestRecurringRevenueMetricsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Report])
                res.report = out

        return res

    