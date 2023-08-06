
import sys, os, json, time, requests, csv
from datetime import datetime
import pandas as pd
from collections import ChainMap
from urllib.parse import urlsplit, quote as urlquote

from requests.exceptions import ConnectionError

from eigeningenuity.core.debug import _debug

def _do_eigen_json_request(requesturl,**params):

    if params:
        if "?" in requesturl:
            sep = "&"
        else:
            sep = "?"

        for k,v in params.items():
            if v is None:
               pass
            else:
                for e in force_list(v):
                    if not isinstance(e, str):
                        if isinstance(e, str):
                            e = e.encode("utf8")
                        else:
                            e = str(e)
                    requesturl += sep + urlquote(k) + "=" + urlquote(e.encode("UTF8"))

                    sep = "&"


    _debug("DEBUG",requesturl)
    if 'DEBUG' in os.environ and os.environ['DEBUG']:
        print("DEBUG: [" + requesturl + "]", file=sys.stderr)

    try:
        data = requests.get(requesturl, verify=False)
    except ConnectionError as e:
        # sys.tracebacklimit = 0
        raise EigenException("No Response from ingenuity instance at https://" + requesturl.split("/")[2] + ". Please check this is correct url and that the instance is currently running") from None


    if data.text.startswith("ERROR:"):
        if "UNKNOWN TAG" in data.text:
            raise RemoteServerException(data.text)
        raise RemoteServerException(data.text.split("\n")[1], requesturl)
    elif data.text.startswith("EXCEPT:") and data.status_code != 200:
        raise RemoteServerException( data.text.split("\n")[0], "API could not parse request, check query syntax is correct",)
    else:
        try:
            ret = data.json()
        except ValueError:
            ret = data.text

    return ret

def _do_eigen_post_request(posturl,data):
    requests.post(posturl,data, verify=False)
    pass

def is_list(x):
    return type(x) in (list, tuple, set)

def force_list(x):
    if is_list(x):
        return x
    else:
        return [x]

def number_to_string(n):
    if type(n) == float:
        return format(n, '^12.5f')
    else:
        return n

def time_to_epoch_millis(t):
    if type(t) == datetime:
        epochmillis = time.mktime(t.timetuple()) * 1000
    elif type(t) == tuple:
        epochmillis = time.mktime(t) * 1000
    elif type(t) == int and t > 100000000000:
        epochmillis = t
    elif type(t) == int:
        epochmillis = t*1000
    elif type(t) == float and t > 100000000000:
        epochmillis = int(t)
    elif type(t) == float:
        epochmillis = int(t)*1000
    elif type(t) == str:
        epochmillis = get_timestamp(t)
    else:
        raise EigenException("Unknown time format " + str(type(t)))
    return int(round(epochmillis))

def get_time_tuple(floatingpointepochsecs):
    time_tuple = time.gmtime(floatingpointepochsecs)
    return time_tuple

def get_timestamp_string(t):
    pattern = '%Y-%m-%d %H:%M:%S UTC'
    s = datetime.fromtimestamp(t).strftime(pattern)
    return s

def get_timestamp(t):
    if type(t) == str:
        try:
            pattern = '%Y-%m-%d %H:%M:%S.%f'
            epochmillis = time.mktime(time.strptime(t, pattern))
        except ValueError:
            try:
                pattern = '%Y-%m-%dT%H:%M:%S.%f%z'
                epochmillis = time.mktime(time.strptime(t, pattern))
            except ValueError:
                try:
                    pattern = '%Y-%m-%d %H:%M:%S'
                    epochmillis = time.mktime(time.strptime(t, pattern))
                except ValueError:
                    try:
                        pattern = '%Y-%m-%d'
                        epochmillis = time.mktime(time.strptime(t, pattern))
                    except ValueError:
                        try:
                            epochmillis = int(t)
                        except ValueError:
                            raise EigenException("Unknown time format " + str(type(t)))

    else:
        epochmillis = time_to_epoch_millis(t)
    return epochmillis



def get_datetime(t):
    timestamp = get_timestamp(t)
    return datetime.fromtimestamp(timestamp)

def pythonTimeToServerTime(ts):
# where ts may be supplied as time tuple, datetime or floating point seconds, and server time is (obviously) millis.
    if type(ts) == datetime:
        epochmillis = time.mktime(ts.timetuple()) * 1000
    elif type(ts) == tuple:
        epochmillis = time.mktime(ts) * 1000
    elif type(ts) == float:
        epochmillis = int(ts * 1000)
    else:
        raise EigenException("Unknown python time format " + str(type(ts)))
    return int(round(epochmillis))


def serverTimeToPythonTime(ts):
# where ts is millis and the returned value is consistently whatever we're using internally in the python library (i.e. floating secs)
    return ts / 1000.0

def pythonTimeToFloatingSecs(ts):
# where ts may be supplied as time tuple, datetime or floating point seconds
    if type(ts) == datetime:
        return time.mktime(ts.timetuple())
    elif type(ts) == tuple:
        return time.mktime(ts)
    elif type(ts) == float or type(ts) == int:
        return ts
    else:
        raise EigenException("Unknown python time format " + str(type(ts)))

def pythonTimeToTuple(ts):
# where ts may be supplied as time tuple, datetime or floating point seconds
    if type(ts) == datetime:
        return ts.timetuple()
    elif type(ts) == tuple:
        return ts
    elif type(ts) == float:
        return ts
    else:
        raise EigenException("Unknown python time format " + str(type(ts)))

def pythonTimeToDateTime(ts):
# where ts may be supplied as time tuple, datetime or floating point seconds
    if type(ts) == datetime:
        return ts
    elif type(ts) == tuple:
        epochmillis = time.mktime(ts) * 1000
        return datetime.fromtimestamp(epochmillis)
    elif type(ts) == float:
        return time.gmtime(ts)
    else:
        raise EigenException("Unknown python time format " + str(type(ts)))

def map_java_exception(myExceptionName, params):
    if myExceptionName == "urllib2.HTTPError":
         return RemoteServerException(params)
#    elif: ...
    else:
        return EigenException(myExceptionName)

def parse_duration(timeWindow):
    unit = timeWindow[-1:]
    value = timeWindow[:-1]

    def seconds():
        int(value)

    def minutes():
        return int(value) * 60

    def hours():
        return int(value) * 3600

    def days():
        return int(value) * 3600 * 24

    def months():
        return int(value) * 3600 * 24 * 30

    def years(): int(value) * 3600 * 24 * 365

    options = {"s" : seconds,
               "m" : minutes,
               "h" : hours,
               "d" : days,
               "M" : months,
               "y" : years,
    }

    duration = options[unit]()*1000

    return duration


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def cypherRespMap(resp):
    return resp["m"]


def jsonToDf(json,transpose:bool=False):
    p = {}
    keys = json.keys()
    if "unknown" in keys: keys.remove("unknown")
    for key in keys:
        if type(json[key]) == list:
            m = list(map(dataMap,json[key]))
            n = dict(ChainMap(*m))
        else:
            n = dataMap(json[key])
        p[key] = n
    try:
        df = pd.DataFrame(p)
        if transpose:
            df = df.T
        return(df[::-1])
    except ValueError:
        return(pd.Series(p))

def dataMap(j):
    try:
        h = {datetime.fromtimestamp(j["timestamp"] / 1000): j["value"]}
    except:
        h = j
    return h

def flattenList(list):
    return [item for sublist in list for item in sublist]

def flattenDict(nestedDict):
    points = []
    keys = nestedDict.keys()
    for key in keys:
        values = nestedDict[key]
        for value in force_list(values):
            tag = {"tag": key}
            tag.update(value)
            points.append(tag)
    return points

def aggMap(x):
    for k in x[1]:
        k["tag"] = x[0]
    return x[1]

def aggToDf(x):
    y = flattenList(list(map(aggMap,x.items())))
    cols = ["tag", "start", "end", "min", "max", "avg", "var", "stddev", "numgood", "numbad"]
    df = pd.DataFrame(y)
    df = df[cols]
    df["start"] = pd.to_datetime(df["start"].apply(lambda s: s.split("+")[0]), unit="ms")
    df["end"] = pd.to_datetime(df["end"].apply(lambda s: s.split("+")[0]), unit="ms")
    df.sort_values(by='start', inplace=True)
    return(df)

def get_eigenserver(url):
    split_url = urlsplit(url)
    return split_url.scheme + "://" + split_url.netloc

def constructURL(y,x):
    x["url"] = y + x["url"]
    k = {"fileName": x["fileName"], "description": x["description"], "url": x["url"]}
    return k

def parseEvents(events):
    if type(events) == dict or type(events) == list:
        events = events
    elif type(events) == str:
        try:
            with open(events,"r") as f:
                events = json.loads(f.read())
        except FileNotFoundError:
            try:
                events = json.loads(events)
            except json.decoder.JSONDecodeError:
                raise EigenException("Could not parse input, enter the path to a file, or a json/dict object")
    try:
        events = events["events"]
    except:
        pass
    events = force_list(events)
    return events

def parse_properties(x):
    return x["graphapi"]["properties"]

def csvWriter(data,historian,filepath,multi_csv,functionName,order=None,headers=False):
    if "Agg" in functionName:
        timeField = 'start'
    else:
        timeField = 'timestamp'
    if multi_csv:
        for item in data:
            sortedDicts=[]
            for entry in force_list(data[item]):
                if order is not None:
                    entry = (dict(sorted(entry.items(), key=lambda item: order.index(item[0]))))
                sortedDicts.append(dict(entry.items()))
            sortedList = sorted(sortedDicts, key=lambda d: (d[timeField])) 
            keys = sortedList[0].keys()
            if filepath is None:
                filepath = item + "-" + functionName + "-" + str(round(datetime.now().timestamp())) + ".csv"
            elif filepath[-1] == "/":
                filepath += item +  "-" + functionName + "-" + str(round(datetime.now().timestamp())) + ".csv"
            else:
                filepath = item +  "-" + functionName + "-" + str(round(datetime.now().timestamp())) + ".csv"

            with open(filepath, 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                if headers:
                    dict_writer.writeheader()
                dict_writer.writerows(sortedList)
        return True       
    else:
        sortedDicts = []
        points = flattenDict(data)
        for entry in points:
            if order is not None:
                entry = dict(sorted(entry.items(), key=lambda item: order.index(item[0])))
            sortedDicts.append(entry)
        sortedList = sorted(sortedDicts, key=lambda d: (d['tag'], d[timeField])) 
        keys = sortedList[0].keys()
        if filepath is None:
            filepath = historian +  "-" + functionName + "-" + str(round(datetime.now().timestamp())) + ".csv"
        elif filepath[-1] == "/":
            filepath += historian +  "-" + functionName + "-" + str(round(datetime.now().timestamp())) + ".csv"

        with open(filepath, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            if headers:
                dict_writer.writeheader()
            dict_writer.writerows(sortedList)
            return True



class EigenException (Exception): pass
class RemoteServerException (EigenException): pass
