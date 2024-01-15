variable "logging_bucket_name" {
  sensitive = true
  type      = string
}

variable "s3_prefix" {
  sensitive = true
  type      = string
}

variable "cloudfront_secret" {
  sensitive = true
  type      = string
}
