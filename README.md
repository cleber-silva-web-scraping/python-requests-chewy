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

![image](https://github.com/cleber-silva-web-scraping/python-requests-chewy/assets/6031795/def65e99-11bb-4bac-aa02-9e3e5844dad7)


### Examples
  * Run first 25% of pages in Dog Category and save results in `dog_result.csv`
    
  `$ python app.py -c dog -p 0-25 -f dog_result.csv`

  * Run second 50%(between 50% and 100%) of pages in Cat Category and save results in `cat_result_50-100.csv`
    
  `$ python app.py -c cat -p 50-100 -f cat_result_50-100.csv`

  * Run first 50%of pages in Fish Category and save results in default format name
    
  `$ python app.py -c fish -p 0-50`
  
  In this case the file name will be `fish_chewy_0-50_YY-MM-DD-HH-mm-ss.csv
  
### Proxies
  * You can use any proxy with parameter `--proxy`
    
    `$ python app.py -c dog -p 0-25 -f dog_result.csv --proxy xxx.xxx.xxx.xxx:yyyy`
    
    `$ python app.py -c dog -p 0-25 -f dog_result.csv --proxy http://user:pass@xxx.xxx.xxx.xxx:yyyy`
    

### Result demo

![image](https://github.com/cleber-silva-web-scraping/python-requests-chewy/assets/6031795/c7c5aa8d-fd5e-43ee-bfda-3c76692c987b)


### Runners

The site Chewy has a ton of products and does not allow simultaneous access from the same origin. If you want to run various processes from the same IP address, you will need to use a lot of proxies.

I've prepared an app called multi_runners.py that can distribute all proxies for a range of pages for each category.

The categories dog and cat are larger, so the runner will split processes to run 2% each.

Other categories will be split for 5%.

#### How to run **runnner.py**

* prepare a file called `proxy.list` you can see an example at `proxy.list.example`
  - example
    ```
    111.222.331.444:8888
    111.222.332.444:8888
    111.222.333.444:8888
    111.222.334.444:8888
    111.222.335.444:8888
    111.222.336.444:8888
    
    ```
  * Proxy Service:
    - The **best** proxy service form me is **proxyscrape**(https://bit.ly/49BjmSL) with Unlimited bandwidth and fix good price
    ![image](https://github.com/cleber-silva-web-scraping/python-requests-chewy/assets/6031795/3cc9f737-a175-4819-bebb-20ab6c68be2e)

    * for the current configuration you will need **240** different proxies to all run on the same machine (source) 
    * **runner.py** will prepare **240** prompts like this:
    ```
      python app.py -c dog -p 0-2 --proxy 154.202.96.xxx:8080
      python app.py -c dog -p 2-4 --proxy 154.202.97.xxx:8080
      python app.py -c dog -p 4-6 --proxy 154.84.143.xxx:8080
      python app.py -c dog -p 15-20 --proxy 154.202.97.xxx:8080
      python app.py -c dog -p 20-25 --proxy 154.201.61.xxx:8080
      python app.py -c dog -p 25-30 --proxy 154.84.143.xxx:8080
      python app.py -c dog -p 30-35 --proxy 154.201.62.xxx:8080
      python app.py -c dog -p 35-40 --proxy 154.202.120.xxx:8080
      python app.py -c dog -p 40-45 --proxy 154.202.110.xxx:8080
      python app.py -c dog -p 45-50 --proxy 154.202.110.xxx:8080
      python app.py -c dog -p 50-55 --proxy 154.201.63.xxx:8080
      python app.py -c dog -p 55-60 --proxy 154.201.63.xxx:8080
      python app.py -c dog -p 60-65 --proxy 154.202.110.xxx:8080
      python app.py -c dog -p 65-70 --proxy 154.201.63.xxx:8080
      python app.py -c dog -p 70-75 --proxy 154.202.111.xxx:8080
      python app.py -c dog -p 75-80 --proxy 154.202.112.xxx:8080
      python app.py -c dog -p 80-85 --proxy 50.117.66.xxx:8080
      python app.py -c dog -p 85-90 --proxy 154.201.61.xxx:8080
      python app.py -c dog -p 90-95 --proxy 50.117.66.xxx:8080
      python app.py -c dog -p 95-100 --proxy 154.202.109.xxx:8080
      python app.py -c cat -p 0-5 --proxy 154.202.97.xxx:8080
      python app.py -c cat -p 5-10 --proxy 154.202.110.xxx:8080
      python app.py -c cat -p 10-15 --proxy 154.202.107.xxx:8080
      python app.py -c cat -p 15-20 --proxy 154.202.98.xxx:8080
      python app.py -c cat -p 20-25 --proxy 154.201.62.xxx:8080
      python app.py -c cat -p 25-30 --proxy 154.202.110.xxx:8080
      python app.py -c cat -p 30-35 --proxy 154.84.143.xxx:8080
      python app.py -c cat -p 35-40 --proxy 154.201.62.xxx:8080
      python app.py -c cat -p 40-45 --proxy 154.201.62.xxx:8080
      python app.py -c cat -p 45-50 --proxy 154.84.142.xxx:8080
      python app.py -c cat -p 50-55 --proxy 154.202.109.xxx:8080
      python app.py -c cat -p 55-60 --proxy 154.202.110.xxx:8080
      python app.py -c cat -p 60-65 --proxy 154.201.63.xxx:8080
      python app.py -c cat -p 65-70 --proxy 154.84.142.xxx:8080
      python app.py -c cat -p 70-75 --proxy 154.202.98.xxx:8080
      python app.py -c cat -p 75-80 --proxy 154.202.122.xxx:8080
      python app.py -c cat -p 80-85 --proxy 154.84.143.xxx:8080
      python app.py -c cat -p 85-90 --proxy 154.201.62.xxx:8080
      python app.py -c cat -p 90-95 --proxy 154.84.143.xxx:8080
      python app.py -c cat -p 95-100 --proxy 154.84.143.xxx:8080
      python app.py -c fish -p 0-10 --proxy 154.202.108.xxx:8080
      python app.py -c fish -p 10-20 --proxy 154.202.120.xxx:8080
      python app.py -c fish -p 20-30 --proxy 154.202.120.xxx:8080
      python app.py -c fish -p 30-40 --proxy 154.202.98.xxx:8080
      python app.py -c fish -p 40-50 --proxy 154.201.62.xxx:8080
      python app.py -c fish -p 50-60 --proxy 154.202.98.xxx:8080
      python app.py -c fish -p 60-70 --proxy 154.202.97.xxx:8080
      python app.py -c fish -p 70-80 --proxy 154.201.62.xxx:8080
      python app.py -c fish -p 80-90 --proxy 154.202.120.xxx:8080
      python app.py -c fish -p 90-100 --proxy 154.202.98.xxx:8080
      python app.py -c bird -p 0-10 --proxy 154.202.109.xxx:8080
      python app.py -c bird -p 10-20 --proxy 154.202.98.xxx:8080
      python app.py -c bird -p 20-30 --proxy 154.84.143.xxx:8080
      python app.py -c bird -p 30-40 --proxy 154.202.97.xxx:8080
      python app.py -c bird -p 40-50 --proxy 154.84.143.xxx:8080
      python app.py -c bird -p 50-60 --proxy 154.202.122.xxx:8080
      python app.py -c bird -p 60-70 --proxy 154.202.120.xxx:8080
      python app.py -c bird -p 70-80 --proxy 154.202.98.xxx:8080
      python app.py -c bird -p 80-90 --proxy 154.202.98.xxx:8080
      python app.py -c bird -p 90-100 --proxy 154.202.98.xxx:8080
      python app.py -c small-pet -p 0-10 --proxy 154.201.61.xxx:8080
      python app.py -c small-pet -p 10-20 --proxy 50.117.66.xxx:8080
      python app.py -c small-pet -p 20-30 --proxy 154.202.121.xxx:8080
      python app.py -c small-pet -p 30-40 --proxy 154.202.109.xxx:8080
      python app.py -c small-pet -p 40-50 --proxy 154.202.120.xxx:8080
      python app.py -c small-pet -p 50-60 --proxy 154.201.62.xxx:8080
      python app.py -c small-pet -p 60-70 --proxy 154.84.142.xxx:8080
      python app.py -c small-pet -p 70-80 --proxy 154.202.122.xxx:8080
      python app.py -c small-pet -p 80-90 --proxy 154.202.108.xxx:8080
      python app.py -c small-pet -p 90-100 --proxy 154.202.97.xxx:8080
      python app.py -c reptile -p 0-10 --proxy 154.202.98.xxx:8080
      python app.py -c reptile -p 10-20 --proxy 50.117.66.xxx:8080
      python app.py -c reptile -p 20-30 --proxy 154.201.61.xxx:8080
      python app.py -c reptile -p 30-40 --proxy 154.202.110.xxx:8080
      python app.py -c reptile -p 40-50 --proxy 154.202.121.xxx:8080
      python app.py -c reptile -p 50-60 --proxy 154.202.108.xxx:8080
      python app.py -c reptile -p 60-70 --proxy 154.202.122.xxx:8080
      python app.py -c reptile -p 70-80 --proxy 154.202.109.xxx:8080
      python app.py -c reptile -p 80-90 --proxy 50.117.66.xxx:8080
      python app.py -c reptile -p 90-100 --proxy 154.202.96.xxx:8080
      python app.py -c horse -p 0-10 --proxy 154.202.96.xxx:8080
      python app.py -c horse -p 10-20 --proxy 154.202.99.xxx:8080
      python app.py -c horse -p 20-30 --proxy 154.202.97.xxx:8080
      python app.py -c horse -p 30-40 --proxy 154.202.111.xxx:8080
      python app.py -c horse -p 40-50 --proxy 154.201.61.xxx:8080
      python app.py -c horse -p 50-60 --proxy 154.201.63.xxx:8080
      python app.py -c horse -p 60-70 --proxy 154.202.108.xxx:8080
      python app.py -c horse -p 70-80 --proxy 154.84.142.xxx:8080
      python app.py -c horse -p 80-90 --proxy 154.202.97.xxx:8080
      python app.py -c horse -p 90-100 --proxy 154.84.143.xxx:8080
      python app.py -c pharmacy -p 0-10 --proxy 154.202.109.xxx:8080
      python app.py -c pharmacy -p 10-20 --proxy 154.84.143.xxx:8080
      python app.py -c pharmacy -p 20-30 --proxy 154.202.110.xxx:8080
      python app.py -c pharmacy -p 30-40 --proxy 154.202.122.xxx:8080
      python app.py -c pharmacy -p 40-50 --proxy 154.201.61.xxx:8080
      python app.py -c pharmacy -p 50-60 --proxy 154.202.96.xxx:8080
      python app.py -c pharmacy -p 60-70 --proxy 50.117.66.xxx:8080
      python app.py -c pharmacy -p 70-80 --proxy 154.202.121.xxx:8080
      python app.py -c pharmacy -p 80-90 --proxy 154.202.97.xxx:8080
      python app.py -c pharmacy -p 90-100 --proxy 154.202.110.xxx:8080
      python app.py -c farm-animal -p 0-10 --proxy 154.202.97.xxx:8080
      python app.py -c farm-animal -p 10-20 --proxy 154.202.109.xxx:8080
      python app.py -c farm-animal -p 20-30 --proxy 50.117.66.xxx:8080
      python app.py -c farm-animal -p 30-40 --proxy 154.202.120.xxx:8080
      python app.py -c farm-animal -p 40-50 --proxy 154.202.121.xxx:8080
      python app.py -c farm-animal -p 50-60 --proxy 154.201.61.xxx:8080
      python app.py -c farm-animal -p 60-70 --proxy 154.202.110.xxx:8080
      python app.py -c farm-animal -p 70-80 --proxy 154.202.120.xxx:8080
      python app.py -c farm-animal -p 80-90 --proxy 50.117.66.xxx:8080
      python app.py -c farm-animal -p 90-100 --proxy 154.202.98.xxx:8080

    ```
    * To run
      
    `$ python runner.py`

    ### The output:
    ![image](https://github.com/cleber-silva-web-scraping/python-requests-chewy/assets/6031795/c7efb3d6-3e1d-4ca9-acdc-ed7b3fa1091e)


    ### The result in folder:
    ![image](https://github.com/cleber-silva-web-scraping/python-requests-chewy/assets/6031795/c14ac790-68f3-452b-94d2-3e9845fc8b9f)

    ### Files per category `[category]_all.csv`(using `multi_runners.py`)
    ![image](https://github.com/cleber-silva-web-scraping/python-requests-chewy/assets/6031795/0ee6d8ef-6577-4103-a991-2e063ead877a)



