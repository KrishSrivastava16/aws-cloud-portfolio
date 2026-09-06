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
                    └──────────────┘      └──────┬───────┘      └──────────────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │  CloudWatch  │
                                          │    Alarm     │──▶ SNS ──▶ Email
                                          └──────────────┘
```

Static content (HTML/CSS) is served from S3 through CloudFront's edge network with HTTPS. Separately, each page load calls a serverless API that increments a visit count stored in DynamoDB. A CloudWatch alarm watches the Lambda's error rate and publishes to an SNS topic (email-subscribed) if anything fails.

## Stack

| Layer | Service | Purpose |
|---|---|---|
| CDN / TLS | Amazon CloudFront | Edge caching, HTTPS termination |
| Static hosting | Amazon S3 | Origin storage for site files, secured via Origin Access Control (not public) |
| API | Amazon API Gateway (HTTP API) | Public endpoint for the visitor counter |
| Compute | AWS Lambda (Python 3.12) | Self-initializing counter logic, least-privilege IAM |
| Database | Amazon DynamoDB | On-demand billing, single-item table |
| Monitoring | CloudWatch + SNS | Alarm on Lambda errors, emailed on trigger |
| IaC | AWS CDK (Python) | Defines and deploys the entire stack |
| CI | GitHub Actions | Runs unit tests and `cdk synth` on every push |

## Notable engineering decisions

- **Origin Access Control over public bucket policy.** The S3 bucket blocks all public access; only CloudFront can read from it — a stricter, more current pattern than the public bucket-policy approach commonly shown in tutorials.
- **Least-privilege IAM.** The Lambda function is granted access to exactly one DynamoDB table (`grant_read_write_data`), rather than the broader managed policies used during initial manual prototyping.
- **Self-healing initialization.** The Lambda's `UpdateExpression` uses `if_not_exists(#c, :zero) + :incr`, so the counter atomically initializes and increments in a single DynamoDB call — no manual database seeding required after deployment.
- **Graceful failure handling.** A DynamoDB `ClientError` (e.g. a transient throttle) returns a clean `503` response instead of surfacing as a raw Lambda `500`.
- **One-command deploys.** `cdk deploy` provisions or updates the entire stack — S3, CloudFront, DynamoDB, Lambda, API Gateway, CloudWatch, SNS, and IAM roles — and uploads the site content, in a single run.
- **Real test coverage.** `tests/unit/` asserts against the actual deployed resources — DynamoDB billing mode, CloudFront distribution count, S3 public access block, the API route, and Lambda runtime — not the default CDK scaffold.

## Project structure

```
.github/workflows/
  ci.yml                        # Runs tests + cdk synth on every push
cdk_portfolio_project/
  app.py                        # CDK app entry point
  cdk_portfolio_project_stack.py  # Full infrastructure definition
lambda/
  visitor_counter.py            # Counter API logic
tests/unit/
  test_cdk_portfolio_project_stack.py  # Real assertions against the stack
website/
  index.html                    # Site content deployed to S3
  error.html
```

## Running this yourself

```bash
cdk bootstrap   # one-time per AWS account/region
cdk deploy
```

Outputs the live CloudFront URL, API endpoint, and SNS alert topic ARN on completion.

To run tests locally:
```bash
pip install -r requirements.txt
pip install pytest
pytest
```

## Roadmap

- [x] Static hosting on S3
- [x] CDN + HTTPS via CloudFront
- [x] Serverless visitor counter (Lambda + API Gateway + DynamoDB)
- [x] Full stack rebuilt as Infrastructure as Code (AWS CDK)
- [x] Real unit tests against deployed resources
- [x] CloudWatch alarm + SNS email alerts on Lambda errors
- [x] CI via GitHub Actions (tests + `cdk synth` on every push)
- [ ] CD (automated deploy on merge to main)
