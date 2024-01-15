import json
import gzip
import boto3
import random
import string
import os
import base64
import re


from datetime import datetime


S3_BUCKETNAME = os.getenv("S3_BUCKETNAME")
S3_PREFIX = os.getenv("S3_PREFIX")
CLOUDFRONT_SECRET = os.getenv("CLOUDFRONT_SECRET", "")

raw_egr = os.getenv("ENABLE_GENERIC_REQUESTS", "true")
ENABLE_GENERIC_REQUESTS = (
    raw_egr.lower()[0] in ["t", "1"] if raw_egr and len(raw_egr) > 0 else False
)
print("ENABLE_GENERIC_REQUESTS:", ENABLE_GENERIC_REQUESTS)

raw_acs = os.getenv("ALLOWED_CSP_SOURCES", "")
ALLOWED_CSP_SOURCES = [
    x.strip().strip(".")
    for x in raw_acs.lower().split(",")
    if len(x.strip().strip(".")) > 0
]
print("ALLOWED_CSP_SOURCES:", ALLOWED_CSP_SOURCES)


def normalise_dict(d: dict = None, prefix: str = ""):
    if d and type(d) == dict:
        res = {}
        for k in d:
            new_k = (
                (prefix + "_" + k)
                .replace("-", "_")
                .replace(" ", "_")
                .strip()
                .strip("_")
            )
            if type(d[k]) == dict:
                res.update(normalise_dict(d[k], prefix=new_k))
            elif type(d[k]) == list:
                counter = 0
                for item in d[k]:
                    res.update(normalise_dict(item, prefix=(new_k + f"_{counter}")))
                    counter += 1
            else:
                res[new_k] = d[k]
        return res
    return {}


def jprint(d=None, *argv):
    res = None

    try:
        if type(d) != dict:
            d = {"message": str(d)}
        if argv:
            if "message" not in d:
                d["message"] = ""
            for a in argv:
                if type(a) == dict:
                    d.update(a)
                else:
                    d["message"] += " " + str(a)
            d["message"] = d["message"].strip()
    except:
        d = {}

    now = datetime.now()
    d = normalise_dict({"_datetime": now.strftime("%Y-%m-%d %H:%M:%S.%f"), **d})
    res = json.dumps(d, default=str)

    if S3_BUCKETNAME and S3_PREFIX:
        gzip_object = gzip.compress(res.encode("utf-8"))

        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        ts = now.strftime("%Y%m%d-%H%M%S")
        rd = "".join(random.choice(string.ascii_letters) for i in range(10))
        key = f"{S3_PREFIX}/{year}/{month}/{day}/{ts}_{rd}.json.gz"

        print(f"Logging {len(gzip_object)} bytes to s3://{S3_BUCKETNAME}/{key}")
        s3client = boto3.client("s3", region_name="eu-west-2")
        s3_resp = s3client.put_object(Bucket=S3_BUCKETNAME, Body=gzip_object, Key=key)
        print(json.dumps(s3_resp, default=str))

    print(res)


def is_csp_report(event: dict) -> bool:
    if not "headers" in event:
        return False
    if not "x-true-host" in event["headers"]:
        return False
    if not event["headers"]["x-true-host"].startswith("csp"):
        return False
    if not "content-type" in event["headers"]:
        return False
    if not event["headers"]["content-type"] in [
        "application/reports+json",
        "application/csp-report",
    ]:
        return False
    if not "body" in event:
        return False
    if not event["body"] or len(event["body"]) == 0:
        return False

    return True


def normalise_csp_report(csp_report: dict):
    if "blockedURL" in csp_report:
        csp_report["blocked-uri"] = csp_report["blockedURL"]
        del csp_report["blockedURL"]

    if "documentURL" in csp_report:
        csp_report["document-uri"] = csp_report["documentURL"]
        del csp_report["documentURL"]

    if ALLOWED_CSP_SOURCES:
        raw_docuri = csp_report.get("document-uri", "")
        matched_domain = re.search(r"^\w+://([^/]+)", raw_docuri)
        if not matched_domain:
            raise Exception("Invalid domain in document-uri", raw_docuri)
        parsed_domain = matched_domain.group(1).lower()
        valid_domain = False
        for x in ALLOWED_CSP_SOURCES:
            if parsed_domain == x:
                valid_domain = True
                break
            if parsed_domain.endswith("." + x):
                valid_domain = True
                break
        if not valid_domain:
            raise Exception("Not authorised domain in document-uri", parsed_domain)

    if "effectiveDirective" in csp_report:
        csp_report["effective-directive"] = csp_report["effectiveDirective"]
        del csp_report["effectiveDirective"]

    if "originalPolicy" in csp_report:
        csp_report["original-policy"] = csp_report["originalPolicy"]
        del csp_report["originalPolicy"]

    if "statusCode" in csp_report:
        csp_report["status-code"] = csp_report["statusCode"]
        del csp_report["statusCode"]
    return csp_report


def process_csp_report(event: dict) -> dict:
    res = []

    body = event["body"]
    if "isBase64Encoded" in event and event["isBase64Encoded"]:
        body = base64.b64decode(body)
    jcsp = json.loads(body)
    if type(jcsp) != list and "csp-report" in jcsp:
        res = [normalise_csp_report(jcsp["csp-report"])]
    elif type(jcsp) == list and len(jcsp) > 0:
        for item in jcsp:
            if "body" in item:
                res.append(normalise_csp_report(item["body"]))

    return res


def bad_response():
    return {
        "statusCode": 502,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
        },
        "body": "Bad Gateway",
        "isBase64Encoded": False,
    }


def lambda_handler(event, context):
    xcf = event.get("headers", {}).get("x-cloudfront", "")
    if xcf:
        del event["headers"]["x-cloudfront"]

    if CLOUDFRONT_SECRET != xcf:
        return bad_response()

    obj = {"event": event, "context": context}

    handle_request = ENABLE_GENERIC_REQUESTS

    if is_csp_report(event):
        try:
            obj["csp"] = process_csp_report(event)
            handle_request = True
        except Exception as e:
            print("lambda_handler:process_csp_report:error:", e)
            handle_request = False

    if handle_request:
        jprint(obj)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/html; charset=utf-8",
            },
            "body": "OK",
            "isBase64Encoded": False,
        }

    return bad_response()
