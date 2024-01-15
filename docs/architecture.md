# Architecture

The below diagram is how the central endpoint for UK government is configured with other resources such as CloudFront and S3.

The primary purpose of CloudFront is to have custom domains for the listener rather than a random Lambda function URL. This allows the service to adapt the origin, potentially to something other than Lambda, in future without needing to communicate a URL change.


```
          ┌──────────┐  ┌──────────────────┐
          │ Generic  │  │ Content Security │
          │ HTTP     │  │ Policy (CSP)     │
          │ Requests │  │ Reports          │
          └─────────┬┘  └─────┬────────────┘
                    │         │
                    ▼         ▼
               GET/POST/HEAD/PUT etc.
                         │
┌────────────────────────┼───────────────────────────────┐
│ AWS                    │                               │
│                   ┌────▼────┐ Both A and AAAA          │
│                   │ Route53 │ wildcard records         │
│                   └────┬────┘                          │
│                        │                               │
│                        │                  Manages      │
│                  ┌─────▼──────┐   ┌─────┐ wildcard     │
│                  │ CloudFront ├───┤ ACM │ certificate  │
│ Uses Function    └─────┬──────┘   └─────┘              │
│ URLs with simple       │                               │
│ 'secret' header set    │    (simply responds "OK" 200) │
│ from CloudFront        │                               │
│                    ┌───▼────┐                          │
│                  ┌─┤ Lambda ├──┐ Optionally logs       │
│    Prints a JSON │ └────────┘  │ to S3 in formatted    │
│  line for use in │             │ gzip files for Athena │
│       CloudWatch │             │                       │
│            ┌─────▼──────┐    ┌─▼──┐                    │
│            │ CloudWatch │    │ S3 │                    │
│            └─────▲──────┘    └─▲──┘                    │
│                  │             │                       │
│            ┌─────┴──────┐   ┌──┴─────┐                 │
│            │ CloudWatch │   │ Athena │                 │
│            │  Insights  │   └────────┘                 │
│            └────────────┘                              │
│                                                        │
└────────────────────────────────────────────────────────┘
```
