# Web Scrapy for site: **https://www.chewy.com/**

### Get Start
* Clone the project
  `$ git clone https://github.com/cleber-silva-web-scraping/python-requests-chewy.git`

* Enter in directory
  `$ cd python-requests-chewy`

* Instal requirements
  `$ pip install -r requirements`

### Run app
You can run `python app.py -h` to see the helper menu

![image](https://github.com/cleber-silva-web-scraping/python-requests-chewy/assets/6031795/47e623ba-f402-4d26-b0e2-d014e8bb82f0)

### Examples
  * Run first 25% of pages in Dog Category and save results in `dog_result.csv`
    
  `$ python app.py -c dog -p 0-25 -f dog_result.csv`

  * Run second 50%(between 50% and 100%) of pages in Cat Category and save results in `cat_result_50-100.csv`
    
  `$ python app.py -c cat -p 50-100 -f cat_result_50-100.csv`

  * Run first 50%of pages in Fish Category and save results in default format name
    
  `$ python app.py -c fish -p 0-50`
  
  In this case the file name will be `fish_chewy_0-50_YY-MM-DD-HH-mm-ss.csv

### Result demo

![image](https://github.com/cleber-silva-web-scraping/python-requests-chewy/assets/6031795/c7c5aa8d-fd5e-43ee-bfda-3c76692c987b)




