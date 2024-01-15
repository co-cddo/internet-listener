# Content Security Policy (CSP) Guidance

To use the central CSP reporting for UK government websites and services, use the following endpoint:  
`https://csp1.ingest.service.security.gov.uk/report` ([sources allowlisted](https://github.com/co-cddo/internet-listener/blob/main/lambda.tf#L96))

## Header Note
For compatibility you should include both a **report-uri** and **report-to** in the CSP header value, **report-to** requires a separate header configured with the reporting endpoint details. See [CSP reporting directives on Mozilla](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy#reporting_directives) for more information.

## Examples

### Trusted Types

As per [guidance on web.dev](https://web.dev/articles/trusted-types#add_a_report-only_csp_header), you can configure a report-only CSP to look for issues with [trusted types](https://web.dev/articles/trusted-types):

|Header Key|Header Value|
|-|-|
|Report-To|`{"group": "primary", "max_age": 86400, "endpoints": [{ "url": "https://csp1.ingest.service.security.gov.uk/report" }]}`|
|Content-Security-Policy-Report-Only|`require-trusted-types-for 'script'; report-uri https://csp1.ingest.service.security.gov.uk/report; report-to primary`|

### Live CSP Example

An example page is deployed to <https://gc3.security.gov.uk/csp-testing> which prevents sources being loaded and the body includes a linked "img" which is blocked.

|Header Key|Header Value|
|-|-|
|Report-To|`{"group": "primary", "max_age": 86400, "endpoints": [{ "url": "https://csp1.ingest.service.security.gov.uk/report" }]}`|
|Content-Security-Policy|`default-src 'none'; report-uri https://csp1.ingest.service.security.gov.uk/report; report-to primary`|
