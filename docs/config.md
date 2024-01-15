# Configuration

## Lambda environment variables

|Environment Variable|Description|Default|
|-|-|-|
|ENABLE_GENERIC_REQUESTS|Enable the logging of all generic requests (not just CSP reports), set to "false" or "0" to disable|"true"|
|ALLOWED_CSP_SOURCES|A CSV of allowed CSP reports via the document URI, `example.com` would allow `example.com` and `anysubdomain.example.com` but not `bad-example.com`, blank allows any source|""|
|S3_BUCKETNAME|Bucket for gz log files of reports and requests, this is useful for subsequent Athena query, blank/not set disables S3 logging|""|
|S3_PREFIX|Prefix for saving gz log files in the `S3_BUCKETNAME`|""|
|CLOUDFRONT_SECRET|A shared secret that is set in the CloudFront origin as the `x-cloudfront` header to block (always 502) direct-to-function URL requests, blank/not set disables checking for the header|""|

## Terraform

The Terraform provided configures the Lambda in a VPC (not tracked in IaC here) with an IAM role and policy to function. To deploy your own instance you will need to adapt the Terraform to your environment.
