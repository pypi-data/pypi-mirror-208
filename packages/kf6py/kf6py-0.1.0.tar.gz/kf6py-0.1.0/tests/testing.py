#%%
import dotenv
import os

from kf6py import KF6API


dotenv.load_dotenv()
kfurl = os.environ.get("KF6_URL")
username = os.environ.get("KF6_USERNAME")
password = os.environ.get("KF6_PASSWORD")

kf6api = KF6API(kfurl, username, password)
#%%
kf6api.get_my_communities()

curr = {
    "community": "63c635b2058caca6a83208fa",
    "view": "63c635b2058caca6a832091e"
}
#%%
kf6api.get_views(curr['community'])
#%%
kf6api.get_notes_from_view(curr['community'], curr["view"])
#%%
kf6api.create_contribution(curr['community'], curr['view'], 'another code', 'hello')

# %%
