#!/usr/bin/env python
import argparse
import csv
import glob
import json
import os

import gspread
from google.oauth2.service_account import Credentials


def init_gspread(key_file):
    scopes = [
        "https://spreadsheets.google.com/feeds",
        'https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    with open(key_file, 'r') as f:
        dic = json.load(f)
    credentials = Credentials.from_service_account_info(dic, scopes=scopes)
    gspread_client = gspread.authorize(credentials)
    return gspread_client


def get_all_values(gspread_client, sheet_id, worksheet_name=''):
    spreadsheet = gspread_client.open_by_key(sheet_id)
    if worksheet_name == '':
        worksheet = spreadsheet.worksheets()[0]
    else:
        worksheet = spreadsheet.worksheet(worksheet_name)
    return worksheet.get_all_values()


def is_downloaded(output_folder, sheet_id):
    pattern = os.path.join(output_folder, f"doc-id_{sheet_id}*.csv")
    matching_files = glob.glob(pattern)

    return len(matching_files) > 0


def save_to_csv(data, output_folder, sheet_name, worksheet_name, sheet_id):
    output_file = os.path.join(output_folder,
                               f"doc-id_{sheet_id}_spreadsheet_{sheet_name}_worksheet_{worksheet_name}.csv")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Google Sheet Downloader")
    parser.add_argument('--key-file', required=True, help="Google service account key JSON file path")
    parser.add_argument('--sheet-ids', required=True, help="Comma separated Google sheet IDs to download")
    parser.add_argument('--output-folder', required=True, help="Output folder path for CSV files")
    parser.add_argument('--force', action='store_true', help="Force download and ignore cache")

    return parser.parse_args()


def download_google_sheets(key_file, sheet_ids, output_folder, force):
    gspread_client = None

    for sheet_id in sheet_ids.split(','):
        if not force and is_downloaded(output_folder, sheet_id):
            print(f"Skipping: Sheet ID {sheet_id} (Already downloaded)")
            continue

        if gspread_client is None:
            gspread_client = init_gspread(key_file)

        sheet = gspread_client.open_by_key(sheet_id)
        for worksheet in sheet.worksheets():
            sheet_name = sheet.title
            worksheet_name = worksheet.title
            print(f"Checking: {sheet_name} - {worksheet_name}")

            data = get_all_values(gspread_client, sheet_id, worksheet_name)
            save_to_csv(data, output_folder, sheet_name, worksheet_name, sheet_id)
            print(f"Saved: {sheet_name} - {worksheet_name}")


def main():
    args = parse_arguments()
    download_google_sheets(args.key_file, args.sheet_ids, args.output_folder, args.force)


if __name__ == '__main__':
    main()
