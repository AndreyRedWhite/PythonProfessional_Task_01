#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
import re
import json
from datetime import datetime
import os
import logging
import argparse

default_config = {
    "REPORT_SIZE": 1000,
    "reports": "./reports",
    "log": "./log",
    "logging": "./log/log_analyzer.log"
}

# Here we use a temp config for logging before either config_file or default_config would be loaded
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')


def setup_logging(config: dict) -> None:
    """
    Func to setup a logging for this script after a CONFIG dict was loaded. Basically it changes an output to
    logfile, provided by CONFIG, instead of STDOUT
    """
    logging.getLogger().handlers.clear()

    log_filename = config.get("logging", None)
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S'
    )


def find_latest_log(log_dir: str) -> tuple[str, str] | None:
    """This function searches in $log dir for the latest logfile of nginx regardless whether it gzipped or not"""

    regex = re.compile("nginx-access-ui\.log-(\d{8})(?:\.gz)?")

    log_files = [
        (file, datetime.strptime(regex.search(file).group(1), "%Y%m%d"))
        for file in os.listdir(log_dir) if regex.search(file)]

    if not log_files:
        return None

    latest_file, latest_date = max(log_files, key=lambda x: x[1])
    logging.info(f'Found a latest logfile: {latest_file}')
    return os.path.join(log_dir, latest_file), latest_date.strftime("%Y%m%d")


def log_reader(filepath: str) -> str:
    """Function for per-row processing a log file"""
    openers_map = {".gz": gzip.open, None: open}
    _, ext = os.path.splitext(filepath)
    opener = openers_map.get(ext, open)
    with opener(filepath, "rt", encoding="utf-8") as f:
        for line in f:
            yield line


def log_parser(line: str) -> tuple:
    """Func for parsing a row from a log file"""
    # log_regex = re.compile("\S+ \S+ \S+ \S+ (\S+).*?([\d.]+)$")
    log_regex = re.compile("\"(?:GET|POST|PUT|DELETE|HEAD) (\S+).*(\d+\.\d+)$")
    match = log_regex.search(line)
    if match:
        return match.group(1), float(match.group(2))


def process_log_file(filepath: str) -> dict:
    """Func for processing a log file"""

    result = {}
    errors = 0
    total_lines = 0

    for line in log_reader(filepath):
        total_lines += 1
        parsed_line = log_parser(line)
        if not parsed_line:
            errors += 1
        else:
            url, time = parsed_line
            if not url in result:
                result[url] = []
            result[url].append(time)
    error_rate = errors / total_lines if total_lines > 0 else 0
    if error_rate > 0.5:
        logging.error(f"Error rate too high: {error_rate:.2%}, which exceeds the threshold of 50%. Exiting.")
        exit(1)
    return result


def calculate_statistics(url_data: dict) -> dict:
    """This function should calculate statistic (counts a various timers for each URL) for a given dict"""

    statistics = {}
    total_requests = sum(len(times) for times in url_data.values())
    total_time = sum(sum(times) for times in url_data.values())

    for url, times in url_data.items():
        times_count = len(times)
        times_sum = round(sum(times), 3)
        times_avg = round(times_sum / times_count, 3)
        times_max = max(times)
        times_med = sorted(times)[times_count // 2]

        statistics[url] = {
            'count': times_count,
            'count_perc': round((times_count / total_requests) * 100, 3),
            'time_sum': times_sum,
            'time_perc': round((times_sum / total_time) * 100, 3),
            'time_avg': times_avg,
            'time_max': times_max,
            'time_med': times_med
        }
    return statistics


def limit_report_data(statistics: dict, report_size: int) -> list:
    """This function serves to limit an output data for just a REPORT_SIZE value provided with a config"""

    sorted_statistics = sorted(statistics.items(), key=lambda item: item[1]['time_sum'], reverse=True)
    top_statistics = sorted_statistics[:report_size]
    return top_statistics


def serialize_data_for_js(statistics: list) -> list:
    """This function just for converting an output data to a suitable for javascript format"""

    data_list = []
    for item in statistics:
        item[1]["url"] = item[0]
        data_list.append(item[1])
    return data_list


def readiness_check(last_log_date: str, report_path: str) -> bool:
    """This function check whether the latest log has already been parsed"""

    for report in os.listdir(report_path):
        if last_log_date in report:
            return True
    return False


def parse_args():
    """
    This function provides a simple CLI interface, that helps to provide an actual filepath of the config to the script
     """

    parser = argparse.ArgumentParser(description="Log Analyzer")
    parser.add_argument("--config", default="./new_config.json", help="Path to configuration file")
    return parser.parse_args()


def read_config(config_path: str, default_config: dict) -> dict:
    """This function reads a config file, loads an internal one and merges is into resulting config, giving an advantage
    for a fileconfig"""

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        try:
            file_config = json.load(f)
        except ValueError as e:
            raise ValueError(f"There was an error: {e}\nwhile parsing a config file: {file_config}")

    merged_config = {**default_config, **file_config}
    return merged_config


def main():
    logging.info("Started of executing a log_analyzer module. This log should go to STDOUT because config hasn't been"
                 "loaded yet. This message just for testing purposes")
    args = parse_args()
    try:
        config = read_config(args.config, default_config)
    except (FileNotFoundError, ValueError) as e:
        logging.error(e)
        exit(1)
    setup_logging(config)

    try:
        log_file_info = find_latest_log(config["log"])
        if log_file_info is None:
            logging.error("No log file was found.\nBreaking")
            return

        log_file, log_date = log_file_info
        if readiness_check(log_date, config["reports"]):
            logging.info(f"The latest logs from {log_file} has been already parsed")
            return

        statistics = calculate_statistics(process_log_file(log_file))
        top_statistics = limit_report_data(statistics, config["REPORT_SIZE"])
        resulted_data = serialize_data_for_js(top_statistics)
        data_for_report = json.dumps(resulted_data)

        with open('report_template.html', 'r') as file:
            template = file.read()

        report_html = template.replace('$table_json', data_for_report)

        with open(os.path.join(config["reports"], f"report_{log_date}.html"), "w", encoding="utf-8") as f:
            f.write(report_html)
        logging.info(
            f"The latest report 'report_{log_date}.html' was successfully generated and stored in: {config['reports']}")
    except Exception as e:
        logging.exception(f"Unexpected error occurred. Here's an exception: {e}")


if __name__ == "__main__":
    main()
