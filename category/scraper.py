import requests
from bs4 import BeautifulSoup
def scrape_trending_courses(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        target_paragraph = soup.find('p', string="Without further ado, here are the 250 most popular online courses of all time.")
        if target_paragraph:
            target_ul = target_paragraph.find_next('ul')
            if target_ul:
                courses = []
                course_list = target_ul.find_all('li')
                for course in course_list:
                    title = course.get_text(strip=True).split('★★★★★')[0].split('★★★★☆')[0] if course else None
                    rating_div = course.find('div', class_='rating-text')
                    reviews = "No reviews"
                    if rating_div:
                        star_rating = rating_div.get_text(strip=True).split('★')[0] 
                        review_count = rating_div.get_text(strip=True).split('(')[-1].split(')')[0] 
                        if star_rating:
                            reviews = f"{star_rating} stars"
                            if review_count:
                                reviews += f" ({review_count} reviews)"
                    if title: 
                        courses.append({
                            "title": title.strip(),
                        })
                return courses
            else:
                print("Couldn't find the <ul> after the specified <p> tag.")
                return []
        else:
            print("Couldn't find the target <p> tag.")
            return []
    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        return []


