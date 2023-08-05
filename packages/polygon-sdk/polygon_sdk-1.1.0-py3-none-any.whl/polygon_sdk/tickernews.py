import requests
import asyncio
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from cfg import your_api_key

from dataclasses import dataclass



@dataclass
class Publisher:
    def __init__(self, name, homepage_url, logo_url, favicon_url):
        self.name = name
        self.homepage_url = homepage_url
        self.logo_url = logo_url
        self.favicon_url = favicon_url
@dataclass
class NewsArticle:
    def __init__(self, id, publisher, title, author, published_utc, article_url, tickers, image_url, description, keywords):
        self.id = id
        self.publisher = publisher
        self.title = title
        self.author = author
        self.published_utc = published_utc
        self.article_url = article_url
        self.tickers = tickers
        self.image_url = image_url
        self.description = description
        self.keywords = keywords
        
keyword_hooks= {
        "Trading Ideas": "https://discord.com/api/webhooks/1092833972125446196/2U9W_bgxJBR0iQKmFTfYg67SjKO3c5-QBZi3kiIxCbfgWQQdhYRQIyKkLGwRNM4e8I68",
        "Long Ideas": "https://discord.com/api/webhooks/1092833972125446196/2U9W_bgxJBR0iQKmFTfYg67SjKO3c5-QBZi3kiIxCbfgWQQdhYRQIyKkLGwRNM4e8I68",
        "Short Sellers":"https://discord.com/api/webhooks/1092833972125446196/2U9W_bgxJBR0iQKmFTfYg67SjKO3c5-QBZi3kiIxCbfgWQQdhYRQIyKkLGwRNM4e8I68",
        "Trading Penny Stocks":"https://discord.com/api/webhooks/1092833972125446196/2U9W_bgxJBR0iQKmFTfYg67SjKO3c5-QBZi3kiIxCbfgWQQdhYRQIyKkLGwRNM4e8I68",
        "penny stocks to watch":"https://discord.com/api/webhooks/1092833972125446196/2U9W_bgxJBR0iQKmFTfYg67SjKO3c5-QBZi3kiIxCbfgWQQdhYRQIyKkLGwRNM4e8I68",
        "top penny stocks":"https://discord.com/api/webhooks/1092833972125446196/2U9W_bgxJBR0iQKmFTfYg67SjKO3c5-QBZi3kiIxCbfgWQQdhYRQIyKkLGwRNM4e8I68",
        "Short Ideas": "https://discord.com/api/webhooks/1092833972125446196/2U9W_bgxJBR0iQKmFTfYg67SjKO3c5-QBZi3kiIxCbfgWQQdhYRQIyKkLGwRNM4e8I68",
        "Penny Stock News":"https://discord.com/api/webhooks/1092835547715739668/JEly4eLjlTOCwAv2sGI8jI9QwXzlmwmNzce6xKugCB0cGH_E2vusLKHBUXWfGtSDKGoN",
        "Tech":"https://discord.com/api/webhooks/1094258778804850798/MZbD0QhX1wJ6M7pgWSox7wgOY6YNUm2ALNHa9sqCqMqkXrHqgvKsuzbfvE05cVD93kfR",
        "Rumors":"https://discord.com/api/webhooks/1094258987203055706/8yhqkJyZ0IkSU0Is-R-1fh16dq-4VP_F4aCCLo2jLkvp5a6ej2dEfIpx9cf7rpXnjc9w",
        "Penny Stocks": "https://discord.com/api/webhooks/1092835547715739668/JEly4eLjlTOCwAv2sGI8jI9QwXzlmwmNzce6xKugCB0cGH_E2vusLKHBUXWfGtSDKGoN",
        "best penny stocks":"https://discord.com/api/webhooks/1092835547715739668/JEly4eLjlTOCwAv2sGI8jI9QwXzlmwmNzce6xKugCB0cGH_E2vusLKHBUXWfGtSDKGoN",
        "list of penny stocks":"https://discord.com/api/webhooks/1092835547715739668/JEly4eLjlTOCwAv2sGI8jI9QwXzlmwmNzce6xKugCB0cGH_E2vusLKHBUXWfGtSDKGoN",
        "Large Cap": "https://discord.com/api/webhooks/1092835309173100617/357tYJFdLnlWoaqcJ9Ra6iqF3ePF82zLDwAzb64F3-vQV1iy3vZplOch5tQSlZYtiCQw",
        "Upgrades": "https://discord.com/api/webhooks/1092835115928920138/OVViNx1aUVaONOfCJDAZjK_u9_R3Rxalfc8FrC5dXyZYRAJa9teErpF2IzgmNMFRSn0Z",
        "Downgrades":"https://discord.com/api/webhooks/1092835047595319336/sUBaeSrfII0zz0LmD-54NVGDGHSd9mOjkR-ZTebAawskaO5Y3EkmWLEmpJ282zU2LZhz",
        "Price Target": "https://discord.com/api/webhooks/1092834977621749911/w92AWpuFI6itXAtpP0sWct1wk_qPEV0BKJvbkuXEpQ0CJKghPxjc4lT6ddLxIdYd_BNe",
        "Small Cap": "https://discord.com/api/webhooks/1092835220484534342/Ul7jnhtP6rdm1w0pvonrvbDZxvY46-sd6mJzzRkCvAfdw-mmGds_WFh2GGUJlZLkM2Gz",
        "Analyst Ratings": "https://discord.com/api/webhooks/1092834903470637157/aBM0LkKpdkhaLGBQ1M5oe90Vm6i4tbluZG0qENZZb2qWDRDJg3A7WpZ0-kcDR_o4j6Hi",
        "Initial Public Offerings": "https://discord.com/api/webhooks/1092836367492452412/qsNyXVqIMqDrZ6iMEkjQWH1AyzybuYIGmQu8P2Ssret3LgesWTmTHmijZ64Ms9Q-y3f0",
        "Financing Agreements": "https://discord.com/api/webhooks/1092837447504773220/h020DYgyTXCy1uezc7-RT_JTxYHTSmeV3luru-wkDKXwoTttbWjNWy0Yn9Pho3eS2Bvy",
        "Conference Calls/ Webcasts":"https://discord.com/api/webhooks/1092837199734652978/yHGhhmol0htH-kOMblOSSgHOM_fWWgarszKaTzH47tfAiRoBLRHFpN5Se-SBpHfX6x5C",
        "Calendar of Events": "https://discord.com/api/webhooks/1094059802440777778/9xZ2bGfHyFzSRBrYwJrMrlzAPxj2rGaVb8nrJ42H1Af_i9M7fkKke515Cz5O4QscMuau",
        "Law & Legal Issues":"https://discord.com/api/webhooks/1092837729856921660/uVYiEsEw0BLghmEEjcdxXniqL33Wbqrh8uLs84f4ETQW1DpSE0rxnE_FYq787MYl_PBs",
        "Company Announcement":"https://discord.com/api/webhooks/1092838958964166806/DkSJI1Avv50Z4dikKP9_8stdHW6oABe0mjaH8qb0NVVNVMaVDvfj8bajx4h2_6D_3QIe",
        "Earnings":"https://discord.com/api/webhooks/1092839677049966724/Qgqxhct-9Xe7ChpPWpPah4DjEqu4vvTV4CCI6Gj6H6dKQx0t7HMNfWowxlabEvRT2ip_",
        "earningscall-transcripts":"https://discord.com/api/webhooks/1092839677049966724/Qgqxhct-9Xe7ChpPWpPah4DjEqu4vvTV4CCI6Gj6H6dKQx0t7HMNfWowxlabEvRT2ip_",
        "Earnings Releases and Operating Results":"https://discord.com/api/webhooks/1092839677049966724/Qgqxhct-9Xe7ChpPWpPah4DjEqu4vvTV4CCI6Gj6H6dKQx0t7HMNfWowxlabEvRT2ip_",
        "Partnerships":"https://discord.com/api/webhooks/1092839861330903090/dBn2wDaGkpcNWBCuZeNRCba9isnyP1iMft6CYcFw4LIwqN-oDEKW5zerx4pyqc5km1Nz",
        "Mergers and Acquisitions":"https://discord.com/api/webhooks/1092839861330903090/dBn2wDaGkpcNWBCuZeNRCba9isnyP1iMft6CYcFw4LIwqN-oDEKW5zerx4pyqc5km1Nz",
        "Movers":"https://discord.com/api/webhooks/1092840263833092216/Ss4XcUcqtkXtqEnV0CxXjtvrfyMuuEsWLOkHQF51k2HP2z9vwc-IiRWenuEcaDbXK9r8",
        "Cryptocurrency":"https://discord.com/api/webhooks/1092840944539271269/L38cTbRcX-rBHgRNy0w2s6okUtWmQswld2SwWvC2oCgb1VjATF6qTy8lagoDD_f3C8L4",
        "Top Stories":"https://discord.com/api/webhooks/1092841025069916160/Qpx0k0YguT_30YfWu2v9Od7fUahPcqghYGHsTJ8PVmgYqL4liZ0MXgEcCYwl97QkN_P5",
        "Global":"https://discord.com/api/webhooks/1092841301814280313/U1vXv-NTX8GHhCsEmwgos77-R5q8HELYsBTHRZ791OfFHjeR7iaDgUyDSjZVdxmO3HFA",
        "Government":"https://discord.com/api/webhooks/1092841301814280313/U1vXv-NTX8GHhCsEmwgos77-R5q8HELYsBTHRZ791OfFHjeR7iaDgUyDSjZVdxmO3HFA",
        "European Regulatory News": "https://discord.com/api/webhooks/1092841823422124052/d2zPUfg9jbpBh4qOrB3H0AxgREK2EWUzSlLaUFMd7GlUUsOWhso1NQMovO-hptZwCuv8",
        "Sector ETFs": "https://discord.com/api/webhooks/1092842400810029097/nqBcxliNoU4SOGkZBkGMl3Y9aCvNev9rkIu1C0sWyvo3HDbUvnYwxHdxczacxSB5bt6W",
        "Broad U.S. Equity ETFs": "https://discord.com/api/webhooks/1092842400810029097/nqBcxliNoU4SOGkZBkGMl3Y9aCvNev9rkIu1C0sWyvo3HDbUvnYwxHdxczacxSB5bt6W",
        "Management statements": "https://discord.com/api/webhooks/1092838958964166806/DkSJI1Avv50Z4dikKP9_8stdHW6oABe0mjaH8qb0NVVNVMaVDvfj8bajx4h2_6D_3QIe",
        "ETFs": "https://discord.com/api/webhooks/1092842400810029097/nqBcxliNoU4SOGkZBkGMl3Y9aCvNev9rkIu1C0sWyvo3HDbUvnYwxHdxczacxSB5bt6W",
        "investing": "https://discord.com/api/webhooks/1092833972125446196/2U9W_bgxJBR0iQKmFTfYg67SjKO3c5-QBZi3kiIxCbfgWQQdhYRQIyKkLGwRNM4e8I68",
        "Company Regulatory Filings": "https://discord.com/api/webhooks/1094060111745519726/rXI0oK_KFSMGB50SkRcJtJ1yJU7JFePklpyAEgOc08EaLZb7inJkh-SE6XCvhtVPziZY",
        "Insider's Buy/Sell": "https://discord.com/api/webhooks/1094257776064213164/6jtzlZg-Pp_t2TL4Pi61o8N63OMddcWR2DMVFM8SVSNy7dSPrs-keYzL6iHAHREgptJ5"

    }