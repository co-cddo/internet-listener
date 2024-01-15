terraform {
  backend "s3" {
    bucket = "gccc-core-security-tfstate"
    key    = "internet-listener.tfstate"
    region = "eu-west-2"
  }
}

variable "production_iam_role" {
  sensitive = true
  type      = string
}

provider "aws" {
  region = "eu-west-2"

  assume_role {
    role_arn = var.production_iam_role
  }

  default_tags {
    tags = {
      "Service" : "internet-listener",
      "Reference" : "https://github.com/co-cddo/internet-listener",
      "Environment" : "production"
    }
  }
}
