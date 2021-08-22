from nba_api.stats.endpoints import shotchartdetail
import json
import pandas
import csv
from PIL import Image
from flask import Flask, request, render_template
import io
import base64

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/get-ID', methods=['GET', 'POST'])
def getplayerid():
	playerid = request.form['search']

# creating csv file with all shots
	response1 = shotchartdetail.ShotChartDetail(
		team_id=0,
		player_id=playerid,
		context_measure_simple='FGA',
		season_nullable='2018-19',
		season_type_all_star='Regular Season'
	)

	content1 = json.loads(response1.get_json())

	results1 = content1['resultSets'][0]
	headers = results1['headers']
	rows = results1['rowSet']
	df1 = pandas.DataFrame(rows)
	df1.columns = headers

	df1.to_csv('all-shots.csv', index=False)

	# creating csv file with only made shots

	response2 = shotchartdetail.ShotChartDetail(
		team_id=0,
		player_id=playerid,
		context_measure_simple='PTS',
		season_nullable='2018-19',
		season_type_all_star='Regular Season'
	)

	content2 = json.loads(response2.get_json())

	results2 = content2['resultSets'][0]
	headers = results2['headers']
	rows = results2['rowSet']
	df2 = pandas.DataFrame(rows)
	df2.columns = headers

	df2.to_csv('made-shots.csv', index=False)

	imgpath = "/Users/pranayamurugan/Downloads/shotmap/final2.jpeg"
	img = Image.open(imgpath)
	datas = img.getdata()
	new_image_data = []
	for r in range(img.size[0] * img.size[1]):
		new_image_data.append(datas[r])

	all = open('/Users/pranayamurugan/Downloads/shotmap/all-shots.csv')
	made = open('/Users/pranayamurugan/Downloads/shotmap/made-shots.csv')

	reader = csv.reader(all, delimiter=',')

	for row in reader:
		if row[0] == "GRID_TYPE":
			continue
		x = 250 + int(row[17])
		y = 470 - (52 + int(row[18]))

		ind = 500 * (y - 1) + x
		for i in range(-1, 2):
			new_image_data[ind + i - 500] = (188, 52, 52)
			new_image_data[ind + i] = (188, 52, 52)
			new_image_data[ind + i + 500] = (188, 52, 52)

	reader1 = csv.reader(made, delimiter=',')
	for row in reader1:
		if row[0] == "GRID_TYPE":
			continue

		x = 250 + int(row[17])
		y = 470 - (52 + int(row[18]))

		ind = 500 * (y - 1) + x

		for i in range(-1, 2):
			new_image_data[ind + i - 500] = (52, 188, 102)
			new_image_data[ind + i] = (52, 188, 102)
			new_image_data[ind + i + 500] = (52, 188, 102)

	img.putdata(new_image_data)
	shots = img
	data = io.BytesIO()
	shots.save(data, "JPEG")
	encoded_img_data = base64.b64encode(data.getvalue())

	return render_template("map.html", img_data=encoded_img_data.decode('utf-8'))


if __name__ == '__main__':
	app.run()
