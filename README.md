# AWS Cloud Portfolio

A personal site running entirely on AWS serverless infrastructure — built manually first to learn each service, then rebuilt as Infrastructure as Code with the AWS CDK.

**Live site:** https://d9wywbarkqdmh.cloudfront.net

---

## What this is

This isn't just a static site — it's a small, complete piece of cloud infrastructure. The homepage itself documents the architecture serving it, and includes a visitor counter backed by a real serverless API (not mock data).

The project was built in two phases:

1. **Manual build** — every resource (S3 bucket, CloudFront distribution, DynamoDB table, Lambda function, API Gateway) was created by hand through the AWS Console, to actually understand what each service does and how they connect.
2. **Infrastructure as Code** — the entire stack was then re-implemented in Python using the AWS CDK, so it can be deployed, updated, or torn down with a single command instead of manual console work.

## Architecture

```
                    ┌──────────────┐      ┌──────────────┐
   Visitor  ───────▶│  CloudFront  │─────▶│  S3 (static) │
                     │  (CDN, TLS)  │      │   assets     │
                     └──────┬───────┘      └──────────────┘
                            │
                            │  GET /count
                            ▼
                    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
                    │ API Gateway  │─────▶│    Lambda    │─────▶│  DynamoDB    │
                    │  (HTTP API)  │      │  (Python)    │      │ (on-demand)  │
                    └──────────────┘      └──────────────┘      └──────────────┘
```

Static content (HTML/CSS) is served from S3 through CloudFront's edge network with HTTPS. Separately, each page load calls a serverless API that increments a visit count stored in DynamoDB — a self-contained example of a full request lifecycle through API Gateway and Lambda.

## Stack

| Layer | Service | Purpose |
|---|---|---|
| CDN / TLS | Amazon CloudFront | Edge caching, HTTPS termination |
| Static hosting | Amazon S3 | Origin storage for site files, secured via Origin Access Control (not public) |
| API | Amazon API Gateway (HTTP API) | Public endpoint for the visitor counter |
| Compute | AWS Lambda (Python 3.12) | Self-initializing counter logic, least-privilege IAM |
| Database | Amazon DynamoDB | On-demand billing, single-item table |
| IaC | AWS CDK (Python) | Defines and deploys the entire stack |

## Notable engineering decisions

- **Origin Access Control over public bucket policy.** The S3 bucket blocks all public access; only CloudFront can read from it. This is a stricter, more current pattern than the public bucket-policy approach commonly shown in tutorials.
- **Least-privilege IAM.** The Lambda function is granted access to exactly one DynamoDB table (`grant_read_write_data`), rather than the broader managed policies used during initial manual prototyping.
- **Self-healing initialization.** The Lambda function doesn't assume its DynamoDB item already exists — it attempts an atomic increment, and on the first-ever invocation (when the row doesn't exist) it creates it. No manual database seeding step is required after deployment.
- **One-command deploys.** `cdk deploy` provisions or updates the entire stack — S3, CloudFront, DynamoDB, Lambda, API Gateway, and IAM roles — and uploads the site content, in a single run.

## Project structure

```
cdk_portfolio_project/
  app.py                       # CDK app entry point
  cdk_portfolio_project_stack.py  # Full infrastructure definition
lambda/
  visitor_counter.py           # Counter API logic
website/
  index.html                   # Site content deployed to S3
  error.html
```

## Running this yourself

```bash
cdk bootstrap   # one-time per AWS account/region
cdk deploy
```

Outputs the live CloudFront URL and API endpoint on completion.

## Roadmap

- [x] Static hosting on S3
- [x] CDN + HTTPS via CloudFront
- [x] Serverless visitor counter (Lambda + API Gateway + DynamoDB)
- [x] Full stack rebuilt as Infrastructure as Code (AWS CDK)
- [ ] CloudWatch monitoring and alarms
- [ ] CI/CD via GitHub Actions
