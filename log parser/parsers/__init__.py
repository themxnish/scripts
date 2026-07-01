from . import apache, syslog, json, generic, csv_parser

LINE_PARSERS = {
    "apache": apache,
    "syslog": syslog,
    "json": json,
}