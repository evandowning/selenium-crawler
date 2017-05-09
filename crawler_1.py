from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

def setup():
    chop = webdriver.ChromeOptions()
    chop.add_extension('Adblock-Plus_v1.13.2.crx')
    prefs = {"download.default_directory": "/Volumes/LLEWELLYN/final/"}
    chop.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=chop)
    return driver
def mycrawler(urllist):
    #for i in range(20, 200):
    driver = setup()
    driver.get(urllist[0])
    try:
        default_handle = driver.current_window_handle
        handles = list(driver.window_handles)
        assert len(handles) > 1,"Contains only one frame before closing one"
        #handles.remove(default_handle)
        #assert len(handles) > 0,"Contains no frames in window"
    except:
        print "Assertion exception"
    driver.switch_to_window(handles[1])
    driver.close()
    driver.switch_to_window(handles[0])
    for i in range(0,2):
        driver.get(urllist[i])
        #driver.switch_to_window(handles[0])
        #print driver.find_element_by_tag_name("title").text

        itemXpath = "//a[@class='item-anchor']"
        for j in range(0,10):
            try:
                items = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_xpath(itemXpath))
                link=items[j].get_attribute('href')
                spanXpath = "//a[@class='item-anchor']["+str(j+1)+"]/div/div/div/span"
                #number of span elements to identify whether it is an external file, which crashes this crawler-Reason unknown yet---FIXED, indexed element is one navigation down, not the parent page.
                no_span=WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_xpath(spanXpath))
                #print len(no_span)
                if len(no_span)!=4:
                    driver.get(link)
                    dlmsg=WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_xpath("//span[@id='button-dlm-sub-message-info']"))
                    if dlmsg.text=="External Download Site":
                        continue
                    WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//a[@class='dln-a']")).click()
                    try:
                        #WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//p[@class='poweredBy']"))
                        #driver.execute_script("window.open('" + urllist[i] + "')")
                        sleep(4)
                        #driver.execute_script("window.history.go(-2)")
                    except:
                        print "Exception through while waiting on *powered by element* in the final download page of element:"+str(j)
                else:
                    pass
            except TimeoutException:
                print "There was a timeout during url:"+str(urllist[i])+" at element "+str(j)
            except WebDriverException as e:
                print "Element not clickable"+str(e)+" for url:"+str(urllist[i])+" at element "+str(j)
            except e:
                print e
            finally:
                driver.execute_script("window.open('" + urllist[i] + "')")
                driver.switch_to_window(driver.window_handles[0])
                driver.close()
                driver.switch_to_window(driver.window_handles[0])
        print urllist[i]+" done"
        sleep(10)
    driver.quit()

if __name__=='__main__':
    urllist=["http://download.cnet.com/s/drivers/windows/"]
    for i in range(2,5572):
        urllist.append("http://download.cnet.com/s/drivers/windows/?page="+str(i))
    mycrawler(urllist)
