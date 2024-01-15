import os
import unittest

os.environ["ALLOWED_CSP_SOURCES"] = "example, testing.com, example.com"

from lambda_function import lambda_handler


class TestLambdaFunction(unittest.TestCase):
    def test_lambda_handler_csp_1(self):
        """
        First Content Security Policy (CSP) test. Base64 "csp-report".
        """
        event = {
            "headers": {
                "x-true-host": "csp.testing.example",
                "content-type": "application/csp-report",
                "x-cloudfront": "",
            },
            "body": "eyJjc3AtcmVwb3J0Ijp7ImJsb2NrZWQtdXJpIjoiaHR0cHM6Ly9leGFtcGxlL3Rlc3QucG5nIiwiZGlzcG9zaXRpb24iOiJyZXBvcnQiLCJkb2N1bWVudC11cmkiOiJodHRwczovL2V4YW1wbGUvY3NwLXRlc3RpbmciLCJlZmZlY3RpdmUtZGlyZWN0aXZlIjoiaW1nLXNyYyIsIm9yaWdpbmFsLXBvbGljeSI6ImRlZmF1bHQtc3JjICdub25lJzsgcmVwb3J0LXVyaSBodHRwczovL2NzcC50ZXN0aW5nLmV4YW1wbGUiLCJyZWZlcnJlciI6IiIsInN0YXR1cy1jb2RlIjoyMDAsInZpb2xhdGVkLWRpcmVjdGl2ZSI6ImltZy1zcmMifX0=",
            "isBase64Encoded": True,
        }
        res = lambda_handler(event, {})
        self.assertEqual(res["statusCode"], 200)

    def test_lambda_handler_csp_2(self):
        """
        Second Content Security Policy (CSP) test. Plain text "reports+json".
        """
        event = {
            "headers": {
                "x-true-host": "csp.testing.example",
                "content-type": "application/reports+json",
                "x-cloudfront": "",
            },
            "body": '[{"age":1396,"body":{"blockedURL":"https://example/favicon.ico","disposition":"report","documentURL":"https://subdomain.testing.com/csp-testing","effectiveDirective":"img-src","originalPolicy":"default-src \'none\'; report-uri https://csp.testing.example; report-to primary","referrer":"https://www.google.com/","sample":"","statusCode":200},"type":"csp-violation","url":"https://example/csp-testing","user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},{"age":1428,"body":{"blockedURL":"https://example/test.png","disposition":"report","documentURL":"https://example/csp-testing","effectiveDirective":"img-src","originalPolicy":"default-src \'none\'; report-uri https://csp.testing.example; report-to primary","referrer":"https://www.google.com/","sample":"","statusCode":200},"type":"csp-violation","url":"https://example/csp-testing","user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}]',
            "isBase64Encoded": False,
        }
        res = lambda_handler(event, {})
        self.assertEqual(res["statusCode"], 200)

    def test_lambda_handler_bad_csp(self):
        """
        Bad CSP body
        """
        event = {
            "headers": {
                "x-true-host": "csp.testing.example",
                "content-type": "application/reports+json",
                "x-cloudfront": "",
            },
            "body": "dGVzdD0xMjM=",
            "isBase64Encoded": True,
        }
        res = lambda_handler(event, {})
        self.assertEqual(res["statusCode"], 502)

    def test_lambda_handler_generic(self):
        """
        Generic request
        """
        event = {
            "headers": {
                "x-true-host": "csp.testing.example",
                "content-type": "text/plain",
                "x-cloudfront": "",
            },
            "body": "abc",
            "isBase64Encoded": False,
        }
        res = lambda_handler(event, {})
        self.assertEqual(res["statusCode"], 200)

    def test_lambda_handler_bad_xcf(self):
        """
        Bad x-cloudfront value
        """
        event = {
            "headers": {
                "x-true-host": "csp.testing.example",
                "content-type": "text/plain",
                "x-cloudfront": "123",
            },
            "body": "",
            "isBase64Encoded": False,
        }
        res = lambda_handler(event, {})
        self.assertEqual(res["statusCode"], 502)

    def test_lambda_handler_bad_csp_domain(self):
        """
        Bad document_uri domain
        """
        event = {
            "headers": {
                "x-true-host": "csp.testing.example",
                "content-type": "application/reports+json",
                "x-cloudfront": "",
            },
            "body": '[{"age":1396,"body":{"blockedURL":"https://example/favicon.ico","disposition":"report","documentURL":"https://bad-example.com/csp-testing","effectiveDirective":"img-src","originalPolicy":"default-src \'none\'; report-uri https://csp.testing.example; report-to primary","referrer":"https://www.google.com/","sample":"","statusCode":200},"type":"csp-violation","url":"https://example/csp-testing","user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},{"age":1428,"body":{"blockedURL":"https://example/test.png","disposition":"report","documentURL":"https://example/csp-testing","effectiveDirective":"img-src","originalPolicy":"default-src \'none\'; report-uri https://csp.testing.example; report-to primary","referrer":"https://www.google.com/","sample":"","statusCode":200},"type":"csp-violation","url":"https://example/csp-testing","user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}]',
            "isBase64Encoded": False,
        }
        res = lambda_handler(event, {})
        self.assertEqual(res["statusCode"], 502)


if __name__ == "__main__":
    unittest.main()
