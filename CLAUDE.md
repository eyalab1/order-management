# CLAUDE.md - Event-Driven Serverless Order Management System

This file is the shared source of truth for both partners and their Claude Code
sessions. Read it fully before writing any code. If a decision changes, update this
file and tell your partner so both sides stay in sync.

## 1. What we are building

A cloud-based, serverless, event-driven Order Management System on AWS (Learner Lab).
Orders are managed through REST APIs. Deleting an order triggers asynchronous side
effects (email notification + backup) that must NOT block the delete response. A
report API builds a PDF summary of deleted orders. A web client (hosted on AWS
Amplify) calls the APIs and displays results.

Total grade is 100 points. The full assignment PDF is the binding spec; this file is
our plan for meeting it. When in doubt, the PDF wins.

### Point map
| Area | Points | Owner |
|---|---|---|
| Order Management: `orders` table + 5 CRUD APIs | 55 | A (Delete API: B) |
| Notification subscription (register / unsubscribe) | 10 | B |
| Async email notification on delete | 10 | B |
| Async S3 TXT backup on delete | 5 | B |
| PDF summary download API | 5 | B |
| Freestyle enhancement | 5 | B |
| Web client (HTML/CSS/JS on Amplify) | 10 | A |

## 2. Team and ownership

- Partner A = Eyal Abisdris. Owns: `orders` table design, the Create / Get-all /
  Get-one / Update Lambdas and their API Gateway routes, and the web client.
- Partner B = Daniel Buts. Owns: the Delete Lambda, the DynamoDB Streams
  processor, SNS notification subscriptions, S3 TXT backup, the PDF summary API, and
  the freestyle enhancement.

Rule of thumb: Partner B owns "everything that happens when an order is deleted, plus
notifications, reporting, and freestyle." Partner A owns "everything else, plus the
client."

## 3. Architecture

```
Web client (Amplify)
        |
   API Gateway (one shared REST API)
        |
   +----+----+----+----+----+----------------+----------------+
   |    |    |    |    |                      |                |
 Create GetAll GetOne Update  Delete      Subscribe        PDF Summary
 (A)   (A)   (A)    (A)     (B)         /Unsubscribe (B)   (B)
                              |              |                |
                         DynamoDB "orders"  SNS topic    reads S3 .txt,
                              |              (emails)     builds PDF,
                              | Streams (REMOVE)          uploads PDF,
                              v                           returns URL
                     Stream-processor Lambda (B)
                        |                  |
                   publish to SNS     write .txt backup
                   (notify emails)    to S3 bucket
```

Key principle: the Delete Lambda only removes the item from DynamoDB and returns
immediately. DynamoDB Streams (REMOVE event) drives the async work, so the user is
never blocked by notification or backup. This is the seam between A and B.

## 4. Shared contract (DO NOT change unilaterally)

### 4.1 Order item schema (`orders` table)
Both partners depend on this exact shape. Partner A owns the table but the schema is
agreed by both.

```json
{
  "orderId":      "string (UUID v4) - partition key",
  "creationDate": "string (ISO 8601, e.g. 2026-05-27T10:00:00Z)",
  "price":        "number",
  "description":  "string",
  "lastModified": "string (ISO 8601)"
}
```

- Partition key: `orderId` (UUID). Justification for the report: a UUID uniquely
  identifies each order, needs no central counter, and is safe under concurrent
  creates in a serverless system.
- "Get all orders sorted by creation date": Partner A sorts by `creationDate` in the
  Lambda after a Scan (acceptable for project scale). If we later need it at scale,
  add a GSI with a fixed partition value and `creationDate` as the sort key. Decide
  together before changing.

### 4.2 Deletion event
Because DynamoDB Streams is the trigger, the event IS the deleted order item (the
schema above, in the stream's `OldImage`). Partner B reads `OldImage` from the REMOVE
record. No separate event format to maintain.

### 4.3 Naming conventions (so resources do not collide)
- DynamoDB table: `orders`
- S3 bucket (backups + PDFs): `oms-backups-<accountId>` (must be globally unique)
- SNS topic: `oms-order-deleted`
- Lambdas: `oms-create-order`, `oms-get-all-orders`, `oms-get-order`,
  `oms-update-order`, `oms-delete-order`, `oms-stream-processor`,
  `oms-subscribe`, `oms-unsubscribe`, `oms-pdf-summary`
- API Gateway: one REST API named `oms-api`. Routes below.

### 4.4 API surface (shared)
| Operation | Method | Path | Owner |
|---|---|---|---|
| Create order | POST | /orders | A |
| Get all orders | GET | /orders | A |
| Get one order | GET | /orders/{orderId} | A |
| Update order | PUT | /orders/{orderId} | A |
| Delete order | DELETE | /orders/{orderId} | B |
| Subscribe email | POST | /subscriptions | B |
| Unsubscribe | DELETE | /subscriptions | B |
| PDF summary | GET | /reports/deleted-orders | B |
| Translate description | POST | /orders/{orderId}/translate | B |

All responses are JSON. The PDF summary returns the download URL in the response body
(never only in logs).

## 5. AWS Learner Lab logistics

Each student has a separate Learner Lab account. To avoid integration pain:
- Pick ONE account as the integration / demo / submission account. All final
  resources live there and the recorded test flows run there.
- During development each partner may build in their own account, then redeploy their
  pieces into the integration account before submission.
- DECIDED: the integration account is Eyal Abisdris's (Partner A) Learner Lab account.
  All shared resources (orders table, Lambdas, SNS topic, S3 bucket, API Gateway,
  Amplify) live there. Partner B deploys into it using the lab's temporary "AWS
  Details" credentials shared by Eyal each session.
- The web client (Amplify) and the final base API URL live in the integration
  account.

## 6. API Gateway sharing

We use ONE REST API (`oms-api`) so all endpoints share a base URL. To avoid
overwriting each other:
- Agree on the resource paths above before deploying.
- Coordinate deploys: whoever owns the integration account does the final "Deploy
  API" after both sides' routes are merged.
- Record the deployed base URL here once stable:
  Base API URL: https://ia2iwtvws0.execute-api.us-east-1.amazonaws.com/prod
  (REST API "oms-api", stage "prod", region us-east-1)

## 7. Client rules (Partner A)

- Web client: HTML + CSS + JavaScript, hosted on AWS Amplify.
- The client only calls APIs and displays results. NO business logic in the client.
- Always display the raw result returned from the backend for every operation.
- Cover every API: create, list, get one, update, delete, subscribe, unsubscribe,
  PDF summary, and the freestyle feature's UI.
- Using GenAI to build the client is explicitly allowed and recommended by the spec.

## 8. Freestyle enhancement (Partner B)

Pick one AWS service available in the Learner Lab, add clear, demonstrable value, and
make it visible in the UI. Candidate ideas (choose one):
- Amazon Translate: translate an order description, show result in the client.
- Amazon Polly: read order details aloud in the client.
- CloudWatch dashboard: surface order metrics from a UI button.

DECIDED: chosen freestyle service: Amazon Translate
- Lambda: oms-freestyle
- Route: POST /orders/{orderId}/translate
- Body: { "targetLanguage": "es" }
- Translates the order description to the target language.
- Returns both original and translated description.
- Supported languages: es, fr, de, ar, he, zh
- IAM permission needed: translate:TranslateText

## 9. Deliverables (one Word document)

Each partner fills in their own rows; one person assembles the final document.
- AWS diagram + short explanation: one partner draws, both review.
- "AWS Setup per service" table: each partner adds the services they own, with a CLI
  command that runs successfully in the Learner Lab.
- "APIs List" table: each partner adds their own API rows (name, method, URL, sample
  input, sample output).
- Client URL (Amplify) and/or code: Partner A.
- List of tested flows with screenshots: each partner documents their own flows; the
  set must cover all functionality end to end.
- Freestyle explanation + screenshot: Partner B.
- Delete Order Lambda code (required as a code listing): Partner B.

## 10. Working agreement / how we stay in sync

- This file is the contract. Any change to schema, naming, paths, or ownership goes
  here first, then a message to the other partner.
- Keep your Lambda code in this repo under `partner-a/` and `partner-b/` so both
  sessions can read each other's code. Suggested layout:
  ```
  order-management-project/
    CLAUDE.md
    partner-a/   (table, create/getall/getone/update, web client)
    partner-b/   (delete, stream processor, subscribe/unsubscribe, pdf, freestyle)
    docs/        (Word doc drafts, diagram, screenshots)
  ```
- Test the seam early: as soon as the table exists and the Delete + stream processor
  exist, run one full delete and confirm an email arrives and a .txt lands in S3.

## 11. Open decisions checklist
- [x] Integration account owner (section 5): Eyal Abisdris (Partner A)
- [x] Deployed base API URL (section 6): https://ia2iwtvws0.execute-api.us-east-1.amazonaws.com/prod
- [x] Freestyle service (section 8): Amazon Translate — POST /orders/{orderId}/translate
- [ ] Who assembles the final Word document
- [ ] GSI vs in-Lambda sort for "get all" (section 4.1), only if needed

## 12. Definition of done (build order, not a timeline)
1. Agree schema + naming (this file) and create the `orders` table.
2. A: Create / GetAll / GetOne / Update Lambdas + routes working via API Gateway.
3. B: Delete Lambda + DynamoDB Streams enabled.
4. B: Stream processor publishes to SNS and writes the S3 .txt backup.
5. B: Subscribe / Unsubscribe APIs working (real email confirmation).
6. B: PDF summary API returns a working download URL.
7. A: Web client wired to every API, deployed on Amplify.
8. B: Freestyle enhancement implemented and visible in the UI.
9. Both: record tested flows with screenshots; assemble the Word document.
