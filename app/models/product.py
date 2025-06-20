import json
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from config import headers
from app.models.review import Review
from app.utils import extract
class Product:
    #if doestn work change reviews to opinionsd
    def __init__(self, product_id, reviews=[], product_name='', stats={}):
        self.product_id=product_id
        self.reviews=reviews
        self.product_name=product_name
        self.stats=stats

    def __str__(self):
        return f"""product_id :{self.product_id}
                product_name:{self.product_name}
                stats: {json.dumps(self.stats, indent=4, ensure_ascii=False)}
                reviews:{"\n\n".join([str(review) for review in self.reviews])}
        """
    def reviews_to_dict(self):
        return [review.to_dict() for review in self.reviews]
    def info_to_dict(self):
        return {
            "product_id":self.product_id,
            "product_name": self.product_name,
            "stats":self.stats
        }
    def reviews_name(self):
        next_page=f"https://www.ceneo.pl/{self.product_id}#tab=reviews"
        response = requests.get(next_page, headers = headers)
        if response.status_code==200:
            page_dom=  BeautifulSoup(response.text, "html.parser")
            self.prouct_name=extract(page_dom,  "h1")
        else:
            self.prouct_name=""
        return self
    def extract_reviews(self):
        next_page=f"https://www.ceneo.pl/{self.product_id}#tab=reviews"
        while next_page:
            response = requests.get(next_page, headers = headers)
            print(next_page)
            if response.status_code==200:
                page_dom=  BeautifulSoup(response.text, "html.parser")
                opinions= page_dom.select('div.js_product-review:not(.user-post--highlight)')
                print(len(opinions))
                for opinion in opinions:

                        single_opinion=Review()
                        self.reviews.append(single_opinion.extract_features(review).transform())
            
                try:
                    next_page="https://www.ceneo.pl"+extract(page_dom, 'a.pagination__next', 'href')
                        
                except TypeError:
                    next_page=None
        return self
    def calculate_stats(self):
        reviews=pd.DataFrame.from_dict(self.reviews_to_dict)
        self.stats["reviews_count"]=opinios.shape[0]
        self.stats["pros_count"]=opinios.pros.astype(bool).sum()
        self.stats['cons_count']=opinios.cons.astype(bool).sum()
        self.stats['pros_cons_count']=opinios.apply(lambda r: bool(r.pros) and bool(r.cons), axis=1).sum()
        self.stats[' avarage_score']=round(opinios.stars.mean(), 2)
        return self

    def export_reviews(self):
        if not os.path.exists("./app/data/opinions"):
            os.mkdir("./app/data/opinions")
        with open(f"./app/data/opinions/{self.product_id}.json", "w", encoding="UTF-8") as jf:
            json.dump(self.reviews_to_dict(), jf, indent= 4, ensure_ascii=False)

    def export_info(self):
        if not os.path.exists("./app/data/products"):
            os.mkdir("./app/data/products")
        with open(f"./app/data/products/{self.product_id}.json", "w", encoding="UTF-8") as jf:
            json.dump(self.info_to_dict(), jf, indent= 4, ensure_ascii=False)

