import csv

csv_file = open("pupil_data.csv", "wb")

w = csv.writer(csv_file, delimiter=',', quotechar='"')

w.writerow([str([1,2]),1,2])
csv_file.flush()

w.writerow([str([1,2]),1,2])
csv_file.flush()

w.writerow([[1,2],1,2])
csv_file.flush()
w.writerow([[1,2],1,2])
csv_file.flush()
w.writerow([[1,2],1,2])
csv_file.flush()
w.writerow([[1,2],1,2])
csv_file.flush()
w.writerow([[1,2],1,2])
csv_file.flush()
w.writerow([[1,2],1,2])
csv_file.flush()
w.writerow([[1,2],1,2])
csv_file.flush()
w.writerow([[1,2],1,2])
csv_file.flush()
w.writerow([[1,2],1,2])
csv_file.flush()
w.writerow([[1,2],1,2])

csv_file.flush()

csv_file.close()

while True :
    print 'a'
