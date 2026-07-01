terraform {
    backend "s3" {
      bucket         = "pgai-tf-state"
      key            = "terraform.tfstate"
      region         = "us-east-2"
      use_lockfile   = true
      encrypt        = true
    }
}