import requests

def modifyPoints(redA=0, redT=0, redE=0, blueA=0, blueT=0, blueE=0):
    request_type = "PATCH"
    request_url = "http://172.16.20.5:8080/api/scores"
    request_data = {}
    if redA != 0:
        request_data["redA"] = redA
    if redT != 0:
        request_data["redT"] = redT
    if redE != 0:
        request_data["redE"] = redE
    if blueA != 0:
        request_data["blueA"] = blueA
    if blueT != 0:
        request_data["blueT"] = blueT
    if blueE != 0:
        request_data["blueE"] = blueE
    requests.request(request_type, request_url, json=request_data)