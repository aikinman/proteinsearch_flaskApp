# proteinsearch.py  
An automated web search for human antibodies labelling neurons and glia in the brain.   
This code takes the direct output of Seurat's `FindMarkers()` and returns a data frame of antibodies based on information from the human protein atlas.  


## Instructions:  
1. Cd to location of code (app.py)
2. make a visual env: python3 -m venv venv
3. Activate venv: source venv/bin/activate
4. Download dependencies to this venv: python3 -m pip install -r requirements.txt
5. Download selenium in terminal using this command if fails: pip install selenium 
6. Download chromedriver: https://chromedriver.chromium.org/downloads
7. Change the input file path for chromedriver on line 75 of app.py
8. Ensure you are in the same directory as app.py and run: python3 app.py and Protein Search should open
9. Under Search: choose your csv file and click search
10. Selenium will run heedlessly if right modules were downloaded (have been bugs with order of selenium modules) otherwise will run non-heedlessly
11. When finished, csv with results will automatically be downloaded to your browser and csv results will display under the heading "CSV data" unless the csv is empty, then will display "No data to display" 