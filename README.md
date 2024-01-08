# internet-listener
A simple endpoint for logging various HTTP requests such as Content Security Policy reports and testing the efficacy of web scanning tools.

## Content Security Policy (CSP) reports
For CSPs, use the following endpoint: `https://csp1.ingest.service.security.gov.uk/report`

> Note: for compatibility you should include both a **report-uri** and **report-to** in the CSP header value, **report-to** requires a separate header configured with the reporting endpoint details. See [CSP reporting directives on Mozilla](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy#reporting_directives) for more information.

### Trusted Types

As per [guidance on web.dev](https://web.dev/articles/trusted-types#add_a_report-only_csp_header), you can configure a report-only CSP to look for issues with [trusted types](https://web.dev/articles/trusted-types):

|Header Key|Header Value|
|-|-|
|Report-To|{"group": "primary", "max_age": 86400, "endpoints": [{ "url": "https://csp1.ingest.service.security.gov.uk/report" }]}|
|Content-Security-Policy-Report-Only|require-trusted-types-for 'script'; report-uri https://csp1.ingest.service.security.gov.uk/report; report-to primary|

### CSP Example

An example page is deployed to <https://gc3.security.gov.uk/csp-testing> which prevents sources being loaded and the body includes a linked "img" which is blocked.

|Header Key|Header Value|
|-|-|
|Report-To|{"group": "primary", "max_age": 86400, "endpoints": [{ "url": "https://csp1.ingest.service.security.gov.uk/report" }]}|
|Content-Security-Policy|default-src 'none'; report-uri https://csp1.ingest.service.security.gov.uk/report; report-to primary|

## Generic requests and testing
To more easily identify web requests during testing, a specific subdomain of `ingest.service.security.gov.uk` should be used. For example, if you wanted to do some `POST` tests on the 8th Jan 2024, you could use: `post-testing-20240108.ingest.service.security.gov.uk`.

## Contact
If you have any queries about the listener, please contact `tech[at]gc3.security.gov.uk`.
