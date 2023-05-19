import csv

with open('media_dump/movies.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    sorted_rows = sorted(reader, key=lambda row: row[4], reverse=True)  # Sort by Age column

with open('media_dump/sorted_movies.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for row in sorted_rows:
        writer.writerow(row)
