from dataclasses import dataclass


@dataclass
class FavoriteLinks:
    name: str
    url: str

    def get_all_links(self):
        pass

    @staticmethod
    def get_favorite_link_by_id(id_favorite_link):
        pass

    def add_favorite_link(self):
        pass

    def edit_favorite_link(self):
        pass

    def delete_favorite_link(self):
        pass
