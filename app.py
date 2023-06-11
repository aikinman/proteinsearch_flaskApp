# Automated Antibody Search
# Kaitlin Sullivan - UBC March 2020
# Updated 11june23 AIK

# This code uses selenium webdriver to automate search for antibodies based on marker genes found via scRNA-seq
# Input: a dataframe containing uniquely upregulated marker genes for a given cluster

# REQUIREMENTS: 
# cd to location of code
# Make a virutal env: python3 -m venv venv
# Activate venv: source venv/bin/activate
# Download dependencies to this venv: python3 -m pip install -r requirements.txt
# Download selenium in terminal using the command: pip install selenium
# Download Chrome driver via https://chromedriver.chromium.org/downloads
# Input the file path for chromedriver on LINE 42


###############SET UP#################
#Import flask - AIK 26may23
from flask import Flask, render_template, request, make_response, Response, redirect, url_for, send_file
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import io
import pandas as pd

#create flask app - AIK 26may23
app = Flask(__name__)

@app.route('/template.html')
def template():
    return render_template('template.html')

#added upload function fed to flask app - AIK 26may23
@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Handle file upload logic here
        csv_file = request.files['csv_file']
        
        # Example code to save the uploaded file
        csv_file.save(csv_file.filename)
	
        # Redirect to the search route and pass the filename as a parameter
        return redirect(url_for('search', filename=csv_file))

    return render_template('template.html', title='Welcome to Protein Search')


#define a route for the home page (ensure HTML file is in same sirectory) - AIK 26may23
@app.route('/')
def index():
    return render_template('index.html')

#re-wrote original python code to route to flask app and template.html for styling - AIK 26mar23
@app.route('/search', methods=['GET', 'POST'])
def search():
	co = ["Gene", "FullName", "Region", "Antibody", "Neurons", "Glia", "pct1", "pct2"]
	df = pd.DataFrame(columns=co)
	
	#toOpen = pd.read_csv(request.files['file'])
	csv_file = request.files['csv_file']
	markers = pd.read_csv(csv_file)

	#create empty list to store antibody search stuff - AIK 26may23
	allgenes = markers['Unnamed: 0']
	# save the pct values
	pct1 = markers['pct.1']
	pct2 = markers['pct.2']

	# this line will open up your controlled chrome window
	# input the filepath of your chromedriver here
	driver = webdriver.Chrome("/Users/adriennekinman/Desktop/Desktop/CembrowskiLab/Projects/proteinSearch/proteinsearch/proteinSearch_26may23/chromedriver")

	# open protein atlas (or any website of choice)
	driver.get("https://www.proteinatlas.org/")
	curs = []

	##############SEARCH FOR GENES IN LIST#################
	# loop through each each and search for protein expression in the hippocampus and cortex
	for z in range(len(allgenes)):
		cur_gene = allgenes[z]
		cur_pct1 = pct1[z]
		cur_pct2 = pct2[z]

		# locate the search bar and submit button
		# if you are looking to use this code for a different website:
		# go to that website and press option+command+U - this will bring up the source code so you can find elements
		#search_bar = driver.find_element_by_id("searchQuery") method is depreciated, changed to below; 15nov22 AIK
		search_bar = driver.find_element(By.CLASS_NAME, "searchQuery")
		#sub_button = driver.find_element_by_id("searchButton") method is depreciated, changed to below; 15nov22 AIK
		sub_button = driver.find_element(By.CLASS_NAME, "searchButton")

		# search gene names via imported marker gene list
		search_bar.clear()
		search_bar.send_keys(cur_gene)
		sub_button.click()
	
		# get the full gene name 
		# this searches for the second HTML element of the table that pops up after searching a given gene name
		# since the gene of choice may not always be at the top of the list, best to iterate through list
		#cur_names = driver.find_element_by_id("tda") method is depreciated, changed to below; 15nov22 AIK
		cur_names = driver.find_elements(By.ID, "tda")
	
		# if there are no genes found skip to next iteration
		if(len(cur_names)==0):
			continue

		# iterate through list of gene names to find gene in question
		i = 0
		exist = True
		while(cur_names[i].text != cur_gene):
			i+=1
			if(i>=len(cur_names)):
				exist = False
				break

		# if the search results do not bring up the gene name, skip to next iteration
		if(exist != True):
			continue
		
		#save the full name of the gene
		cur_name = cur_names[i+1].text
	
		# select brain tissue protein expression by finding correct gene HTML element
		gene_xpath = "//a[contains(@href, '-" + cur_gene + "/brain')]"
		brain = driver.find_elements(By.XPATH, gene_xpath)

		# if there is no brain tissue info skip
		curs=[]
		if(len(brain) == 0):
			cur_region = "NA"
			cur_ab = "NA"
			cur_neur = "NA"
			cur_glia = "NA"

			# write empty line for gene
			cur = pd.DataFrame([[cur_gene, cur_name, cur_region, cur_ab, cur_neur, cur_glia, cur_pct1, cur_pct2]], columns=co)
			curs.append(cur)
			pd.concat(curs, ignore_index=True) # df.append depreciated; changed to pd.concat 15nov22 AIK 
			continue
		
		brain[0].click()
    	#brain = driver.find_elements_by_xpath(gene_xpath) method is depreciated, changed to below; 15nov22 AIK
		brain = driver.find_elements(By.XPATH, "gene_path")
	
		# select tissue menu
		#tissue = driver.find_element_by_class_name("tissue_menu_opener") method is depreciated, changed to below; 15nov22 AIK
		tissue = driver.find_elements(By.CLASS_NAME, "tissue_menu_opener")
		
		if tissue:
			tissue[0].click()
			
		tissue = driver.find_elements(By.XPATH, '//div/span/a/span')
		
		# convert from web elements to strings
		tissue_text = [None]*len(tissue)
		for y in range(len(tissue)):
			tissue_text[y] = tissue[y].text
	
		if("CEREBRAL CORTEX" in tissue_text):
		
			# click on the hippocampus
			#cortex = driver.find_elements_by_xpath("//a[contains(@href, '/cerebral+cortex')]") method is depreciated, changed to below; 15nov22 AIK
			cortex = driver.find_elements(By.XPATH, "//a[contains(@href, '/cerebral+cortex')]")
			cortex[0].click()
			cur_region = "Cortex"

			# save antibody names as a list
			#ab_h = driver.find_elements_by_class_name("head_nohex") method is depreciated, changed to below; 15nov22 AIK
			ab_h = driver.find_elements(By.CLASS_NAME, "head_nohex")

			if(len(ab_h)==0):
				cur_ab = "NA"
				cur_neur = "NA"
				cur_glia = "NA"

				# write empty line for gene in HC
				cur = pd.DataFrame([[cur_gene, cur_name, cur_region, cur_ab, cur_neur, cur_glia, cur_pct1, cur_pct2]], columns=co)
				curs.append(cur) # df.append depreciated; changed to pd.concat 15nov22 AIK 
				df = pd.concat(curs, ignore_index=True)
			
			else:
				# find parent element of table holding values
				parent = driver.find_element_by_xpath("//table[@class='border dark']") 
				# find the values
				#cells = parent.find_elements_by_tag_name("td") method is depreciated, changed to below; 15nov22 AIK
				cells = parent.find_elements(By.TAG_NAME, "td")

				for x in range(len(ab_h)):
			
					# manually check that there are 4 variables as assumed
					if len(cells)<4:
						# save line to table
						cur = pd.DataFrame([[cur_gene, cur_name, cur_region, cur_ab, "check", "check", cur_pct1, cur_pct2]], columns=co)
						curs.append(cur)
						df = pd.concat(curs, ignore_index=True)
						#df = pd.concat(curs, ignore_index=True) # df.append depreciated; changed to pd.concat 15nov22 AIK
			        
					else:
						cur_ab = ab_h[x].text
						cur_glia = cells[len(ab_h)+x].text
						cur_neur = cells[(len(ab_h)*2)+x].text
					
						#save line to table
						cur = pd.DataFrame([[cur_gene, cur_name, cur_region, cur_ab, cur_neur, cur_glia, cur_pct1, cur_pct2]], columns=co)
						curs.append(cur) # df.append depreciated; changed to pd.concat 15nov22 AIK
						df = pd.concat(curs, ignore_index=True)


		if("HIPPOCAMPAL FORMATION" in tissue_text):
			if("CEREBRAL CORTEX" in tissue_text):
				# open tissue menu
				# tissue = driver.find_element_by_class_name("tissue_menu_opener") method is depreciated, changed to below; 15nov22 AIK
				tissue = driver.find_element(By.CLASS_NAME, "tissue_menu_opener")
				tissue.click()
			# click on the hippocampus
			# hippo = driver.find_elements_by_xpath("//span[@title='Hippocampal formation']") method is depreciated, changed to below; 15nov22 AIK
			hippo = driver.find_elements(By.XPATH, "//span[@title='Hippocampal formation']")
			hippo[0].click()	
			cur_region = "Hippocampus"

			# save antibody names as a list
			# ab_h = driver.find_elements_by_class_name("head_nohex") method is depreciated, changed to below; 15nov22 AIK
			ab_h = driver.find_elements(By.CLASS_NAME, "head_nohex")

			if(len(ab_h)==0):
				cur_a = "NA"
				cur_neur = "NA"
				cur_glia = "NA"
	
				# write empty line for gene in HC
				cur = pd.DataFrame([[cur_gene, cur_name, cur_region, cur_ab, cur_neur, cur_glia, cur_pct1, cur_pct2]], columns=co)
				curs.append(cur) # df.append depreciated; changed to pd.concat 15nov22 AIK
				df = pd.concat(curs, ignore_index=True)
			
			else:
				# find parent element of table holding values
				# parent = driver.find_element_by_xpath("//table[@class='border dark']") method is depreciated, changed to below; 15nov22 AIK
				parent = driver.find_element(By.XPATH, "//table[@class='border dark']")
				# find the values
				# cells = parent.find_elements_by_tag_name("td") method is depreciated, changed to below; 15nov22 AIK
				cells = parent.find_elements(By.TAG_NAME, "td")

				for x in range(len(ab_h)):
					cur_ab = ab_h[x].text
					cur_glia = cells[x].text
					cur_neur = cells[len(ab_h)+x].text
						
					#save line to table
					cur = pd.DataFrame([[cur_gene, cur_name, cur_region, cur_ab, cur_neur, cur_glia, cur_pct1, cur_pct2]], columns=co)
					curs.append(cur) # df.append depreciated; changed to pd.concat 15nov22 AIK
					df = pd.concat(curs, ignore_index=True)
				
	# create the CSV to send to def download below- AIK 26may23
	csv_data = df.to_csv(index=False)

	# allow csv to be both downloaded by the user and dsiplayed on the flask app under heading 'CSV data" - see template.html for more info -AIK 11june23
	if request.method == 'POST':
		csv_file = io.StringIO()
		df.to_csv(csv_file, index=False)
		csv_file.seek(0)

		response = make_response(csv_file.getvalue())
		response.headers['Content-Disposition'] = 'attachment; filename=results.csv'
		response.headers['Content-Type'] = 'text/csv'

		return response
	else:
		csv_data = df.to_html(index=False)
		return render_template('template.html', title='Protein Search', csv_data=df.to_html(index=False))

#Rerout csv data to be downloaded automatically after def search is run - AIK 26may23
@app.route('/download')
def download():
    csv_data = request.args.get('csv_data', '')
    return render_template('download.html', csv_data=csv_data)

# this will run the app - AIK 26nov23 
if __name__ == '__main__':
    app.run()