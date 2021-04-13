from xml.dom import minidom
from mkw_ghosts import MkwGhosts
from mii import Mii
import raceutil
import io


def create_top_10(amount):

	#creating the xml document
	returned_packet = minidom.Document()
	returned_packet.toxml(encoding="UTF-8")
	xml = returned_packet.createElement('RankingDataResponse') #xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://gamespy.net/RaceService/"')
	xml.setAttribute('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
	xml.setAttribute('xmlns:xsd', "http://www.w3.org/2001/XMLSchema")
	xml.setAttribute('xmlns', "http://gamespy.net/RaceService/")
	returned_packet.appendChild(xml)
	responseCode = returned_packet.createElement('responseCode')
	responseCodeValue = returned_packet.createTextNode("0")
	responseCode.appendChild(responseCodeValue)
	xml.appendChild(responseCode)
	dataArray = returned_packet.createElement('dataArray')
	numrecords = returned_packet.createElement('numrecords')
	data = returned_packet.createElement('data')

	#open ghosts and write their data to a list
	ghosts = []
	for i in range(amount):
		with open(f'ghost{i+1}.rkg', 'rb') as g:
			ghosts.append(g.read())
			g.close()

	#read the time data from the ghost and append it to an xml text node
	timevalues = []
	for ghost in ghosts:
		ghost_obj = MkwGhosts.from_bytes(ghost)
		timevalue = returned_packet.createTextNode(str(raceutil.channel_time_parse(str(ghost_obj.finishing_time_minutes) + ':' + str(ghost_obj.finishing_time_seconds).zfill(2) + '.' + str(ghost_obj.finishing_time_milliseconds).zfill(3))))
		timevalues.append(timevalue)

	#creating mii data aka userdata from the ghost
	userdatas = []
	for i, ghost in enumerate(ghosts):

		encode = raceutil.create_base64_encode(ghosts[i], ghost_obj.country_code)	
		userdatas.append(encode)

	#creating rankingdata, which is pid + rank + time + miidata, this is the container for each leaderboard entry
	rankingdatas = []
	for i in range(amount):
		RankingData = returned_packet.createElement('RankingData')
		ownerid = returned_packet.createElement('ownerid')
		owneridvalue = returned_packet.createTextNode('600000000')
		ownerid.appendChild(owneridvalue)
		rank = returned_packet.createElement('rank')
		rankValue = returned_packet.createTextNode(str(i))
		rank.appendChild(rankValue)
		userdata = returned_packet.createElement('userdata')
		userdataValue = returned_packet.createTextNode(str(userdatas[i])[2:-1])
		userdata.appendChild(userdataValue)
		time = returned_packet.createElement('time')
		time.appendChild(timevalues[i])
		RankingData.appendChild(ownerid)
		RankingData.appendChild(rank)
		RankingData.appendChild(time)
		RankingData.appendChild(userdata)
		rankingdatas.append(RankingData)

	#append all of the ranking data nodes to the main data node
	for i in range(amount):
		data.appendChild(rankingdatas[i])


	numrecordsValue = returned_packet.createTextNode(str(amount))
	numrecords.appendChild(numrecordsValue)
	dataArray.appendChild(numrecords)
	dataArray.appendChild(data)
	xml.appendChild(dataArray)
	xml_str = returned_packet.toxml(encoding="utf-8")

	#write the response to a file, for many reasons including debugging and also for the sake of having a valid response handy
	f = open('last_response.xml', 'wb+')
	f.write(xml_str)
	f.close()

	#send the xml to be returned to the client
	return xml_str

create_top_10(10)