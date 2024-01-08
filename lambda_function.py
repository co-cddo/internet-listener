import json
import gzip
import boto3
import random
import string
import os
import base64


from datetime import datetime


S3_BUCKETNAME = os.getenv("S3_BUCKETNAME")
S3_PREFIX = os.getenv("S3_PREFIX")
CLOUDFRONT_SECRET = os.getenv("CLOUDFRONT_SECRET", "")


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
        csp_report["blocked_uri"] = csp_report["blockedURL"]
        del csp_report["blockedURL"]

    if "documentURL" in csp_report:
        csp_report["document_uri"] = csp_report["documentURL"]
        del csp_report["documentURL"]

    if "effectiveDirective" in csp_report:
        csp_report["effective_directive"] = csp_report["effectiveDirective"]
        del csp_report["effectiveDirective"]

    if "originalPolicy" in csp_report:
        csp_report["original_policy"] = csp_report["originalPolicy"]
        del csp_report["originalPolicy"]

    if "statusCode" in csp_report:
        csp_report["status_code"] = csp_report["statusCode"]
        del csp_report["statusCode"]
    return csp_report


def process_csp_report(event: dict) -> dict:
    res = []
    try:
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
    except Exception as e:
        print("process_csp_report:error:", e)
    return res


def lambda_handler(event, context):
    if "headers" in event:
        if "x-cloudfront" in event["headers"]:
            if event["headers"]["x-cloudfront"] == CLOUDFRONT_SECRET:
                del event["headers"]["x-cloudfront"]

                obj = {"event": event, "context": context}

                if is_csp_report(event):
                    obj["csp"] = process_csp_report(event)

                jprint(obj)
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "text/html; charset=utf-8",
                    },
                    "body": "OK",
                    "isBase64Encoded": False,
                }
    return {
        "statusCode": 502,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
        },
        "body": "Bad Gateway",
        "isBase64Encoded": False,
    }
