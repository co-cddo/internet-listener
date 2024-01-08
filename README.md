# internet-listener
A simple endpoint for logging various HTTP requests such as Content Security Policy reports and testing scanning tools

## Content Security Policy (CSP) reports
For CSPs, use the following endpoint: `https://csp1.ingest.service.security.gov.uk/report`

> Note: for compatibility you should include both a **report-uri** and **report-to** in the CSP header value, **report-to** requires a separate header configured with the reporting endpoint details. See [CSP reporting directives on Mozilla](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy#reporting_directives) for more information.

### Example

An example page is deployed to <https://gc3.security.gov.uk/csp-testing> which prevents sources being loaded and the body includes a linked "img" which is blocked.

|Header Key|Header Value|
|-|-|
|Report-To|{"group": "primary", "max_age": 86400, "endpoints": [{ "url": "https://csp1.ingest.service.security.gov.uk/report" }]}|
|Content-Security-Policy-Report-Only|default-src 'none'; report-uri https://csp1.ingest.service.security.gov.uk/report; report-to primary|
