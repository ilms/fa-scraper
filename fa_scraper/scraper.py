from bs4 import BeautifulSoup
from typing import List, Optional, Tuple
import requests
import json

from .cooldown import Cooldown
from .models import Favorite, Post


_global_scraper_cd = Cooldown(1)


class Scraper:
    def __init__(self):
        self._session = requests.Session()

    def login(self, cookies_path: str) -> None:
        with open(cookies_path) as file:
            cookies = json.load(file)
            for cookie in cookies:
                domain = cookie["domain"]
                name = cookie["name"]
                value = cookie["value"]
                self._session.cookies.set(domain=domain, name=name, value=value)

    @_global_scraper_cd
    def get_post(self, post_id: int) -> Post:
        """
        Gets post details from a post id.

        :param post_id: The id of the post
        :return: Post containing information scraped from the FA post.
        """
        url = f"https://www.furaffinity.net/view/{post_id}/"
        page = self._session.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        preview_url = soup.find("meta", attrs={"property": "og:image:secure_url"}).attrs["content"]
        content_url = soup.find(class_="download").find("a").attrs["href"]
        content_type = content_url.split(".")[-1]
        view_count = int(soup.find(class_="views").find("span").text)
        fav_count = int(soup.find(class_="favorites").find("span").text)
        rating = soup.find(class_="rating-box").text
        title = soup.find(class_="submission-title").find("p").text
        creator = soup.find(class_="minigallery-more").find("a").text
        tags_row = soup.find(class_="tags-row")
        tags = [tag.text for tag in tags_row.find_all("a")]
        return Post(
            id=post_id,
            source=url,
            preview_url=preview_url,
            content_url=content_url,
            content_type=content_type,
            view_count=view_count,
            fav_count=fav_count,
            rating=rating,
            title=title,
            creator=creator,
            tags=tags,
        )

    @classmethod
    def _build_fav(cls, figure, user: str) -> Favorite:
        fav_id = int(figure.attrs["data-fav-id"])
        post_id = int(figure.attrs["id"][4:])
        return Favorite(
            id=fav_id,
            post_id=post_id,
            user=user,
        )

    @_global_scraper_cd
    def get_favorites(self, user: str, after: Optional[int] = None) -> Tuple[List[Favorite], Optional[int]]:
        """
        Returns a list of a user's favorites.

        :param user: The username of the favorite owner
        :param after: The last fav id of the previous page
        :return: A 2-tuple of
            1. a list of Favorite and
            2. int representing the last fav id, None if last page
        """
        url = f"https://www.furaffinity.net/favorites/{user}/"
        if after is not None:
            url += f"{after}/next"
        page = self._session.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        gallery = soup.find(id="gallery-favorites")
        figures = gallery.find_all("figure")
        next_button = soup.find(class_="pagination").find(class_="right")
        last_id = None
        if next_button is not None:
            last_id = int(figures[-1].attrs["data-fav-id"])
        return [self._build_fav(figure, user) for figure in figures], last_id

    @_global_scraper_cd
    def get_gallery(self, user: str, page: Optional[int] = 1) -> List[int]:
        """
        Returns a list of post id's from a users gallery

        :param user: The username of the gallery owner
        :param page: The gallery page
        :return: A list of post id's
        """
        url = f"https://www.furaffinity.net/gallery/{user}/"
        if page > 1:
            url += f"{page}/"
        page = self._session.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        gallery = soup.find(id="gallery-gallery")
        figures = gallery.find_all("figure")
        return [int(figure.attrs["id"][4:]) for figure in figures]
