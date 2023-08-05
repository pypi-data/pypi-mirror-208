"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

import requests as requests_http
from . import utils
from codatassess.models import operations, shared
from typing import Optional

class ExcelReports:
    r"""Downloadable reports"""
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
        
    
    def download_excel_report(self, request: operations.DownloadExcelReportRequest, retries: Optional[utils.RetryConfig] = None) -> operations.DownloadExcelReportResponse:
        r"""Download generated excel report
        Download the previously generated Excel report to a local drive.
        
        Deprecated: this method will be removed in a future release, please migrate away from it as soon as possible
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.DownloadExcelReportRequest, base_url, '/data/companies/{companyId}/assess/excel/download', request)
        
        query_params = utils.get_query_params(operations.DownloadExcelReportRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('POST', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.DownloadExcelReportResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/octet-stream'):
                res.body = http_res.content

        return res

    
    def generate_excel_report(self, request: operations.GenerateExcelReportRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GenerateExcelReportResponse:
        r"""Generate an Excel report
        Generate an Excel report which can subsequently be downloaded.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GenerateExcelReportRequest, base_url, '/data/companies/{companyId}/assess/excel', request)
        
        query_params = utils.get_query_params(operations.GenerateExcelReportRequest, request)
        
        client = self._security_client
        
        retry_config = retries
        if retry_config is None:
            retry_config = utils.RetryConfig('backoff', True)
            retry_config.backoff = utils.BackoffStrategy(500, 60000, 1.5, 3600000)
            

        def do_request():
            return client.request('POST', url, params=query_params)
        
        http_res = utils.retry(do_request, utils.Retries(retry_config, [
            '408',
            '429',
            '5XX'
        ]))
        content_type = http_res.headers.get('Content-Type')

        res = operations.GenerateExcelReportResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.ExcelStatus])
                res.excel_status = out

        return res

    
    def get_accounting_marketing_metrics(self, request: operations.GetAccountingMarketingMetricsRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetAccountingMarketingMetricsResponse:
        r"""Get the marketing metrics from an accounting source for a given company.
        Request an Excel report for download.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetAccountingMarketingMetricsRequest, base_url, '/data/companies/{companyId}/connections/{connectionId}/assess/accountingMetrics/marketing', request)
        
        query_params = utils.get_query_params(operations.GetAccountingMarketingMetricsRequest, request)
        
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

        res = operations.GetAccountingMarketingMetricsResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.Report])
                res.report = out

        return res

    
    def get_excel_report(self, request: operations.GetExcelReportRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetExcelReportResponse:
        r"""Download generated excel report
        Download the previously generated Excel report to a local drive.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetExcelReportRequest, base_url, '/data/companies/{companyId}/assess/excel/download', request)
        
        query_params = utils.get_query_params(operations.GetExcelReportRequest, request)
        
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

        res = operations.GetExcelReportResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/octet-stream'):
                res.body = http_res.content

        return res

    
    def get_excel_report_generation_status(self, request: operations.GetExcelReportGenerationStatusRequest, retries: Optional[utils.RetryConfig] = None) -> operations.GetExcelReportGenerationStatusResponse:
        r"""Get status of Excel report
        Returns the status of the latest report requested.
        """
        base_url = self._server_url
        
        url = utils.generate_url(operations.GetExcelReportGenerationStatusRequest, base_url, '/data/companies/{companyId}/assess/excel', request)
        
        query_params = utils.get_query_params(operations.GetExcelReportGenerationStatusRequest, request)
        
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

        res = operations.GetExcelReportGenerationStatusResponse(status_code=http_res.status_code, content_type=content_type, raw_response=http_res)
        
        if http_res.status_code == 200:
            if utils.match_content_type(content_type, 'application/json'):
                out = utils.unmarshal_json(http_res.text, Optional[shared.ExcelStatus])
                res.excel_status = out

        return res

    