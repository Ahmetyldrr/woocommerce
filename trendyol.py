class TrendyolMain():
    def __init__(self,sellerId,page,RATE,fileName=None):
        self.session = self.openRequestSession()
        self.sellerId = sellerId
        self.page = page
        self.fileName = fileName
        self.RATE = RATE
        self.curreny = 0
        
        self.translator = Translator()

        self.GET_try_to_dolar()
        mainData = "Handle ,Title,Body (HTML),Vendor,Standardized Product Type,Custom Product Type,Tags,Published,Option1 Name,Option1 Value,Option2 Name,Option2 Value,Option3 Name,Option3 Value,Variant SKU,Variant Grams,Variant Inventory Tracker,Variant Inventory Qty,Variant Inventory Policy,Variant Fulfillment Service,Variant Price,Variant Compare At Price,Variant Requires Shipping,Variant Taxable,Variant Barcode,Image Src,Image Position,Image Alt Text,Gift Card,SEO Title,SEO Description,Google Shopping / Google Product Category,Google Shopping / Gender,Google Shopping / Age Group,Google Shopping / MPN,Google Shopping / AdWords Grouping,Google Shopping / AdWords Labels,Google Shopping / Condition,Google Shopping / Custom Product,Google Shopping / Custom Label 0,Google Shopping / Custom Label 1,Google Shopping / Custom Label 2,Google Shopping / Custom Label 3,Google Shopping / Custom Label 4,Variant Image,Variant Weight Unit,Variant Tax Code,Cost per item,Price / International,Compare At Price / International,Status"
        reviewsData = "Customer country code,Product ID,Customer name,Rating,Content,Customer email,Published date,Image Link"
        self.productSave(mainData)
        self.commentSave(reviewsData)
        self.getSelleridProduct(self.sellerId,self.page)
        print("Urun Sayısı : {}".format(len(self.urls)))
        print("Urun ekleme islemi baslatılacak...")
        self.getProductDetails()

    def getSelleridProduct(self,sellerid,page):
        self.urls = []
        for p in range(1,page+1):
            headers = {
            'authority': 'public.trendyol.com',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'accept': 'application/json, text/plain, */*',
            'authorization': 'Bearer',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://www.trendyol.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            }

            params = (
            ('mid', sellerid),
            ('sellerId', sellerid),
            ('pi', p))

            r = requests.get('https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/sr', headers=headers, params=params)

            data = r.json()
            for dt in data['result']["products"]:
                self.urls.append("https://www.trendyol.com"+dt["url"])

    def openRequestSession(self):
        self.session = requests.Session()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
        Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        self.session.headers = {'User-Agent': user_agent}
        self.session.headers = {'Accept': Accept}
        return self.session
    
    def trendyol_img(self,imgs):
        img_list = []
        for img in imgs :
            img_list.append("https://www.trendyol.com"+img)
        return img_list
    
    def getProductDetails(self):
        progressValue = round(100 / len(self.urls),2)
        value = 0
        for url in self.urls :
            value += progressValue
            imageCount = 1
            rq = self.session.get(url)
            trendData = re.search(r'window.__PRODUCT_DETAIL_APP_INITIAL_STATE__=({.+};window.)', rq.text).group(1)
            trendData = str(trendData).strip().strip(";window.")
            datajson = json.loads(trendData)
            price = round((float(datajson["product"]["price"]["sellingPrice"]["value"]) / self.curreny) * self.RATE,2)
            imgs = self.trendyol_img(datajson["product"]["images"])
            category = self.translateData(datajson["product"]["category"]["name"])
            productName = self.translateData(datajson["product"]["name"]).replace(","," ")
            description = self.translateData(datajson["product"]["contentDescriptions"][0]["description"]).replace(","," ")
            
            variantDetails = self.variantsFilter({"variants":datajson["product"]["allVariants"],"variantCategory":datajson["product"]["variants"][0]["attributeType"],"productGroupId":datajson["product"]["productGroupId"]})
            data = {"title":productName,"productGroupId":datajson["product"]["productGroupId"],"description":description,"price":price,"variants":datajson["product"]["allVariants"],"reviews":datajson["product"]["reviewsUrl"],"images":imgs,"variantCategory":datajson["product"]["variants"][0]["attributeType"]}
            self.variants = variantDetails[1]
            self.variants.reverse()
            self.variant_attr = variantDetails[0]
            self.variant_attr.reverse()

            saveDATA = "{},{},{},REXGOLL,,{},{},TRUE,".format(data["title"].replace(" ","-"),data["title"],data["description"],category,category)
            if len(self.variant_attr) > 1 :
                n = 0
                for attr in self.variant_attr :
                    if n < 3 :
                        saveDATA+= "{},{},".format(attr,self.variants[n][0]["value"])
                    else :
                        break
                    n+=1
                if len(self.variant_attr) == 2 :
                    saveDATA+=",,"
                    
            elif len(self.variant_attr) == 1 :
                saveDATA+= "{},{},,,,,".format(self.variant_attr[0],self.variants[0][0]["value"])
            else :
                saveDATA+=",,,,,,"
            
            quantity = random.randint(50,8888)

            saveDATA+=",200,shopify,{},deny,manual,{},{},TRUE,TRUE,{},{},,FALSE,,,,,,,,,used,FALSE,,,,,,,g,,,,,active".format(quantity,data["price"],data["price"],data["images"][0],imageCount,)            
            self.productSave(saveDATA)
            imageCount+=1
            if len(self.variant_attr) > 1 :
                for one in self.variants[0] :
                    for two in self.variants[1] :
                        saveDATA = "{},,,,,,,,{},{},{},{},,,,,,,,,,,,,,{},{},,,,,,,,,,,,,,,,,,,,,,,,".format(data["title"].replace(" ","-"),
                                                                                                                  self.variant_attr[0],one["value"],
                                                                                                                  self.variant_attr[1],two["value"],
                                                                                                                  one["images"][0],imageCount)
                        self.productSave(saveDATA)
                        imageCount+=1
            elif len(self.variant_attr) == 1 : 
                for one in self.variants[0] :
                    saveDATA = "{},,,,,,,,{},{},,,,,,,,,,,,,,,,{},{},,,,,,,,,,,,,,,,,,,,,,,,".format(data["title"].replace(" ","-"),
                                                                                                            self.variant_attr[0],one["value"],
                                                                                                            data["images"][0],imageCount)
                    self.productSave(saveDATA)
                    imageCount+=1
                    
            for img in data["images"]:
                if img != data["images"][0]:
                    saveDATA = "{},,,,,,,,,,,,,,,,,,,,,,,,,{},{},,,,,,,,,,,,,,,,,,,,,,,,".format(data["title"].replace(" ","-"),img,imageCount)
                    self.productSave(saveDATA)
                    imageCount+=1

            self.commentProcess(data)
            sys.stdout.write(u"\u001b[1000D")
            sys.stdout.write(u"\u001b[2K"+"/"*10+" "+str(round(float(value),2))+"% "+"\\"*10)
            sys.stdout.flush()
        print()
        print("Program Kapatilacek.")

    def variantsFilter(self,data):
        attributes_value = [data["variants"]]
        attr = [data["variantCategory"]]
        attributeURL = "https://public.trendyol.com/discovery-web-websfxproductgroups-santral/api/v1/product-groups/%s"%data["productGroupId"]
        responce = self.session.get(attributeURL).json()
        if len(responce["result"]["slicingAttributes"]) != 0 :
            all = responce["result"]["slicingAttributes"][0]
            attr2 = self.translateData(all["displayName"])
            if len(attr) != 0 :
                attr.append(attr2)
                attributes_value.append([])
                for i in all["attributes"] :
                    attributeImg = []
                    for j in i["contents"]:
                        attributeImg.append("https://cdn.dsmcdn.com%s"%j["imageUrl"])
                        price = round((float(j["price"]["sellingPrice"]["value"]) / self.curreny )* self.RATE,2)
                    name = self.translateData(str(i["beautifiedName"])) 
                    attributes_value[1].append({"value":name,"price":price,"images":attributeImg})   
            
                return (attr,attributes_value)
            else :
                return (attr,attributes_value)
        else :
            return (attr,attributes_value)

    
    def productSave(self,data):
        with open("{}.csv".format(self.fileName),"a+",encoding="UTF-8") as file :
            file.write(data+"\n")
        
    def GET_try_to_dolar(self):
        print("Dolar Kuru alÄ±nÄ±yor..")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"  }
        session = requests.Session()
        session.headers = headers

        try :
            dlr = session.get("https://www.google.com/search?q=usd-try&oq=usd-try&aqs=chrome..69i57j0i512l2j0i30l7.16479j1j7&sourceid=chrome&ie=UTF-8").content
            soup = BeautifulSoup(dlr,"html.parser")
            currency = soup.find("span",{"class":"DFlfde SwHCTb"}).text.replace(",",".")
        except :
            dlr = session.get("https://www.bloomberght.com/doviz/dolar").content
            soup = BeautifulSoup(dlr,"html.parser")
            currency = soup.find("span",{"class":"LastPrice"}).text.text.replace(",",".")
        
        currency = round(float(currency),2)
        
        print("Anlık dolar kuru : {}".format(currency))
        self.curreny = currency
     
    def translateData(self,data):
        try :
            Text = self.translator.translate(data,"en").text
            return Text
        except :
            try :
                Text = TextBlob(data).translate(to="en")
                return Text
            except :
                return data


    def commentProcess(self,data):
        reviewsLink = "https://public-mdc.trendyol.com/discovery-web-socialgw-service/reviews/%s?culture=tr-TR&storefrontId=1&logged-in=false&isBuyer=false"%data["reviews"]
        revReq = self.session.get(reviewsLink)
        trendData = re.search(r'window.__REVIEW_APP_INITIAL_STATE__ = ({.+})', revReq.text).group(1)
        trendData = trendData.strip().strip(";").replace('\\',"")
        
        commentData = []
        mails = ["outlook","hotmail","gmail","yahoo"]
        for trdata in trendData.split("isElite"):
            if trdata.find("isInfluencer") != -1 :
                try :
                    editData = '{"isElite"'+trdata.strip(',{"').strip('"')
                    editData = json.loads(editData)
                    commentData.append(editData)
                except :
                    pass

        if len(commentData) != 0 :
            
            commentCount = randint(0,len(commentData)-1)
            for i in range(0,commentCount):
                img = ""
                selectData = commentData[i]
                userName = selectData["userFullName"]
                try :
                    date = selectData["commentDateISOtype"] + " 12:14:54"
                    date = datetime.fromisoformat(date)
                except :
                    date = "2022-02-06 12:55:19"
                rate = selectData["rate"]
                comment = self.translateData(selectData["comment"])
                e_mail = "{}@{}.com".format(userName,mails[randint(0,3)]).replace(" ","")
                if list(selectData.keys()).count("mediaFiles") != 0 :
                    for j in selectData["mediaFiles"]:
                        img = j["url"]

                saveData = f"EN,{data['title']},{str(userName)},{str(rate)},{str(comment).replace(',','')},{str(e_mail)},{str(date)},{str(img)}"
                self.commentSave(saveData)
            
    def commentSave(self,data):
        with open("{}Comment.csv".format(self.fileName),"a+",encoding="UTF-8") as file :
            file.write(data+"\n")
               
def libraryControl():
    print("Kütüphane Kontrolü yapılıyor...")
    librarys = ["textblob"]
    piplist = os.popen("pip list").read()
    for library in librarys:
        if piplist.find(library) == -1 :
            os.system("pip install {}".format(library))
    print("Kütüphane Kontrolü yapıldı.")
    if os.name in ("nt","dos"):
        os.system("cls")
    else :
        os.system("clear")
        
if __name__ == "__main__":
    from random import randint
    import random
    import sys
    import requests,os,re,json,logging
    libraryControl()
    from datetime import datetime
    from bs4 import BeautifulSoup
    from googletrans import Translator
    from textblob import TextBlob
    
    print("#"*15+" Program Başlatıldı±. "+"#"*15)
    os.system("")
    print(
"""-Program Kullanimi-
SellerID 6 haneli bir sayidir.
Sayfa sayısı verilen sellerIDye ait urunlerin sayfa sayısını belirtir.
Dosya ismi kayıt edilecek dosyanın ismidir. Örn : deneme1
Fiyat oranı urunn normal fiyatÄina ne kadar fark koyacaktır. 
urun : urunn fiyati 5$ fiyat oranina 1.5 verirsek 5 * 1.5 = 7.5$ olarak dosyaya ekler.\n""")
    while True :
        sellerID = input("SellerID Giriniz : ")
        if sellerID != "" and sellerID.isdigit() :
            break
        else :
            print("SellerID yanlistir.")
    while True : 
        try :
            pageCount = input("Sayfa sayısı (Varsayilan 5) : ")
            if pageCount == "" :
                pageCount = 5
                break
            elif type(int(pageCount)) == int :
                break
            else :
                print("Sayfa sayisi 'sayisal bir deger' olmalidir.")
        except :
            print("Sayfa sayisi 'sayisal bir deger' olmalidir.")
            
    fileName = input("Dosya ismi : ")
    while True :
        try :
            rate = input("Fiyat Orani (1.50) : ")
            if rate == "" :
                rate = 1.20
                break
            elif type(float(rate)) == float :
                break
            else :
                print("Fiyat orani 'ondalikli bir deger' olmalidir.")
        except :
            print("Fiyat orani 'ondalikli bir deger' olmalidir.")
    try :
        TrendyolMain(sellerId=sellerID,
                    page=int(pageCount),
                    RATE=float(rate),
                    fileName=fileName)
    except :
        print("Program acılırken sorun ile karsılaşıldı.")
    