import sys
import os
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

from pyvirtualdisplay import Display

# NOTE: This crawler cannot be multi-threaded, because selenium is not thread safe.
# Might look into multiprocess in the future...

# Installs extension and sets target directory
def setup(folder):
    chop = webdriver.ChromeOptions()

#   service_log_path = 'chromedriver.log'
#   service_args = ['--verbose']

    chop.add_argument('--disable-gpu')

    # The adblocker extension for preventing unexpected popups in the form of advertisements and redirects
    chop.add_extension('Adblock-Plus_v1.13.2.crx')

    # Disable images from being loaded
    prefs = {'download.default_directory': folder}
    chop.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome('/usr/local/bin/chromedriver',chrome_options=chop)
#       service_args=service_args,
#       service_log_path=service_log_path)

    return driver

# Crawler function
def mycrawler(urllist, folder):
    # Set up crawler
    driver = setup(folder)

    print 'After setup'

    # Opens the first page of the category specified by the URL
    driver.get(urllist[0])
    try:
        default_handle = driver.current_window_handle
        handles = list(driver.window_handles)
        assert len(handles) > 1, 'Contains only one frame before closing one'
    except Exception as e:
        print 'Assertion exception: {0}'.format(str(e))
        return
    driver.switch_to_window(handles[1])
    driver.close()
    driver.switch_to_window(handles[0])

    itemXpath = "//a[@class='item-anchor']"

    # For each page
    for i in range(0,len(urllist)):
        print 'getting {0}'.format(urllist[i])
        driver.get(urllist[i])

        # There are 10 items to download on each page
        for j in range(0,10):
            sys.stdout.write('   item {0}: '.format(j))
            start = time.time()

            try:
                items = WebDriverWait(driver,10).until(lambda driver: driver.find_elements_by_xpath(itemXpath))
                link = items[j].get_attribute('href')
                spanXpath = "//a[@class='item-anchor'][" + str(j+1) + "]/div/div/div/span"

                # The number of span elements to identify whether it is an
                # external file, which crashes this crawler-Reason unknown yet
                no_span = WebDriverWait(driver,10).until(lambda driver: driver.find_elements_by_xpath(spanXpath))

                if len(no_span) != 4:
                    driver.get(link)
                    dlmsg = WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_xpath("//span[@id='button-dlm-sub-message-info']"))
                    if dlmsg.text == 'External Download Site':
                        continue
                    WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_xpath("//a[@class='dln-a']")).click()
                else:
                    pass

            except TimeoutException:
                print '    There was a timeout during url: {0} at element {1}'.format(urllist[i], j)
            except WebDriverException as e:
                print '    Element not clickable {0} for url: {1} at element {2}'.format(e, urllist[i], j)
            except Exception as e:
                print '    Exception: {0}'.format(str(e))

            finally:
                driver.execute_script("window.open('" + urllist[i] + "')")
                driver.switch_to_window(driver.window_handles[0])
                driver.close()
                driver.switch_to_window(driver.window_handles[0])
                sys.stdout.write('{0} seconds\n'.format(time.time()-start))

        # Print status
        print '{0} done'.format(urllist[i])

    # Exit crawler
    driver.quit()

def usage():
    print 'usage: python crawler.py target-folder/'
    sys.exit(2)

def _main():
    if len(sys.argv) != 2:
        usage()

    folder = sys.argv[1]

    # If this folder doesn't exist yet, create it
    if not os.path.exists(folder):
        os.mkdir(folder)

    # Get full path of folder
    folder = os.path.abspath(folder)
    print folder

    # Start up display
    display = Display(visible=0, size=(800, 800))  
    display.start()

    # Read each URL
    with open('urllist.txt','r') as fr:
        for line in fr:
            line = line.strip('\n')
            url,end,directory = line.split(' ')
            print url,end,directory

            # Directory this category's samples will be downloaded to
            target = os.path.join(folder,directory)

            # If this folder doesn't exist yet, create it
            if not os.path.exists(target):
                os.mkdir(target)

            # URL to pass to Chrome
            urllist = [url]

            # For each page of the URL
            for i in range(2,int(end)+1):
                urllist.append(url + '?page=' + str(i))

            # Run the crawler
            mycrawler(urllist,target)

    # Stop display
    display.stop()

if __name__=='__main__':
    _main()
