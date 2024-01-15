# internet-listener
A simple endpoint for logging various HTTP requests such as Content Security Policy reports and testing the efficacy of web scanning tools.

## Content Security Policy (CSP) reports
To use the central CSP reporting for UK government websites and services, use the following endpoint:  
`https://csp1.ingest.service.security.gov.uk/report` ([sources allowlisted](https://github.com/co-cddo/internet-listener/blob/main/lambda.tf#L96))  
See [here for further guidance on CSP](docs/csp.md).

## Generic requests and testing
To more easily identify web requests during testing, a specific subdomain of `ingest.service.security.gov.uk` should be used. For example, if you wanted to do some `POST` tests on the 8th Jan 2024, you could use: `post-testing-20240108.ingest.service.security.gov.uk`.

## Architecture
See the [architect documentation](docs/architecture.md) to see how the central endpoint for UK government is deployed.

## Running and configuration
See the [configuration documentation](docs/config.md) to see how to configure various elements if you are running your own instance.

## Contact
If you have any queries about the listener, please contact `tech[at]gc3.security.gov.uk` or use the [#ask-gc3 channel in x-gov Slack](https://ukgovernmentdigital.slack.com/archives/C066WUHDJ10).
